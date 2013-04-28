# -*- encoding: utf8 -*-
import re
import urllib
import htmlentitydefs
import random
import logging
from datetime import datetime

from twisted.internet import reactor

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


class QDB(Module):
    try:    
        from bs4 import BeautifulSoup
    except ImportError:
        BeautifulSoup = None

    quotesCache = []
    
    def __init__(self, settings):
        self.log = logging.getLogger(".".join([__name__,"QDB"]))
        if not self.BeautifulSoup:
            ex = Exception("Unmet dependency: BeautifulSoup 4 not installed. This dependency needs to be installed before you can use the module %s" % ".".join([__name__,"QDB"]))
            self.log.error(ex)
            raise ex
        self.settings = settings
        self.maxLinesPerQuote = int(self.settings.get("module.qdb", "maxLinesPerQuote"))
    
    @event.handler(trigger="qdb")
    def cmdQdb(self, event):
        if len(event.args) == 1 and event.args[0].isdigit() \
        or len(event.args) >= 2 and event.args[0].lower() == "read":
            if event.args[0].isdigit():
                id = int(event.args[0])
            else:
                id = int(event.args[1])
            self.log.debug("Fetching qdb.us/%i", id)
            data = urllib.urlopen("http://qdb.us/%i" % id)
            if data.getcode() == 404:
                event.client.msg(event.channel, str("[QDB #%s] Quote not found." % id))
                return
            if data.getcode() == 200:
                html = data.read()
                soup = self.BeautifulSoup(html)
                quote = soup.find("span", {"class":"qt"}).text
                self.sendQuote(event.client, event.channel, (id, quote))
                return
            self.log.error("Got unknown HTTP error code %i when fetching qdb.us/%i", data.getcode(), id)
            event.client.msg(event.channel, str("[QDB] An unknown exception occurred. Please notify the bot master and try again later."))
            return

        if len(event.args) <= 0 or event.args[0].lower() == "random":
            self.cacheIfNeeded()
            quote = self.quotesCache.pop()
            self.sendQuote(event.client, event.channel, quote)
            return
    
    def sendQuote(self, client, channel, quote):
        lines = quote[1].split("\n")
        if len(lines) > self.maxLinesPerQuote:
            client.msg(channel, str("[QDB #%s] Quote too long, read it at QDB instead: http://qdb.us/%s" % (quote[0], quote[0])))
            return
        for line in lines:
            client.msg(channel, str(("[QDB #%s] %s" % (quote[0], line)).encode("utf-8")))

    def cacheIfNeeded(self):
        if not self.quotesCache:
            self.log.debug("Fetching new quotes from qdb.us/random")
            html = urllib.urlopen("http://qdb.us/random").read()
            soup = self.BeautifulSoup(html)
            data = soup.findAll("span", {"class":"qt"})
            for item in data:
                id = item["id"].split("qt")[1]
                self.quotesCache.append((id, item.text))
            self.log.debug("Got %i new quotes", len(self.quotesCache))
            random.shuffle(self.quotesCache, random.random)


class MinecraftServerList(Module):
    @event.handler(trigger="mc")
    def cmdMc(self, event):
        event.client.msg(event.channel, "%s: Wait wait, I'm charging my batteries!" % event.user.nickname)


class NickFix(Module):
    nickIWant = None

    @event.handler(event="UserQuit")
    @event.handler(event="UserNickChanged")
    def somethingHappened(self, myEvent):
        user = None
        if self.nickIWant == None:
            self.nickIWant = self.settings.get("bot", "nickname")

        if isinstance(myEvent, event.UserNickChangedEvent) is True:
            user = myEvent.oldname
        else:
            user = myEvent.user

        if user.lower() == self.nickIWant.lower():
            myEvent.client.setNick(self.nickIWant)

class UselessResponses(Module):
    danceCooldown = {}
    danceCooldownTime = None

    @event.handler(event="Privmsg")
    def DANCE(self, event, step=0):
        msg = re.sub("\x02|\x1f|\x1d|\x16|\x0f|\x03\d{0,2}(,\d{0,2})?", "", event.msg)
        if "DANCE" in msg:
            if not self.danceCooldownTime:
                self.danceCooldownTime = int(self.settings.get("module.UselessResponses", "dance.cooldown"))
            if step == 0:
                if event.channel in self.danceCooldown:
                    last = self.danceCooldown[event.channel]
                    now = datetime.utcnow()
                    delta = now - last
                    if delta.seconds < self.danceCooldownTime:
                        wait = self.danceCooldownTime - delta.seconds
                        event.client.notice(event.user.nickname, "Please wait %s more seconds." % wait)
                        return
                self.danceCooldown[event.channel] = datetime.utcnow()
                event.client.ctcpMakeQuery(event.channel, [('ACTION', "dances")])
                reactor.callLater(1.5, self.DANCE, event, step=1)
            elif step == 1:
                event.client.msg(event.channel, r":D\-<")
                reactor.callLater(1.0, self.DANCE, event, step=2)
            elif step == 2:
                event.client.msg(event.channel, r":D|-<")
                reactor.callLater(1.0, self.DANCE, event, step=3)
            elif step == 3:
                event.client.msg(event.channel, r":D/-<")
            

    @event.handler(trigger="hi5")
    def cmdHi5(self, event):
        target = ""
        if len(event.args) > 0:
            target = event.args[0]
        event.client.msg(event.channel, "(　｀ー´)八(｀ー´　) ＨＩ５ %s" % target)
    
    @event.handler(trigger="hue")
    def cmdHue(self, event):
        event.client.msg(event.channel, "ヾ（´▽｀） \x038ＨＵＥ\x034ＨＵＥ\x0313ＨＵＥ")

    @event.handler(trigger="huehue")
    def cmdHueHue(self, event):
        event.client.msg(event.channel, "ヾ（´▽｀） \x038ＨＵＥ\x034ＨＵＥ\x0313ＨＵＥ\x0312ＨＵＥ\x039ＨＵＥ\x034ＨＵＥ\x0313ＨＵＥ\x038ＨＵＥ\x039ＨＵＥ\x0311ＨＵＥＨＵＥ\x0312ＨＵＥ")


