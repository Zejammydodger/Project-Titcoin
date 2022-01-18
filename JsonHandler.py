import os

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

            if type(temp) == type(self.JSONify):
                continue
            
            if type(temp) == list:
                for ie , e in enumerate(temp):
                    if isinstance(e , DataClass):
                        temp[ie] = e.JSONify()

            elif type(temp) == dict:
                for key , e in temp.items():
                    if isinstance(e , DataClass):
                        temp[key] = e.JSONify()

            
            #if temp has JSONify, call that
            if isinstance(e , DataClass):
                temp = e.JSONify()
        dataDict[attr] = temp
        return dataDict

    def populateFromDict(self , attribs : dict):
        for attr in attribs.keys():
            setattr(self, attr , attribs[attr])


class JSONHandler:
    #implements a load and dump function
    def __init__(self , path : str) -> None:
        assert os.path.exists(path) , f"[{path}] does not exsist"
        assert path.endswith(".json") , "path must point to a json file"
        self.path = path
        
    def load(self) -> dict:
        pass
    
    def dump(self , data : dict):
        pass
    