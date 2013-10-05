# -*- encoding: utf-8 -*-
from ConfigParser import SafeConfigParser

class BaseConfiguration(object):
    def __init__(self, file):
        self._conf = SafeConfigParser()
        self._conf.read(file)

    def get(self, section, option, server=None):
        if server and self._conf.has_section("server.%s.%s" % (server, section)):
            if self._conf.has_option("server.%s.%s" % (server, section), option):
                return self._conf.get("server.%s.%s" % (server, section), option)
        if self._conf.has_section(section):
            if self._conf.has_option(section, option):
                return self._conf.get(section, option)
        return None
    
    def rehash(self):
        self._conf.read(file)

    def server(self, server):
        return ServerConfiguration(server, self)

class ServerConfiguration(object):
    def __init__(self, server, configuration):
        self.config = configuration
        self.server = server
        self.data = {}
        self.load()

    def load(self):
        queue = []
        sections = self.config._conf.sections()

        for section in sections:
            try:
                self.data[section.lower()]
            except KeyError:
                self.data[section.lower()] = {}
            if section.lower().startswith("server."):
                tmp = section.split(".")
                if self.server and tmp[1] == self.server:
                    queue.append(section)
            else:
                for data in self.config._conf._sections[section]:
                    if not data == "__name__":
                        self.data[section.lower()][data] = self.config._conf._sections[section][data]

        for section in queue:
            tmp = section.split(".")
            if len(tmp) > 2:
                stmp = ".".join(tmp[2:]).lower()
            elif section.lower() == ("server.%s" % self.server).lower():
                stmp = "server"
            else:
                stmp = section.lower()
            try:
                self.data[stmp]
            except KeyError:
                self.data[stmp] = {}
            for data in self.config._conf._sections[section]:
                if not data == "__name__":
                    self.data[stmp][data] = self.config._conf._sections[section][data.lower()]

    def get(self, section, option):
        return self.data[section.lower()][option.lower()]
