import bones.bot
import bones.event
import sqlite3
import re

NICK_RE = "[a-z_\-\[\]\\^{}|`][a-z0-9_\-\[\]\\^{}|`]{2,15}"
# DB table created using
# CREATE TABLE stats(Id INTEGER PRIMARY KEY , source TEXT, dest TEXT, type INT)

class Karmabot(bones.bot.Module):

    # registers an event handler for whenever somebody speaks in channel
    @bones.event.handler(event=bones.event.ChannelMessageEvent)
    def publicMessage(self, event):
        # matches start of line with colon or space and inline but without colon or space
        s = re.search("(^(%s):? ?(?:\+\+|==)|(%s)(?:\+\+|==))" % (NICK_RE, NICK_RE), event.message)
        conn = sqlite3.connect('stats.db')
        c = conn.cursor()
        if(s):
            if(s.group(2)):
                dest = s.group(2)
            else:
                dest = s.group(3)
            if(event.user.name == dest):
                event.channel.msg("You can't karma yourself")
            else:
                c.execute("INSERT INTO stats VALUES (NULL, '%s', '%s', 0)" % (event.user.nickname, dest))
                conn.commit()
        # matches start of line ".karma SOMENICK"
        # is slighlty vulnerable to SQL injection
        s = re.search("\A\.karma (%s)" % (NICK_RE), event.message)
        if(s):    
            c.execute("SELECT count(*) FROM stats WHERE dest LIKE '%s'" % (s.group(1)))
            results = c.fetchone()[0]
            event.channel.msg(
                "%s has %d karma" % (s.group(1), results)
            )
        conn.close()
        
    # registers an event handler for whenever somebody private messages the bot
    @bones.event.handler(event=bones.event.UserMessageEvent)
    def privMessage(self, event):
        event.user.msg(
            "Why are you sending me private messages?"
        )
