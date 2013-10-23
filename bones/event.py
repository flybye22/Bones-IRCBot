import logging
from twisted.internet import threads

log = logging.getLogger(__name__)

eventHandlers = {}


def fire(server, event, *args, **kwargs):
    """Call all event handlers with the specified event identifier,
    registered to the provided server with the provided arguments.

    This may be called by your :term:`Bones module` to create and
    provide custom events. :code:`*args` and :code:`**kwargs` will
    be passed on to the event handlers.

    :param server: the server tag for the server this event occured
        at.
    :type server: str
    :param event: the event instance or the event identifier for the
        event which occured.
    :type event: object
    """
    def threadedFire(server, event, *args, **kwargs):
        callback = None
        if "callback" in kwargs:
            callback = kwargs["callback"]
            del kwargs["callback"]
        if isinstance(event, Event):
            args = (event,) + args
            event = event.__class__
        if server.lower() in eventHandlers:
            if event in eventHandlers[server.lower()]:
                for h in eventHandlers[server.lower()][event]:
                    try:
                        h['f'](h['c'], *args, **kwargs)
                    except Exception, ex:
                        log.exception(ex)
        if callback:
            callback(*args, **kwargs)
    threads.deferToThread(threadedFire, server, event, *args, **kwargs)


def handler(event=None, trigger=None):
    """Register the decorated method as an event handler for the supplied
    :term:`event` or :term:`trigger`.

    You can only supply one event/trigger per decorator call, and you can
    not supply both event and trigger in the same call. You cannot leave both
    of them empty.

    :param event: the class of the event you are going to handle
        (defaults to None).
    :type event: object.
    :param trigger: the trigger command to react to (defaults to None).
    :type trigger: str.
    """
    def realHandler(func):
        if event is not None or trigger is not None:
            if getattr(func, '_event', None) is None:
                func._event = []
            if event and not trigger:
                func._event.append(event)
            if trigger and not event:
                func._event.append("<Trigger: %s>" % trigger.lower())
            if trigger and event:
                log.error(
                    "Can't register both an event and a trigger with the same "
                    "bones.event.handler call."
                )
        return func
    return realHandler


def register(obj, server):
    """Look through a Module for registered event handlers and add
    them to the event handler list.

    This is an internal function automatically called by the server bot
    factory while creating the factory. **Do not** call this in your
    modules!

    :param obj: the :class:`Module` instance to look at.
    :type obj: :class:`bones.bot.Module`
    :param server: the server tag that the supplied module runs under.
    :type server: :class:`bones.bot.BonesBot`
    """
    klass = obj.__class__
    for name, item in klass.__dict__.iteritems():
        if getattr(item, '_event', None) is not None:
            for event in item._event:
                if server.lower() not in eventHandlers:
                    eventHandlers[server.lower()] = {}
                if event not in eventHandlers[server.lower()]:
                    eventHandlers[server.lower()][event] = []
                eventHandlers[server.lower()][event].append({"c": obj, "f": item})


class User():
    """Utility class turning a hostmask into distinguishable nickname,
    user and hostname attributes.

    :param mask: The IRC hostmask to be parsed. Ex:
        :code:`Bones!bot@192.168.0.2`
    :type mask: str

    .. attribute:: mask

        A string of the hostmask that this object originated from.

    .. attribute:: nickname

        A string of the nickname for the provided hostmask. Given
        the hostmask above, the nickname will be :code:`Bones`.

    .. attribute:: hostname

        A string of the hostname for the provided hostmask. Given
        the hostmask above, the hostname will be :code:`192.168.0.2`.

    .. attribute:: username

        A string of the username for the provided hostmask. Given
        the hostmask above, the hostname will be :code:`bot`.
    """
    def __init__(self, mask):
        self.mask = mask
        tmp = mask.split("!")
        self.nickname = tmp[0]
        tmp = tmp[1].split("@")
        self.username = tmp[0]
        self.hostname = tmp[1]


# ------------------------------------ #


