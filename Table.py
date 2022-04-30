#ok so im bored and i keep thinking about these tables so imma make the tables

#init table with a list of column classes 
#then the tabe class will have a "addrow" method which adds a row of pre formatted data to the column
#then the table class will have a __str__ that converts all of the data to a neatly formatted table useing the funky charaters
# ╔ ═ ╤ ║ │ ╪ ╗ ╣ ╝ ╚ ─ ┼

from math import floor , ceil , log10


def numToCharLen(num : int | float , floatRounding = 1):
    #takes a number and returns the number of characters the string form of that int will take up
    if isinstance(num , int):
        num = abs(num)
        if num == 0:
            num += 1
        return floor(log10(num)) + 1
    else:
        num = round(num , floatRounding)
        extra = 1 + floatRounding # 1 for the decimal place
        return floor(log10(num)) + extra

def typesafeCharNum(element):
    if isinstance(element , (int , float)):
        return numToCharLen(element)
    else:
        return len(element)
        
        
class BaseColumn:
    def __init__(self , name : str , padding = 1 , floatRounding = 1): #can add things like a "percentage of" kind of thing which will format each column into [#####     ] 50% kind of thing
        self.name = name
        self.rows = [name]
        self.__padding = padding * 2
        self.pad = padding # yeha i know this is dumb shuuuush
        self.__floatRounding = floatRounding
        self.maxCharLen = len(name) + self.__padding # pad each end
        
    def addElement(self , row):
        #do it this way so that the maximum charLen can be updated
        isFloat = isinstance(row , float) 
        if isFloat:
            row = round(row , self.__floatRounding)
        
        self.rows.append(row)
        
        if isinstance(row , int) or isFloat:
            length = numToCharLen(row , floatRounding = self.__floatRounding) 
        else:
            length = len(row)
        
        length += self.__padding
        
        if length > self.maxCharLen:
            self.maxCharLen = length
        
        print(f"maxlen of {self.name} is {self.maxCharLen}")
            
    def getThickLineSeg(self) -> str:
        #gets the header / footer string without joiners or like the edge bits
        return "═"*self.maxCharLen
        
    def getThinLineSeg(self) -> str:
        return "─"*self.maxCharLen
    
    def getRowStr(self , index) -> str:
        #gets the str of the row at index, add padding etc 
        data = self.rows[index]
        dataStr = str(data)
        padStr = " " * self.pad
        #ahhh fuck i forgot about whitespace
        charLen = typesafeCharNum(data)
        whiteSpace = self.maxCharLen - charLen
        
        return f"{padStr}{dataStr}{' ' * whiteSpace}{padStr}"
        
class PercentOfColumn(BaseColumn):
    pass

class IndexColumn(BaseColumn):
    def __init__(self, padding = 1, startsAt = 0):
        super().__init__("#" , padding, 1)
        self.__index = startsAt

    def addElement(self , row = None):
        #had to make row = None becuase python be weird sometimes, it doesnt actually do anything tho
        super().addElement(self.__index)
        self.__index += 1

class Table:
    def __init__(self , columns : list[BaseColumn] , maxWidth = 100 , maxCharCount = 2000):
        #if either of the max attributes are exceeded when generateing the string, an error should be thrown
        #for now anyway
        self.columns  = columns
        self.maxWidth = maxWidth
        self.maxCharCount = maxCharCount

    def addRowList(self , data : list):
        if len(data) != len(self.columns):
            raise ValueError("the number of columns provided in this row is not the same as the number of columns this table posesses")
        for i , dat in enumerate(data):
            col : BaseColumn = self.columns[i]
            col.addElement(dat)
            
    def addRow(self , *data):
        #provides 2 methods, but they do the same thing
        self.addRowList(list(data))
        
        
    def __str__(self):
        #ok this is where most of the actuall shit happens
        header = f"╔{'╤'.join([col.getThickLineSeg() for col in self.columns])}╗\n"
        footer = f"╚{'╧'.join([col.getThickLineSeg() for col in self.columns])}╝"
        
        seperator = f"\n╟{'┼'.join([col.getThinLineSeg() for col in self.columns])}╢\n"
        
        rows = []
        for i in range(len(self.columns[0].rows)):
            row = "│".join([col.getRowStr(i) for col in self.columns])
            rows.append(f"║{row}║")
            
        main = seperator.join(rows)+"\n"
        return f"{header}{main}{footer}"
        
        
if __name__ == "__main__":
    import random 
    
    index = IndexColumn()
    nameCol = BaseColumn("name")
    balance = BaseColumn("titcoin")
    
    table = Table([index , nameCol , balance])
    for i in range(10):
        table.addRow(i , "a"*random.randint(1,6) , random.randint(60 , 10000))
    
    #print(table.columns[0].rows)
    print(table)