# -*- encoding: utf8 -*-
import re
import sys
import os
import logging
import logging.config
import urllib2

from twisted.words.protocols import irc
from twisted.internet import protocol, reactor

from bones import event


log = logging.getLogger(__name__)


class InvalidBonesModuleException(Exception):
    pass

class InvalidConfigurationException(Exception):
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
    
    def _get_tag(self):
        return self.factory.tag
    tag = property(_get_tag)
    
    def signedOn(self):
        self.factory.reconnectAttempts = 0

        if self.factory.settings.get("server", "setBot") == "true":
            self.mode(self.nickname, True, "B")

        thisEvent = event.BotSignedOnEvent(self)
        event.fire(self.tag, "BotSignedOn", thisEvent)
        log.info("Signed on as %s.", self.nickname)

        for channel in self.factory.channels:
            self.join(channel)
            
    def created(self, when):
        log.debug("Received server creation info: %s", when)
        thisEvent = event.ServerCreatedEvent(self, when)
        event.fire(self.tag, "ServerCreated", thisEvent)
    
    def yourHost(self, info):
        log.debug("Received server host info: %s", info)
        thisEvent = event.ServerHostInfoEvent(self, info)
        event.fire(self.tag, "ServerHostInfo", thisEvent)
    
    def myInfo(self, servername, version, umodes, cmodes):
        log.debug("Received server info from %s: Version %s, Usermodes %s, Channelmodes %s", servername, version, umodes, cmodes)
        thisEvent = event.ServerInfoEvent(self, servername, version, umodes, cmodes)
        event.fire(self.tag, "ServerInfo", thisEvent)

    def luserClient(self, info):
        log.debug("Received client info from server: %s", info)
        thisEvent = event.ServerClientInfoEvent(self, info)
        event.fire(self.tag, "ServerClientInfo", thisEvent)
    
    def bounce(self, info):
        log.debug("Received bounce info: %s", info)
        thisEvent = event.BounceEvent(self, info)
        event.fire(self.tag, "Bounce", thisEvent)
    
    def isupport(self, options):
        log.debug("Received server support flags: %s", " ".join(options))
        thisEvent = event.ServerSupportEvent(self, options)
        event.fire(self.tag, "ServerSupport", thisEvent)

    def luserChannels(self, channels):
        log.debug("This server have %s channels", channels)
        thisEvent = event.ServerChannelCountEvent(self, channels)
        event.fire(self.tag, "ServerChannelCount", thisEvent)
    
    def luserOp(self, ops):
        log.debug("There's currently %s opered clients on this server", ops)
        thisEvent = event.ServerOpCountEvent(self, ops)
        event.fire(self.tag, "ServerOpCount", thisEvent)

    def luserMe(self, info):
        log.debug("Received local server info: %s", info)
        thisEvent = event.ServerLocalInfoEvent(self, info)
        event.fire(self.tag, "ServerLocalInfo", thisEvent)
    
    def noticed(self, user, channel, message):
        log.debug("NOTICE in %s from %s: %s", channel, user, message)
        thisEvent = event.BotNoticeReceivedEvent(self, user, channel, message)
        event.fire(self.tag, "BotNoticeReceived", thisEvent)
    
    def modeChanged(self, user, channel, set, modes, args):
        if set:
            setString = "+"
        else:
            setString = "-"
        log.debug("Mode change in %s: %s set %s%s (%s)", channel, user, setString, modes, args)
        thisEvent = event.ModeChangedEvent(self, user, channel, set, modes, args)
        event.fire(self.tag, "ModeChanged", thisEvent)
    
    def kickedFrom(self, channel, kicker, message):
        log.info("Kicked from channel %s by %s. Reason: %s", channel, kicker, message)
        thisEvent = event.BotKickedEvent(self, channel, kicker, message)
        event.fire(self.tag, "BotKicked", thisEvent)

    def nickChanged(self, nick):
        thisEvent = event.BotNickChangedEvent(self, nick)
        log.info("Changed nick to %s", nick)
        event.fire(self.tag, "BotNickChanged", thisEvent)
    
    def userLeft(self, user, channel):
        log.debug("User %s parted from %s", user, channel)
        thisEvent = event.UserPartEvent(self, user, channel)
        event.fire(self.tag, "UserPart", thisEvent)
    
    def userQuit(self, user, quitMessage):
        log.debug("User %s quit (Reason: %s)", user, quitMessage)
        thisEvent = event.UserQuitEvent(self, user, quitMessage)
        event.fire(self.tag, "UserQuit", thisEvent)
    
    def userKicked(self, kickee, channel, kicker, message):
        log.debug("User %s was kicked from %s by %s (Reason: %s)", kickee, channel, kicker, message)
        thisEvent = event.UserKickedEvent(self, kickee, channel, kicker, message)
        event.fire(self.tag, "UserKicked", thisEvent)
    
    def action(self, user, channel, data):
        log.debug("User %s actioned in %s: %s", user, channel, data)
        thisEvent = event.UserActionEvent(self, user, channel, data)
        event.fire(self.tag, "UserAction", thisEvent)
    
    def topicUpdated(self, user, channel, newTopic):
        log.debug("User %s changed topic of %s to %s", user, channel, newTopic)
        thisEvent = event.ChannelTopicChangedEvent(self, user, channel, newTopic)
        event.fire(self.tag, "ChannelTopicChanged", thisEvent)
    
    def userRenamed(self, oldname, newname):
        log.debug("User %s changed nickname to %s", oldname, newname)
        thisEvent = event.UserNickChangedEvent(self, oldname, newname)
        event.fire(self.tag, "UserNickChanged", thisEvent)
    
    def receivedMOTD(self, motd):
        thisEvent = event.ServerMOTDReceivedEvent(self, motd)
        event.fire(self.tag, "ServerMOTDReceived", thisEvent)

    def joined(self, channel):
        thisEvent = event.BotJoinEvent(self, channel)
        event.fire(self.tag, "BotJoin", thisEvent)
        log.info("Joined channel %s.", channel)
    
    def join(self, channel):
        thisEvent = event.BotPreJoinEvent(self, channel)
        def doJoin(thisEvent):
            if thisEvent.isCancelled == False:
                irc.IRCClient.join(thisEvent.client, thisEvent.channel)
        event.fire(self.tag, "BotPreJoin", thisEvent, callback=doJoin)
    
    def userJoin(self, user, channel):
        thisEvent = event.UserJoinEvent(self, user, channel)
        event.fire(self.tag, "UserJoin", event)
        log.debug("Event userJoin: %s %s", user, channel)
    
    def privmsg(self, user, channel, msg):
        log.debug("Event privmsg: %s %s :%s", user, channel, msg)
        if channel[0:1] != "#":
            channel = user.split("!")[0]
        thisEvent = event.PrivmsgEvent(self, user, channel, msg)
        event.fire(self.tag, "Privmsg", thisEvent)
        data = self.factory.reCommand.match(msg.decode("utf-8"))
        if data:
            trigger = data.group(2)
            args = msg.split(" ")[1:]
            log.info("Received trigger %s%s." % (data.group(1),trigger))
            triggerEvent = event.TriggerEvent(self, user=user, channel=channel, msg=msg, args=args, match=data)
            event.fire(self.tag, "Trigger:%s" % trigger, triggerEvent)
    
    def pong(self, user, secs):
        log.debug("CTCP pong: %fs from %s", secs, user)
        thisEvent = event.CTCPPongEvent(self, user, secs)
        event.fire(self.tag, "CTCPPong", thisEvent)
    
    def irc_unknown(self, prefix, command, params):
        log.debug("Unknown RAW: %s; %s; %s", prefix, command, params)
        if command.lower() == "invite" and self.factory.settings.get("bot", "joinOnInvite") == "true":
            log.info("Got invited to %s, joining.", params[1])
            self.join(params[1])
        event.fire(self.tag, "irc_unknown", self, prefix, command, params)

    def irc_ERR_NICKNAMEINUSE(self, prefix, params):
        thisEvent = event.PreNicknameInUseError(self, prefix, params)
        def callback(event):
            if thisEvent.isCancelled == False:
                if len(self.factory.nicknames) > 0:
                    self.register(self.factory.nicknames.pop(0))
                    return
                irc.IRCClient.irc_ERR_NICKNAMEINUSE(self, event.prefix, event.params)
        event.fire(self.tag, "PreNicknameInUseError", thisEvent, callback=callback)

    def ctcpQuery_VERSION(self, user, channel, data):
        if data is None and self.versionName:
            thisEvent = event.CTCPVersionEvent(user)
            def eventCallback(thisEvent):
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
            event.fire(self.tag, "CTCPVersion", thisEvent, callback=eventCallback)


