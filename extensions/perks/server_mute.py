class serverMute(Perc):
    def __init__(self, bot: commands.Bot, basePrice=75):
        super().__init__(bot, basePrice)
        self.description = "server mute someone for 30 seconds"
        self.registerCommand(self.mute)
        self.muteRoleID = 799600022936223755

    @commands.command()
    async def mute(self, ctx: commands.Context, friend: discord.Member):
        muteRole = ctx.guild.get_role(self.muteRoleID)
        await friend.add_roles(muteRole)
        await asyncio.sleep(30)
        await friend.remove_roles(muteRole)
