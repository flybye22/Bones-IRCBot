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
import bones.event
from bones.bot import Module, urlopener
from bones.modules import storage


class UserQuotes(Module):

    @events.handler(event=storage.DatabaseInitializedEvent)
    def gotDB(self, event):
        self.db = event.module

    @events.handler(trigger="quoterandom")
    def trigger(self, event):
        session = self.db.new_session()
        nick = event.user.nickname
        if len(event.args) > 0:
            nick = event.args[0]
        quote = session.query(UserQuote).filter(UserQuote.nickname==nick).order_by(func.random()).limit(1).first()
        if not quote:
            event.channel.msg(str("%s: The specified user is very quiet!" % event.user.nickname))
            return
        style = "<%s> %s"
        if quote.type == "action":
            style = "* %s %s"
        event.channel.msg(str((style % (quote.nickname, quote.quote)).encode("utf-8")))

    @events.handler(event=bones.event.ChannelMessageEvent)
    @events.handler(event=bones.event.UserActionEvent)
    def logQuote(self, event):
        if isinstance(event, events.UserActionEvent):
            eventtype = "action"
            msg = event.data
        else:
            eventtype = "privmsg"
            msg = event.message
        tmp = msg.strip()
        if tmp[1:].lower() != "quoterandom":
            session = self.db.new_session()
            quote = UserQuote(
                    event.user.nickname,
                    event.channel.name,
                    msg.decode("utf-8", "ignore"),
                    eventtype
                )
            session.begin()
            session.add(quote)
            session.commit()
            session.close()


class ChannelQuotes(Module):

    @events.handler(event=storage.DatabaseInitializedEvent)
    def gotDB(self, event):
        self.db = event.module

    @events.handler(trigger="quote")
    def trigger(self, event):
        if len(event.args) < 1 or event.args[0].lower() not in ["read", "random", "add", "delete", "search"]:
            event.user.notice(str("[Quote] Need one of the following arguments: 'read', 'random', 'add', 'delete'"))
            return

        if event.args[0].lower() == "add":
            quote = " ".join(event.args[1:])
            if quote.isspace() or quote == "":
                event.user.notice(str("[Quote] That quote is empty!"))
                return

            cquote = ChannelQuote(
                    event.user.nickname,
                    event.channel.name,
                    quote.decode("utf-8", "ignore"),
                )
            session = self.db.new_session()
            session.begin()
            session.add(cquote)
            session.commit()
            event.channel.msg("Quote #%i saved." % cquote.id)
            return

        if event.args[0].lower() == "delete":
            if not len(event.args) >= 2:
                event.user.notice("[Quote] You need to provide a quote id!")
                return
            if not event.args[1].isdigit():
                event.user.notice("[Quote] Quote id needs to be a number!")
                return

            session = self.db.new_session()
            quote = session.query(ChannelQuote).filter(ChannelQuote.id==event.args[1]).limit(1).first()

            if not quote:
                event.channel.notice("[Quote] No such quote '%s'" % event.args[1])
                return

            dateThen = quote.timestamp.replace(tzinfo=None)
            dateNow = datetime.now()
            diff = dateNow - dateThen
            if quote.submitter != event.user.nickname:
                event.user.notice("[Quote] You do not have permission do delete this quote.")
                return
            if diff.seconds > 3600:
                event.user.notice("[Quote] This quote has been archived and thus cannot be removed.")
                return

            session.begin()
            session.delete(quote)
            session.commit()
            event.channel.msg("[Quote] Quote #%s deleted." % event.args[1])
            return

        if event.args[0].lower() == "random":
            session = self.db.new_session()
            quote = session.query(ChannelQuote).filter(ChannelQuote.channel==event.channel.name).order_by(func.random()).limit(1).first()
            self.sendQuote(event, quote)
            return

        if event.args[0].lower() == "search":
            if len(event.args) < 2:
                event.user.notice("[Quote] You need to provide a search term!")
                return

            session = self.db.new_session()
            quotes = session.query(ChannelQuote).filter(ChannelQuote.quote.like("%%%s%%" % " ".join(event.args[1:]))).order_by(ChannelQuote.id.asc()).all()
            if len(quotes) > 1:
                results = ""
                for result in quotes:
                    if results != "":
                        results = results + ", "
                    results = results + ("#%d" % result.id)
                event.channel.msg("[Quote] Results found: %s" % results)
                return
            if len(quotes) == 1:
                self.sendQuote(event, quotes.pop())
                return
            event.channel.msg("[Quote] No results found")
            return

        if event.args[0].lower() == "read":
            if not len(event.args) >= 2:
                event.user.notice("[Quote] You need to provide a quote id!")
                return
            if not event.args[1].isdigit():
                event.user.notice("[Quote] Quote id needs to be a number!")
                return

            session = self.db.new_session()
            quote = session.query(ChannelQuote).filter(ChannelQuote.id==event.args[1]).limit(1).first()
            self.sendQuote(event, quote)
            return


    def sendQuote(self, event, quote):
        if not quote:
            event.channel.msg(str(("[Quote] No such quote '%s'" % event.args[1]).encode("utf-8")))
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
        event.channel.msg(str(("[Quote] Quote #%i added %s ago by %s:" % (quote.id, ", ".join(date), quote.submitter)).encode("utf-8")))
        event.channel.msg(str(("[Quote] %s" % quote.quote).encode("utf-8")))


class UserQuote(storage.Base):
    __tablename__ = "bones_quotes_user"

    id = Column(Integer, primary_key=True)
    nickname = Column(Text)
    channel = Column(Text)
    quote = Column(Text)
    type = Column(Enum('privmsg','mode','notice','ctcp','action','quit','leave','nick','dcc', name="irc_message"))
    timestamp = Column(DateTime(timezone=True))

    def __init__(self, nickname, channel, quote, msgtype):
        self.nickname = nickname
        self.channel = channel
        self.quote = quote
        self.type = msgtype
        self.timestamp = datetime.now()


class ChannelQuote(storage.Base):
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

if __name__ == "__main__":
    from ConfigParser import SafeConfigParser
    from sqlalchemy import engine_from_config
    import sys
    settings = SafeConfigParser()
    if len(sys.argv) < 2:
        print "Error: You need to provide a config file!"
        sys.exit(1)
    settings.read(sys.argv[1])
    if "storage" not in settings._sections:
        print "Error: Config file does not contain a 'storage' section."
        sys.exit(1)
    elif "sqlalchemy.url" not in settings._sections["storage"]:
        print "Error: Section 'storage' does not contain an 'sqlalchemy.url' key."
        sys.exit(1)
    print "Connecting to '%s'..." % settings._sections["storage"]["sqlalchemy.url"]
    engine = engine_from_config(settings._sections["storage"], "sqlalchemy.")
    print "Creating tables..."
    from bones.modules.storage import Base
    Base.metadata.create_all(engine)
    print "Have a nice day!"
