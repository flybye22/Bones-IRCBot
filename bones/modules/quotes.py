import urllib
from bs4 import BeautifulSoup

from sqlalchemy import (
    Column,
    Integer,
    Text,
    )
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )
from sqlalchemy.sql.expression import func

from bones import event as events
from bones.bot import Module, urlopener
from bones.modules.storage import Base
from bones.modules.utilities import unescape


class RandomQuote(Module):
    def __init__(self, settings):
        self.settings = settings

    @events.handler(event="storage.Database:init")
    def gotDB(self, db):
        self.db = db

    @events.handler(trigger="quoterandom")
    def trigger(self, event):
        session = self.db.new_session()
        nick = event.user.nickname
        if len(event.args) > 0:
            nick = event.args[0]
        quote = session.query(RandomUserQuote).filter(RandomUserQuote.nickname==nick).order_by(func.random()).limit(1).first()
        if not quote:
            event.client.msg(event.channel, str("%s: The specified user is very quiet!" % event.user.nickname))
            return
        event.client.msg(event.channel, str(("%s: %s" % (quote.nickname, quote.quote)).encode("utf-8")))

    @events.handler(event="Privmsg")
    def logQuote(self, event):
        tmp = event.msg.strip()
        if tmp[1:].lower() != "quoterandom":
            session = self.db.new_session()
            quote = RandomUserQuote(
                    event.user.nickname,
                    event.channel,
                    event.msg,
                )
            session.begin()
            session.add(quote)
            session.commit()
            session.close()


class RandomUserQuote(Base):
    __tablename__ = "bones_randomquotes"

    id = Column(Integer, primary_key=True)
    nickname = Column(Text)
    channel = Column(Text)
    quote = Column(Text)

    def __init__(self, nickname, channel, quote):
        self.nickname = nickname
        self.channel = channel
        self.quote = quote
