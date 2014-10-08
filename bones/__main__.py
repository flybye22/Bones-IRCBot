# -*- encoding: utf8 -*-
import sys
import os
import logging
import subprocess
import ConfigParser

from twisted.internet import reactor

from bones.bot import BonesBotFactory
from bones.config import BaseConfiguration

if __name__ == "__main__":
    try:
        logging.config.fileConfig(sys.argv[1])
    except Exception, ex:
        import traceback
        traceback.print_exc()
        print "-" * 10
        print "Couldn't load logger configuration:"
        print ex.message
        raise SystemExit()
    log = logging.getLogger(__package__)
    settings = BaseConfiguration(sys.argv[1])

    servers = []
    for section in settings._conf.sections():
        tmp = section.split(".")
        if len(tmp) == 2 and tmp[0].lower() == "server":
            servers.append(tmp[1])

    if len(servers) < 1:
        log.error("""No server sections found in your configuration file!
Have you remembered to update your configuration file?
Read the following link for more info, namely the "Changes" section:
https://github.com/404d/Bones-IRCBot/pull/13""")
        raise SystemExit

    for server in servers:
        botFactory = BonesBotFactory(settings.server(server))
        botFactory.connect()
    reactor.run()