class BonesBotFactory(protocol.ClientFactory):
    sourceURL = "https://github.com/404d/Bones-IRCBot"
    versionName = "Bones IRCBot"
    versionNum = "0.2.0-DEV"
    versionEnv = ""

    protocol = BonesBot
    
    def __init__(self, settings):
        self.modules = []
        self.tag = settings.server

        self.urlopener = urllib2.build_opener()
        self.urlopener.addheaders = [('User-agent', 'urllib/2 BonesIRCBot/%s' % self.versionNum)]

        self.reconnectAttempts = 0

        self.settings = settings
        self.channels = settings.get("bot", "channel").split("\n")
        self.nicknames = settings.get("bot", "nickname").split("\n")
        try:
            self.nickname = self.nicknames.pop(0)
        except IndexError:
            raise InvalidConfigurationException, "No nicknames configured, property bot.nickname is empty"
        self.realname = settings.get("bot", "realname")
        self.username = settings.get("bot", "username")

        # Build the trigger regex using the trigger prefixes specified in settings
        prefixChars = settings.get("bot", "triggerPrefixes").decode("utf-8") # UTF-8 fix
        regex = "([%s])([a-zA-Z0-9]*)( .+)*?" % prefixChars
        self.reCommand = re.compile(regex, re.UNICODE)
        
        modules = settings.get("bot", "modules").split("\n")
        for module in modules:
            self.loadModule(module)
        event.fire(self.tag, "BotInitialized", self)

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
            event.register(instance, self.tag)
            log.info("Loaded module %s", path)
            event.fire(self.tag, "ModuleLoaded", module, userloaded)
        else:
            ex = InvalidBonesModuleException("Could not load module %s: Module is not a subclass of bones.bot.Module" % path)
            log.exception(ex)
            raise ex
    
    def clientConnectionLost(self, connector, reason):
        time = 10.0 * self.reconnectAttempts
        self.reconnectAttempts += 1
        log.info("{%s} Lost connection (%s), reconnecting in %i seconds.", self.tag, reason, time)
        reactor.callLater(time, connector.connect)
    
    def clientConnectionFailed(self, connector, reason):
        time = 30.0 * self.reconnectAttempts
        self.reconnectAttempts += 1
        log.info("{%s} Could not connect (%s), reconnecting in %i seconds.", self.tag, reason, time)
        reactor.callLater(time, connector.connect)

    def connect(self):
        serverHost = self.settings.get("server", "host")
        serverPort = int(self.settings.get("server", "port"))
        if self.settings.get("server", "useSSL") == "true":
            log.info("Connecting to server %s:+%i", serverHost, serverPort)
            try:
                from twisted.internet import ssl
            except ImportError:
                ex = Exception("Unmet dependency: pyOpenSSL not installed. This dependency needs to be installed before you can use SSL server connections")
                log.exception(ex)
                raise ex
            reactor.connectSSL(serverHost, serverPort, self, ssl.ClientContextFactory())
        else:
            log.info("Connecting to server %s:%i", serverHost, serverPort)
            reactor.connectTCP(serverHost, serverPort, self)


class Module():
    def __init__(self, settings):
        self.settings = settings
