import math

class Building(object):
    def __init__(self, x, y, angle, gridWidth, gridDepth):
        self.x = x
        self.y = y
        self.angle = angle * 2 * math.pi / 360
        self.gridWidth = gridWidth
        self.gridDepth = gridDepth

    def getX(self):
        return self.x
    def getY(self):
        return self.y
    def getAngle(self):
        return self.angle * 360 / (2 * math.pi)
    def getWidth(self):
        return self.width
    def getDepth(self):
        return self.depth
    def randomPosition(self):
        # Places the building at a random place on the grid
        self.x = random.random() * self.gridWidth
        self.y = random.random() * self.gridDepth
        self.angle = random.random() * 2 * math.pi
    def translate(self, dx, dy):
        # Translate building to place (x + dx, y + dy)
        self.x += dx
        self.y += dy
    def newPosition(self, x, y):
        # Place building at another place
        self.x = x
        self.y = y
    def newAngle(self, angle):
        # Give a new angle to building
        self.angle = angle * 2 * math.pi / 360
    def changeShortestDist(self, shortestDist, shortestNeighbor):
        self.shortestDist = shortestDist
        self.shortestNeighbor = shortestNeighbor
    def getShortestDist(self):
        return self.shortestDist
    def getShortestNeighbor(self):
        return self.shortestNeighbor


class EengezinsWoning(Building):
    def __init__(self, x, y, angle, gridWidth, gridDepth):
        Building.__init__(self, x, y, angle, gridWidth, gridDepth)
        self.name = 'eengezinswoning'
        self.width = 8
        self.depth = 8
        self.value = 285000
        self.percentage = .03
        self.vrijstand = 2

class Bungalow(Building):
    def __init__(self, x, y, angle, gridWidth, gridDepth):
        Building.__init__(self, x, y, angle, gridWidth, gridDepth)
        self.name = 'bungalow'
        self.width = 10
        self.depth = 7.5
        self.value = 399000
        self.percentage = .04
        self.vrijstand = 3

class Maison(Building):
    def __init__(self, x, y, angle, gridWidth, gridDepth):
        Building.__init__(self, x, y, angle, gridWidth, gridDepth)
        self.name = 'maison'
        self.width = 11
        self.depth = 10.5
        self.value = 610000
        self.percentage = .06
        self.vrijstand = 6

