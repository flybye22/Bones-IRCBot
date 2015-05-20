# -*- encoding: utf-8 -*-
from datetime import datetime
import json
import logging
import urllib

from sqlalchemy import (
    Column,
    Integer,
    Text,
    )

import bones.event
from bones.bot import Module
from bones.modules import storage


class Lastfm(Module):

    def __init__(self, *args, **kwargs):
        Module.__init__(self, *args, **kwargs)
        self.apikey = self.settings.get("module.Lastfm", "apikey", default=None)
        if not self.apikey:
            self.log.error("No API key provided. Last.fm will be disabled.")

    @bones.event.handler(event=storage.DatabaseInitializedEvent)
    def gotDB(self, event):
        self.db = event.module

    @bones.event.handler(trigger="lastfm")
    def trigger(self, event):
        if not self.apikey:
            self.log.error("No API key provided. Last.fm will be disabled.")
            event.channel.msg("[Last.fm] Configuration error; check the logs for more info.")
            return
        argc = len(event.args)
        action = None
        nickname = None
        if argc <= 0:
            nickname = event.user.nickname
        elif event.args[0] in ["-r", "-d"]:
            action = event.args[0]
            if len(event.args) >= 2:
                nickname = event.args[1]
        else:
            nickname = event.args[0].decode("utf-8")

        session = self.db.new_session()
        if not action:
            user = session.query(User).filter(User.nickname == nickname) \
                .first()
            if not user:
                event.channel.msg(
                    str("%s: No user registered for nick '%s'"
                        % (event.user.nickname, nickname))
                )
                return
            params = urllib.urlencode({
                "method": "user.getRecentTracks",
                "user": user.username,
                "api_key": self.apikey,
                "format": "json",
                "extended": 1
            })
            try:
                data = self.factory.urlopener.open(
                    "http://ws.audioscrobbler.com/2.0/?%s" % params).read()
                data = json.loads(data)
            except:
                event.channel.msg(
                    "[Last.fm] An unexpected error occurred. Please tell the "
                    "bot manager to file a bug report."
                )
                self.log.exception(
                    "An error occurred while fetching user.getRecentTracks for"
                    "user %s", nickname)
                return
            if "error" in data:
                self.log.error("API error %i: %s", data["error"],
                               data["message"])
                event.channel.msg(
                    "[Last.fm] An error occurred while processing your "
                    "request. Please notify the bot manager"
                )
                return
            if "track" not in data["recenttracks"] \
                    or len(data['recenttracks']['track']) < 1:
                event.channel.msg(str(
                    "%s: No tracks found for user '%s'. Are you sure that the "
                    "user exists?"
                    % (event.user.nickname, user.username)
                ))
                return
            track = data['recenttracks']['track'][0]
            artist = track["artist"]["name"]
            tracktitle = track["name"]
            if "@attr" in track and "nowplaying" in track["@attr"] \
                    and track["@attr"]["nowplaying"].lower() == "true":
                loved = ""
                if "loved" in track and track["loved"] == "1":
                    loved = u"\x034♥\x03"
                msg = u"\x02%s\x02 ♪ %s \x0305–\x03 %s %s"
                msg %= (user.username, tracktitle, artist, loved)
            else:
                timestamp = track["date"]["uts"]
                date = []

                dateThen = datetime.fromtimestamp(float(timestamp))
                dateNow = datetime.now()
                diff = dateNow - dateThen

                if diff.days > 0:
                    if diff.days != 1:
                        suffix = "s"
                    else:
                        suffix = ""
                    date.append("%s day%s" % (diff.days, suffix))

                hours = (diff.seconds//3600) % 24
                if hours > 0:
                    if hours != 1:
                        suffix = "s"
                    else:
                        suffix = ""
                    date.append("%s hour%s" % (hours, suffix))

                minutes = (diff.seconds//60) % 60
                if minutes != 1:
                    suffix = "s"
                else:
                    suffix = ""
                date.append("%s minute%s" % (minutes, suffix))
                msg = (
                    "'%s' is not playing anything now, but played this %s "
                    "ago: %s - %s"
                    % (user.username, ", ".join(date), tracktitle, artist)
                )
            event.channel.msg(str(msg.encode("utf-8")))
            return

        elif action == "-r":
            if not nickname:
                event.user.notice(str(
                    "[Last.fm] You need to provide a Last.fm username."))
                return

            user = session.query(User) \
                .filter(User.nickname == event.user.nickname).first()
            if not user:
                user = User(event.user.nickname)
            user.username = nickname
            session.begin()
            session.add(user)
            session.commit()
            event.user.notice(str(
                "[Last.fm] Registered '%s' to your nick" % nickname))
            return

        elif action == "-d":
            user = session.query(User) \
                .filter(User.nickname == event.user.nickname).first()
            if not user:
                event.user.notice(str(
                    "[Last.fm] No user registered for nick '%s'" % nickname))
                return

            session.begin()
            session.delete(user)
            session.commit()
            event.channel.notice(str(
                "[Last.fm] Unregistered your nick from '%s'" % user.username))
            return


class User(storage.Base):
    __tablename__ = "bones_lastfm"

    id = Column(Integer, primary_key=True)
    nickname = Column(Text)
    username = Column(Text)

    def __init__(self, nickname):
        self.nickname = nickname
        self.username = ""


if __name__ == "__main__":
    from ConfigParser import SafeConfigParser
    from sqlalchemy import engine_from_config
    import sys
    settings = SafeConfigParser()
    if len(sys.argv) < 2:
        print "Error: You need to provide a config file!"
        sys.exit(1)
    settings.read(sys.argv[1])
    if "storage" not in settings._sections:
        print "Error: Config file does not contain a 'storage' section."
        sys.exit(1)
    elif "sqlalchemy.url" not in settings._sections["storage"]:
        print ("Error: Section 'storage' does not contain an 'sqlalchemy.url' "
               "key.")
        sys.exit(1)
    print ("Connecting to '%s'..."
           % settings._sections["storage"]["sqlalchemy.url"])
    engine = engine_from_config(settings._sections["storage"], "sqlalchemy.")
    print "Creating table '%s'..." % User.__tablename__
    from bones.modules.storage import Base
    Base.metadata.create_all(engine)
    print "Have a nice day!"
