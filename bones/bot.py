# -*- encoding: utf8 -*-
import re
import sys
import os
import logging
import logging.config
import urllib2

from twisted.words.protocols import irc
from twisted.internet import protocol

from bones import event


log = logging.getLogger(__name__)

urlopener = urllib2.build_opener()
urlopener.addheaders = [('User-agent', 'urllib/2 BonesIRCBot/0.0')]


class InvalidBonesModuleException(Exception):
    pass


class NoSuchBonesModuleException(Exception):
    pass
    
    
class BonesModuleAlreadyLoadedException(Exception):
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
        if self.factory.settings.get("server", "setBot") == "true":
            self.mode(self.nickname, True, "B")

        thisEvent = event.BotSignedOnEvent(self)
        event.fire("BotSignedOn", thisEvent)
        log.info("Signed on as %s.", self.nickname)

        for channel in self.factory.channels:
            self.join(channel)
            
    def created(self, when):
        log.debug("Received server creation info: %s", when)
        thisEvent = event.ServerCreatedEvent(self, when)
        event.fire("ServerCreated", thisEvent)
    
    def yourHost(self, info):
        log.debug("Received server host info: %s", info)
        thisEvent = event.ServerHostInfoEvent(self, info)
        event.fire("ServerHostInfo", thisEvent)
    
    def myInfo(self, servername, version, umodes, cmodes):
        log.debug("Received server info from %s: Version %s, Usermodes %s, Channelmodes %s", servername, version, umodes, cmodes)
        thisEvent = event.ServerInfoEvent(self, servername, version, umodes, cmodes)
        event.fire("ServerInfo", thisEvent)

    def luserClient(self, info):
        log.debug("Received client info from server: %s", info)
        thisEvent = event.ServerClientInfoEvent(self, info)
        event.fire("ServerClientInfo", thisEvent)
    
    def bounce(self, info):
        log.debug("Received bounce info: %s", info)
        thisEvent = event.BounceEvent(self, info)
        event.fire("Bounce", thisEvent)
    
    def isupport(self, options):
        log.debug("Received server support flags: %s", " ".join(options))
        thisEvent = event.ServerSupportEvent(self, options)
        event.fire("ServerSupport", thisEvent)

    def luserChannels(self, channels):
        log.debug("This server have %s channels", channels)
        thisEvent = event.ServerChannelCountEvent(self, channels)
        event.fire("ServerChannelCount", thisEvent)
    
    def luserOp(self, ops):
        log.debug("There's currently %s opered clients on this server", ops)
        thisEvent = event.ServerOpCountEvent(self, ops)
        event.fire("ServerOpCount", thisEvent)

    def luserMe(self, info):
        log.debug("Received local server info: %s", info)
        thisEvent = event.ServerLocalInfoEvent(self, info)
        event.fire("ServerLocalInfo", thisEvent)
    
    def noticed(self, user, channel, message):
        log.debug("NOTICE in %s from %s: %s", channel, user, message)
        thisEvent = event.BotNoticeReceivedEvent(self, user, channel, message)
        event.fire("BotNoticeReceived", thisEvent)
    
    def modeChanged(self, user, channel, set, modes, args):
        if set:
            setString = "+"
        else:
            setString = "-"
        log.debug("Mode change in %s: %s set %s%s (%s)", channel, user, setString, modes, args)
        thisEvent = event.ModeChangedEvent(self, user, channel, set, modes, args)
        event.fire("ModeChanged", thisEvent)
    
    def kickedFrom(self, channel, kicker, message):
        log.info("Kicked from channel %s by %s. Reason: %s", channel, kicker, message)
        thisEvent = event.BotKickedEvent(self, channel, kicker, message)
        event.fire("BotKicked", thisEvent)

    def nickChanged(self, nick):
        thisEvent = event.BotNickChangedEvent(self, nick)
        log.info("Changed nick to %s", nick)
        event.fire("BotNickChanged", thisEvent)
    
    def userLeft(self, user, channel):
        log.debug("User %s parted from %s", user, channel)
        thisEvent = event.UserPartEvent(self, user, channel)
        event.fire("UserPart", thisEvent)
    
    def userQuit(self, user, quitMessage):
        log.debug("User %s quit (Reason: %s)", user, quitMessage)
        thisEvent = event.UserQuitEvent(self, user, quitMessage)
        event.fire("UserQuit", thisEvent)
    
    def userKicked(self, kickee, channel, kicker, message):
        log.debug("User %s was kicked from %s by %s (Reason: %s)", kickee, channel, kicker, message)
        thisEvent = event.UserKickedEvent(self, kickee, channel, kicker, message)
        event.fire("UserKicked", thisEvent)
    
    def action(self, user, channel, data):
        log.debug("User %s actioned in %s: %s", user, channel, data)
        thisEvent = event.UserActionEvent(self, user, channel, data)
        event.fire("UserAction", thisEvent)
    
    def topicUpdated(self, user, channel, newTopic):
        log.debug("User %s changed topic of %s to %s", user, channel, newTopic)
        thisEvent = event.ChannelTopicChangedEvent(self, user, channel, newTopic)
        event.fire("ChannelTopicChanged", thisEvent)
    
    def userRenamed(self, oldname, newname):
        log.debug("User %s changed nickname to %s", oldname, newname)
        thisEvent = event.UserNickChangedEvent(self, oldname, newname)
        event.fire("UerNickChanged", thisEvent)
    
    def receivedMOTD(self, motd):
        thisEvent = event.ServerMOTDReceivedEvent(self, motd)
        event.fire("ServerMOTDReceived", thisEvent)

    def joined(self, channel):
        thisEvent = event.BotJoinEvent(self, channel)
        event.fire("BotJoin", thisEvent)
        log.info("Joined channel %s.", channel)
    
    def join(self, channel):
        thisEvent = event.BotPreJoinEvent(self, channel)
        event.fire("BotPreJoin", thisEvent)
        if thisEvent.isCancelled is False:
            irc.IRCClient.join(self, channel)
    
    def userJoin(self, user, channel):
        thisEvent = event.UserJoinEvent(self, user, channel)
        event.fire("UserJoin", thisEvent)
        log.debug("Event userJoin: %s %s", user, channel)
    
    def privmsg(self, user, channel, msg):
        log.debug("Event privmsg: %s %s :%s", user, channel, msg)
        if channel[0:1] != "#":
            channel = user.split("!")[0]
        thisEvent = event.PrivmsgEvent(self, user, channel, msg)
        event.fire("Privmsg", thisEvent)
        data = self.factory.reCommand.match(msg.decode("utf-8"))
        if data:
            trigger = data.group(2)
            args = msg.split(" ")[1:]
            log.info("Received trigger %s%s." % (data.group(1),trigger))
            triggerEvent = event.TriggerEvent(self, user=user, channel=channel, msg=msg, args=args, match=data)
            event.fireTrigger(trigger.lower(), triggerEvent)
    
    def pong(self, user, secs):
        log.debug("CTCP pong: %fs from %s", secs, user)
        thisEvent = event.CTCPPongEvent(self, user, secs)
        event.fire("CTCPPong", thisEvent)
    
    def irc_unknown(self, prefix, command, params):
        log.debug("Unknown RAW: %s; %s; %s", prefix, command, params)
        if command.lower() == "invite" and self.factory.settings.get("bot", "joinOnInvite") == "true":
            log.info("Got invited to %s, joining.", params[1])
            self.join(params[1])
        event.fire("irc_unknown", self, prefix, command, params)

    def ctcpQuery_VERSION(self, user, channel, data):
        if data is None and self.versionName:
            thisEvent = event.CTCPVersionEvent(user)
            event.fire("CTCPVersion", thisEvent)
            if not thisEvent.isCancelled:
                version = "%s %s %s" % (
                    self.versionName,
                    self.versionNum,
                    self.versionEnv,
                )
                version = version.replace("\n", "")
                self.ctcpMakeReply(thisEvent.user.nickname, [('VERSION', version)])
                log.debug("Received CTCP VERSION query from %s, replied '%s'.", user, version)
            else:
                log.debug("Received CTCP VERSION query from %s, but event was cancelled by an eventhandler.", user)


