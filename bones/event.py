eventHandlers = {}

def fire(event, *args, **kwargs):
    for h in eventHandlers[event]:
        h['f'](h['c'], *args, **kwargs)

def handler(event=None):
    def realHandler(func):
        func._event = event
        return func
    return realHandler

def module(klass):
    for name, item in klass.__dict__.iteritems():
        if getattr(item, '_event', None):
            if item._event not in eventHandlers:
                eventHandlers[item._event] = []
            eventHandlers[item._event].append({"c":klass, "f":item})
    return klass

def injectInstance(klass):
    for event in eventHandlers:
        for handler in eventHandlers[event]:
            if handler['c'] == klass.__class__:
                handler['c'] = klass
