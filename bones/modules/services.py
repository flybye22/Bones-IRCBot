import logging
log = logging.getLogger(__name__)

import bones.event
from bones.bot import Module


class NickServ(Module):
    @bones.event.handler(event=bones.event.BotSignedOnEvent)
    def identifySignOn(self, event):
        # Make sure that we're supposed to identify now.
        if self.settings.get("services", "nickserv.waitForNotice") == "false":
            # We're good to go!
            log.info("Identifying with NickServ")
            event.client.msg("NickServ", "IDENTIFY %s" % self.settings.get("services", "nickserv.password"))

    @bones.event.handler(event=bones.event.BotNoticeReceivedEvent)
    def identifyNotice(self, event):
        # Make sure that we're supposed to identify now.
        if self.settings.get("services", "nickserv.waitForNotice") == "true" \
                and "IDENTIFY" in event.message \
                and bones.event.User(event.user, event.client).nickname.lower() == "nickserv":
            # We're good to go!
            log.info("Identifying with NickServ (triggered by notice)")
            event.client.msg(
                "NickServ",
                "IDENTIFY %s" %
                (self.settings.get("services", "nickserv.password"),)
            )


class HostServ(Module):

    def __init__(self, *args, **kwargs):
        Module.__init__(self, *args, **kwargs)
        self.channelJoinQueue = []
        self.haveVhost = False
        self.haveIdentified = False
        log.info(
            "HostServ module enabled, all joins will be cancelled until we "
            "have received a vhost."
        )

    @bones.event.handler(event=bones.event.BotSignedOnEvent)
    def cleanup(self, event):
        self.channelJoinQueue = []
        self.haveVhost = False
        self.haveIdentified = False

    @bones.event.handler(event=bones.event.BotPreJoinEvent)
    def preventUncloakedJoins(self, event):
        # One of the most important things we need to do is prevent
        # joining while we do not have a vhost
        if not self.haveVhost:
            log.debug("Queueing join to channel %s", event.channel.name)
            # Add channel to join queue
            self.channelJoinQueue.append(event.channel.name)
            # Cancel the event so that the bot won't join the channel
            event.isCancelled = True

    @bones.event.handler(event=bones.event.IRCUnknownCommandEvent)
    def manageReplies(self, event):
        # If the server is using cloaks, it will send a 396 while
        # giving us a cloak. Therefore we need to wait until we've
        # identified with services
        if event.command == "900":
            self.haveIdentified = True

        # Now that we've finally gotten our vhost, let's join all
        # those channels!
        elif event.command == "396" and self.haveIdentified:
            log.info("Received Vhost, joining all queued channels")
            # As we've got a vhost, we shouldn't prevent joins anymore.
            self.haveVhost = True
            while self.channelJoinQueue:
                event.client.join(self.channelJoinQueue.pop())
