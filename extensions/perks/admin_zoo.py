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
        self.register_command(self.letMeIn)

    @commands.command()
    async def letMeIn(self, ctx: commands.Context):
        admin_zoo_channel = ctx.guild.get_channel(954805755624697916)
        over_write = discord.PermissionOverwrite()
        over_write.send_messages = True
        await admin_zoo_channel.set_permissions(ctx.author, overwrite=over_write)
        await ctx.send("you're in go go go go")
        await asyncio.sleep(60)
        over_write.send_messages = False
        await admin_zoo_channel.set_permissions(ctx.author, overwrite=over_write)
        await ctx.send("times up")
