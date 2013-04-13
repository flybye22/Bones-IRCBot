# -*- encoding: utf8 -*-
import re
import sys

from twisted.words.protocols import irc
from twisted.internet import protocol


reCommand = re.compile("\.([a-zA-Z0-9]*)( .+)*?")


class BonesBot(irc.IRCClient):
    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname)

    def _get_realname(self):
        return self.factory.realname
    realname = property(_get_realname)
    
    def _get_username(self):
        return self.factory.username
    username = property(_get_username)

    def _get_versionName(self):
        return self.factory.versionName
    versionName = property(_get_versionName)
    
    def _get_versionNum(self):
        return self.factory.versionNum
    versionNum = property(_get_versionNum)
    
    def _get_versionEnv(self):
        return self.factory.versionEnv
    versionEnv = property(_get_versionEnv)
    
    def _get_sourceURL(self):
        return self.factory.sourceURL
    sourceURL = property(_get_sourceURL)
    
    def signedOn(self):
        if self.factory.settings.get("server", "nickserv") == "true":
            print "Identifying with NickServ."
            self.msg("NickServ", "IDENTIFY %s" % self.factory.settings.get("server", "nickserv.password"))
        for channel in self.factory.channels:
            self.join(channel)
        print "Signed on as %s." % (self.nickname,)
    
    def joined(self, channel):
        print "Joined %s." % (channel,)
    
    def privmsg(self, user, channel, msg):
        data = reCommand.match(msg)
        if data:
            trigger = data.group(1)
            print "Received trigger %s." % (trigger,)
            for module in self.factory.modules:
                if trigger in module.triggerMap and callable(module.triggerMap[trigger]):
                    module.triggerMap[trigger](module, self, user=user, channel=channel, args=data, msg=msg)
    
    def pong(self, user, secs):
        event = "pong"
        for module in self.factory.modules:
            if event in module.eventMap and callable(module.eventMap[event]):
                module.eventMap[event](module, self, user, secs)


class BonesBotFactory(protocol.ClientFactory):
    sourceURL = "https://github.com/404d/Bones-IRCBot"
    versionName = "Bones-IRCBot"
    versionNum = "0.0"
    versionEnv = sys.platform

    protocol = BonesBot
    modules = []
    
    def __init__(self, settings, nickname="Bones"):
        self.settings = settings
        self.channels = settings.get("bot", "channel").split("\n")
        self.nickname = settings.get("bot", "nickname")
        self.realname = settings.get("bot", "realname")
        self.username = settings.get("bot", "username")
    
    def clientConnectionLost(self, connector, reason):
        print "Lost connection (%s), reconnecting." % (reason,)
        connector.connect()
    
    def clientConnectionFailed(self, connector, reason):
        print "Could not connect: %s" % (reason,)

class Module():
    triggerMap = {}
    eventMap = {}
