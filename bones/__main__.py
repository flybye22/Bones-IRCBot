# -*- encoding: utf8 -*-
import sys
import os
import logging
import subprocess

from twisted.internet import reactor

from bones.bot import BonesBotFactory
from bones.config import BaseConfiguration

if __name__ == "__main__":
    logging.config.fileConfig(sys.argv[1])
    log = logging.getLogger(__package__)
    settings = BaseConfiguration(sys.argv[1])

    servers = []
    for section in settings._conf.sections():
        tmp = section.split(".")
        if len(tmp) == 2 and tmp[0].lower() == "server":
            servers.append(tmp[1])

    for server in servers:
        botFactory = BonesBotFactory(settings.server(server))
        botFactory.connect()
    reactor.run()
