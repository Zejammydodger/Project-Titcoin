
class AdminZoo(Perc):
    def __init__(self, bot: commands.Bot, basePrice=50):
        super().__init__(bot, basePrice)
        self.description = "allows you to talk in admin zoo for 3 minutes, make em count"
        self.registerCommand(self.letMeIn)

    @commands.command()
    async def letMeIn(self, ctx : commands.Context):
        aZoo = ctx.guild.get_channel(954805755624697916)
        overWrite = discord.PermissionOverwrite()
        overWrite.send_messages = True
        await aZoo.set_permissions(ctx.author , overwrite = overWrite)
        await ctx.send("youre in go go go go")
        await asyncio.sleep(60)
        overWrite.send_messages = False
        await aZoo.set_permissions(ctx.author , overwrite = overWrite)
        await ctx.send("times up")