class BonesBotFactory(protocol.ClientFactory):
    sourceURL = "https://github.com/404d/Bones-IRCBot"
    versionName = "Bones IRCBot"
    versionNum = "0.0"
    versionEnv = ""

    protocol = BonesBot
    modules = []
    
    def __init__(self, settings):
        self.settings = settings
        self.channels = settings.get("bot", "channel").split("\n")
        self.nickname = settings.get("bot", "nickname")
        self.realname = settings.get("bot", "realname")
        self.username = settings.get("bot", "username")

        # Build the trigger regex using the trigger prefixes specified in settings
        prefixChars = settings.get("bot", "triggerPrefixes").decode("utf-8") # UTF-8 fix
        regex = "([%s])([a-zA-Z0-9]*)( .+)*?" % prefixChars
        self.reCommand = re.compile(regex, re.UNICODE)
        
        modules = settings.get("bot", "modules").split("\n")
        for module in modules:
            self.loadModule(module)
        event.fire("BotInitialized", self)

    def loadModule(self, path, userloaded=False):
        """
        Loads the specified module and adds it to the bot.
        """
        tmppath = path.split(".")
        package = ".".join(tmppath[:len(tmppath)-1])
        name = tmppath[len(tmppath)-1:len(tmppath)][0]

        try:
            module = __import__(package, fromlist=[name])
        except ImportError as ex_raised:
            ex = NoSuchBonesModuleException("Could not load module %s: No such package. (ImportException: %s)" % (path, ex_raised.message))
            log.exception(ex)
            raise ex

        try:
            module = getattr(module, name)
        except AttributeError as ex_raised:
            ex = NoSuchBonesModuleException("Could not load module %s: No such class. (AttributeException: %s)" % (path, ex_raised.message))
            log.exception(ex)
            raise ex

        if issubclass(module, Module):
            if module in [m.__class__ for m in self.modules]:
                ex = BonesModuleAlreadyLoadedException("Could not load module %s: Module already loaded" % path)
                log.exception(ex)
                raise ex
            instance = module(self.settings)
            self.modules.append(instance)
            event.register(instance)
            log.info("Loaded module %s", path)
            event.fire("ModuleLoaded", module, userloaded)
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
