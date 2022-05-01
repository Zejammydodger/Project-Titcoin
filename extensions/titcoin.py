import discord, asyncio, math, random, datetime
from discord.ext import commands, tasks
from sqlHelper import Profile, Company, Share, load, save, initDataBase, blankHistory
from extensions import util
from extensions.perks.perk import Perk
from Table import Table , BaseColumn , IndexColumn , PercentOfColumn


# the actual titcoin functionality


# {"profiles" : { discordID : Profile } , "companies" : [Company]}
# print(profiles)

channelExclusions = [
    762305909497659483,     # impastas tradition
    731163650106065016,     # poc pog
    723333207398809730,     # pride parade
    732621533729521717,     # feminism
    716135506710233119,     # politics
    715386476342411318,     # rules
    705213814462742558,     # announcements
    776862596687069274,     # staff list
    741048386928771244,     # roles
    906531291791523920,     # new roles
    705222627509141594,     # command list wip
    811762377695035392,     # suggestions
    795667559693156352,     # suggestions disc
    838555163563786250,     # stream announce
    778335359225430026,     # command list
    953568041873047562,     # beat saber announce
]

### titcoin values

messageVal = 1
voiceVal = 1

### titcoin values


class TitCoin(commands.Cog):
    def __init__(self, bot) -> None:
        super().__init__()
        self.bot: commands.Bot = bot
        print("Titcoin innit, profiles loaded")
        self.tiddleton: discord.Guild = None
        self.channelsOnCooldown: list[discord.TextChannel] = []
        self.perks = []

        self.connection = initDataBase()
        self.profiles: dict[str: dict | list] = load(self.connection)

        self.cooldown: list[int] = []  # a list of userIDs that represents users on cooldown
        self.cooldownTime = 60

        self.VCcheck.start()    # starting tasks

    async def randomAward(self):
        
        while True:
            # place a reward for 25tc in a channel that hasn't been used for at least 5 minutes every 1 - 3 hours
            possibleChannels = []
            for chan in self.tiddleton.text_channels:
                chan: discord.TextChannel
                if chan.id in channelExclusions:
                    continue
                mostRecent: list[discord.Message] = await chan.history(limit=1).flatten()
                if len(mostRecent) == 0:
                    possibleChannels.append(chan)
                    continue
                mostRecent: discord.Message = mostRecent[0]
                timeSent = mostRecent.created_at
                now = datetime.datetime.utcnow()
                now - datetime.timedelta(minutes=5)
                if timeSent < now:
                    possibleChannels.append(chan)
                    
            chosenChannel = random.choice(possibleChannels)
            
            def messageCheck(message: discord.Message):
                return message.channel == chosenChannel
            # send the reward message
            ammount = random.randint(25, 69)
            e = discord.Embed(title="QUICK!", description=f"the first person to say something in this channel will receive `[{ammount}tc]`\n\n**you have 30 seconds**")
            msg: discord.Message = await chosenChannel.send(embed=e)
            message: discord.Message = await self.bot.wait_for("message", check=messageCheck)
            if message is not None:
                P = self.profiles["profiles"][message.author.id]
                P.addBal(ammount)
            await msg.delete(delay=5)
            
            await asyncio.sleep(60 * 60 * random.randint(1, 3))
            
    @tasks.loop(minutes=1)
    async def VCcheck(self):
        # awards all users currently sat in a VC voiceVal*[number of people in that vc]tc per minute
        if self.tiddleton is None:
            return
        for VC in self.tiddleton.voice_channels:
            VC: discord.VoiceChannel
            numConnected = len(VC.members)
            if numConnected > 0:
                for mem in VC.members:
                    mem: discord.Member
                    P = self.profiles["profiles"][mem.id]
                    P.addBal(voiceVal * numConnected) 

    @commands.Cog.listener()
    async def on_ready(self):
        print("flag")
        # tiddleton
        self.tiddleton = self.bot.get_guild(693537199500689439)
        if self.tiddleton is None:                  # it took me an embarrassing amount of time to realize the bot looks for tiddleton specifically. Anyways this is my test server
            self.tiddleton = self.bot.get_guild(969731141890363402)
        assert self.tiddleton is not None, "Bot not in tiddleton"
        for mem in self.tiddleton.members:
            if mem.id not in self.profiles["profiles"].keys():
                p = Profile(blankHistory(), mem.id)
                self.profiles["profiles"][mem.id] = p
                
                # print(f"profile added: {p}\n\t{p.discordID}\n\t{p.currentBal}\n")
        
        # self.bot.loop.create_task(self.randomAward()) #ill add this back at some point
                    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id in self.cooldown:
            # if the user is on cooldown, pass
            return
        else:
            asyncio.create_task(util.cooldownFunc(message.author.id, self.cooldownTime, self.cooldown))
            try:
                self.profiles["profiles"][message.author.id].addBal(messageVal)
            except KeyError:
                print(f"[{message.author.id}]['{message.author.display_name}'] not found, adding to system")
                P = Profile(blankHistory(balance=messageVal), message.author.id)
                self.profiles["profiles"][message.author.id] = P
                
    @commands.command()
    async def titcoin(self, ctx: commands.Context, user: discord.Member = None):
        # displays the users balance
        # with some other funky stuff
        if user is None:
            user = ctx.author
        richest: Profile = max(self.profiles["profiles"].values(), key=lambda x: x.currentBal)
        isrichest: bool = user.id == richest.discordID
        prof = self.profiles["profiles"][user.id]
        embed = prof.getEmbed(user, isrichest)
        await ctx.send(embed=embed)
        print(prof)
            
    @commands.command()
    async def leaderboard(self, ctx: commands.Context):
        # get top 10 wealthiest people in tiddleton
        profs = sorted(self.profiles["profiles"].values(), key=lambda x: x.currentBal, reverse=True)[:10]
        index = IndexColumn(startsAt=1)
        name = BaseColumn("name")
        bal = BaseColumn("Balance in tc")
        table = Table([index , name , bal])
        
        for p in profs:
            user = ctx.guild.get_member(p.discordID)
            table.addRow(None , user.display_name if user is not None else "[unkown user]" , math.floor(p.currentBal))
        
        embed = discord.Embed(title="Top 10 Richest people in Tiddleton", description=f"```{str(table)}```")
        await ctx.send(embed=embed)
                
    @commands.command()
    async def sellTo(self, ctx: commands.Context, user2: discord.Member):
        # WIP
        
        # trade tc between members
        #   user1 starts the trade
        #       prompt for trade contents
        #       prompt for trade ... currency?
        #   user2 either:
        #       accepts
        #       declines
        
        # -= gonna remove counter offer functionaility until i can be bothered =-
        #       counter offers
        #   if counter offer
        #       wait for other user to accept decline or counter offer 
        #   loop counter offer till accept or decline
        
        def checkAuthor(auth: discord.Member):
            def check(message: discord.Message) -> bool:
                return message.author == auth
            return check
        
        def checkAuthorAndInt(auth: discord.Member):
            def check(message: discord.Message) -> bool:
                return message.author == auth and str(message.content).isnumeric()
            return check
        
        def checkAuthorAndresponse(auth: discord.Member):
            def check(message: discord.Message) -> bool:
                return message.author == auth and str(message.content).lower() in ["accept", "decline"]
            return check
        
        # 'globals'
        user1: discord.Member = ctx.author
        dialog = lambda x: ctx.send(embed=discord.Embed(title=f"[{user1.display_name}] <-> [{user2.display_name}]", description=x))
        profile1: Profile = self.profiles["profiles"][user1.id]
        profile2: Profile = self.profiles["profiles"][user2.id]

        await dialog("What are you selling?")
        message: discord.Message = await self.bot.wait_for("message", check=checkAuthor(user1), timeout=60)
        contents = message.content
        
        await dialog(f"How much do you want for [{contents}]")
        messageAmount: discord.Message = await self.bot.wait_for("message", check=checkAuthorAndInt(user1), timeout=60)
        amount: int = int(messageAmount.content)
        
        while profile2.currentBal < amount:
            await dialog(f"[{user2.display_name}] does not possess the funds to make this trade, please choose an amount less than or equal to [{profile2.currentBal}]")
            await dialog(f"How much do you want for [{contents}]")
            messageAmount: discord.Message = await self.bot.wait_for("message", check=checkAuthorAndInt(user1), timeout=60)
            amount: int = int(messageAmount.content)
            
        await dialog(f"[{user2.display_name}] do you accept or decline?\n__type 'accept' or 'decline'__")
        response: discord.Message = await self.bot.wait_for("message", check=checkAuthorAndresponse(user2), timeout=60)
        if response.content == "accept":
            # trade accepted
            profile2.addBal(-amount)
            profile1.addBal(amount)
            # recordTrade(user1.id , user2.id , f"[{user1.name}] sold [{user2.name}] ['{contents}'] for [{amount}]")
            await ctx.send(embed=discord.Embed(title="Trade accepted", color=0x00ff00))
        else:
            # trade declined
            await ctx.send(embed=discord.Embed(title="Trade declined", color=0xff0000))
        
    @commands.command()
    async def wealthDist(self, ctx: commands.Context, top: int = 15, granularity: int = 10):
        # produces a leaderboard type thing but its a percentage distribution of wealth, ie #1 == 100% and #2 is some percentage of #1
        profs = sorted(self.profiles["profiles"].values(), key=lambda x: x.currentBal, reverse=True)[:top]
        maxBal = profs[0].currentBal
        index = IndexColumn(startsAt=1 , padding=0)
        name = BaseColumn("Name" , padding=0)
        percOfMax = PercentOfColumn("relative wealth to #1" , maxBal , granularity=granularity , padding=0)
        table = Table([index , name , percOfMax])
        for prof in profs:
            user: discord.Member = ctx.guild.get_member(prof.discordID)
            table.addRow(None , user.display_name if user is not None else "[unkown user]" , math.floor(prof.currentBal))
        await ctx.send(embed=discord.Embed(title=f"distribution of wealth in tiddleton", description=f"```{str(table)}```"))

    @commands.command()
    async def shop(self, ctx: commands.Context):
        embed = discord.Embed(title="Shop")
        for perk in self.perks:
            perk: Perk
            perk.extendEmbed(embed)
        await ctx.send(embed=embed)
            
    ### cog unload
    def cog_unload(self):
        print("unloading...")
        save(self.connection, self.profiles)
        return super().cog_unload()


# importing the perks
from extensions.perks import admin_zoo, change_nick, mute_friend, server_mute, start_company


def setup(bot):
    tc = TitCoin(bot)
    bot.add_cog(tc)

    # load the perks in
    mute_friend.MuteFriendPerk(bot, tc)
    change_nick.ChangeNick(bot, tc)
    admin_zoo.AdminZoo(bot, tc)
    server_mute.ServerMute(bot, tc)
    start_company.StartCompany(bot, tc)
