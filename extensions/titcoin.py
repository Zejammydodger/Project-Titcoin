import discord, asyncio, math, random, datetime , time
from discord.ext import commands, tasks
from sqlHelper import Profile, Company, Share, load, save, initDataBase, blankHistory
from extensions import util
from extensions.perks.perk import Perk
from Table import Table , BaseColumn , IndexColumn , PercentOfColumn
from Graph import BasicTextGraph , BasicGraph , AutoUpdateGraph
import sqlalchemy_helper as sqlh
import sqlalchemy as sq
import sqlalchemy.orm as orm

"""
#discord ui testing imports
from discord_ui import SlashInteraction , UI , Button , LinkButton
from discord_ui.cogs import slash_command, subslash_command, listening_component
"""

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

MESSAGE_VAL = 1
VOICE_VAL = 1
START_BALANCE = 0

### titcoin values

class test(commands.Cog):
    def __init__(self , bot):
        super().__init__()
        bot.add_cog(self)

    @commands.command()
    async def textGraphTest(self , ctx : commands.Context):
        #tests the super cool giga chad text graph
        g = BasicTextGraph("ur mum" , "# times i did" , width=30 , height=30)
        for i in range(30):
            g.addPoint(random.randint(0 , 69) , random.randint(0 , 69))
        await ctx.send(embed = discord.Embed(title = "lol" , description = f"```{str(g)}```"))
    
    @commands.command()
    async def testGraph(self , ctx : commands.Context):
        #tests the matplot lib version with a basic graph
        g = BasicGraph("# of times i did ur mum" , "# of times" , "ur mum")
        for i in range(30):
            g.addPoint(random.randint(0 , 69) , random.randint(0 , 69))
        e = g.getEmbed()
        await ctx.send(embed = e , file = g.file)
        
    @commands.command()
    async def testAutoGraph(self , ctx : commands.Context):
        #tests the auto graph functionality
        pass 


