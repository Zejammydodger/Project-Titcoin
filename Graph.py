#like table.py but for actual properly orientated graphs
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
        self.maxVal_x = 1000000000
        self.maxVal_y = 1000000000
        self.minVal_x = -1000000000
        self.minVal_y = -1000000000
        self.__graph = [[False for w in range(width)] for h in range(height)]
        
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
        return floor((x / (self.maxVal_x - self.minVal_x)) * self.width) 
        
    def __scaleToY(self , y) -> int:
        return floor((y / (self.maxVal_y - self.minVal_y)) * self.height)
        
    def plotPoints(self):
        #go through th points, scales to maxVal , minVal
        for x , y in self.points:
            self.__graph[self.__scaleToY(y)][self.__scaleToX(x)] = True
        
    def __str__(self):
        #this will take all of the data and spit out a nicely formatted graph
        pass