# -*- encoding: utf8 -*-
import re
import logging
import logging.config
import urllib2

from twisted.words.protocols import irc
from twisted.internet import protocol, reactor

import bones.event


log = logging.getLogger(__name__)

urlopener = urllib2.build_opener()
urlopener.addheaders = [('User-agent', 'urllib/2 BonesIRCBot/0.2.0-DEV')]


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

        event = bones.event.BotSignedOnEvent(self)
        bones.event.fire(self.tag, event)
        log.info("Signed on as %s.", self.nickname)

        for channel in self.factory.channels:
            self.join(channel)

    def created(self, when):
        log.debug(
            "Received server creation info: %s",
            when
        )
        event = bones.event.ServerCreatedEvent(self, when)
        bones.event.fire(self.tag, event)

    def yourHost(self, info):
        log.debug(
            "Received server host info: %s",
            info
        )
        event = bones.event.ServerHostInfoEvent(self, info)
        bones.event.fire(self.tag, event)

    def myInfo(self, servername, version, umodes, cmodes):
        log.debug(
            "Received server info from %s: Version %s, Usermodes %s, "
            "Channelmodes %s",

            servername, version, umodes, cmodes
        )
        event = bones.event.ServerInfoEvent(
            self, servername, version, umodes, cmodes
        )
        bones.event.fire(self.tag, event)

    def luserClient(self, info):
        log.debug(
            "Received client info from server: %s",
            info
        )
        event = bones.event.ServerClientInfoEvent(self, info)
        bones.event.fire(self.tag, event)

    def bounce(self, info):
        log.debug(
            "Received bounce info: %s",
            info
        )
        event = bones.event.BounceEvent(self, info)
        bones.event.fire(self.tag, event)

    def isupport(self, options):
        log.debug(
            "Received server support flags: %s",
            " ".join(options)
        )
        event = bones.event.ServerSupportEvent(self, options)
        bones.event.fire(self.tag, event)

    def luserChannels(self, channels):
        log.debug(
            "This server have %s channels",
            channels
        )
        event = bones.event.ServerChannelCountEvent(self, channels)
        bones.event.fire(self.tag, event)

    def luserOp(self, ops):
        log.debug(
            "There's currently %s opered clients on this server",
            ops
        )
        event = bones.event.ServerOpCountEvent(self, ops)
        bones.event.fire(self.tag, event)

    def luserMe(self, info):
        log.debug(
            "Received local server info: %s",
            info
        )
        event = bones.event.ServerLocalInfoEvent(self, info)
        bones.event.fire(self.tag, event)

    def noticed(self, user, channel, message):
        log.debug(
            "NOTICE in %s from %s: %s",
            channel, user, message
        )
        event = bones.event.BotNoticeReceivedEvent(
            self, user, channel, message
        )
        bones.event.fire(self.tag, event)

    def modeChanged(self, user, channel, set, modes, args):
        if set:
            setString = "+"
        else:
            setString = "-"
        log.debug(
            "Mode change in %s: %s set %s%s (%s)",
            channel, user, setString, modes, args
        )
        event = bones.event.ModeChangedEvent(
            self, user, channel, set, modes, args
        )
        bones.event.fire(self.tag, event)

    def kickedFrom(self, channel, kicker, message):
        log.info(
            "Kicked from channel %s by %s. Reason: %s",
            channel, kicker, message
        )
        event = bones.event.BotKickedEvent(self, channel, kicker, message)
        bones.event.fire(self.tag, event)

    def nickChanged(self, nick):
        log.info(
            "Changed nick to %s",
            nick
        )
        event = bones.event.BotNickChangedEvent(self, nick)
        bones.event.fire(self.tag, event)

    def userLeft(self, user, channel):
        log.debug(
            "User %s parted from %s",
            user, channel
        )
        event = bones.event.UserPartEvent(self, user, channel)
        bones.event.fire(self.tag, event)

    def userQuit(self, user, quitMessage):
        log.debug(
            "User %s quit (Reason: %s)",
            user, quitMessage
        )
        event = bones.event.UserQuitEvent(self, user, quitMessage)
        bones.event.fire(self.tag, event)

    def userKicked(self, kickee, channel, kicker, message):
        log.debug(
            "User %s was kicked from %s by %s (Reason: %s)",
            kickee, channel, kicker, message
        )
        event = bones.event.UserKickedEvent(
            self, kickee, channel, kicker, message
        )
        bones.event.fire(self.tag, event)

    def action(self, user, channel, data):
        log.debug(
            "User %s actioned in %s: %s",
            user, channel, data
        )
        event = bones.event.UserActionEvent(self, user, channel, data)
        bones.event.fire(self.tag, event)

    def topicUpdated(self, user, channel, newTopic):
        log.debug(
            "User %s changed topic of %s to %s",
            user, channel, newTopic
        )
        event = bones.event.ChannelTopicChangedEvent(
            self, user, channel, newTopic
        )
        bones.event.fire(self.tag, event)

    def userRenamed(self, oldname, newname):
        log.debug(
            "User %s changed nickname to %s",
            oldname, newname
        )
        event = bones.event.UserNickChangedEvent(self, oldname, newname)
        bones.event.fire(self.tag, event)

    def receivedMOTD(self, motd):
        event = bones.event.ServerMOTDReceivedEvent(self, motd)
        bones.event.fire(self.tag, event)

    def joined(self, channel):
        log.info(
            "Joined channel %s.",
            channel
        )
        event = bones.event.BotJoinEvent(self, channel)
        bones.event.fire(self.tag, event)

    def join(self, channel):
        event = bones.event.BotPreJoinEvent(self, channel)

        def doJoin(thisEvent):
            if thisEvent.isCancelled is False:
                irc.IRCClient.join(thisEvent.client, thisEvent.channel)

        bones.event.fire(self.tag, event, callback=doJoin)

    def userJoin(self, user, channel):
        event = bones.event.UserJoinEvent(self, user, channel)
        bones.event.fire(self.tag, event)
        log.debug("Event userJoin: %s %s", user, channel)

    def privmsg(self, user, channel, msg):
        log.debug(
            "Event privmsg: %s %s :%s",
            user, channel, msg
        )
        if not channel.startswith("#") and not channel.startswith("&"):
            channel = user.split("!")[0]
        event = bones.event.PrivmsgEvent(self, user, channel, msg)
        bones.event.fire(self.tag, event)
        data = self.factory.reCommand.match(msg.decode("utf-8"))
        if data:
            trigger = data.group(2)
            args = msg.split(" ")[1:]
            log.info(
                "Received trigger %s%s.",
                data.group(1), trigger
            )
            triggerEvent = bones.event.TriggerEvent(
                self, user=user, channel=channel, msg=msg, args=args,
                match=data
            )
            bones.event.fire(self.tag, "<Trigger: %s>" % trigger.lower(), triggerEvent)

    def pong(self, user, secs):
        log.debug(
            "CTCP pong: %fs from %s",
            secs, user
        )
        event = bones.event.CTCPPongEvent(self, user, secs)
        bones.event.fire(self.tag, event)

    def irc_unknown(self, prefix, command, params):
        log.debug(
            "Unknown RAW: %s; %s; %s",
            prefix, command, params
        )
        if command.lower() == "invite" \
                and self.factory.settings.get("bot", "joinOnInvite") == "true":
            log.info(
                "Got invited to %s, joining.",
                params[1]
            )
            self.join(params[1])
        bones.event.fire(
            self.tag, "irc_unknown", self, prefix, command, params
        )

    def irc_ERR_NICKNAMEINUSE(self, prefix, params):
        event = bones.event.PreNicknameInUseError(self, prefix, params)

        def callback(event):
            if event.isCancelled is False:
                if len(self.factory.nicknames) > 0:
                    self.register(self.factory.nicknames.pop(0))
                    return
                irc.IRCClient.irc_ERR_NICKNAMEINUSE(
                    self, event.prefix, event.params
                )

        bones.event.fire(
            self.tag, event,
            callback=callback
        )

    def ctcpQuery_VERSION(self, user, channel, data):
        if data is None and self.versionName:
            event = bones.event.CTCPVersionEvent(user)

            def eventCallback(thisEvent):
                if not event.isCancelled:
                    version = "%s %s %s" % (
                        self.versionName,
                        self.versionNum,
                        self.versionEnv,
                    )
                    version = version.replace("\n", "")
                    self.ctcpMakeReply(
                        event.user.nickname, [('VERSION', version)]
                    )
                    log.debug(
                        "Received CTCP VERSION query from %s, replied '%s'.",
                        user, version
                    )
                else:
                    log.debug(
                        "Received CTCP VERSION query from %s, but event was"
                        "cancelled by an eventhandler.",
                        user
                    )
            bones.event.fire(
                self.tag, event, callback=eventCallback
            )


