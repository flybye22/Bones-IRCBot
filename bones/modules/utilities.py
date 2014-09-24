# -*- encoding: utf8 -*-
import re
import htmlentitydefs
import logging
log = logging.getLogger(__name__)

from bones import event
from bones.bot import Module


##
# Removes HTML or XML character references and entities from a text string.
#
# 404d edit start:
# Code snippet obtained from http://effbot.org/zone/re-sub.htm#unescape-html
# This code snippet have been slightly altered to fix some issues with htmlparser and/or htmlentitydefs choking on some UTF-8 characters.
# 404d edit end
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.

def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = chr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub(ur"&#?\w+;", fixup, text, re.UNICODE)


class NickFix(Module):
    def __init__(self, *args, **kwargs):
        Module.__init__(self, *args, **kwargs)
        self.nickIWant = None
        self.isRecovering = False

    @event.handler(event="UserQuit")
    @event.handler(event="UserNickChanged")
    def somethingHappened(self, myEvent):
        user = None
        if self.nickIWant == None:
            self.nickIWant = self.settings.get("bot", "nickname").split("\n")[0]

        if isinstance(myEvent, event.UserNickChangedEvent) is True:
            user = myEvent.oldname
        else:
            user = myEvent.user

        if user.lower() == self.nickIWant.lower():
            myEvent.client.factory.nicknames = self.settings.get("bot", "nickname").split("\n")[1:]
            self.isRecovering = True
            myEvent.client.setNick(self.nickIWant)

    @event.handler(event="BotSignedOn")
    def resetMe(self, event):
        self.isRecovering = False
        self.nickIWant = None

    @event.handler(event="PreNicknameInUseError")
    def shouldWeEvenTry(self, event):
        if self.isRecovering:
            event.isCancelled = True
            self.isRecovering = False


class Utilities(Module):
    bs = None
    
    reYouTubeLink = re.compile("http(s)?\:\/\/(m\.|www\.)?(youtube\.com\/watch\?(.+)?v\=|youtu\.be\/)([a-zA-Z-0-9\_\-]*)")
    reTwitterLink = re.compile("https?\:\/\/twitter\.com\/[a-zA-Z0-9\-\_]+\/status\/\d+", re.IGNORECASE)

    def __init__(self, *args, **kwargs):
        Module.__init__(self, *args, **kwargs)
        self.ongoingPings = {}
        try:
            from bs4 import BeautifulSoup
            self.bs = BeautifulSoup
        except ImportError:
            log.warn("Unmet dependency BeautifulSoup4: The URL checkers will be disabled.")

    @event.handler(trigger="ping")
    def cmdPing(self, event):
        nick = event.user.nickname
        if nick not in self.ongoingPings:
            self.ongoingPings[nick] = event.channel
            event.client.ping(nick)
        else:
            event.client.notice(nick, "Please wait until your ongoing ping in %s is finished until trying again." % self.ongoingPings[nick])
            
    @event.handler(event="privmsg")
    def eventURLInfo_Twitter(self, event):
        if self.bs is not None:
            if "twitter" in event.msg and "http" in event.msg:
                data = self.reTwitterLink.search(event.msg)
                if data:
                    url = data.group(0)
                    html = event.client.factory.urlopener.open(url).read()
                    soup = self.bs(html)
                    tweet = soup.find("div", {"class":"permalink-inner permalink-tweet-container"}).find("p", {"class":"tweet-text"}).text
                    user = soup.find("div", {"class":"permalink-inner permalink-tweet-container"}).find("span", {"class":"username js-action-profile-name"}).text
                    msg = u"\x0310Twitter\x03 \x0311::\x03 %s \x0311––\x03 %s" % (tweet, user)
                    msg = unescape(msg)
                    msg = msg.encode("utf-8")
                    msg = str(msg)
                    event.client.msg(event.channel, msg)

    @event.handler(event="privmsg")
    def eventURLInfo_YouTube(self, event):
        if self.bs is not None:
            if "youtu" in event.msg and "http" in event.msg:
                data = self.reYouTubeLink.search(event.msg)
                if data:
                    vid = data.group(5)
                    url = "http://youtu.be/%s" % vid
                    html = event.client.factory.urlopener.open(url).read()
                    soup = self.bs(html)
                    title = soup.find("span", {"id":"eow-title"}).text.strip()
                    if title:
                        event.client.msg(event.channel, str("\x030,1You\x030,4Tube\x03 \x034::\x03 %s \x034::\x03 %s" % (unescape(title), url)).replace("\n", ""))
        
    @event.handler(event="CTCPPong")
    def eventPingResponseReceive(self, event):
        nick = event.user.nickname
        if nick in self.ongoingPings:
            channel = self.ongoingPings[nick]
            event.client.msg(channel, "%s: Your response time was %.3f seconds." % (nick, event.secs))
            del self.ongoingPings[nick]
    
