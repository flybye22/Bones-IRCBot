import bones.bot
import bones.event
import sqlite3
import re

NICK_RE = "[a-z_\-\[\]\\^{}|`][a-z0-9_\-\[\]\\^{}|`]{1,15}"
# DB table created using
# CREATE TABLE stats(Id INTEGER PRIMARY KEY , source TEXT, dest TEXT, type INT)

class Karmabot(bones.bot.Module):

    def __init__(self, factory, settings):
        self.conn = sqlite3.connect('stats.db', check_same_thread = False)
        self.cursor = self.conn.cursor()

    def getUserScore(self, user):
        self.cursor.execute("SELECT count(*) FROM stats WHERE dest LIKE '%s'" % (user))
        return self.cursor.fetchone()[0]

    def getAllScores(self):
        self.cursor.execute("SELECT dest, count(*) FROM stats GROUP BY dest ORDER BY count(*) DESC")
        return self.cursor.fetchall()

    def getUserScoreByPerson(self, user):
        self.cursor.execute("SELECT source, count(*) FROM stats WHERE dest LIKE '%s' GROUP BY source ORDER BY count(*) DESC" % user)
        return self.cursor.fetchall()

    def addKarmaEntry(self, source, dest, kind, event):
        if(source == dest):
            event.channel.msg("You can't karma yourself")
        else:
            self.cursor.execute("INSERT INTO stats VALUES (NULL, '%s', '%s', %d)" % (source, dest, kind))
            self.conn.commit()

    # registers an event handler for whenever somebody speaks in channel
    @bones.event.handler(event=bones.event.ChannelMessageEvent)
    def publicMessage(self, event):
        # various ++ and == rules
        search = re.search("^(%s):? ?\+\+" % (NICK_RE), event.message)
        if(search):
            self.addKarmaEntry(event.user.name, search.group(1), 0, event)
            return
        search = re.search("(%s)\+\+" % (NICK_RE), event.message)
        if(search):
            self.addKarmaEntry(event.user.name, search.group(1), 0, event)
            return
        search = re.search("^== ?(%s)" % (NICK_RE), event.message)
        if(search):
            self.addKarmaEntry(event.user.name, search.group(1), 1, event)
            return
        search = re.search("==(%s)" % (NICK_RE), event.message)
        if(search):
            self.addKarmaEntry(event.user.name, search.group(1), 1, event)
            return

        # commands
        search = re.search("\A\.karma (%s)" % (NICK_RE), event.message)
        if(search):
            val = self.getUserScore(search.group(1))
            #slightly vulnerable to sql injection
            event.channel.msg("%s has %d karma" % (search.group(1), val))

    # registers an event handler for whenever somebody private messages the bot
    @bones.event.handler(event=bones.event.UserMessageEvent)
    def privMessage(self, event):
        if(event.message == "totals"):
            result = "List of Karmas:\r"
            for person in self.getAllScores():
                result += str(person[0]) + ": " + str(person[1]) + "\r" 
            event.user.msg(result)
        elif(event.message == "breakdown"):
            result = "You have "
            for person in self.getUserScoreByPerson(event.user.name):
                result += str(person[1]) + " from " + str(person[0]) + ", "
            result = result[:-2]
            event.channel.msg(result)
        else:
            event.user.msg("I don't support any private commands besides 'totals' and 'breakdown' right now")
