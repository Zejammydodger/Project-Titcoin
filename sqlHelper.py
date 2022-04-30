import math
from typing import Tuple
import mysql , os
import mysql.connector
import mysql.connector.connection as Conn
import datetime
import discord


#NOTE need a way to delete oldest record of balance and worth by PID and CID respectively

"""
The idea with this helper is that it will have a save and load function that take in / output this data structure

{
    "profiles" : {
        discordID : Profile
    },
    "companies" : [
        Company   
    ]
}

ideally all shares in companies are referenced from profiles so that it doesnt create duplicate objects
same with the owner of a company
the company part of profile should also be a reference

database structure:
 refer to scripts/setup.sql 

"""

MAXHISTORY = 30

def datetimeToStr(dt : datetime.datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S") #YYYY-MM-DD hh:mm:ss

def strToDatetime(string : str) -> datetime.datetime:
    return datetime.datetime.strptime(string , "%Y-%m-%d %H:%M:%S")

def executeScript(pathToScript : str , connection : Conn.MySQLConnection , *args) -> list[tuple] | None:
    #executes a script
    connection.reconnect()
    cursor : Conn.MySQLCursor = connection.cursor()
    assert os.path.exists(pathToScript) , f"[{pathToScript}] does not exist"
    with open(pathToScript , "r") as F:
        statement = " ".join(F.readlines())
    newArgs = []
    for arg in args:
        if arg == None:
            newArgs.append("null")
        elif isinstance(arg , Tuple):
            #print("wack ass tuple bullshit")
            newArgs.append(arg[0])
        elif isinstance(arg , str):
            newArgs.append(f"'{arg}'")
        else:
            newArgs.append(arg)
    args = tuple(newArgs)
    statement = statement.format(*args)
    #print(f"{'='*20}\nexecuteing:\n{statement}\n{'='*20}")
    cursor.execute(statement)
    data = cursor.fetchall()
    assert cursor.close() , "cursor did not close properly"
    
    #connection.commit()
    return data

def initDataBase() -> Conn.MySQLConnection:
    #ensures the database has its tables n such
    with open("secrets/password.txt" , "r") as F: #lmao
        pword = F.readline()
    c = mysql.connector.connect(
        host = "127.0.0.1",
        username = "root",
        password = pword ,
        database = "TitCoin"
    )
    path = "scripts/setup.sql"
    executeScript(path , c)
    return c

def blankHistory(balance = 0.0) -> dict[datetime.datetime : float]:
    return {datetime.datetime.now() : balance}

class Profile:
    def __init__(self , balanceHist : dict[datetime.datetime : float] , discordID : int):
        if len(balanceHist) == 0:
            balanceHist = blankHistory()
        self.balanceHist = dict(sorted(balanceHist.items() , key = lambda x : x[0])) #newest to oldest
        self.discordID = discordID
        self.currentBal = self.balanceHist[max(self.balanceHist.keys())]
        self.company = None
        self.shares = []
        
    def addBal(self , amount):
        #adds amount to current bal and then creates a new balhist
        self.currentBal += amount
        self.balanceHist[datetime.datetime.now()] = self.currentBal
    
    def getEmbed(self , user : discord.Member , richest : bool) -> discord.Embed:
        title = f"Titcoin balance for [{user.display_name}]"
        desc = f"Your total Titcoin Balance is:\n`{self.currentBal}tc`\n{'**You are the wealthiest person in tiddleton**' if richest else ''}"
        colour = 0xFFD700 if richest else 0x000000
        emb = discord.Embed(title = title , description = desc , colour = colour)
        
        #create worth history graph etc
        sortedBalHist = sorted(self.balanceHist.items() , key = lambda x : x[0])[:10]
        oldest = sortedBalHist[-1]
        newest = sortedBalHist[0]
        maxBal = max(sortedBalHist , key = lambda x : x[1])[1]
        maxBal = maxBal if maxBal > 0 else 1
        graph = ""
        for date , bal in sortedBalHist:
            graph += datetimeToStr(date) + " | "
            multiplier = bal / maxBal
            graph += ("#" * math.ceil(10*multiplier))
            graph += "\n"
        
        emb.add_field(name=f"Worth history [{oldest[0].date()} to {newest[0].date()}]" , value=f"```{graph}```")
        return emb
        
    def INSERT(self , connection : Conn.MySQLConnection):
        connection.reconnect()
        executeScript("scripts/insertProfile.sql" , connection , self.discordID) # ensures there is a profile in the DB with the discordID
        connection.reconnect() # wow i really have to do that all the time
        if self.company is not None:
            #need a way to get CID
            CID = self.company.getCID(connection , self.discordID)
            self.company.INSERT(connection , self.discordID , CID)
        
        for DT , bal in self.balanceHist.items():
            DT = datetimeToStr(DT)
            #print(f"insertBal | DID : {self.discordID} , bal : {bal} , DT : {DT}")
            executeScript("scripts/insertBalance.sql" , connection , self.discordID , bal , DT)
        
        for s in self.shares:
            CID = s.company.getCID(connection , self.discordID)
            s.INSERT(connection , self.discordID , CID)
        
    def __str__(self) -> str:
        retStr = f"[{self.discordID}]\n"
        for date , bal in self.balanceHist.items():
            retStr += f"\t[{datetimeToStr(date)}] : [{bal}]\n"
        retStr += f"\n\n{'='*10}\nCurrent balance : [{self.currentBal}]\n\n"
        return retStr
        
    @staticmethod
    def SELECTALL(connection : Conn.MySQLConnection) -> list[dict[str : int]]:
        #select from profiles all profiles
        #returns {"PID" : PID , "discordID" : discordID}
        cur : Conn.MySQLCursor = connection.cursor()
        cur.execute("SELECT * FROM Profiles")
        result = cur.fetchall()
        #[(discordID)]
        returnList = []
        for did in result:
            returnList.append({"discordID" : did[0]})
        return returnList
    
    @staticmethod
    def getBalanceHist(connection : Conn.MySQLConnection , discordID) -> list[dict[str : int]]:
        rows = executeScript("scripts/getBalanceHistory.sql" , connection , discordID)
        #print(f"discordID : {discordID}\trows len : {len(rows)}")
        # validated, returns a lot of rows not just 2
        retList = []
        for r in rows:
            temp = {
                "balance" : r[0],
                "created" : r[1]
            }
            retList.append(temp)
        return retList
        
    def updateBalanceHist(self):
        now = datetime.datetime.now()
        hist = list(self.balanceHist.items())
        if len(hist) == MAXHISTORY:
            #max size reached
            hist.pop(-1) #pop oldest
        hist.insert(0 , (now , self.currentWorth))
        self.balanceHist = dict(hist)
        
    def getWorth(self) -> float:
        return self.currentBal + sum([s.getWorth() for s in self.shares])
        
        
class Share:
    def __init__(self , company , profile : Profile , percentage : float , sid : int):
        self.company = company
        self.profile = profile
        self.percentage = percentage
        self.ID = sid
    
    def INSERT(self , connection : Conn.MySQLConnection , discordID , CID):
        #no need to worry about inserting company, that's done from profile
        executeScript("scripts/insertShare.sql" , connection , (discordID , CID , self.percentage , self.ID))
    
    @staticmethod
    def SELECTALL(connection : Conn.MySQLConnection) -> list[dict[str : int]]:
        #get all shares
        cur = connection.cursor()
        cur.execute("SELECT * FROM Shares")
        results = cur.fetchall() #(pid , cid , perk)
        retList = []
        for did , cid , perk in results:
            temp = {
                "discordID" : did,
                "CID" : cid,
                "percent" : perk
            }
            retList.append(temp)
        return retList
        
    def getWorth(self) -> float:
        return self.company.currentWorth * self.percentage
    
    def sell(self):
        worth = self.getWorth()
        self.company.currentWorth -= worth
        self.profile.currentBal += worth
        self.profile.shares.pop(self)
        self.company.updateWorthHist()
        
class Company:
    def __init__(self , owner : Profile , worthHist : dict[datetime.datetime : float] , shares : list , name : str):
        self.owner = owner
        self.owner.company = self
        self.worthHist = dict(sorted(worthHist.items() , key = lambda x : x[0]))#newest to oldest
        self.shares = shares
        self.currentWorth = self.worthHist.values()[0]
        self.name = name
        
    def INSERT(self , connection : Conn.MySQLConnection , discordID , CID):
        #dont have to worry about shares or profile
        executeScript("scripts/insertCompany.sql" , connection , (discordID , self.name))
        for date , worth in self.worthHist.items():
            date : datetime.datetime
            date = datetimeToStr(date)
            executeScript("scripts/insertWorth.sql" , connection , (CID , date , worth))
        
    @staticmethod
    def SELECTALL(connection : Conn.MySQLConnection) -> list[dict[str : int]]:
        #gets a list of all companies
        cur = connection.cursor()
        cur.execute("SELECT * FROM companies") # i dont know how i thought getting shit from shares was the way to do this lmao
        results = cur.fetchall() #(cid , pid)
        retList = []
        for cid , did , name in results:
            temp = {
                "discordID" : did,
                "CID" : cid,
                "name" : name
            }
            retList.append(temp)
        return retList
        
    @staticmethod
    def getWorthHist(connection : Conn.MySQLConnection , CID):
        rows = executeScript("scripts/getWorthHistory.sql" , connection , (CID,))
        #[(created , worth)]
        retlist = []
        for created , worth in rows:
            temp = {
                "created" : created,
                "worth" : worth
            }
            retlist.append(temp)
        return retlist
    
    def updateWorthHist(self):
        now = datetime.datetime.now()
        hist = list(self.worthHist.items())
        if len(hist) == MAXHISTORY:
            #max size reached
            hist.pop(-1) #pop oldest
        hist.insert(0 , (now , self.currentWorth))
        self.worthHist = dict(hist)
    
    def createShare(self, profile : Profile, amount : float):
        #need to figure out how to readjust all share percentages
        
        # go through list of shares, figure out its current worth, then recalculate the percentage based on the companies total worth
        shareData = {}
        for s in self.shares:
            s : Share
            sWorth = self.currentWorth * s.percentage
            shareData[sWorth] = s
        
        self.currentWorth += amount
        percent = amount / self.currentWorth
        self.updateWorthHist()
        s = Share(self , profile , percent)
        self.shares.append(s)
        profile.shares.append(s)
        
        for worth , share in shareData.items():
            percent = worth / self.currentWorth
            share.percentage = percent
        
    def sellShare(self , share : Share):
        share.sell() # the reason its done this way is so the share can remove itself from the profile 
        
    def __str__(self):
        #string method so i can print it and have it not look shit
        retStr = f"{'='*5}[company]{'='*5}\nname : {self.name}\nowner : {self.owner.discordID}\nworth history :\n"
        for date , worth in self.worthHist.items():
            date = datetimeToStr(date)
            retStr += f"\t[{date} | {worth}]\n"
        return retStr + "\n"
        
        
def save(connection : Conn.MySQLConnection , database : dict):
    #goes through all of the profiles and calls the INSERT method on each
    #{
    #   "profiles" : 
    #               {
    #                   discordID : Profile
    #               }
    #   ,
    #   "companies" : 
    #               [ 
    #                   Company 
    #               ]
    #}
    #we only care about profiles here
    profiles : dict[int : Profile] = database["profiles"]
    print("Saving ...")
    for discordID , P in profiles.items():
        P : Profile
        P.INSERT(connection) #and that should do it?
        #connection.reconnect()
        #print(f"saved [{discordID}]")
    print("saved")

def load(connection : Conn.MySQLConnection) -> dict:
    print("loading...")
    #loads all data in then constructs all of the required objects making sure to reference where possible
    #start by selecting all Profile , company and share data
    connection.reconnect()
    profileData = Profile.SELECTALL(connection) # [{"discordID" : did , "discordID" : did}]
    connection.reconnect()
    companyData = Company.SELECTALL(connection) # [{"discordID" : did , "CID" : cid}]
    connection.reconnect()
    shareData = Share.SELECTALL(connection)     # [{"discordID" : did , "CID" : cid , "percent" : perk}]
    connection.reconnect() # these reconnects are ridiculous
    
    print(f"profileData : {len(profileData)}\ncompanyData : {len(companyData)}\nshareData : {len(shareData)}")
    
    profiles = {} # discordID : Profile[incomplete]
    for pDat in profileData:
        DID = pDat["discordID"]
        balHist = Profile.getBalanceHist(connection , DID)
        #print(f"bal hist : {balHist}")
        connection.reconnect()
        hist = {}
        #print(f"[{DID}]")
        #there was an issue here where DID was a 1 len tuple, man fuck tuples
        for dat in balHist:
            hist[dat["created"]] = dat["balance"]
            #print(f"\t[{datetimeToStr(dat['created'])}] : [{dat['balance']}]")
        #print()
        profiles[DID] = Profile(hist , DID)
        if profiles[DID].currentBal > 0:
            print(f"currentBal : {profiles[DID].currentBal}")
        
    companies = {} #CID : Company
    for cDat in companyData:
        DID = cDat["discordID"]
        CID = cDat["CID"]
        owner = profiles[DID]
        name = cDat["name"]
        worthHist = Company.getWorthHist(connection , CID)
        connection.reconnect()
        hist = {}
        for dat in worthHist:
            hist[dat["created"]] = dat["worth"]
        company = Company(owner , hist , [] , name) # initialised as empty
        companies[CID] = company        
    
    for sDat in shareData:
        DID = sDat["discordID"]
        CID = sDat["CID"]
        percent = sDat["percent"]
        prof : Profile = profiles[DID]
        comp : Company = companies[CID]
        shareObj = Share(comp , prof , percent)
        prof.shares.append(shareObj)
        comp.shares.append(shareObj)
        
    retDict = {
        "profiles" : {P.discordID : P for P in profiles.values()},
        "companies" : list(companies.values())
    }
    print("loaded")
    return retDict


#create a test database connection just to be sure
if __name__ == "__main__":
    # in case i accidentally run this file
    quit()
    connection = initDataBase()
    connection.reconnect()
    cur = connection.cursor()
    cur.execute("insert into Profiles values(5); commit")
    connection.reconnect()
    cur : Conn.MySQLCursor= connection.cursor()
    cur.execute("select * from Profiles")
    print(cur.arraysize)
    print([r for r in cur])
    print(cur.fetchall())
    
    quit()
    connection = initDataBase()
    P = Profile(blankHistory() , 0)
    db = {"profiles" : {P.discordID : P} , "companies" : []}
    save(connection , db)
    