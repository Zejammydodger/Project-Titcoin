
import discord , os
from discord.ext import commands
from cogwatch import Watcher

"""
from discord_ui import UI
from discord_ui import SlashInteraction , UI , Button , LinkButton
from discord_ui.cogs import slash_command, subslash_command, listening_component
"""
# this is the main file of the bot, all globals and shit happen here

modules = ["titcoin"]   # add extension names here
extFolder = "extensions"

bot = commands.Bot("$", intents=discord.Intents.all())
#ui = UI(bot)


for ext in modules:
    bot.load_extension(f"{extFolder}.{ext}")

"""
@ui.slash.command(name="slashTest" , guild_ids=[693537199500689439])
async def command(ctx):
    await ctx.respond("yep")
"""
@bot.event
async def on_ready():
    watcher = Watcher(bot, path=extFolder)
    await watcher.start()
    print("Ready")
    
with open("secrets/token.txt", "r") as F:
    token = F.readline()
    
bot.run(token)
