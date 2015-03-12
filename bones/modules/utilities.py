# -*- encoding: utf8 -*-
import re
import logging
log = logging.getLogger(__name__)

import bones.event
from bones.bot import Module, urlopener


class NickFix(Module):
    def __init__(self, *args, **kwargs):
        Module.__init__(self, *args, **kwargs)
        self.nickIWant = None
        self.isRecovering = False

    @bones.event.handler(event=bones.event.UserQuitEvent)
    @bones.event.handler(event=bones.event.UserNickChangedEvent)
    def somethingHappened(self, myEvent):
        user = None
        if self.nickIWant is None:
            self.nickIWant = \
                self.settings.get("bot", "nickname").split("\n")[0]

        if isinstance(myEvent, bones.event.UserNickChangedEvent) is True:
            user = myEvent.oldname
        else:
            user = myEvent.user.nickname

        if user.lower() == self.nickIWant.lower():
            myEvent.client.factory.nicknames = \
                self.settings.get("bot", "nickname").split("\n")[1:]
            self.isRecovering = True
            myEvent.client.setNick(self.nickIWant)

    @bones.event.handler(event=bones.event.BotSignedOnEvent)
    def resetMe(self, event):
        self.isRecovering = False
        self.nickIWant = None

    @bones.event.handler(event=bones.event.PreNicknameInUseError)
    def shouldWeEvenTry(self, event):
        if self.isRecovering:
            event.isCancelled = True
            self.isRecovering = False


class Utilities(Module):
    bs = None

    reYouTubeLink = re.compile("(https?\:\/\/)?(m\.|www\.)?(youtube\.com\/watch\?(.+)?v\=|youtu\.be\/)([a-zA-Z-0-9\_\-]*)")  # NOQA
    reTwitterLink = re.compile("(https?\:\/\/)?twitter\.com\/[a-zA-Z0-9\-\_]+\/status\/\d+", re.IGNORECASE)  # NOQA

    def __init__(self, *args, **kwargs):
        Module.__init__(self, *args, **kwargs)
        self.ongoingPings = {}
        try:
            from bs4 import BeautifulSoup
            self.bs = BeautifulSoup
        except ImportError:
            log.warn(
                "Unmet dependency BeautifulSoup4: The URL checkers will be "
                "disabled."
            )

    @bones.event.handler(trigger="ping")
    def cmdPing(self, event):
        nick = event.user.nickname
        if nick not in self.ongoingPings:
            self.ongoingPings[nick] = event.channel.name
            event.user.ping()
        else:
            event.user.notice(
                "Please wait until your ongoing ping in %s is finished until "
                "trying again."
                % self.ongoingPings[nick]
            )

    @bones.event.handler(event=bones.event.ChannelMessageEvent)
    def eventURLInfo_Twitter(self, event):
        if self.bs is not None:
            if "twitter" in event.message and "http" in event.message:
                data = self.reTwitterLink.search(event.message)
                if data:
                    url = data.group(0)
                    html = urlopener.open(url).read()
                    soup = self.bs(html)
                    tweet = soup \
                        .find("div", {"class": "permalink-inner permalink-tweet-container"}) \
                        .find("p", {"class": "tweet-text"}) \
                        .text
                    tweet = u"↵ ".join(tweet.split("\n"))
                    user = soup \
                        .find("div", {"class": "permalink-inner permalink-tweet-container"}) \
                        .find("span", {"class": "username js-action-profile-name"}) \
                        .text

                    # shitty fix for pic.twitter.com links
                    # could be improved by going through all links, check
                    # whether they start with http and if not replace the
                    # nodeText with the href attribute.
                    out = []
                    for word in tweet.split(" "):
                        if word.startswith("pic.twitter.com"):
                            word = "https://%s" % word
                        out.append(word)
                    tweet = " ".join(out)

                    msg = (u"\x0310Twitter\x03 \x0311::\x03 %s \x0311––\x03 %s"
                           % (tweet, user))
                    event.channel.msg(msg.encode("utf-8"))

    @bones.event.handler(event=bones.event.ChannelMessageEvent)
    def eventURLInfo_YouTube(self, event):
        if self.bs is not None:
            if "youtu" in event.message and "http" in event.message:
                data = self.reYouTubeLink.search(event.message)
                if data:
                    vid = data.group(5)
                    url = "http://youtu.be/%s" % vid
                    html = urlopener.open(url).read()
                    soup = self.bs(html)
                    title = soup.find("span", {"id": "eow-title"}).text.strip()
                    msg = (u"\x0314You\x035Tube \x034::\x03 %s \x034::\x03 %s"
                           % (title, url))
                    msg = u"↵ ".join(msg.split("\n"))
                    if title:
                        event.channel.msg(msg.encode("utf-8"))

    @bones.event.handler(event=bones.event.CTCPPongEvent)
    def eventPingResponseReceive(self, event):
        nick = event.user.nickname
        if nick in self.ongoingPings:
            event.user.notice("%s: Your response time was %.3f seconds."
                              % (nick, event.secs))
            del self.ongoingPings[nick]
