import time
import discord , asyncio , math , random , datetime
from discord.ext import commands , tasks
from titcoinHelpers import NoVoice , Denied
from sqlHelper import Profile , Company , Share , load , save , initDataBase , blankHistory

#the actual titcoin functionality

cooldown : list[int] = [] # a list of userIDs that represents users on cooldown
cooldownTime = 60

connection = initDataBase()

profiles : dict[str : dict | list] = load(connection) 
    #{"profiles" : { discordID : Profile } , "companies" : [Company]}
#print(profiles)
percs = []
tiddleton : discord.Guild = None

channelExclusions = [
    762305909497659483, #impastas tradition
    731163650106065016, #poc pog
    723333207398809730, #pride parade
    732621533729521717, #feminism
    716135506710233119, #politics
    715386476342411318, #rules
    705213814462742558, #announcments
    776862596687069274, #staff list
    741048386928771244, #roles
    906531291791523920, #new roles
    705222627509141594, #command list wip
    811762377695035392, #suggestions
    795667559693156352, #suggestions disc
    838555163563786250, #stream announce
    778335359225430026, #command list
    953568041873047562, #beat saber announce
]

### titcoin values

messageVal = 1
voiceVal = 1

### titcoin values

### cooldown async function

async def cooldownFunc(userID : int):
    cooldown.append(userID)
    await asyncio.sleep(cooldownTime)
    cooldown.pop(cooldown.index(userID))
    
### cooldown async function
# Perc base class
class Perc(commands.Cog):
    def __init__(self , bot : commands.Bot , basePrice = 10):
        super().__init__()
        self.description = "N/A" # implement a description for your perc
        self.basePrice : int = basePrice
        self.currentPrice = basePrice
        self.modifyVal = 0.1
        self.bot = bot
        self.commands : list[commands.Command] = []
        percs.append(self)
        bot.add_cog(self)
        self.deflate.start()
    
    @tasks.loop(hours=1)
    async def deflate(self):
        #reduces the current price down to baseprice 
        if math.floor(self.currentPrice - (self.currentPrice * self.modifyVal)) <= self.basePrice:
            self.currentPrice = self.basePrice
        else:
            self.currentPrice -= (self.currentPrice * self.modifyVal)
    
    def hasFunds(self):
        def memHasFundsCheck(ctx : commands.Context):
            #stops the command based on weather the member has enough tc to use this command
            P = profiles["profiles"][ctx.author.id]
            return P.currentBal >= self.currentPrice
        return memHasFundsCheck
    
    def confirmed(self):
        #prompts the user to confirm if they want to spend that much
        yes = "✅"
        no = "❌"
        async def confirmCheck(ctx : commands.Context):
            def sameAuth(reaction : discord.Reaction , user):
                return ctx.author == user and str(reaction.emoji) in [yes , no] 
            
            msg : discord.Message = await ctx.send(embed = discord.Embed(title = "u sure homie?" , description = f"You are about to spend `[{round(self.currentPrice , 2)}tc]`"))
            await msg.add_reaction(yes) #yes
            await msg.add_reaction(no) #no
            reaction , user = await self.bot.wait_for("reaction_add" , check = sameAuth)
            if str(reaction.emoji) == yes:
                return True
            else:
                raise Denied          
        
        return confirmCheck
    
    async def modifyPrice(self , _ , ctx : commands.Context):
        # modifies the price of the command
        # god i hope this only goes off if the actual command is run ;-;
        self.currentPrice += self.currentPrice * 0.1
        P = profiles["profiles"][ctx.author.id]
        P.addBal(-self.currentPrice)
    
    async def checkFail(self , _ , ctx , error):
        #print(f"_ : {_}  ctx : {ctx}   err : {error}")
        if isinstance(error , commands.errors.CheckFailure):
            await ctx.send(embed = discord.Embed(title = "no titcoin?" , description = f"You lack the funds to do this, the current price sits at : `{self.currentPrice}tc`"))
        elif isinstance(error , NoVoice):
            await ctx.send(embed = discord.Embed(title = "smh" , description = "you need to be in a voice channel to use this"))
        elif isinstance(error , Denied):
            await ctx.send(embed = discord.Embed(title = "bruh -_-" , description = "you denied the check"))
        else:
            await ctx.send(f"oop there was an error, ping neo\n\n{error}")
        
    def registerCommand(self , command : commands.Command):
        command.after_invoke(self.modifyPrice)
        command.error(self.checkFail)
        command.add_check(self.hasFunds())
        command.add_check(self.confirmed())
        self.commands.append(command)
    
    def extendEmbed(self , embed : discord.Embed):
        commandNames = [f"${c.name}" for c in self.commands]
        commands = "\n\t".join(commandNames)
        embed.add_field(name = self.__class__.__name__ , value=f"```Description:\n\t{self.description}\n\nPrice:\n\tbase : [{self.basePrice}tc]\n\tcurrent : [{self.currentPrice}tc]\n\nUse:\n\t{commands}```")

        
