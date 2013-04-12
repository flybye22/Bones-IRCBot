import sys
from twisted.internet import reactor
from bones.bot import BonesBotFactory

if __name__ == "__main__":
    chan = sys.argv[1]
    reactor.connectTCP('10.0.1.161', 6667, BonesBotFactory('#' + chan))
    reactor.run()