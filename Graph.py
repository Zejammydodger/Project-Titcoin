#like table.py but for actual properly orientated graphs
import random
from re import A

from click import Abort
from Table import typesafeCharNum
from math import floor

class Graph:
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
        e = f"{' '*(yPadding+1)}"
        f = f"{xAxisName}"

        footer = f"{a}*{b}\n{c}{d}\n{e}{f}" # adds the bottom axis 
        return "".join(rows) + footer
    
    
    
if __name__ == "__main__":
    g = Graph("random" , "random")
    for i in range(100):
        g.addPoint(random.randint(0 , 1000) , random.randint(0 , 1000))
    print(g)