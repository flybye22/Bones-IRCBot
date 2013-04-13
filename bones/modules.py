# -*- encoding: utf8 -*-
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

    def cmdPing(self, client, args=None, channel=None, user=None, msg=None):
        nick = user.split("!")[0]
        if nick not in self.ongoingPings:
            self.ongoingPings[nick] = channel
            client.ping(nick)
        else:
            client.notice(nick, "Please wait until your ongoing ping in %s is finished until trying again." % self.ongoingPings[nick])

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
    }