import logging
log = logging.getLogger(__name__)

from sqlalchemy import engine_from_config
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    sessionmaker,
)

import bones.event
from bones.bot import Module

Base = declarative_base()


class Database(Module):

    def __init__(self, **args):
        Module.__init__(self, **args)
        self.sessionmaker = None
        self.engine = None

    def new_session(self):
        return self.sessionmaker()

    def get_config(self):
        config = {}
        if "storage" in self.settings.data:
            config = self.settings.data["storage"]
        if "sqlalchemy.url" not in config:
            config["sqlalchemy.url"] = "sqlite:///bones.db"
        if "sqlalchemy.encoding" not in config:
            config["sqlalchemy.encoding"] = "utf-8"
        if "sqlalchemy.convert_unicode" not in config:
            config["sqlalchemy.convert_unicode"] = "true"
        return config

    @bones.event.handler(event=bones.event.BotInitializedEvent)
    def botReady(self, event):
        self.engine = engine_from_config(self.get_config(), "sqlalchemy.")
        log.debug("Connected to database")
        dbInitEvent = DatabaseInitializedEvent(self)
        bones.event.fire(event.factory.tag, dbInitEvent)
        self.sessionmaker = sessionmaker(bind=self.engine, autocommit=True)


class DatabaseInitializedEvent(bones.event.Event):
    def __init__(self, module):
        self.module = module