class Utilities(Module):
    bs = None
    ongoingPings = {}
    
    reYouTubeLink = re.compile("http(s)?\:\/\/(m\.|www\.)?(youtube\.com\/watch\?(.+)?v\=|youtu\.be\/)([a-zA-Z-0-9\_\-]*)")
    reSpotifyLink = re.compile("http(s)?\:\/\/open\.spotify\.com\/(track|artist|album|user)\/[a-zA-Z0-9]+(\/playlist\/[a-zA-Z0-9]+)?", re.IGNORECASE)
    reTwitterLink = re.compile("https?\:\/\/twitter\.com\/[a-zA-Z0-9\-\_]+\/status\/\d+", re.IGNORECASE)

    def __init__(self, *args, **kwargs):
        Module.__init__(self, *args, **kwargs)
        try:
            from bs4 import BeautifulSoup
            self.bs = BeautifulSoup
        except ImportError:
            log.warn("Unmet dependency BeautifulSoup4: The Twitter URL checker will be disabled.")

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
                    html = urllib.urlopen(url).read()
                    soup = self.bs(html)
                    tweet = soup.find("p", {"class":"tweet-text"}).text
                    user = soup.find("span", {"class":"username js-action-profile-name"}).text
                    msg = u"\x030,10Twitter\x03 \x0311::\x03 %s \x0311––\x03 %s" % (tweet, user)
                    msg = unescape(msg)
                    msg = msg.encode("utf-8")
                    msg = str(msg)
                    event.client.msg(event.channel, msg)

    @event.handler(event="privmsg")
    def eventURLInfo_YouTube(self, event):
        if "youtu" in event.msg and "http" in event.msg:
            data = self.reYouTubeLink.search(event.msg)
            if data:
                vid = data.group(5)
                url = "http://youtu.be/%s" % vid
                html = urllib.urlopen(url).read()
                data = re.search("<meta name=\"title\" content=\"(.+)\">", html)
                if data:
                    event.client.msg(event.channel, str("\x030,1You\x030,4Tube\x03 \x034::\x03 %s \x034::\x03 %s" % (unescape(data.group(1)), url)))
        
    @event.handler(event="privmsg")
    def eventURLInfo_Spotify(self, event):
        if "open.spotify" in event.msg and "http" in event.msg:
            data = self.reSpotifyLink.search(event.msg)
            if data:
                url = data.group(0)
                html = urllib.urlopen(url).read()
                type = data.group(2)
                if type == "track":
                    songtitle = re.search("<meta property=\"twitter:title\" content=\"(.+)\">", html).group(1)
                    artist = re.search("<h2> by <a.+>(.+)</a", html).group(1)
                    if data:
                        event.client.msg(event.channel, str("\x031,3Spotify\x03 Track \x033::\x03 %s \x033::\x03 %s" % (unescape(songtitle), unescape(artist))))
                elif type == "album":
                    albumtitle = re.search("<meta property=\"twitter:title\" content=\"(.+)\">", html).group(1)
                    artist = re.search("<h2>by <a.+>(.+)</a", html).group(1)
                    if data:
                        event.client.msg(event.channel, str("\x031,3Spotify\x03 Album \x033::\x03 %s \x033::\x03 %s" % (unescape(albumtitle)), unescape(artist)))
                elif type == "artist":
                    artist = re.search("<meta property=\"twitter:title\" content=\"(.+)\">", html).group(1)
                    if data:
                        event.client.msg(event.channel, str("\x031,3Spotify\x03 Artist \x033::\x03 %s" % (unescape(artist))))
                elif type == "user" and data.group(3) is not None:
                    playlist = re.search("<meta property=\"twitter:title\" content=\"(.+)\">", html).group(1)
                    user = re.search("<h2>by <a.+>(.+)</a", html).group(1)
                    if data:
                        event.client.msg(event.channel, str("\x031,3Spotify\x03 Playlist \x033::\x03 %s \x033::\x03 %s" % (unescape(playlist), unescape(user))))
                elif type == "user":
                    user = re.search("<meta property=\"twitter:title\" content=\"(.+)\">", html).group(1)
                    if data:
                        event.client.msg(event.channel, str("\x031,3Spotify\x03 User \x033::\x03 %s" % (unescape(user))))

    @event.handler(event="CTCPPong")
    def eventPingResponseReceive(self, event):
        nick = event.user.nickname
        if nick in self.ongoingPings:
            channel = self.ongoingPings[nick]
            event.client.msg(channel, "%s: Your response time was %.3f seconds." % (nick, event.secs))
            del self.ongoingPings[nick]
