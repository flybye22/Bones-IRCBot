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
    scoped_session,
    sessionmaker,
    )

from bones.bot import Module
from bones import event

Base = declarative_base()

class Database(Module):
    try:
        from zope.sqlalchemy import ZopeTransactionExtension
        session = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
    except ImportError:
        log.warning("zope.sqlalchemy unavailable, won't use ZopeTransactionExtension()")
        session = scoped_session(sessionmaker())

    def __init__(self, settings):
        self.settings = settings
    
    @event.handler(event="BotInitialized")
    def botReady(self, factory):
        self.engine = engine_from_config(self.settings._sections["storage"], "sqlalchemy.")
        self.session.configure(bind=self.engine)
        log.debug("Connected to database")
        event.fire("storage.Database:init", self.session, self.engine)
