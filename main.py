
import discord , os
from discord.ext import commands
from cogwatch import Watcher

# this is the main file of the bot, all globals and shit happen here

modules = ["titcoin"] # add extension names here
extFolder = "extensions"

bot = commands.Bot("$" , intents = discord.Intents.all())

for ext in modules:
    bot.load_extension(f"{extFolder}.{ext}")
    
@bot.event
async def on_ready():
    watcher = Watcher(bot , path = extFolder)
    await watcher.start()
    print("Ready")
    
with open("secrets/token.txt" , "r") as F:
    token = F.readline()
    
bot.run(token)