class MuteFriendPerc(Perc):
    def __init__(self, bot: commands.Bot, basePrice=10):
        super().__init__(bot, basePrice)
        self.registerCommand(self.muteFriend)
        self.description = "Mute your freind in a VC for a minute"

    @staticmethod
    def voiceConnected():
        async def check(ctx):
            #ctx.cog to get self
            if ctx.author.voice is None:
                raise NoVoice()
            else:
                return True    
        return commands.check(check)
    
    @commands.command()
    @voiceConnected()
    async def muteFriend(self , ctx : commands.Context , friend : discord.Member):
        assert friend.voice is not None , "The freind is not in a voice channel doofus"
        await friend.edit(mute = True)
        await asyncio.sleep(60)
        await friend.edit(mute = False)

class ChangeNick(Perc):
    def __init__(self, bot: commands.Bot, basePrice=15):
        super().__init__(bot, basePrice)
        self.description = "Change someones nickname for 10 minutes, the change will revert"
        self.registerCommand(self.changeNick)
        
    @commands.command()
    async def changeNick(self , ctx : commands.Context , friend : discord.Member , nickname : str):
        current = friend.nick
        await friend.edit(nick = nickname)
        await asyncio.sleep(60 * 10) # 10 minutes
        await friend.edit(nick = current)

class AdminZoo(Perc):
    def __init__(self, bot: commands.Bot, basePrice=50):
        super().__init__(bot, basePrice)
        self.description = "allows you to talk in admin zoo for 3 minutes, make em count"
        self.registerCommand(self.letMeIn)

    @commands.command()
    async def letMeIn(self, ctx : commands.Context):
        aZoo = ctx.guild.get_channel(954805755624697916)
        overWrite = discord.PermissionOverwrite()
        overWrite.send_messages = True
        await aZoo.set_permissions(ctx.author , overwrite = overWrite)
        await ctx.send("youre in go go go go")
        await asyncio.sleep(60)
        overWrite.send_messages = False
        await aZoo.set_permissions(ctx.author , overwrite = overWrite)
        await ctx.send("times up")

class serverMute(Perc):
    def __init__(self, bot: commands.Bot, basePrice=75):
        super().__init__(bot, basePrice)
        self.description = "server mute someone for 30 seconds"
        self.registerCommand(self.mute)
        self.muteRoleID = 799600022936223755
        
    @commands.command()
    async def mute(self , ctx : commands.Context , friend : discord.Member):
        muteRole = ctx.guild.get_role(self.muteRoleID)
        await friend.add_roles(muteRole)
        await asyncio.sleep(30)
        await friend.remove_roles(muteRole)

