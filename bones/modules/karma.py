import bones.bot
import bones.event
import sqlite3
import re

NICK_RE = "[a-z_\-\[\]\\^{}|`][a-z0-9_\-\[\]\\^{}|`]{1,15}"
# DB table created using
# CREATE TABLE stats(Id INTEGER PRIMARY KEY , source TEXT, dest TEXT, type INT)

class Karmabot(bones.bot.Module):

    def getUserScore(self, user):
        conn = sqlite3.connect('stats.db')
        c = conn.cursor()
        c.execute("SELECT count(*) FROM stats WHERE dest LIKE '%s'" % (user))
        result = c.fetchone()[0]
        conn.close()
        return result

    def getAllScores(self):
        conn = sqlite3.connect('stats.db')
        c = conn.cursor()
        c.execute("SELECT dest, count(*) FROM stats GROUP BY dest ORDER BY count(*) DESC")
        result = c.fetchall()
        conn.close()
        return result

    def addKarmaEntry(self, source, dest, kind):
        conn = sqlite3.connect('stats.db')
        c = conn.cursor()
        c.execute("INSERT INTO stats VALUES (NULL, '%s', '%s', %d)" % (source, dest, kind))
        conn.commit()
        conn.close()

    # searches, assumes username match will be the first group
    def searchAndAdd(self, regex, event, kind):
        s = re.search(regex, event.message)
        if(s):
            if(event.user.name == s.group(1)):
                event.channel.msg("You can't karma yourself")
            else:
                self.addKarmaEntry(event.user.name, s.group(1), kind)
            return True
        return False

    # registers an event handler for whenever somebody speaks in channel
    @bones.event.handler(event=bones.event.ChannelMessageEvent)
    def publicMessage(self, event):
        # various ++ and == rules
        if(self.searchAndAdd("^(%s):? ?\+\+" % (NICK_RE), event, 0)):
            pass
        elif(self.searchAndAdd("(%s)\+\+" % (NICK_RE), event, 0)):
            pass
        elif(self.searchAndAdd("^== ?(%s)" % (NICK_RE), event, 1)):
            pass
        elif(self.searchAndAdd("==(%s)" % (NICK_RE), event, 1)):
            pass
        
        # matches start of line ".karma SOMENICK"
        # is slighlty vulnerable to SQL injection
        s = re.search("\A\.karma (%s)" % (NICK_RE), event.message)
        if(s):
            val = self.getUserScore(s.group(1))
            event.channel.msg("%s has %d karma" % (s.group(1), val))
        
    # registers an event handler for whenever somebody private messages the bot
    @bones.event.handler(event=bones.event.UserMessageEvent)
    def privMessage(self, event):
        if(event.message == "totals"):
            result = "List of Karmas:\r"
            for person in self.getAllScores():
                result += str(person[0]) + ": " + str(person[1]) + "\r" 
            event.user.msg(result)
        else:
            event.user.msg("I don't support any private command besides 'totals' right now")
