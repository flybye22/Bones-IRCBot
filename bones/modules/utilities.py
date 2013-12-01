# -*- encoding: utf8 -*-
import re
import htmlentitydefs
import logging
log = logging.getLogger(__name__)

import bones.event
from bones.bot import Module, urlopener


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
    """
    Turns HTML entities like &amp; into the character it represents
    (& in this case).

        .. deprecated: Use BeautifulSoup's built-in handling for this.
    """
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

    @bones.event.handler(event=bones.event.UserQuitEvent)
    @bones.event.handler(event=bones.event.UserNickChangedEvent)
    def somethingHappened(self, myEvent):
        user = None
        if self.nickIWant == None:
            self.nickIWant = self.settings.get("bot", "nickname").split("\n")[0]

        if isinstance(myEvent, bones.event.UserNickChangedEvent) is True:
            user = myEvent.oldname
        else:
            user = myEvent.user.nickname

        if user.lower() == self.nickIWant.lower():
            myEvent.client.factory.nicknames = self.settings.get("bot", "nickname").split("\n")[1:]
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

    reYouTubeLink = re.compile("(https?\:\/\/)?(m\.|www\.)?(youtube\.com\/watch\?(.+)?v\=|youtu\.be\/)([a-zA-Z-0-9\_\-]*)")
    reSpotifyLink = re.compile("(https?\:\/\/)?(open|play)\.spotify\.com\/(track|artist|album|user)\/[a-zA-Z0-9]+(\/playlist\/[a-zA-Z0-9]+)?", re.IGNORECASE)
    reTwitterLink = re.compile("(https?\:\/\/)?twitter\.com\/[a-zA-Z0-9\-\_]+\/status\/\d+", re.IGNORECASE)

    def __init__(self, *args, **kwargs):
        Module.__init__(self, *args, **kwargs)
        self.ongoingPings = {}
        try:
            from bs4 import BeautifulSoup
            self.bs = BeautifulSoup
        except ImportError:
            log.warn("Unmet dependency BeautifulSoup4: The URL checkers will be disabled.")

    @bones.event.handler(trigger="ping")
    def cmdPing(self, event):
        nick = event.user.nickname
        if nick not in self.ongoingPings:
            self.ongoingPings[nick] = event.channel.name
            event.user.ping()
        else:
            event.user.notice("Please wait until your ongoing ping in %s is finished until trying again." % self.ongoingPings[nick])

    @bones.event.handler(event=bones.event.PrivmsgEvent)
    def eventURLInfo_Twitter(self, event):
        if self.bs is not None:
            if "twitter" in event.msg and "http" in event.msg:
                data = self.reTwitterLink.search(event.msg)
                if data:
                    url = data.group(0)
                    html = urlopener.open(url).read()
                    soup = self.bs(html)
                    tweet = soup.find("div", {"class":"permalink-inner permalink-tweet-container"}).find("p", {"class":"tweet-text"}).text
                    tweet = u"↵ ".join(tweet.split("\n"))
                    user = soup.find("div", {"class":"permalink-inner permalink-tweet-container"}).find("span", {"class":"username js-action-profile-name"}).text
                    msg = u"\x0310Twitter\x03 \x0311::\x03 %s \x0311––\x03 %s" % (tweet, user)
                    event.channel.msg(msg.encode("utf-8"))

    @bones.event.handler(event=bones.event.PrivmsgEvent)
    def eventURLInfo_YouTube(self, event):
        if self.bs is not None:
            if "youtu" in event.msg and "http" in event.msg:
                data = self.reYouTubeLink.search(event.msg)
                if data:
                    vid = data.group(5)
                    url = "http://youtu.be/%s" % vid
                    html = urlopener.open(url).read()
                    soup = self.bs(html)
                    title = soup.find("span", {"id":"eow-title"}).text.strip()
                    msg = u"\x0314You\x035Tube \x034::\x03 %s \x034::\x03 %s" % (title, url)
                    msg = u"↵ ".join(msg.split("\n"))
                    if title:
                        event.channel.msg(msg.encode("utf-8"))

    @bones.event.handler(event=bones.event.PrivmsgEvent)
    def eventURLInfo_Spotify(self, event):
        if self.bs is not None:
            if "open.spotify" in event.msg and "http" in event.msg:
                data = self.reSpotifyLink.search(event.msg)
                if data:
                    url = data.group(0)
                    html = urlopener.open(url).read()
                    soup = self.bs(html)
                    type = data.group(2)
                    if type == "track":
                        songtitle = soup.find("meta", {"property":"og:title"})['content'].strip()
                        artist = soup.find("div", {"class":"player-header"}) \
                                     .find("h2").find("a").text.strip()
                        if data:
                            event.channel.msg(str("\x031,3Spotify\x03 Track \x033::\x03 %s \x033::\x03 %s" % (songtitle, artist)).replace("\n",""))
                    elif type == "album":
                        albumtitle = soup.find("meta", {"property":"og:title"})['content'].strip()
                        artist = soup.find("div", {"class":"player-header"}) \
                                     .find("h2").find("a").text.strip()
                        if data:
                            event.channel.msg(str("\x031,3Spotify\x03 Album \x033::\x03 %s \x033::\x03 %s" % (albumtitle, artist)).replace("\n",""))
                    elif type == "artist":
                        artist = soup.find("meta", {"property":"og:title"})['content'].strip()
                        if data:
                            event.channel.msg(str("\x031,3Spotify\x03 Artist \x033::\x03 %s" % (artist)).replace("\n",""))
                    elif type == "user" and data.group(3) is not None:
                        playlist = soup.find("meta", {"property":"og:title"})['content'].strip()
                        user = soup.find("div", {"class":"player-header"}) \
                                     .find("h2").find("a").text.strip()
                        if data:
                            event.channel.msg(str("\x031,3Spotify\x03 Playlist \x033::\x03 %s \x033::\x03 %s" % (playlist, user)).replace("\n",""))
                    elif type == "user":
                        user = soup.find("meta", {"property":"og:title"})['content'].strip()
                        if data:
                            event.channel.msg(str("\x031,3Spotify\x03 User \x033::\x03 %s" % (user)).replace("\n",""))

    @bones.event.handler(event=bones.event.CTCPPongEvent)
    def eventPingResponseReceive(self, event):
        nick = event.user.nickname
        if nick in self.ongoingPings:
            event.user.notice("%s: Your response time was %.3f seconds." % (nick, event.secs))
            del self.ongoingPings[nick]

