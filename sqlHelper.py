import mysql , os
import mysql.connector
import mysql.connector.connection as Conn
import datetime
import discord


#NOTE need a way to delete oldest record of balance and worth by PID and CID respectivily

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

Profile table
PID [primary key][autoIncr] | discordID [NN]

Company table
CID [primary key][autoIncr] | PID [foreign key][ref PID]

Share table
PID [foreign key][ref PID] | CID [foreign key][ref CID] | ammount [NN]

Balance history table
PID [foreign key][ref PID] | balance [NN] | created [NN][date time]

Worth history table
CID [Foreign key][ref CID] | created [NN][date time] | worth [NN]

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
    assert os.path.exists(pathToScript) , f"[{pathToScript}] does not exsist"
    with open(pathToScript , "r") as F:
        statement = " ".join(F.readlines())
    newArgs = []
    for arg in args:
        if arg == None:
            newArgs.append("null")
        else:
            newArgs.append(arg)
    args = tuple(newArgs)
    statement = statement.format(*args)
    #print(f"{'='*20}\nexecuteing:\n{statement}\n{'='*20}")
    print(f"executeing : {pathToScript}")
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
        password = pword 
    )
    path = "scripts/setup.sql"
    executeScript(path , c)
    print(c)
    return c

def blankHistory(balance = 0.0) -> dict[datetime.datetime : float]:
    return {datetime.datetime.now() : balance}

