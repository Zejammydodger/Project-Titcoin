
"""
ok heres the idea:
    this will be essentially a header file in a C program, it will contain definitions for types such as 
    Person or Company each with all of their *essential* functions defined to raise notimplemented by defualt
    
    the reason for doing this is so that any new version of sqlhelper for example can just override the essential
    functions (while defineing new ones if need be) and the main titcoin file will just work based off the 
    assumtion that all of these types are the interface types, meaning they will always work (or raise notImplemented)
    
    tl;dr:
    define the types here so that we dont have to re write the implementation every time we change how it works 

"""

#NOTE
"""
    also swap to useing **kwargs wherever possible
"""

import datetime , discord
from datetime import datetime as dt

class Profile:
    def __init__(self , **kwargs):
        raise NotImplementedError()
    
    def addBal(self , amount : float):
        raise NotImplementedError()
    
    def getEmbed(self, richest : bool):
        raise NotImplementedError()
    
    def __str__(self) -> str:
        raise NotImplementedError()     
    
class Share:
    def __init__(self , **kwargs):
        raise NotImplementedError()
    
    def getWorth(self) -> float:
        raise NotImplementedError()
    
    def sell(self):
        raise NotImplementedError()
    
    def __str__(self) -> str:
        raise NotImplementedError()
    
class Company:
    def __init__(self , **kwargs):
        raise NotImplementedError()
    
    def createShare(self , profile : Profile , amount : float):
        raise NotImplementedError()
    
    def sellShare(self , share : Share):
        raise NotImplementedError()
    
    def __str__(self) -> str:
        raise NotImplementedError()
    
    
class TitcoinDB:
    #basically just a data class that holds the data in the database
    def __init__(self):
        raise NotImplementedError()
    
    def save(self):
        raise NotImplementedError()
    
    def load(self):
        raise NotImplementedError()