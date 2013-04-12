import sys
from twisted.internet import reactor
from bones.bot import BonesBotFactory
from bones.modules import MinecraftServerList

if __name__ == "__main__":
    chan = sys.argv[1]
    botFactory = BonesBotFactory('#' + chan)
    botFactory.modules.append(MinecraftServerList())
    reactor.connectTCP('10.0.1.161', 6667, botFactory)
    reactor.run()