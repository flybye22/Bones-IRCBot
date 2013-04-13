# -*- encoding: utf8 -*-
import re
import urllib
import HTMLParser

from bones.bot import Module

class MinecraftServerList(Module):
    def cmdMc(self, client, args=None, channel=None, user=None, msg=None):
        client.msg(channel, "%s: Wait wait, I'm charging my batteries!" % user.split("!")[0])
        
    triggerMap = {
        "mcservers": cmdMc
    }

class UselessResponses(Module):
    def cmdHue(self, client,  args=None, channel=None, user=None, msg=None):
        client.msg(channel, "ヾ（´▽｀） \x038ＨＵＥ\x034ＨＵＥ\x0313ＨＵＥ")

    def cmdHueHue(self, client,  args=None, channel=None, user=None, msg=None):
        client.msg(channel, "ヾ（´▽｀） \x038ＨＵＥ\x034ＨＵＥ\x0313ＨＵＥ\x0312ＨＵＥ\x039ＨＵＥ\x034ＨＵＥ\x0313ＨＵＥ\x038ＨＵＥ\x039ＨＵＥ\x0311ＨＵＥＨＵＥ\x0312ＨＵＥ")

    triggerMap = {
        "hue": cmdHue,
        "huehue": cmdHueHue,
    }

class Utilities(Module):
    ongoingPings = {}
    h = HTMLParser.HTMLParser()
    
    reYouTubeLink = re.compile("http(s)?\:\/\/(www\.)?(youtube\.com\/watch\?(.+)?v\=|youtu\.be\/)([a-zA-Z-0-9\_\-]*)")

    def cmdPing(self, client, args=None, channel=None, user=None, msg=None):
        nick = user.split("!")[0]
        if nick not in self.ongoingPings:
            self.ongoingPings[nick] = channel
            client.ping(nick)
        else:
            client.notice(nick, "Please wait until your ongoing ping in %s is finished until trying again." % self.ongoingPings[nick])
            
    def eventPrivmsgYouTube(self, client, user, channel, msg):
        if "youtu" in msg and "http" in msg:
            data = self.reYouTubeLink.search(msg)
            if data:
                vid = data.group(5)
                url = "http://youtu.be/%s" % vid
                html = urllib.urlopen(url).read()
                data = re.search("<meta name=\"title\" content=\"(.+)\">", html)
                if data:
                    client.msg(channel, "\x030,1You\x030,4Tube\x03 \x034::\x03 %s \x034::\x03 %s" % (str(self.h.unescape(data.group(1))), url))
                

    def eventPingResponseReceive(self, client, user, secs):
        nick = user.split("!")[0]
        if nick in self.ongoingPings:
            channel = self.ongoingPings[nick]
            client.msg(channel, "%s: Your response time was %.3f seconds." % (nick, secs))
            del self.ongoingPings[nick]
    
    triggerMap = {
        "ping": cmdPing,
    }

    eventMap = {
        "pong": eventPingResponseReceive,
        "privmsg": eventPrivmsgYouTube,
    }
