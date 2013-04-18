import logging

log = logging.getLogger(__name__)

eventHandlers = {}
triggerHandlers = {}

def fire(event, *args, **kwargs):
    if event in eventHandlers:
        for h in eventHandlers[event]:
            h['f'](h['c'], *args, **kwargs)
            
def fireTrigger(trigger, *args, **kwargs):
    if trigger in triggerHandlers:
        for h in triggerHandlers[trigger]:
            h['f'](h['c'], *args, **kwargs)

def handler(event=None, trigger=None):
    def realHandler(func):
        if event is not None:
            func._event = event
        if trigger is not None:
            func._trigger = trigger.lower()
        return func
    return realHandler

def module(klass):
    log.warning("Decorator @event.module is deprecated and will be removed in the future")
    return klass

def register(obj):
    klass = obj.__class__
    for name, item in klass.__dict__.iteritems():
        if getattr(item, '_event', None) is not None:
            if item._event not in eventHandlers:
                eventHandlers[item._event] = []
            eventHandlers[item._event].append({"c":obj, "f":item})
        
        if getattr(item, '_trigger', None) is not None:
            if item._trigger not in triggerHandlers:
                triggerHandlers[item._trigger] = []
            triggerHandlers[item._trigger].append({"c":obj, "f":item})


class User():
    def __init__(self, mask):
        self.mask = mask
        tmp = mask.split("!")
        self.nickname = tmp[0]
        tmp = tmp[1].split("@")
        self.username = tmp[0]
        self.hostname = tmp[1]


class Event():
    pass


class UserJoinEvent(Event):
    def __init__(self, client, channel):
        self.client = client
        self.channel = channel
        self.user = User(user)


class BotJoinEvent(Event):
    def __init__(self, client, channel):
        self.client = client
        self.channel = channel


class BotSignedOnEvent(Event):
    def __init__(self, client):
        self.client = client


class PrivmsgEvent(Event):
    def __init__(self, client, user, channel, msg):
        self.client = client
        self.channel = channel
        self.user = User(user)
        self.msg = msg


class TriggerEvent(PrivmsgEvent):
    def __init__(self, client, args=None, channel=None, user=None, msg=None):
        PrivmsgEvent.__init__(self, client, user, channel, msg)
        self.args = args

class CTCPPongEvent(Event):
    def __init__(self, client, user, secs):
        self.client = client
        self.secs = secs
        self.user = User(user)