class Profile:
    def __init__(self , balanceHist : dict[datetime.datetime : float] , discordID : int):
        self.balanceHist = dict(sorted(balanceHist.items() , key = lambda x : x[0])) #newest to oldest
        self.discordID = discordID
        self.currentBal = list(self.balanceHist.values())[0] 
        self.company = None
        self.shares = []
        
    
    def getEmbed(self , user : discord.Member , richest : bool) -> discord.Embed:
        title = f"Titcoin balance for [{user.display_name}]"
        desc = f"Your total Titcoin Balance is:\n`{self.currentBal}tc`\n{'**You are the wealthiest person in tiddleton**' if richest else ''}"
        colour = 0xFFD700 if richest else 0x000000
        return discord.Embed(title = title , description = desc , colour = colour)
        
    def INSERT(self , connection : Conn.MySQLConnection):
        connection.reconnect()
        executeScript("scripts/insertProfile.sql" , connection , self.discordID) # ensures there is a profile in the DB with the discordID
        connection.reconnect() # wow i really have to do that all the time
        PID = self.getPID(connection) #gets the auto generated PID 
        
        if self.company is not None:
            #need a way to get CID
            CID = self.company.getCID(connection , PID)
            self.company.INSERT(connection , PID , CID)
        
        for DT , bal in self.balanceHist.items():
            DT = datetimeToStr(DT)
            executeScript("scripts/insertBalance.sql" , connection , PID , bal , DT)
        
        for s in self.shares:
            CID = s.company.getCID(connection , s.profile.getPID(connection))
            s.INSERT(connection , PID , CID)
        
    @staticmethod
    def SELECTALL(connection : Conn.MySQLConnection) -> list[dict[str : int]]:
        #select from profiles all profiles
        #returns {"PID" : PID , "discordID" : discordID}
        cur = connection.cursor()
        cur.execute("USE TitCoin; SELECT * FROM Profiles")
        result = cur.fetchall()
        #[(PID , discordID)]
        returnList = []
        for pid , did in result:
            returnList.append({"PID" : pid , "discordID" : did})
        return returnList
    
    @staticmethod
    def getBalanceHist(connection : Conn.MySQLConnection , PID) -> list[dict[str : int]]:
        rows = executeScript("scripts/getBalanceHistory.sql" , connection , (PID,))
        retList = []
        for r in rows:
            temp = {
                "balance" : r[0],
                "created" : r[1]
            }
            retList.append(temp)
        return retList
        
    def getPID(self , connection : Conn.MySQLConnection):
        cur = connection.cursor()
        cur.execute("USE TitCoin; SELECT PID FROM Profiles WHERE discordID = %s" , (self.discordID,))
        PID = cur.fetchone()
        print(f"PID from getPID = {PID} where did = {self.discordID}")
        return PID
        
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
    
    def INSERT(self , connection : Conn.MySQLConnection , PID , CID):
        #no need to worry about inserting company, thats done from profile
        executeScript("scripts/insertShare.sql" , connection , (PID , CID , self.percentage , self.ID))
    
    @staticmethod
    def SELECTALL(connection : Conn.MySQLConnection) -> list[dict[str : int]]:
        #get all shares
        cur = connection.cursor()
        cur.execute("USE TitCoin; SELECT * FROM Shares")
        results = cur.fetchall() #(pid , cid , perc)
        retList = []
        for pid , cid , perc in results:
            temp = {
                "PID" : pid,
                "CID" : cid,
                "percent" : perc
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
        self.worthHist = dict(sorted(worthHist.items() , key = lambda x : x[0]))#newest to oldest
        self.shares = shares
        self.currentWorth = self.balanceHist.values()[0]
        self.name = name
        
    def getCID(self , connection : Conn.MySQLConnection , PID) -> int:
        #this is probably gonna do way too many queries but ehhhh
        pass
        
    def INSERT(self , connection : Conn.MySQLConnection , PID , CID):
        #dont have to worry about shares or profile
        executeScript("scripts/insertCompany.sql" , connection , (PID , self.name))
        for date , worth in self.worthHist.items():
            date : datetime.datetime
            date = datetimeToStr(date)
            executeScript("scripts/insertWorth.sql" , connection , (CID , date , worth))
        
    @staticmethod
    def SELECTALL(connection : Conn.MySQLConnection) -> list[dict[str : int]]:
        #gets a list of all companies
        cur = connection.cursor()
        cur.execute("USE TitCoin; SELECT * FROM Shares")
        results = cur.fetchall() #(cid , pid)
        retList = []
        for cid , pid , name in results:
            temp = {
                "PID" : pid,
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
    
    def createShare(self , profile : Profile , ammount : float) -> Share:
        self.currentWorth += ammount
        percent = ammount / self.currentWorth
        self.updateWorthHist()
        return Share(self , profile , percent)
    
    def sellShare(self , share : Share):
        share.sell() # the reason its done this way is so the share can remove itself from the profile 
        
        
def save(connection : Conn.MySQLConnection , database : dict):
    #goes through all of the profiles and calls the INSERT method on each
    #{
    #"profiles" : {
    #    discordID : Profile
    #},
    #"companies" : [
    #    Company   
    #]
    #}
    #we only care about profiles here
    profiles : dict[int : Profile] = database["profiles"]
    print(profiles)
    for discordID , P in profiles.items():
        P : Profile
        P.INSERT(connection) #and that should do it?
        connection.reconnect()
        print(f"saved [{discordID}]")
    

def load(connection : Conn.MySQLConnection) -> dict:
    #loads all data in then contructs all of the required objects makeing sure to reference where possible
    #start by selecting all Profile , company and share data
    connection.reconnect()
    profileData = Profile.SELECTALL(connection) # [{"PID" : pid , "discordID" : did}]
    connection.reconnect()
    companyData = Company.SELECTALL(connection) # [{"PID" : pid , "CID" : cid}]
    connection.reconnect()
    shareData = Share.SELECTALL(connection)     # [{"PID" : pid , "CID" : cid , "percent" : perc}]
    connection.reconnect() # these reconnects are rediculous
    
    profiles = {} # PID : Profile[incomplete]
    for pDat in profileData:
        PID = pDat["PID"]
        DID = pDat["discordID"]
        balHist = Profile.getBalanceHist(connection , PID)
        connection.reconnect()
        hist = {}
        for dat in balHist:
            hist[dat["created"]] = dat["balance"]
        profiles[PID] = Profile(hist , DID)
        
    companies = {} #CID : Company
    for cDat in companyData:
        PID = cDat["PID"]
        CID = cDat["CID"]
        owner = profiles[PID]
        name = cDat["name"]
        worthHist = Company.getWorthHist(connection , CID)
        connection.reconnect()
        hist = {}
        for dat in worthHist:
            hist[dat["created"]] = dat["worth"]
        company = Company(owner , hist , [] , name) # initialised as empty
        companies[CID] = company        
    
    for sDat in shareData:
        PID = sDat["PID"]
        CID = sDat["CID"]
        percent = sDat["percent"]
        prof : Profile = profiles[PID]
        comp : Company = companies[CID]
        shareObj = Share(comp , prof , percent)
        prof.shares.append(shareObj)
        comp.shares.append(shareObj)
        
    retDict = {
        "profiles" : {P.discordID : P for P in profiles.values()},
        "companies" : list(companies.values())
    }
    return retDict


#create a test database connection just to be sure
if __name__ == "__main__":
    quit() # in case i accidentally run this file
    connection = initDataBase()
    P = Profile(blankHistory() , 0)
    db = {"profiles" : {P.discordID : P} , "companies" : []}
    save(connection , db)
    