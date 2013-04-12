from bones.bot import Module

class MinecraftServerList(Module):
    def cmdMc(self, client, data, channel):
        client.msg(channel, "Ouch!")
        
    triggerMap = {
        "mc": cmdMc
    }