class TitCoin(commands.Cog):
    def __init__(self , bot) -> None:
        super().__init__()
        self.bot : commands.Bot = bot
        print("Titcoin innit, profiles loaded")
        self.tiddleton : discord.Guild = None
        tiddleton = self.tiddleton
        self.channelsOnCooldown : list[discord.TextChannel] = []
        
        #starting tasks
        self.VCcheck.start()

    async def randomAward(self):
        
        while True:
            # place a reward for 25tc in a channel that hasnt been used for at least 5 minutes every 1 - 3 hours
            possibleChannels = []
            for chan in self.tiddleton.text_channels:
                chan : discord.TextChannel
                if chan.id in channelExclusions:
                    continue
                mostRecent : list[discord.Message] = await chan.history(limit=1).flatten()
                if len(mostRecent) == 0:
                    possibleChannels.append(chan)
                    continue
                mostRecent : discord.Message = mostRecent[0]
                timeSent = mostRecent.created_at
                now = datetime.datetime.utcnow()
                now - datetime.timedelta(minutes=5)
                if timeSent < now:
                    possibleChannels.append(chan)
                    
            chosenChannel = random.choice(possibleChannels)
            
            def messageCheck(message : discord.Message):
                return message.channel == chosenChannel
            #send the reward message
            ammount = random.randint(25 , 69)
            e = discord.Embed(title = "QUICK!" , description = f"the first person to say something in this channel will receive `[{ammount}tc]`\n\n**you have 30 seconds**")
            msg : discord.Message = await chosenChannel.send(embed = e)
            message : discord.Message = await self.bot.wait_for("message" , check = messageCheck)
            if message is not None:
                P = profiles["profiles"][message.author.id]
                P.addBal(ammount)
            await msg.delete(delay=5)
            
            await asyncio.sleep(60 * 60 * random.randint(1 , 3))
            

    @tasks.loop(minutes=1)
    async def VCcheck(self):
        #awards all users currently sat in a VC voiceVal*[number of people in that vc]tc per minute
        if self.tiddleton is None:
            return
        for VC in self.tiddleton.voice_channels:
            VC : discord.VoiceChannel
            numConnected = len(VC.members)
            if numConnected > 0:
                for mem in VC.members:
                    mem : discord.Member
                    P = profiles["profiles"][mem.id]
                    P.addBal(voiceVal * numConnected) 

    @commands.Cog.listener()
    async def on_ready(self):
        print("flag")
         # tiddleton
        self.tiddleton = self.bot.get_guild(693537199500689439)
        assert self.tiddleton is not None , "Bot not in tiddleton"
        for mem in self.tiddleton.members:
            if mem.id not in profiles["profiles"].keys():
                p = Profile(blankHistory() , mem.id)
                profiles["profiles"][mem.id] = p
                
                #print(f"profile added: {p}\n\t{p.discordID}\n\t{p.currentBal}\n")
        
        #self.bot.loop.create_task(self.randomAward()) #ill add this back at some point
                
        
                
    @commands.Cog.listener()
    async def on_message(self , message : discord.Message):
        if message.author.id in cooldown:
            # if the user is on cooldown, pass
            return
        else:
            asyncio.create_task(cooldownFunc(message.author.id))
            try:
                profiles["profiles"][message.author.id].addBal(messageVal)
            except KeyError:
                print(f"[{message.author.id}]['{message.author.display_name}'] not found, adding to system")
                P = Profile(blankHistory(balance = messageVal) , message.author.id)
                profiles["profiles"][message.author.id] = P
                
    @commands.command()
    async def titcoin(self , ctx : commands.Context , user : discord.Member = None):
        # displays the users balance
        #with some other funky stuff
        if user == None:
            user = ctx.author
        richest : Profile = max(profiles["profiles"].values() , key = lambda x : x.currentBal)
        isrichest : bool = user.id == richest.discordID
        prof = profiles["profiles"][user.id]
        embed = prof.getEmbed(user , isrichest)
        await ctx.send(embed = embed)
        
    @commands.command()
    async def leaderboard(self , ctx : commands.Context):
        #get top 10 wealthiest people in tiddleton
        profs = sorted(profiles["profiles"].values() , key = lambda x : x.currentBal , reverse=True)[:10]
        maxBal = profs[0].currentBal
        digits = lambda x : math.floor(math.log10(x if x > 0 else x + 1)) + 1
        lenDigits = digits(len(profs))
        maxBalDigits = digits(maxBal)
        board = ""
        for i , prof in enumerate(profs):
            user = ctx.guild.get_member(prof.discordID)
            board += f"[{i+1}{' ' * (lenDigits - digits(i+1))}] | [{prof.currentBal}{' ' * (maxBalDigits - digits(prof.currentBal))}] | {user.display_name}\n"
            
        embed = discord.Embed(title = "Top 10 Richest people in Tiddleton" , description = f"```{board}```")
        await ctx.send(embed = embed)
                
    @commands.command()
    async def sellTo(self , ctx : commands.Context , user2 : discord.Member):
        #WIP
        
        #trade tc between members
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
        
        def checkAuthor(auth : discord.Member):
            def check(message : discord.Message) -> bool:
                return message.author == auth
            return check
        
        def checkAuthorAndInt(auth : discord.Member):
            def check(message : discord.Message) -> bool:
                return message.author == auth and str(message.content).isnumeric()
            return check
        
        def checkAuthorAndresponse(auth : discord.Member):
            def check(message : discord.Message) -> bool:
                return message.author == auth and str(message.content).lower() in ["accept" , "decline"]
            return check
        
        # 'globals'
        user1 : discord.Member = ctx.author
        dialog = lambda x : ctx.send(embed = discord.Embed(title = f"[{user1.display_name}] <-> [{user2.display_name}]" , description = x))
        profile1 : Profile = profiles["profiles"][user1.id]
        profile2 : Profile = profiles["profiles"][user2.id]
        
        
        await dialog("What are you selling?")
        message : discord.Message = await self.bot.wait_for("message" , check = checkAuthor(user1) , timeout=60)
        contents = message.content
        
        await dialog(f"How much do you want for [{contents}]")
        messageAmount : discord.Message = await self.bot.wait_for("message" , check = checkAuthorAndInt(user1) , timeout=60)
        amount : int = int(messageAmount.content)
        
        while profile2.currentBal < amount:
            await dialog(f"[{user2.display_name}] does not possess the funds to make this trade, please choose an amount less than or equal to [{profile2.currentBal}]")
            await dialog(f"How much do you want for [{contents}]")
            messageAmount : discord.Message = await self.bot.wait_for("message" , check = checkAuthorAndInt(user1) , timeout=60)
            amount : int = int(messageAmount.content)
            
        await dialog(f"[{user2.display_name}] do you accept or decline?\n__type 'accept' or 'decline'__")
        response : discord.Message = await self.bot.wait_for("message" , check = checkAuthorAndresponse(user2) , timeout=60)
        if response.content == "accept":
            #trade accepted
            profile2.addBal(-amount)
            profile1.addBal(amount)
            #recordTrade(user1.id , user2.id , f"[{user1.name}] sold [{user2.name}] ['{contents}'] for [{amount}]")
            await ctx.send(embed = discord.Embed(title = "Trade accepted" , color = 0x00ff00))
        else:
            #trade declined
            await ctx.send(embed = discord.Embed(title = "Trade declined" , color = 0xff0000))
        
    @commands.command()
    async def wealthDist(self , ctx : commands.Context, top : int = 20 , granularity : int = 10):
        # produces a leaderboard type thing but its a percentage distribution of wealth, ie #1 == 100% and #2 is some percentage of #1
        profs = sorted(profiles["profiles"].values() , key = lambda x : x.currentBal , reverse=True)[:top]
        maxBal = profs[0].currentBal
        board = ""
        for i , prof in enumerate(profs):
            user : discord.Member = ctx.guild.get_member(prof.discordID)
            perc = math.ceil(prof.currentBal / maxBal * granularity)
            board += f"[{'#' * perc}{' ' * (granularity - perc)}] - {user.display_name}\n"
            
        await ctx.send(embed = discord.Embed(title = f"distribution of wealth in tiddleton" , description = f"```{board}```"))

    @commands.command()
    async def shop(self , ctx : commands.Context):
        embed = discord.Embed(title = "Shop")
        for perc in percs:
            perc : Perc
            perc.extendEmbed(embed)
        await ctx.send(embed = embed)
            
    ### cog unload
    def cog_unload(self):
        print("unloading...")
        save(connection , profiles)
        return super().cog_unload()
    
def setup(bot):
    bot.add_cog(TitCoin(bot))
    MuteFriendPerc(bot)
    ChangeNick(bot)
    AdminZoo(bot)
    serverMute(bot)