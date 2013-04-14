# -*- encoding: utf8 -*-
import re
import urllib
import htmlentitydefs

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
    
    reYouTubeLink = re.compile("http(s)?\:\/\/(www\.)?(youtube\.com\/watch\?(.+)?v\=|youtu\.be\/)([a-zA-Z-0-9\_\-]*)")
    reSpotifyLink = re.compile("http(s)?\:\/\/open\.spotify\.com\/(track|artist|album|user)\/[a-zA-Z0-9]+(\/playlist\/[a-zA-Z0-9]+)?", re.IGNORECASE)

    def cmdPing(self, client, args=None, channel=None, user=None, msg=None):
        nick = user.split("!")[0]
        if nick not in self.ongoingPings:
            self.ongoingPings[nick] = channel
            client.ping(nick)
        else:
            client.notice(nick, "Please wait until your ongoing ping in %s is finished until trying again." % self.ongoingPings[nick])
            
    def eventPrivmsg(self, client, user, channel, msg):
        if "youtu" in msg and "http" in msg:
            data = self.reYouTubeLink.search(msg)
            if data:
                vid = data.group(5)
                url = "http://youtu.be/%s" % vid
                html = urllib.urlopen(url).read()
                data = re.search("<meta name=\"title\" content=\"(.+)\">", html)
                if data:
                    client.msg(channel, str("\x030,1You\x030,4Tube\x03 \x034::\x03 %s \x034::\x03 %s" % (unescape(data.group(1)), url)))
        
        if "open.spotify" in msg and "http" in msg:
            data = self.reSpotifyLink.search(msg)
            if data:
                url = data.group(0)
                html = urllib.urlopen(url).read()
                type = data.group(2)
                if type == "track":
                    songtitle = re.search("<meta property=\"twitter:title\" content=\"(.+)\">", html).group(1)
                    artist = re.search("<h2> by <a.+>(.+)</a", html).group(1)
                    if data:
                        client.msg(channel, str("\x031,3Spotify\x03 Track \x033::\x03 %s \x033::\x03 %s" % (unescape(songtitle), unescape(artist))))
                elif type == "album":
                    albumtitle = re.search("<meta property=\"twitter:title\" content=\"(.+)\">", html).group(1)
                    artist = re.search("<h2>by <a.+>(.+)</a", html).group(1)
                    if data:
                        client.msg(channel, str("\x031,3Spotify\x03 Album \x033::\x03 %s \x033::\x03 %s" % (unescape(albumtitle)), unescape(artist))))
                elif type == "artist":
                    artist = re.search("<meta property=\"twitter:title\" content=\"(.+)\">", html).group(1)
                    if data:
                        client.msg(channel, str("\x031,3Spotify\x03 Artist \x033::\x03 %s" % (unescape(artist))))
                elif type == "user" and data.group(3) is not None:
                    playlist = re.search("<meta property=\"twitter:title\" content=\"(.+)\">", html).group(1)
                    user = re.search("<h2>by <a.+>(.+)</a", html).group(1)
                    if data:
                        client.msg(channel, str("\x031,3Spotify\x03 Playlist \x033::\x03 %s \x033::\x03 %s" % (unescape(playlist), unescape(user))))
                elif type == "user":
                    user = re.search("<meta property=\"twitter:title\" content=\"(.+)\">", html).group(1)
                    if data:
                        client.msg(channel, str("\x031,3Spotify\x03 User \x033::\x03 %s" % (unescape(user))))
                

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
        "privmsg": eventPrivmsg,
    }
