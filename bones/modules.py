from bones.bot import Module

class MinecraftServerList(Module):
    def cmdMc(self, client, args=None, channel=None, user=None, msg=None):
        client.msg(channel, "%s: Wait wait, I'm charging my batteries!" % user.split("!")[0])
        
    triggerMap = {
        "mcservers": cmdMc
    }