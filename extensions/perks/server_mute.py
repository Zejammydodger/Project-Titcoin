import asyncio
import discord
from discord.ext import commands, tasks
from titcoinHelpers import NoVoice, Denied, HasCompany
from sqlHelper import Profile, Company, Share, load, save, initDataBase, blankHistory
from extensions import titcoin      # be careful with this one, there's a big risk of circular import errors
from extensions.perks.perk import Perk


class ServerMute(Perk):
    def __init__(self, bot: commands.Bot, titcoin: titcoin.TitCoin, basePrice=75):
        super().__init__(bot, titcoin, basePrice)
        self.description = "server mute someone for 30 seconds"
        self.registerCommand(self.mute)
        self.muteRoleID = 799600022936223755

    @commands.command()
    async def mute(self, ctx: commands.Context, friend: discord.Member):
        muteRole = ctx.guild.get_role(self.muteRoleID)
        await friend.add_roles(muteRole)
        await asyncio.sleep(30)
        await friend.remove_roles(muteRole)
