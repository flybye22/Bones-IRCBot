import logging
from twisted.internet import threads

log = logging.getLogger(__name__)

eventHandlers = {}

def fire(server, event, *args, **kwargs):
    def threadedFire(server, event, *args, **kwargs):
        callback = None
        if "callback" in kwargs:
            callback = kwargs["callback"]
            del kwargs["callback"]
        if server.lower() in eventHandlers:
            if event.lower() in eventHandlers[server.lower()]:
                for h in eventHandlers[server.lower()][event.lower()]:
                    try:
                        h['f'](h['c'], *args, **kwargs)
                    except Exception, ex:
                        log.exception(ex)
        if callback:
            callback(*args, **kwargs)
    threads.deferToThread(threadedFire, server, event, *args, **kwargs)

def handler(event=None, trigger=None):
    def realHandler(func):
        if event is not None or trigger is not None:
            if getattr(func, '_event', None) is None:
                func._event = []
            if event:
                func._event.append(event.lower())
            if trigger:
                func._event.append("Trigger:%s" % trigger.lower())
        return func
    return realHandler

def register(obj, server):
    klass = obj.__class__
    for name, item in klass.__dict__.iteritems():
        if getattr(item, '_event', None) is not None:
            for event in item._event:
                if server.lower() not in eventHandlers:
                    eventHandlers[server.lower()] = {}
                if event.lower() not in eventHandlers[server.lower()]:
                    eventHandlers[server.lower()][event.lower()] = []
                eventHandlers[server.lower()][event.lower()].append({"c":obj, "f":item})


class User():
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


class BotNoticeReceivedEvent(Event):
    def __init__(self, client, user, channel, message):
        self.client = client
        self.user = user
        self.channel = channel
        self.message = message


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
    def __init__(self, client, ops):
        self.client = client
        self.ops = ops


class ServerSupportEvent(Event):
    def __init__(self, client, options):
        self.client = client
        self.options = options


class TriggerEvent(PrivmsgEvent):
    def __init__(self, client, args=None, channel=None, user=None, msg=None, match=None):
        PrivmsgEvent.__init__(self, client, user, channel, msg)
        self.args = args
        self.match = match


class UserActionEvent(Event):
    def __init__(self, client, user, channel, data):
        self.client = client
        self.user = User(user)
        self.channel = channel
        self.data = data


class UserJoinEvent(Event):
    def __init__(self, client, channel):
        self.client = client
        self.channel = channel
        self.user = User(user)


class UserNickChangedEvent(Event):
    def __init__(self, client, oldname, newname):
        self.client = client
        self.oldname = oldname
        self.newname = newname


class UserPartEvent(Event):
    def __init__(self, client, user, channel):
        self.client = client
        self.user = user
        self.channel = channel

class UserQuitEvent(Event):
    def __init__(self, client, user, quitMessage):
        self.client = client
        self.user = user
        self.quitMessage = quitMessage

class UserKickedEvent(Event):
    def __init__(self, client, kickee, channel, kicker, message):
        self.client = client
        self.kickee = kickee
        self.kicker = kicker
        self.message = message
