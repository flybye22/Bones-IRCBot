import bones.bot
import bones.event
import sqlite3
import re

class Karmabot(bones.bot.Module):

    @bones.event.handler(event=bones.event.ChannelMessageEvent)
    def publicMessage(self, event):
        s = re.search("\A([a-z_\-\[\]\\^{}|`][a-z0-9_\-\[\]\\^{}|`]{2,15})(:)?( )?(\+\+|==)", event.message)
        conn = sqlite3.connect('stats.db')
        c = conn.cursor()
        if(s):
            if(event.user.name == s.group(1)):
                event.channel.msg("You can't karma yourself")
            else:
#                c.execute("CREATE TABLE stats(Id INTEGER PRIMARY KEY , source TEXT, dest TEXT, type INT)")
                c.execute("INSERT INTO stats VALUES (NULL, '%s', '%s', 0)" % (event.user.nickname, s.group(1)))
                conn.commit()
        s = re.search("\A\.karma ([a-z_\-\[\]\\^{}|`][a-z0-9_\-\[\]\\^{}|`]{2,15})", event.message)
        if(s):    
            c.execute("SELECT count(*) FROM stats WHERE dest LIKE '%s'" % (s.group(1)))
            results = c.fetchone()[0]
            event.channel.msg(
                "%s has %d karma" % (s.group(1), results)
            )
        conn.close()
        

    @bones.event.handler(event=bones.event.UserMessageEvent)
    def privMessage(self, event):
        event.user.msg(
            "Why are you sending me private messages?"
        )