class TitCoin(commands.Cog):
    def __init__(self, bot) -> None:
        super().__init__()
        self.bot: commands.Bot = bot
        self.tiddleton: discord.Guild = None
        self.channels_on_cooldown: list[discord.TextChannel] = []
        self.perks = []

        self.sessionmaker = sqlh.generate_session                        # sessionmaker
        self._engine = sqlh.engine                                  # preconfigured engine

        self.cooldown: list[int] = []  # a list of userIDs that represents users on cooldown
        self.cooldownTime = 5

        self.vc_check.start()    # starting tasks
        print("Titcoin innit, profiles loaded")

    def get_profile(self, session, member: discord.Member) -> sqlh.Profile:
        for row in session.execute(sq.select(sqlh.Profile).where(sqlh.Profile.id == member.id)):
            row[0]: sqlh.Profile
            return row[0]

    async def random_award(self):
        while True:
            # place a reward for 25tc in a channel that hasn't been used for at least 5 minutes every 1 - 3 hours
            possible_channels = []
            for chan in self.tiddleton.text_channels:
                chan: discord.TextChannel
                if chan.id in channelExclusions:
                    continue
                most_recent: list[discord.Message] = await chan.history(limit=1).flatten()
                if len(most_recent) == 0:
                    possible_channels.append(chan)
                    continue
                most_recent: discord.Message = most_recent[0]
                time_sent = most_recent.created_at
                now = datetime.datetime.utcnow()
                now - datetime.timedelta(minutes=5)
                if time_sent < now:
                    possible_channels.append(chan)
                    
            chosen_channel = random.choice(possible_channels)
            
            def message_check(message: discord.Message):
                return message.channel == chosen_channel
            # send the reward message
            ammount = random.randint(25, 69)
            e = discord.Embed(title="QUICK!", description=f"the first person to say something in this channel will receive `[{ammount}tc]`\n\n**you have 30 seconds**")
            msg: discord.Message = await chosen_channel.send(embed=e)
            message: discord.Message = await self.bot.wait_for("message", check=message_check)
            if message is not None:
                P = self.profiles["profiles"][message.author.id]
                P.addBal(ammount)
            await msg.delete(delay=5)
            
            await asyncio.sleep(60 * 60 * random.randint(1, 3))
            
    @tasks.loop(minutes=1)
    async def vc_check(self):
        # awards all users currently sat in a VC voiceVal*[number of people in that vc]tc per minute
        if self.tiddleton is None:
            return
        for VC in self.tiddleton.voice_channels:
            VC: discord.VoiceChannel
            num_connected = len(VC.members)
            if num_connected > 0:
                for member in VC.members:
                    member: discord.Member
                    with self.sessionmaker() as session:
                        profile: sqlh.Profile = self.get_profile(session, member)
                        profile.change_balance(amount=VOICE_VAL * num_connected, tag="vc_reward")
                    print(f"[{member.id}]['{member.display_name}'] was rewarded for vc")

    @commands.Cog.listener()
    async def on_ready(self):
        print("flag")
        # tiddleton
        self.tiddleton = self.bot.get_guild(693537199500689439)
        if self.tiddleton is None:      # the tiddleton bot test site
            self.tiddleton = self.bot.get_guild(979099481591132200)
        if self.tiddleton is None:                  # it took me an embarrassing amount of time to realize the bot looks for tiddleton specifically. Anyways this is my test server
            self.tiddleton = self.bot.get_guild(969731141890363402)
        assert self.tiddleton is not None, "Bot not in tiddleton"

        # make sure all members are in the database
        for member in self.tiddleton.members:
            with self.sessionmaker() as session:
                if member.id not in [row[0].id for row in session.execute(sq.select(sqlh.Profile))]:
                    print(f"[{member.id}]['{member.display_name}'] not found, adding to system")

                    profile = sqlh.Profile(id=member.id, balance=START_BALANCE)
                    session.add(profile)
                    profile.initialize()

                # print(f"profile added: {p}\n\t{p.discordID}\n\t{p.currentBal}\n")
        
        # self.bot.loop.create_task(self.randomAward()) #ill add this back at some point

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        print(f"[{member.id}]['{member.display_name}'] joined, adding to system")
        with self.sessionmaker() as session:
            profile = sqlh.Profile(id=member.id, balance=START_BALANCE)
            session.add(profile)
            profile.initialize()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id in self.cooldown:
            # if the user is on cooldown, pass
            return
        else:
            asyncio.create_task(util.cooldownFunc(message.author.id, self.cooldownTime, self.cooldown))
            try:
                with self.sessionmaker() as session:
                    self.get_profile(session, message.author).change_balance(MESSAGE_VAL, tag="message")
                print(f"[{message.author.id}]['{message.author.display_name}'] was rewarded for message")
            except NotImplementedError:
                print(f"[{message.author.id}]['{message.author.display_name}'] not found")
                
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
    async def sell_to(self, ctx: commands.Context, user2: discord.Member):
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
        
        def check_author(auth: discord.Member):
            def check(message: discord.Message) -> bool:
                return message.author == auth
            return check
        
        def check_author_and_int(auth: discord.Member):
            def check(message: discord.Message) -> bool:
                return message.author == auth and str(message.content).isnumeric()
            return check
        
        def check_author_and_response(auth: discord.Member):
            def check(message: discord.Message) -> bool:
                return message.author == auth and str(message.content).lower() in ["accept", "decline"]
            return check
        
        # 'globals'
        user1: discord.Member = ctx.author
        dialog = lambda x: ctx.send(embed=discord.Embed(title=f"[{user1.display_name}] <-> [{user2.display_name}]", description=x))
        profile1: Profile = self.profiles["profiles"][user1.id]
        profile2: Profile = self.profiles["profiles"][user2.id]

        await dialog("What are you selling?")
        message: discord.Message = await self.bot.wait_for("message", check=check_author(user1), timeout=60)
        contents = message.content
        
        await dialog(f"How much do you want for [{contents}]")
        message_amount: discord.Message = await self.bot.wait_for("message", check=check_author_and_int(user1), timeout=60)
        amount: int = int(message_amount.content)
        
        while profile2.currentBal < amount:
            await dialog(f"[{user2.display_name}] does not possess the funds to make this trade, please choose an amount less than or equal to [{profile2.currentBal}]")
            await dialog(f"How much do you want for [{contents}]")
            message_amount: discord.Message = await self.bot.wait_for("message", check=check_author_and_int(user1), timeout=60)
            amount: int = int(message_amount.content)
            
        await dialog(f"[{user2.display_name}] do you accept or decline?\n__type 'accept' or 'decline'__")
        response: discord.Message = await self.bot.wait_for("message", check=check_author_and_response(user2), timeout=60)
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
    async def wealth_dist(self, ctx: commands.Context, top: int = 15, granularity: int = 10):
        # produces a leaderboard type thing but its a percentage distribution of wealth, ie #1 == 100% and #2 is some percentage of #1
        profs = sorted(self.profiles["profiles"].values(), key=lambda x: x.currentBal, reverse=True)[:top]
        max_bal = profs[0].currentBal
        index = IndexColumn(startsAt=1, padding=0)
        name = BaseColumn("Name", padding=0)
        percent_of_max = PercentOfColumn("relative wealth to #1", max_bal, granularity=granularity, padding=0)
        table = Table([index, name, percent_of_max])
        for prof in profs:
            user: discord.Member = ctx.guild.get_member(prof.discordID)
            table.addRow(None, user.display_name if user is not None else "[unkown user]", math.floor(prof.currentBal))
        await ctx.send(embed=discord.Embed(title=f"distribution of wealth in tiddleton", description=f"```{str(table)}```"))

    @commands.command()
    async def shop(self, ctx: commands.Context):
        embed = discord.Embed(title="Shop")
        for perk in self.perks:
            perk: Perk
            perk.extend_embed(embed)
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
    
    test(bot)