class Event():
    pass


class BotModuleLoaded(Event):
    def __init__(self, module):
        self.module = module


class BotNoticeReceivedEvent(Event):
    def __init__(self, client, user, channel, message):
        self.client = client
        self.user = user
        self.channel = channel
        self.message = message


class BotInitializedEvent(Event):
    def __init__(self, factory):
        self.factory = factory


class BotJoinEvent(Event):
    def __init__(self, client, channel):
        self.client = client
        self.channel = channel


class BotKickedEvent(Event):
    def __init__(self, client, channel, kicker, message):
        self.client = client
        self.channel = channel
        self.kicker = kicker
        self.message = message


class BotNickChangedEvent(Event):
    def __init__(self, client, nick):
        self.client = client
        self.nick = nick


class BotPreJoinEvent(Event):
    def __init__(self, client, channel):
        self.isCancelled = False
        self.client = client
        self.channel = channel


class PreNicknameInUseError(Event):
    def __init__(self, client, prefix, params):
        self.isCancelled = False
        self.client = client
        self.prefix = prefix
        self.params = params


class BotSignedOnEvent(Event):
    """An event which is fired whenever the bot finishes connecting
    and registrating with the server.

    :param client: The bot instance that this event originates from.
    :type client: :class:`bones.bot.BonesBot`
    """
    def __init__(self, client):
        self.client = client


class BounceEvent(Event):
    def __init__(self, client, info):
        self.client = client
        self.info = info


class ChannelTopicChangedEvent(Event):
    def __init__(self, client, user, channel, newTopic):
        self.client = client
        self.user = user
        self.channel = channel
        self.newTopic = newTopic


class CTCPVersionEvent(Event):
    def __init__(self, user):
        self.isCancelled = False
        self.user = User(user)


class CTCPPongEvent(Event):
    def __init__(self, client, user, secs):
        self.client = client
        self.secs = secs
        self.user = User(user)


class IRCUnknownCommandEvent(Event):
    def __init__(self, client, prefix, command, params):
        self.client = client
        self.prefix = prefix
        self.command = command
        self.params = params


class ModeChangedEvent(Event):
    def __init__(self, client, user, channel, set, modes, args):
        self.client = client
        self.user = user
        self.channel = channel
        self.set = set
        self.modes = modes
        self.args = args


class PrivmsgEvent(Event):
    def __init__(self, client, user, channel, msg):
        self.client = client
        self.channel = channel
        self.user = User(user)
        self.msg = msg


class ServerChannelCountEvent(Event):
    def __init__(self, client, channels):
        self.client = client
        self.channels = channels


class ServerCreatedEvent(Event):
    def __init__(self, client, when):
        self.client = client
        self.when = when


class ServerClientInfoEvent(Event):
    def __init__(self, client, info):
        self.client = client
        self.info = info


class ServerHostInfoEvent(Event):
    def __init__(self, client, info):
        self.client = client
        self.info = info


class ServerInfoEvent(Event):
    def __init__(self, client, servername, version, umodes, cmodes):
        self.client = client
        self.servername = servername
        self.version = version
        self.umodes = umodes
        self.cmodes = cmodes


class ServerLocalInfoEvent(Event):
    def __init__(self, client, info):
        self.client = client
        self.info = info


class ServerMOTDReceivedEvent(Event):
    def __init__(self, client, motd):
        self.client = client
        self.motd = motd


class ServerOpCountEvent(Event):
    """An event that is fired during server connection. This event details
    how many operators are connected to the server.

    :param client: The bot instance for the server this event originated from.
    :type client: :class:`bones.bot.BonesBot`

    .. warning::

        This event is not fully documented

    .. attribute:: client

        A :class:`bones.bot.BonesBot` instance representing the server connection
        which received this event.
    """
    def __init__(self, client, ops):
        self.client = client
        self.ops = ops


