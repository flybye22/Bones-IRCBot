# -*- encoding: utf8 -*-
import re
import sys
import os
import logging
import logging.config

from twisted.words.protocols import irc
from twisted.internet import protocol


logging.config.fileConfig(sys.argv[1])
log = logging.getLogger(__name__)

reCommand = re.compile("\.([a-zA-Z0-9]*)( .+)*?")


class InvalidBonesModuleException(Exception):
    pass


class NoSuchBonesModuleException(Exception):
    pass


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
            log.info("Identifying with NickServ.")
            self.msg("NickServ", "IDENTIFY %s" % self.factory.settings.get("server", "nickserv.password"))

        if self.factory.settings.get("server", "setBot") == "true":
            self.mode(self.nickname, True, "B")

        for channel in self.factory.channels:
            self.join(channel)

        log.info("Signed on as %s.", self.nickname)
    
    def joined(self, channel):
        log.info("Joined channel %s.", channel)
    
    def userJoin(self, user, channel):
        event = "userJoin"
        log.debug("Event userJoin: %s %s", user, channel)
        for module in self.factory.modules:
            if event in module.eventMap and callable(module.eventMap[event]):
                module.eventMap[event](module, self, user, channel)
        data = reCommand.match(msg)
    
    def privmsg(self, user, channel, msg):
        event = "privmsg"
        log.debug("Event privmsg: %s %s :%s", user, channel, msg)
        if channel[0:1] != "#":
            channel = user.split("!")[0]
        for module in self.factory.modules:
            if event in module.eventMap and callable(module.eventMap[event]):
                module.eventMap[event](module, self, user, channel, msg)
        data = reCommand.match(msg)
        if data:
            trigger = data.group(1)
            args = msg.split(" ")[1:]
            log.info("Received trigger %s." % (trigger,))
            for module in self.factory.modules:
                if trigger in module.triggerMap and callable(module.triggerMap[trigger]):
                    module.triggerMap[trigger](module, self, user=user, channel=channel, args=args, msg=msg)
                else:
                    altTrigger = trigger.lower()
                    if trigger.lower() in module.triggerMap and callable(module.triggerMap[altTrigger]):
                        module.triggerMap[altTrigger](module, self, user=user, channel=channel, args=args, msg=msg)
    
    def pong(self, user, secs):
        event = "pong"
        log.debug("CTCP pong: %fs from %s", secs, user)
        for module in self.factory.modules:
            if event in module.eventMap and callable(module.eventMap[event]):
                module.eventMap[event](module, self, user, secs)
    
    def irc_unknown(self, prefix, command, params):
        log.debug("Unknown RAW: %s; %s; %s", prefix, command, params)
        if command.lower() == "invite" and self.factory.settings.get("bot", "joinOnInvite") == "true":
            log.info("Got invited to %s, joining.", params[1])
            self.join(params[1])
        event = "irc_unknown"
        for module in self.factory.modules:
            if event in module.eventMap and callable(module.eventMap[event]):
                module.eventMap[event](module, prefix, command, params)


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
        
        modules = settings.get("bot", "modules").split("\n")
        for module in modules:
            self.loadModule(module)

    def loadModule(self, path):
        """
        Loads the specified module and adds it to the bot.
        """
        tmppath = path.split(".")
        package = ".".join(tmppath[:len(tmppath)-1])
        name = tmppath[len(tmppath)-1:len(tmppath)][0]
        
        try:
            module = __import__(package, fromlist=[name])
        except ImportError:
            ex = NoSuchBonesModuleException("Could not load module %s: No such package" % path)
            log.exception(ex)
            raise ex
        try:
            module = getattr(module, name)
        except AttributeError:
            ex = NoSuchBonesModuleException("Could not load module %s: No such class" % path)
            log.exception(ex)
            raise ex

        if issubclass(module, Module):
            self.modules.append(module(self.settings))
            log.info("Loaded module %s", path)
        else:
            ex = InvalidBonesModuleException("Could not load module %s: Module is not a subclass of bones.bot.Module" % path)
            log.exception(ex)
            raise ex
    
    def clientConnectionLost(self, connector, reason):
        log.info("Lost connection (%s), reconnecting.", reason)
        connector.connect()
    
    def clientConnectionFailed(self, connector, reason):
        log.info("Could not connect: %s", reason)


class Module():
    def __init__(self, settings):
        self.settings = settings
    
    triggerMap = {}
    eventMap = {}
