from datetime import datetime
import urllib

from bs4 import BeautifulSoup
from sqlalchemy import (
    Column,
    Integer,
    Text,
    )

from bones import event as events
from bones.bot import Module, urlopener
from bones.modules.storage import Base
from bones.modules.utilities import unescape

class Lastfm(Module):
    apikey = ""

    def __init__(self, settings):
        self.settings = settings
        self.apikey = settings.get("module.Lastfm", "apikey")

    @events.handler(event="storage.Database:init")
    def gotDB(self, db):
        self.db = db

    @events.handler(trigger="lastfm")
    def trigger(self, event):
        argc = len(event.args)
        action = None
        nickname = None
        if argc <= 0:
            nickname = event.user.nickname
        elif event.args[0] in ["-r","-d"]:
            action = event.args[0]
            if len(event.args) >= 2:
                nickname = event.args[1]
        else:
            nickname = event.args[0].decode("utf-8")

        session = self.db.new_session()
        if action == None:
            user = session.query(User).filter(User.nickname==nickname).first()
            if not user:
                event.client.msg(event.channel, str("%s: No user registered for nick '%s'" % (event.user.nickname, nickname)))
                return
            params = urllib.urlencode({"method":"user.getRecentTracks","user":user.username,"api_key":self.apikey})
            data = urlopener.open("http://ws.audioscrobbler.com/2.0/?%s" % params).read()
            soup = BeautifulSoup(data, "lxml")
            track = soup.find("track")
            if not track:
                event.client.msg(event.channel, str("%s: No tracks found for user '%s'. Are you sure that the user exists?" % (event.user.nickname, user.username)))
                return
            artist = track.find("artist").text
            tracktitle = track.find("name").text
            if "nowplaying" in track.attrs and track.attrs["nowplaying"] == "true":
                msg = "'%s' is now playing: %s - %s" % (user.username, artist, tracktitle)
            else:
                timestamp = track.find("date")
                date = []
                if timestamp and "uts" in timestamp.attrs:

                    dateThen = datetime.fromtimestamp(float(timestamp.attrs["uts"]))
                    dateNow = datetime.utcnow()
                    diff = dateNow - dateThen

                    if diff.days > 0:
                        if diff.days != 1:
                            suffix = "s"
                        else:
                            suffix = ""
                        date.append("%s day%s" % (diff.days, suffix))

                    hours = (diff.seconds//3600)%24
                    if hours > 0:
                        if hours != 1:
                            suffix = "s"
                        else:
                            suffix = ""
                        date.append("%s hour%s" % (hours, suffix))

                    minutes = (diff.seconds//60)%60
                    if minutes != 1:
                        suffix = "s"
                    else:
                        suffix = ""
                    date.append("%s minute%s" % (minutes, suffix))
                msg = "'%s' is not playing anything now, but played this %s ago: %s - %s" % (user.username, ", ".join(date), artist, tracktitle)
            event.client.msg(event.channel, str(unescape(msg).encode("utf-8")))
            return

        elif action == "-r":
            if not nickname:
                event.client.notice(event.user.nickname, str("[Last.fm] You need to provide a Last.fm username."))
                return
                
            user = session.query(User).filter(User.nickname==event.user.nickname).first()
            if not user:
                user = User(event.user.nickname)
            user.username = nickname
            session.begin()
            session.add(user)
            session.commit()
            event.client.notice(event.user.nickname, str("[Last.fm] Registered '%s' to your nick" % nickname))
            return

        elif action == "-d":
            user = session.query(User).filter(User.nickname==event.user.nickname).first()
            if not user:
                event.client.notice(event.user.nickname, str("[Last.fm] No user registered for nick '%s'" % nickname))
                return

            session.begin()
            session.delete(user)
            session.commit()
            event.client.notice(event.user.nickname, str("[Last.fm] Unregistered your nick from '%s'" % user.username))
            return


class User(Base):
    __tablename__ = "bones_lastfm"
    
    id = Column(Integer, primary_key=True)
    nickname = Column(Text)
    username = Column(Text)
    
    def __init__(self, nickname):
        self.nickname = nickname
        self.username = ""
