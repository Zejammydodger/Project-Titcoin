import time
import asyncio
import math
import random
import datetime
import discord
from discord.ext import commands, tasks
from titcoinHelpers import NoVoice, Denied, HasCompany
from sqlHelper import Profile, Company, Share, load, save, initDataBase, blankHistory
from extensions import titcoin      # be careful with this one, there's a big risk of circular import errors
import traceback


# Perk base class
class Perk(commands.Cog):
    def __init__(self, bot: commands.Bot, titcoin: titcoin.TitCoin, basePrice=10):
        super().__init__()
        self.description = "N/A"            # implement a description for your perc
        self.basePrice: int = basePrice
        self.currentPrice = basePrice
        self.modifyVal = 0.1
        self.bot = bot
        self.commands: list[commands.Command] = []
        self.titcoin = titcoin
        self.titcoin.perks.append(self)
        bot.add_cog(self)
        self.deflate.start()

    @tasks.loop(hours=1)
    async def deflate(self):
        # reduces the current price down to baseprice
        if math.floor(self.currentPrice - (self.currentPrice * self.modifyVal)) <= self.basePrice:
            self.currentPrice = self.basePrice
        else:
            self.currentPrice -= (self.currentPrice * self.modifyVal)

    def hasFunds(self):
        async def memHasFundsCheck(ctx: commands.Context):
            # stops the command based on weather the member has enough tc to use this command
            P = self.titcoin.profiles["profiles"][ctx.author.id]
            return P.currentBal >= self.currentPrice

        return memHasFundsCheck

    def confirmed(self):
        # prompts the user to confirm if they want to spend that much
        yes = "✅"
        no = "❌"

        async def confirmCheck(ctx: commands.Context):
            def sameAuth(reaction: discord.Reaction, user):
                return ctx.author == user and str(reaction.emoji) in [yes, no]

            msg: discord.Message = await ctx.send(embed=discord.Embed(title="u sure homie?",
                                                                      description=f"You are about to spend `[{round(self.currentPrice, 2)}tc]`"))
            await msg.add_reaction(yes)  # yes
            await msg.add_reaction(no)  # no
            reaction, user = await self.bot.wait_for("reaction_add", check=sameAuth)
            if str(reaction.emoji) == yes:
                return True
            else:
                raise Denied

        return confirmCheck

    async def modifyPrice(self, _, ctx: commands.Context):
        # modifies the price of the command
        # god i hope this only goes off if the actual command is run ;-;
        self.currentPrice += self.currentPrice * 0.1
        P = self.titcoin.profiles["profiles"][ctx.author.id]
        P.addBal(-self.currentPrice)

    async def checkFail(self, _, ctx, error):
        # print(f"_ : {_}  ctx : {ctx}   err : {error}")
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.send(embed=discord.Embed(title="no titcoin?",
                                               description=f"You lack the funds to do this, the current price sits at : `{self.currentPrice}tc`"))
        elif isinstance(error, NoVoice):
            await ctx.send(
                embed=discord.Embed(title="smh", description="you need to be in a voice channel to use this"))
        elif isinstance(error, Denied):
            await ctx.send(embed=discord.Embed(title="bruh -_-", description="you denied the check"))
        else:
            await ctx.send(f"oop there was an error, ping neo\n\n```{error}```")
            traceback.print_exc()

    def registerCommand(self, command: commands.Command):
        command.after_invoke(self.modifyPrice)
        command.error(self.checkFail)
        command.add_check(self.hasFunds())
        command.add_check(self.confirmed())
        self.commands.append(command)

    def extendEmbed(self, embed: discord.Embed):
        commandNames = [f"${c.name}" for c in self.commands]
        commands = "\n\t".join(commandNames)
        embed.add_field(name=self.__class__.__name__,
                        value=f"```Description:\n\t{self.description}\n\nPrice:\n\tbase : [{self.basePrice}tc]\n\tcurrent : [{self.currentPrice}tc]\n\nUse:\n\t{commands}```")
