import logging
log = logging.getLogger(__name__)

from bones import event as events
from bones.bot import Module

class NickServ(Module):
    @events.handler(event="signedOn")
    def identifySignOn(self, event):
        # Make sure that we're supposed to identify now.
        if self.settings.get("services", "nickserv.waitForNotice") == "false":
            # We're good to go!
            log.info("Identifying with NickServ")
            event.client.msg("NickServ", "IDENTIFY %s" % self.settings.get("services", "nickserv.password"))

    @events.handler(event="noticed")
    def identifyNotice(self, event):
        # Make sure that we're supposed to identify now.
        if self.settings.get("services", "nickserv.waitForNotice") == "true" \
        and "IDENTIFY" in event.message \
        and events.User(event.user).nickname.lower() == "nickserv":
            # We're good to go!
            log.info("Identifying with NickServ (triggered by notice)")
            event.client.msg("NickServ", "IDENTIFY %s" % self.settings.get("services", "nickserv.password"))

class HostServ(Module):
    channelJoinQueue = []
    haveVhost = False
    haveIdentified = False
    
    def __init__(self, *args, **kwargs):
        Module.__init__(self, *args, **kwargs)
        log.info("HostServ module enabled, all joins will be cancelled until we have received a vhost.")

    @events.handler(event="preJoin")
    def preventUncloakedJoins(self, event):
        # One of the most important things we need to do is prevent
        # joining while we do not have a vhost
        if not self.haveVhost:
            log.debug("Queueing join to channel %s", event.channel)
            # Add channel to join queue
            self.channelJoinQueue.append(event.channel)
            # Cancel the event so that the bot won't join the channel
            event.isCancelled = True

    @events.handler(event="irc_unknown")
    def manageReplies(self, client, prefix, command, params):
        # If the server is using cloaks, it will send a 396 while
        # giving us a cloak. Therefore we need to wait until we've
        # identified with services
        if command == "900":
            self.haveIdentified = True
        
        # Now that we've finally gotten our vhost, let's join all those channels!
        elif command == "396" and self.haveIdentified:
            log.info("Received Vhost, joining all queued channels")
            # As we've got a vhost, we shouldn't prevent joins anymore.
            self.haveVhost = True
            while self.channelJoinQueue:
                client.join(self.channelJoinQueue.pop())
