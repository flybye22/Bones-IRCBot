from datetime import datetime
import urllib

from bs4 import BeautifulSoup
from sqlalchemy import (
    Column,
    Integer,
    Text,
    Enum,
    DateTime,
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


class UserQuotes(Module):

    @events.handler(event="storage.Database:init")
    def gotDB(self, db):
        self.db = db

    @events.handler(trigger="quoterandom")
    def trigger(self, event):
        session = self.db.new_session()
        nick = event.user.nickname
        if len(event.args) > 0:
            nick = event.args[0]
        quote = session.query(UserQuote).filter(UserQuote.nickname==nick).order_by(func.random()).limit(1).first()
        if not quote:
            event.client.msg(event.channel, str("%s: The specified user is very quiet!" % event.user.nickname))
            return
        style = "<%s> %s"
        if quote.type == "action":
            style = "* %s %s"
        event.client.msg(event.channel, str((style % (quote.nickname, quote.quote)).encode("utf-8")))

    @events.handler(event="Privmsg")
    @events.handler(event="UserAction")
    def logQuote(self, event):
        if isinstance(event, events.UserActionEvent):
            eventtype = "action"
            msg = event.data
        else:
            eventtype = "privmsg"
            msg = event.msg
        tmp = msg.strip()
        if tmp[1:].lower() != "quoterandom":
            session = self.db.new_session()
            quote = UserQuote(
                    event.user.nickname,
                    event.channel,
                    msg,
                    eventtype
                )
            session.begin()
            session.add(quote)
            session.commit()
            session.close()


class ChannelQuotes(Module):

    @events.handler(event="storage.Database:init")
    def gotDB(self, db):
        self.db = db

    @events.handler(trigger="quote")
    def trigger(self, event):
        if len(event.args) < 1 or event.args[0].lower() not in ["read","random","add"]:
            event.client.notice(event.user.nickname, str("[Quote] Need one of the following arguments: 'read', 'random', 'add'"))
            return

        if event.args[0].lower() == "add":
            quote = " ".join(event.args[1:])
            if quote.isspace() or quote == "":
                event.client.notice(event.user.nickname, str("[Quote] That quote is empty!"))
                return

            cquote = ChannelQuote(
                    event.user.nickname,
                    event.channel,
                    quote,
                )
            session = self.db.new_session()
            session.begin()
            session.add(cquote)
            session.commit()
            event.client.msg(event.channel, "Quote #%i saved." % cquote.id)
            return

        if event.args[0].lower() == "random":
            session = self.db.new_session()
            quote = session.query(ChannelQuote).filter(ChannelQuote.channel==event.channel).order_by(func.random()).limit(1).first()
            self.sendQuote(event, quote)
            return

        if event.args[0].lower() == "read":
            if not len(event.args) >= 2:
                event.client.notice(event.user.nickname, "[Quote] You need to provide a quote id!")
                return
            if not event.args[1].isdigit():
                event.client.notice(event.user.nickname, "[Quote] Quote id needs to be a number!")
                return

            session = self.db.new_session()
            quote = session.query(ChannelQuote).filter(ChannelQuote.id==event.args[1]).limit(1).first()
            self.sendQuote(event, quote)
            return


    def sendQuote(self, event, quote):
        if not quote:
            event.client.msg(event.channel, str(("[Quote] No such quote '%s'" % event.args[1]).encode("utf-8")))
            return
        date = []
        dateThen = quote.timestamp.replace(tzinfo=None)
        dateNow = datetime.now()
        diff = dateNow - dateThen

        if diff.days > 0:
            if diff.days != 1:
                suffix = "s"
            else:
                suffix = ""
            date.append("%s day%s" % (diff.days, suffix))

        hours = (diff.seconds//3600)%24
        if hours > 0:
            if hours != 1:
                suffix = "s"
            else:
                suffix = ""
            date.append("%s hour%s" % (hours, suffix))

        minutes = (diff.seconds//60)%60
        if minutes != 1:
            suffix = "s"
        else:
            suffix = ""
        date.append("%s minute%s" % (minutes, suffix))
        event.client.msg(event.channel, str(("[Quote] Quote #%i added %s ago by %s:" % (quote.id, ", ".join(date), quote.submitter)).encode("utf-8")))
        event.client.msg(event.channel, str(("[Quote] %s" % quote.quote).encode("utf-8")))


class UserQuote(Base):
    __tablename__ = "bones_quotes_user"

    id = Column(Integer, primary_key=True)
    nickname = Column(Text)
    channel = Column(Text)
    quote = Column(Text)
    type = Column(Enum('privmsg','mode','notice','ctcp','action','quit','leave','nick','dcc'))
    timestamp = Column(DateTime(timezone=True))

    def __init__(self, nickname, channel, quote, msgtype):
        self.nickname = nickname
        self.channel = channel
        self.quote = quote
        self.type = msgtype
        self.timestamp = datetime.now()


class ChannelQuote(Base):
    __tablename__ = "bones_quotes_channel"
    
    id = Column(Integer, primary_key=True)
    submitter = Column(Text)
    channel = Column(Text)
    quote = Column(Text)
    timestamp = Column(DateTime(timezone=True))

    def __init__(self, submitter, channel, quote):
        self.submitter = submitter
        self.channel = channel
        self.quote = quote
        self.timestamp = datetime.now()
