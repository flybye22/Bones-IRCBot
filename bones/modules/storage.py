import logging
log = logging.getLogger(__name__)

from sqlalchemy import engine_from_config
from sqlalchemy import (
    Column,
    Text,
    Integer,
    )
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    sessionmaker,
    )

from bones.bot import Module
from bones import event

Base = declarative_base()

class Database(Module):
    sessionmaker = None

    def __init__(self, settings):
        self.settings = settings
    
    def new_session(self):
        return self.sessionmaker()
    
    @event.handler(event="BotInitialized")
    def botReady(self, factory):
        self.engine = engine_from_config(self.settings._sections["storage"], "sqlalchemy.")
        log.debug("Connected to database")
        event.fire("storage.Database:init", self)
        self.sessionmaker = sessionmaker(bind=self.engine, autocommit=True)
