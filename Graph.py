#like table.py but for actual properly orientated graphs
import random
from typing import Tuple

from Table import typesafeCharNum
from math import floor

#imports for pyplot
from matplotlib import pyplot
from discord import Embed , File , TextChannel , Message
from discord.ext.commands import Context
import io , asyncio

class BasicTextGraph:
    def __init__(self , xAxisName : str , yAxisName : str , width = 50 , height = 50 , pointChar = "#"):
        assert len(xAxisName) <= width and len(yAxisName) <= height , "one or both axis names are too long"
        self.width = width
        self.height = height
        self.xAxis = xAxisName
        self.yAxis = yAxisName
        self.char = pointChar
        self.points : list[tuple] = []
        self.maxVal_x = -1000000000
        self.maxVal_y = -1000000000
        self.minVal_x = 1000000000
        self.minVal_y = 1000000000
        self.__graph = [[" " for w in range(width)] for h in range(height)]
        
    def addPointTuple(self , point : tuple):
        
        x , y = point
        self.maxVal_x = x if x > self.maxVal_x else self.maxVal_x
        self.minVal_x = x if x < self.minVal_x else self.minVal_x
        
        self.maxVal_y = y if y > self.maxVal_y else self.maxVal_y
        self.minVal_y = y if y < self.minVal_y else self.minVal_y
        
        self.points.append(point)
        
    def addPoint(self , x , y):
        self.addPointTuple((x , y))
        
    def __scaleToX(self , x) -> int:
        return floor((x / (self.maxVal_x - self.minVal_x)) * self.width) - 1 
        
    def __scaleToY(self , y) -> int:
        return floor((y / (self.maxVal_y - self.minVal_y)) * self.height) - 1
        
    def plotPoints(self):
        #go through th points, scales to maxVal , minVal
        for x , y in self.points:
            sy = self.__scaleToY(y)
            sx = self.__scaleToX(x)
            self.__graph[sy][sx] = self.char
        
    def __str__(self):
        #this will take all of the data and spit out a nicely formatted graph
        self.plotPoints()
        yPadding = typesafeCharNum(self.maxVal_y)
        yAxisLen = typesafeCharNum(self.yAxis)
        rows = [] # actual data (plus y axis but it doesnt start like that shhhhhh)
        for i , row in enumerate(self.__graph):
            line = "".join(row)
            if i == 0:
                axis = f"{str(self.maxVal_y)}|" #this places the maximum value at the top
            else:    
                axis = f"{' '*yPadding}|"  #padding for comment above
                
            rows.append(axis+line+"\n")
        
        ypad = floor((self.height-yAxisLen)/2)
        xpad = floor((self.width-typesafeCharNum(self.xAxis))/2)
        yAxisName = f"{' '*ypad}{self.yAxis}{' '*ypad}" # this centres the yaxis name
        xAxisName = f"{' '*xpad}{self.xAxis}{' '*xpad}" 
        for i , c in enumerate(yAxisName):
            r = rows[i]
            rows[i] = c + r # this adds the yaxis name down the side
            
        a = f"{' '*yPadding}"
        b = f"{'-'*self.width}"
        c = f"{' ' * (1+yPadding+self.width-typesafeCharNum(self.maxVal_x))}"
        d = f"{str(self.maxVal_x)}"
        e = f"{' '*(yPadding+2)}"
        f = f"{xAxisName}"

        footer = f"{a}*{b}\n{c}{d}\n{e}{f}" # adds the bottom axis 
        return "".join(rows) + footer
    
class BasicGraph:
    def __init__(self , title : str , xAxisName : str , yAxisName : str , width = 500 , height = 500 , fname = "graph"):
        self.xName = xAxisName
        self.yName = yAxisName
        self.width = width
        self.height = height
        self.title = title
        self.fname = fname
        self.__FileForm = "png"
        self.__fullFileName = f"{self.fname}.{self.__FileForm}"
        self.__data : list[tuple] = []
        self.__buffer = io.BytesIO()
        
    def addPointTuple(self , point : Tuple):
        self.__data.append(point)
        
    def addPoint(self , x , y):
        self.addPointTuple((x , y))
        
    def plot(self):
        #plots the current data and saves it into the buffer
        self.__buffer.seek(0)
        pyplot.title(self.title)
        pyplot.xlabel(self.xName)
        pyplot.ylabel(self.yName)
        pyplot.plot(self.__data)
        pyplot.savefig(self.__buffer , format = self.__FileForm)
        
    def __getFile(self) -> File:
        self.__buffer.seek(0)
        return File(self.__buffer , filename=self.__fullFileName)
        
    def getEmbed(self , color = 0x000000) -> Embed:
        #returns an embeded with the graph as the only thing in it
        f = self.__getFile()
        e = Embed(title = self.title , color = color)
        e.set_image(url = "attachment://" + self.__fullFileName)
        return e
    
    def extendEmbed(self , emb : Embed):
        #adds a field to the embed with the graph
        f = self.__getFile()
        emb.set_image(url = "attachment://" + self.__fullFileName)
        
    def __del__(self):
        #this is the destructor of this obj
        self.__buffer.close()
        
    
class AutoUpdateGraph(BasicGraph):
    def __init__(self, title: str, xAxisName: str, yAxisName: str, embed = None , interval = 300 , width=500, height=500, fname="graph" , color = 0x000000):
        super().__init__(title, xAxisName, yAxisName, width, height, fname)
        self.embed = self.extendEmbed(embed) if embed is not None else self.getEmbed(color = color)#basically if this is none, then send a new embed, and update from there
        self.message : Message = None # this will be the message object generated when the embed is sent
        self.interval = interval
        self.__running = False
        self.__changed = False
        
        #starting task
        self.__task = asyncio.create_task(self.updater)
        
    async def sendToChannel(self , discordChannel : TextChannel):
        self.message = await discordChannel.send(embed = self.embed)
        self.__running = True # only allowed to run when the message has been sent
        
    async def sendToCtx(self , ctx : Context):
        await self.sendToChannel(ctx.channel)
        
    def startWithMessage(self , msg : Message):
        #skips sending the message, this is here in case the message is loaded say after the bot closes and reopens
        self.message = msg
        self.__running = True
        
    async def plot(self):
        super().plot()
        await self.message.edit(embed = self.embed)
        
    def addPoint(self, x, y):
        self.__changed = True
        return super().addPoint(x, y)
    
    async def updater(self):
        #asyncio task that updates the message every interval seconds
        while True:
            if self.__running and self.__changed:
                await self.plot()
                self.__changed = False
            await asyncio.sleep(self.interval)
            
    def __del__(self):
        self.__running = False
        self.__task.cancel()
    
if __name__ == "__main__":
    g = BasicTextGraph("random" , "random")
    for i in range(100):
        g.addPoint(random.randint(0 , 1000) , random.randint(0 , 1000))
    print(g)