class ServerSupportEvent(Event):
    """An event that is fired whenever the bot receives an :code:`ISUPPORT`
    during connection. This should be used by your :term:`Bones module` if
    you for example need :code:`WATCH` for your module to work.

    :param client: The bot instance for the server this event originated from.
    :type client: :class:`bones.bot.BonesBot`


    .. warning::

        This event is not fully documented

    .. attribute:: client

        A :class:`bones.bot.BonesBot` instance representing the server connection
        which received this event.
    """
    def __init__(self, client, options):
        self.client = client
        self.options = options


class TriggerEvent(PrivmsgEvent):
    """An event that is fired by the bot whenever it receives a :code:`PRIVMSG`
    event that starts with a valid trigger prefix and is a valid command.

    :param client: The bot instance which the event originated from.
    :type client: :class:`bones.bot.BonesBot`
    :param args: A list of all the arguments provided with the trigger command.
    :type args: list
    :param user: The user which initiated this event.
    :type user: :class:`bones.bot.User`
    :param msg: The original message that was parsed to reveal the trigger
        command.
    :type msg: str.
    :param match: The Regular Expression match object containing additional
        information about the parsing of the trigger command.
    :type match: :class:`SRE_Match`


    .. seealso::

        :class:`Event`,
        :class:`PrivmsgEvent`

    .. attribute:: args

        A list of strings containing all the arguments passed to the trigger
        command.

    .. attribute:: match

        The regex match object that was returned while parsing the original
        message, :attr:`msg`
    """
    def __init__(self, client, args=None, channel=None, user=None, msg=None, match=None):
        PrivmsgEvent.__init__(self, client, user, channel, msg)
        self.args = args
        self.match = match


class UserActionEvent(Event):
    """An event that is fired whenever another user sends a
    :code:`CTCP ACTION` to the channel.

    :param client: The bot instance where this event occured.
    :type client: :class:`bones.bot.BonesBot`
    :param user: The hostmask of the user which initiated this event.
    :type user: str.
    :param channel: The channel the :code:`CTCP ACTION` was sent to.
    :type channel: str.
    :param data: The text which is actioned.
    :type data: str.

    .. attribute:: channel

        A string representation of the channel the :class:`User` joined.

    .. attribute:: client

        The :class:`bones.bot.BonesBot` instance representing the connection
        to the server that this event originated from.

    .. attribute:: data

        A string representing the text which was actioned. Using the following
        example,
        ::

            * Nickname slaps Operator around a bit with a large trout

        the actioned text is everything following the nickname and the space
        immediately following i, or in other words
        :code:`slaps Operator around a bit with a large trout`.

    .. attribute:: user

        A :class:`User` instance representing the user who initiated
        this event.
    """
    def __init__(self, client, user, channel, data):
        self.client = client
        self.user = User(user)
        self.channel = channel
        self.data = data


class UserJoinEvent(Event):
    """An event that is fired whenever another user joins one
    of the channels the bot is in.

    :param client: The bot instance where this event occured.
    :type client: :class:`bones.bot.BonesBot`
    :param channel: The channel where this event occured.
    :type channel: str.
    :param user: The user who fired this event.
    :type user: :class:`User`

    .. attribute:: channel

        A string representation of the channel the :class:`User`
        joined.

    .. attribute:: client

        The :class:`bones.bot.BonesBot` instance representing the connection
        to the server that this event originated from.

    .. attribute:: user

        A :class:`User` instance representing the user who joined.
    """
    def __init__(self, client, channel, user):
        self.client = client
        self.channel = channel
        self.user = User(user)


class UserNickChangedEvent(Event):
    """An event which is fired whenever a user in one of the joined channels
    changes his/her nickname.

    :param client: The bot instance that this event originated from.
    :param oldname: The previous nickname the user went by.
    :type oldname: str
    :param newname: The new nickname the user is now using.
    :type newname: str

    .. attribute:: client

        The :class:`bones.bot.BonesBot` instance representing the connection
        to the server that this event originated from.

    .. attribute:: newname

        A string representation of the new nickname the user is using on the
        server.

    .. attribute:: oldname

        A string representation of the nickname the user went by on the server
        before the nickname change.

    """
    def __init__(self, client, oldname, newname):
        self.client = client
        self.oldname = oldname
        self.newname = newname


