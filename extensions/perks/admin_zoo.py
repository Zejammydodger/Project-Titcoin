from __future__ import annotations
import asyncio
import discord
from discord.ext import commands, tasks
from titcoinHelpers import NoVoice, Denied, HasCompany
from sqlHelper import Profile, Company, Share, load, save, initDataBase, blankHistory
from extensions import titcoin      # be careful with this one, there's a big risk of circular import errors
from extensions.perks.perk import Perk


class AdminZoo(Perk):
    def __init__(self, bot: commands.Bot, titcoin: titcoin.TitCoin, basePrice=50):
        super().__init__(bot, titcoin, basePrice)
        self.description = "allows you to talk in admin zoo for 3 minutes, make em count"
        self.registerCommand(self.letMeIn)

    @commands.command()
    async def letMeIn(self, ctx: commands.Context):
        aZoo = ctx.guild.get_channel(954805755624697916)
        overWrite = discord.PermissionOverwrite()
        overWrite.send_messages = True
        await aZoo.set_permissions(ctx.author, overwrite=overWrite)
        await ctx.send("you're in go go go go")
        await asyncio.sleep(60)
        overWrite.send_messages = False
        await aZoo.set_permissions(ctx.author, overwrite=overWrite)
        await ctx.send("times up")
