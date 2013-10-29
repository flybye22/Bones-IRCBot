# -*- encoding: utf8 -*-
import re
import htmlentitydefs
import random
import logging
from datetime import datetime

from twisted.internet import reactor

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
        self.log = logging.getLogger(".".join([__name__, "QDB"]))
        if not self.BeautifulSoup:
            ex = Exception(
                "Unmet dependency: BeautifulSoup 4 not installed. This "
                "dependency needs to be installed before you can use the "
                "module %s" %

                (".".join([__name__, "QDB"],))
            )
            self.log.error(ex)
            raise ex
        self.settings = settings
        self.maxLinesPerQuote = int(self.settings.get("module.qdb", "maxLinesPerQuote"))

    @bones.event.handler(trigger="qdb")
    def cmdQdb(self, event):
        if len(event.args) == 1 and event.args[0].isdigit() \
        or len(event.args) >= 2 and event.args[0].lower() == "read":
            if event.args[0].isdigit():
                id = int(event.args[0])
            else:
                id = int(event.args[1])
            self.log.debug("Fetching qdb.us/%i", id)
            data = urlopener.open("http://qdb.us/%i" % id)
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
            client.msg(channel.name, str("[QDB #%s] Quote too long, read it at QDB instead: http://qdb.us/%s" % (quote[0], quote[0])))
            return
        for line in lines:
            client.msg(channel.name, str(("[QDB #%s] %s" % (quote[0], line)).encode("utf-8")))

    def cacheIfNeeded(self):
        """
        Ensures that the quote cache is not empty, and will fetch new quotes
        once the cache is empty.
        """
        if not self.quotesCache:
            self.log.debug("Fetching new quotes from qdb.us/random")
            html = urlopener.open("http://qdb.us/random").read()
            soup = self.BeautifulSoup(html)
            data = soup.findAll("span", {"class":"qt"})
            for item in data:
                id = item["id"].split("qt")[1]
                self.quotesCache.append((id, item.text))
            self.log.debug("Got %i new quotes", len(self.quotesCache))
            random.shuffle(self.quotesCache, random.random)


class UselessResponses(Module):
    def __init__(self, *args, **kwargs):
        Module.__init__(self, *args, **kwargs)

        self.danceCooldown = {}
        self.danceCooldownTime = None

    @bones.event.handler(event=bones.event.PrivmsgEvent)
    def DANCE(self, event, step=0):
        msg = re.sub("\x02|\x1f|\x1d|\x16|\x0f|\x03\d{0,2}(,\d{0,2})?", "", event.msg)
        if "DANCE" in msg:
            if not self.danceCooldownTime:
                self.danceCooldownTime = int(self.settings.get("module.UselessResponses", "dance.cooldown"))
            if step == 0:
                if event.channel.name in self.danceCooldown:
                    last = self.danceCooldown[event.channel.name]
                    now = datetime.utcnow()
                    delta = now - last
                    if delta.seconds < self.danceCooldownTime:
                        wait = self.danceCooldownTime - delta.seconds
                        event.client.notice(event.user.nickname, "Please wait %s more seconds." % wait)
                        return
                self.danceCooldown[event.channel.name] = datetime.utcnow()
                event.client.ctcpMakeQuery(event.channel.name, [('ACTION', "dances")])
                reactor.callLater(1.5, self.DANCE, event, step=1)
            elif step == 1:
                event.client.msg(event.channel.name, r":D\-<")
                reactor.callLater(1.0, self.DANCE, event, step=2)
            elif step == 2:
                event.client.msg(event.channel.name, r":D|-<")
                reactor.callLater(1.0, self.DANCE, event, step=3)
            elif step == 3:
                event.client.msg(event.channel.name, r":D/-<")

    @bones.event.handler(trigger="hi5")
    def cmdHi5(self, event):
        target = ""
        if len(event.args) > 0:
            target = " ".join(event.args)
        event.client.msg(event.channel.name, "(　｀ー´)八(｀ー´　) ＨＩ５ %s" % target)

    @bones.event.handler(trigger="kira")
    def cmdKira(self, event):
        prefix = event.match.group(1)
        if prefix.encode("utf-8") in "★✫✦✧✩✪✫✬✭✮✯✰✴✵✶✷✸✹⭑⭒⭐🌟":
            event.client.msg(event.channel.name, "(ﾉゝ∀・)\x038~キラ%s" % prefix.encode("utf-8"))

    @bones.event.handler(trigger="hue")
    def cmdHue(self, event):
        event.client.msg(event.channel.name, "ヾ（´▽｀） \x038ＨＵＥ\x034ＨＵＥ\x0313ＨＵＥ")

    @bones.event.handler(trigger="huehue")
    def cmdHueHue(self, event):
        event.client.msg(event.channel.name, "ヾ（´▽｀） \x038ＨＵＥ\x034ＨＵＥ\x0313ＨＵＥ\x0312ＨＵＥ\x039ＨＵＥ\x034ＨＵＥ\x0313ＨＵＥ\x038ＨＵＥ\x039ＨＵＥ\x0311ＨＵＥＨＵＥ\x0312ＨＵＥ")