class BonesBotFactory(protocol.ClientFactory):
    """The Twisted client factory that provides connection management
    and configuration for each individual bot configuration.


    .. attribute:: sourceURL

        A hardcoded string URL to the Bones IRC Bot repository. Sent
        to clients in response to a :code:`CTCP SOURCEURL` query.

    .. attribute:: versionEnv

        Currently unused. Sent to clients as a part of a
        :code:`CTCP VERSION` reply.

    .. attribute:: versionName

        The name of the bot. Sent to clients as a part of a
        :code:`CTCP VERSION` reply.

    .. attribute:: versionNum

        The release name of the current bot version. Sent to clients
        as a part of a :code:`CTCP VERSION` reply.
    """

    sourceURL = "https://github.com/404d/Bones-IRCBot"
    versionName = "Bones IRCBot"
    versionNum = "0.2.0-DEV"
    versionEnv = ""

    protocol = BonesBot

    def __init__(self, settings):
        self.modules = []
        self.tag = settings.server

        self.reconnectAttempts = 0

        self.settings = settings
        self.channels = settings.get("bot", "channel").split("\n")
        self.nicknames = settings.get("bot", "nickname").split("\n")
        try:
            self.nickname = self.nicknames.pop(0)
        except IndexError:
            raise InvalidConfigurationException(
                "No nicknames configured, property bot.nickname is empty"
            )
        self.realname = settings.get("bot", "realname")
        self.username = settings.get("bot", "username")

        # Build the trigger regex using the trigger prefixes
        # specified in settings
        prefixChars = settings.get("bot", "triggerPrefixes").decode("utf-8")
        regex = "([%s])([a-zA-Z0-9]*)( .+)*?" % prefixChars
        self.reCommand = re.compile(regex, re.UNICODE)

        modules = settings.get("bot", "modules").split("\n")
        for module in modules:
            self.loadModule(module)
        bones.event.fire(self.tag, bones.event.BotInitializedEvent(self))

    def loadModule(self, path):
        """Loads the specified module and adds it to the bot if it is a
        valid :term:`Bones module`.

        :param path: The Python dot-notation path to the module that should be
            loaded.
        :type path: str.

        :raises:
            :class:`~bones.bot.BonesModuleAlreadyLoadedException,`
            :class:`~bones.bot.InvalidBonesModuleException,`
            :class:`~bones.bot.InvalidConfigurationException,`
            :class:`~bones.bot.NoSuchBonesException`
        """
        tmppath = path.split(".")
        package = ".".join(tmppath[:len(tmppath)-1])
        name = tmppath[len(tmppath)-1:len(tmppath)][0]

        try:
            module = __import__(package, fromlist=[name])
        except ImportError as ex_raised:
            ex = NoSuchBonesModuleException(
                "Could not load module %s: No such package. "
                "(ImportException: %s)" %

                (path, ex_raised.message)
            )
            log.exception(ex)
            raise ex

        try:
            module = getattr(module, name)
        except AttributeError as ex_raised:
            ex = NoSuchBonesModuleException(
                "Could not load module %s: No such class. "
                "(AttributeException: %s)" %

                (path, ex_raised.message)
                )
            log.exception(ex)
            raise ex

        if issubclass(module, Module):
            if module in [m.__class__ for m in self.modules]:
                ex = BonesModuleAlreadyLoadedException(
                    "Could not load module %s: Module already loaded" %
                    (path,)
                )
                log.exception(ex)
                raise ex
            instance = module(self.settings)
            self.modules.append(instance)
            bones.event.register(instance, self.tag)
            log.info("Loaded module %s", path)
            bones.event.fire(self.tag, "ModuleLoaded", module)
        else:
            ex = InvalidBonesModuleException(
                "Could not load module %s: Module is not a subclass of "
                "bones.bot.Module" %

                path
            )
            log.exception(ex)
            raise ex

    def clientConnectionLost(self, connector, reason):
        """Called when the connection to the server was lost. This method
        will take care of reconnecting the bot to the server after a variable
        time period.
        """

        time = 10.0 * self.reconnectAttempts
        self.reconnectAttempts += 1
        log.info(
            "{%s} Lost connection (%s), reconnecting in %i seconds.",
            self.tag, reason, time
        )
        reactor.callLater(time, connector.connect)

    def clientConnectionFailed(self, connector, reason):
        """Called when an error occured with the connection. This method
        will take care of reconnecting the bot to the server after a variable
        time period.
        """

        time = 30.0 * self.reconnectAttempts
        self.reconnectAttempts += 1
        log.info(
            "{%s} Could not connect (%s), reconnecting in %i seconds.",
            self.tag, reason, time
        )
        reactor.callLater(time, connector.connect)

    def connect(self):
        """Connects this bot factory to the server it is configured for.
        Gets called automatically by the default manager at boot and by
        the factory when reconnecting a lost or failed connection.
        """

        serverHost = self.settings.get("server", "host")
        serverPort = int(self.settings.get("server", "port"))
        if self.settings.get("server", "useSSL") == "true":
            log.info("Connecting to server %s:+%i", serverHost, serverPort)
            try:
                from twisted.internet import ssl
            except ImportError:
                ex = Exception(
                    "Unmet dependency: pyOpenSSL not installed. This "
                    "dependency needs to be installed before you can use SSL "
                    "server connections"
                )
                log.exception(ex)
                raise ex
            reactor.connectSSL(
                serverHost, serverPort, self, ssl.ClientContextFactory()
            )
        else:
            log.info("Connecting to server %s:%i", serverHost, serverPort)
            reactor.connectTCP(serverHost, serverPort, self)


class Module():
    """:term:`Bones module` base class

    :param settings: The settings for the current server factory.
    :type settings: :class:`bones.config.ServerConfiguration`

    .. attribute:: settings

        A :class:`bones.config.ServerConfiguration` instance containing all the
        currently loaded settings for this server factory and all its bots and
        modules.
    """

    def __init__(self, settings):
        self.settings = settings
