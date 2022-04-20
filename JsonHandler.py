import os , json

class DataClass:
    # uses the dir() method and filters dunders to save any object to a json file
    #NOTE the names of the attributes are what will be used as keys in the dictionary
    "This is the base class that acts as a struct kind of. inherit this into whatever data type you have"

    def JSONify(self) -> dict:
        allAttribs = dir(self)
        dataDict = {}
        for attr in allAttribs:
            attr : str
            if not attr.startswith("__"):
                temp = getattr(self , attr)
                #if temp is a list, loop over and convert any dataclass types to 

            if type(temp) == type(self.JSONify) or type(temp) == type(self.populateFromDict):
                # if temp is function, continue
                continue
            
            if type(temp) == list:
                # if temp = list
                for ie , e in enumerate(temp):
                    #index, element 
                    if isinstance(e , DataClass):
                        # if element is dataclass replace element with json serialized data class
                        temp[ie] = e.JSONify()

            elif type(temp) == dict:
                # if temp = dict
                for key , e in temp.items():
                    # key , element
                    if isinstance(e , DataClass):
                        # if element is a dataclass, replace with json serialized
                        temp[key] = e.JSONify()

            
            #if temp has JSONify, call that
            #if isinstance(e , DataClass):
            #    temp = e.JSONify()
        dataDict[attr] = temp
        print(dataDict)
        return dataDict

    def populateFromDict(self , attribs : dict):
        for attr in attribs.keys():
            setattr(self, attr , attribs[attr])

class Profile(DataClass):
    def __init__(self) -> None:
        super().__init__()
        self.id = 0
        self.balance = 0


class JSONHandler:
    #implements a load and dump function
    def __init__(self , path : str) -> None:
        assert os.path.exists(path) , f"[{path}] does not exsist"
        assert path.endswith(".json") , "path must point to a json file"
        self.path = path
        
    def loadMain(self) -> list:
        #loads the main.json file
        #returns a list of Profile dataClasses 
        with open(self.path , "r") as F:
            data = json.load(F)
            
        data = data["profiles"]
        profiles = []
        for p in data:
            prof = Profile()
            prof.populateFromDict(p)
            profiles.append(prof)
        return profiles
        
    
    def dumpMain(self , data : list):
        #dumps a list of profiles to main.json
        dictList = []
        for p in data: 
            dictList.append(p.JSONify())
        dump = {"profiles" : dictList}
        with open(self.path , "w") as F:
            json.dump(dump , F)
    