class UserPartEvent(Event):
    """An event that is fired whenever a user leaves a channel. This should
    not be confused with a :class:`bones.event.UserQuitEvent`, which is sent
    only when a user quits from the server.

    A :class:`UserPartEvent` is sent once to each channel the user parts
    from. The user may still be connected to IRC, but the user is not
    available in the channel designated by the :attr:`channel` attribute.

    :param client: The bot instance that this event originated from.
    :type client: :class:`bones.bot.BonesBot`
    :param user: The nickname of the user who parted from the channel.
    :type user: str.
    :param channel: The name of the channel the user parted from.
    :type channel: str.

    .. attribute:: channel

        A string representation of the name of the channel the parted from.

    .. attribute:: client

        The :class:`bones.bot.BonesBot` instance representing the connection
        to the server that this event originated from.

    .. attribute:: user

        A string representing the nickname of the user who parted from the
        channel.
    """
    def __init__(self, client, user, channel):
        self.client = client
        self.user = user
        self.channel = channel

class UserQuitEvent(Event):
    """An event that is fired whenever a user quits IRC, or in other words
    leaves the server. This may be either because of a ping timeout,
    server/IRC operator :code:`KILL` or the user sending :code:`QUIT` to the
    server. This event should not be confused with a
    :class:`bones.event.UserPartEvent`, which is sent once only when a user
    leaves a channel the bot is a part of.

    A :class:`UserQuitEvent` is sent once to the bot when the user quits from
    IRC, and does not mention what channels the user left while doing so. As
    such, when a :class:`UserQuitEvent` is sent all plugins should usually
    treat this as the user parted from all channels the users where in.

    The bot will not receive a :class:`UserQuitEvent` if the user has only been
    involved with the bot through a query, and not been in any of the channels
    the bot is in. The bot will also not receive a :class:`UserQuitEvent` if
    the user left all the channels the bot was in, and then :code:`QUIT` from
    IRC afterwards.

    :param client: The bot instance where this event occured.
    :type client: :class:`bones.bot.BonesBot`
    :param user: The user who quit IRC.
    :type user: str.
    :param quitMessage: The message sent with the quit command.
    :type quitMessage: str.

    .. attribute:: client

        The :class:`bones.bot.BonesBot` instance representing the connection to
        the server where this event occured.

    .. attribute:: user

        A string representing the nickname of the user who quit IRC.

    .. attribute:: quitMessage

        A string representing the message that was sent with the quit. This
        message is usually formated by the server so that user-specified
        quit messages doesn't look like i.e. a ping timeout or an operator
        :code:`KILL`.
    """
    def __init__(self, client, user, quitMessage):
        self.client = client
        self.user = user
        self.quitMessage = quitMessage

class UserKickedEvent(Event):
    """An event that is fired whenever a user have been kicked from a channel.

    :param client: The bot instance where this event occured.
    :type client: :class:`bones.bot.BonesBot`
    :param kickee: The nickname of the user who was kicked.
    :type kickee: str.
    :param kicker: The nickname of the user who kicked the kickee.
    :type kicker: str.
    :param message: The message provided with the kick, usually as a reason
        for the kick.
    :type message: str.

    .. attribute:: client

        A :class:`bones.bot.BonesBot` instance representing the server from
        which the event originated.

    .. attribute:: kickee

        A string representing the nickname of the user who was kicked by the
        kicker.

    .. attribute:: kicker

        A string representing the nickname of the user who kicked the kickee.
        This is the user who initiated this event.

    .. attribute:: message

        A string representing the message the kicker sent with the kick. This
        is often used as a reason for explaining the kick.
    """
    def __init__(self, client, kickee, channel, kicker, message):
        self.client = client
        self.kickee = kickee
        self.kicker = kicker
        self.message = message
