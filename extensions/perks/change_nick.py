class ChangeNick(Perc):
    def __init__(self, bot: commands.Bot, basePrice=15):
        super().__init__(bot, basePrice)
        self.description = "Change someones nickname for 10 minutes, the change will revert"
        self.registerCommand(self.changeNick)

    @commands.command()
    async def changeNick(self, ctx: commands.Context, friend: discord.Member, nickname: str):
        current = friend.nick
        await friend.edit(nick=nickname)
        await asyncio.sleep(60 * 10)  # 10 minutes
        await friend.edit(nick=current)
