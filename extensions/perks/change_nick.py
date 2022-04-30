import asyncio
import discord
from discord.ext import commands, tasks
from titcoinHelpers import NoVoice, Denied, HasCompany
from sqlHelper import Profile, Company, Share, load, save, initDataBase, blankHistory
from extensions import titcoin      # be careful with this one, there's a big risk of circular import errors
from extensions.perks.perk import Perk


class ChangeNick(Perk):
    def __init__(self, bot: commands.Bot, titcoin: titcoin.TitCoin, basePrice=15):
        super().__init__(bot, titcoin, basePrice)
        self.description = "Change someones nickname for 10 minutes, the change will revert"
        self.registerCommand(self.changeNick)

    @commands.command()
    async def changeNick(self, ctx: commands.Context, friend: discord.Member, nickname: str):
        current = friend.nick
        await friend.edit(nick=nickname)
        await asyncio.sleep(60 * 10)  # 10 minutes
        await friend.edit(nick=current)
