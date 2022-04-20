import discord , os , json
from discord.ext import commands

DBmain = "DB/main.json"
DBtrades = "DB/trades.json"

class Profile:
    def __init__(self , id : int , balance : int = 0) -> None:
        self.id = id
        self.balance = balance
        
    def toDict(self):
        return {"id" : self.id , "balance" : self.balance}
    
    def getEmbed(self , user : discord.Member , richest : bool) -> discord.Embed:
        title = f"Titcoin balance for [{user.display_name}]"
        desc = f"Your total Titcoin Balance is:\n`{self.balance}tc`\n{'**You are the wealthiest person in tiddleton**' if richest else ''}"
        colour = 0xFFD700 if richest else 0x000000
        return discord.Embed(title = title , description = desc , colour = colour)

class NoVoice(commands.CommandError):
    def __init__(self):
        super().__init__(message = "user is not connected to a voice channel")

class Denied(commands.CommandError):
    def __init__(self):
        super().__init__(message = "User denied the check")


def load() -> dict[int , Profile]:
    assert os.path.exists(DBmain) , f"[{DBmain}] file does not exsist"
    with open(DBmain , "r") as F:
        data = json.load(F)
    data = data["profiles"]
    profiles = {}
    for pDict in data:
        P = Profile(pDict["id"] , pDict["balance"])
        profiles[pDict["id"]] = P
    return profiles

def save(profiles : dict[int , Profile]):
    profiles : list[Profile] = list(profiles.values())
    data = {"profiles" : [p.toDict() for p in profiles]}
    with open(DBmain , "w+") as F:
        json.dump(data , F)

def recordTrade(user1id : int , user2id : int , trade : str):
    # records a trade in trades.txt
    assert os.path.exists(DBtrades) , f"[{DBtrades}] does not exsist"
    with open(DBtrades , "r") as F:
        data = json.load(F)

    data[{user1id : user2id}] = trade
    print(data)
    with open(DBtrades , "w") as F:
        json.dump(data , F)    

def getUserTradeHistory(userid , numtrades = 50) -> list[str]:
    with open(DBtrades , "r") as F:
        data : dict = json.load(F)
    userTrades = filter(lambda x: userid in x[0].items()[0] , data.items())
    tradeHistory = []
    for i in range(numtrades):
        t = next(userTrades)
        if t is None:
            break
        tradeHistory.append(t[1])
    return tradeHistory

