

class StartCompany(Perc):
    def __init__(self, bot: commands.Bot, basePrice=500):
        super().__init__(bot, basePrice)
        self.registerCommand(self.startCompany)
        self.description = "Start your own company!"

    @staticmethod
    def hasNoCompany():
        async def check(ctx):
            P = profiles["profiles"][ctx.author.id]
            print(P.company)
            if P.company is None:
                return True
            else:
                raise HasCompany()

        return commands.check(check)

    @commands.command()
    @hasNoCompany()
    async def startCompany(self, ctx: commands.Context):
        # starts a dialoug sequence
        # information needed:
        # name
        # how much extra if any they would like to invest in their own company
        def checkFactory(auth: discord.Member, lambdaFunc=None):
            if lambdaFunc is None:
                lambdaFunc = lambda x: True

            def check(message: discord.Message) -> bool:
                return message.author == auth and lambdaFunc(message)

            return check

        P: Profile = profiles["profiles"][ctx.author.id]

        emb = discord.Embed(title="Company Name", description="what should the company be called")
        await ctx.send(embed=emb)
        while True:
            message: discord.Message = await self.bot.wait_for("message", check=checkFactory(ctx.author))
            if message is not None:
                break
            else:
                await ctx.send("you failed to respond in time, try again")
        name = message.content
        # weve got the name

        emb = discord.Embed(title="Extra funds",
                            description=f"would you like to invest any extra tc into `{name}`?\n\njust respond with 0 if you dont, else respond with a number")
        await ctx.send(embed=emb)

        while True:
            message: discord.Message = await self.bot.wait_for("message", check=checkFactory(ctx.author, lambda
                x: x.content.isdigit()))
            if message is None:
                await ctx.send("you failed to respond in time, try again")
            else:
                extra = float(message.content)
                if extra > P.currentBal:
                    await ctx.send(f"you do not posess the funds to do that, you have `{P.currentBal}`")
                else:
                    break
        # weve got extra
        Comp = Company(P, blankHistory(), [], name)  # creates company and adds it to profile
        Comp.createShare(P, self.currentPrice + extra)  # creates share, recalculates and adds to profile
        profiles["companies"].append(Comp)  # add comp to database

        emb = discord.Embed(title=f"{Comp.name}, established in {datetime.datetime.year}",
                            description=f"Founded by {Comp.owner}.\n{Comp.shares}")
        await ctx.send(embed=emb)