# -*- encoding: utf8 -*-
import sys
from twisted.internet import reactor
from bones.bot import BonesBotFactory
from bones.modules import (
        MinecraftServerList,
        UselessResponses,
    )

if __name__ == "__main__":
    botFactory = BonesBotFactory([
        "#Minecraft",
        "#StepMania",
        "#Temporals",
        "#Gameshaft",
    ])
    botFactory.modules.append(MinecraftServerList())
    botFactory.modules.append(UselessResponses())
    reactor.connectTCP('10.0.1.161', 6667, botFactory)
    reactor.run()
