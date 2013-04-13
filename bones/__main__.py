# -*- encoding: utf8 -*-
import sys
from ConfigParser import SafeConfigParser

from twisted.internet import reactor

from bones.bot import BonesBotFactory
from bones.modules import (
        MinecraftServerList,
        UselessResponses,
    )


if __name__ == "__main__":
    settings = SafeConfigParser()
    settings.read(sys.argv[1])

    botFactory = BonesBotFactory(settings)
    botFactory.modules.append(MinecraftServerList())
    botFactory.modules.append(UselessResponses())

    serverHost = settings.get("server", "host")
    serverPort = int(settings.get("server", "port"))
    if settings.get("server", "useSSL") == "true":
        print "Using SSL."
        from twisted.internet import ssl
        reactor.connectSSL(serverHost, serverPort, botFactory, ssl.ClientContextFactory())
    else:
        reactor.connectTCP(serverHost, serverPort, botFactory)
    reactor.run()
