

class MuteFriendPerc(Perc):
    def __init__(self, bot: commands.Bot, basePrice=10):
        super().__init__(bot, basePrice)
        self.registerCommand(self.muteFriend)
        self.description = "Mute your freind in a VC for a minute"

    @staticmethod
    def voiceConnected():
        async def check(ctx):
            # ctx.cog to get self
            if ctx.author.voice is None:
                raise NoVoice()
            else:
                return True

        return commands.check(check)

    @commands.command()
    @voiceConnected()
    async def muteFriend(self, ctx: commands.Context, friend: discord.Member):
        assert friend.voice is not None, "The freind is not in a voice channel doofus"
        await friend.edit(mute=True)
        await asyncio.sleep(60)
        await friend.edit(mute=False)
