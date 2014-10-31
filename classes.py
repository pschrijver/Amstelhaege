from Tkinter import *
import random

# Uses code from the Robot assignment MIT

# Eengezinswoningen = Green
# Bungalows = Yellow
# Maisons = Red
class GridVisualisation:
    def __init__(self, width, height, buildings):
        "Initializes a visualization with the specified parameters."
        self.max_dim = max(width, height)
        self.width = width
        self.height = height
        self.buildings = buildings

        # Initialize a drawing surface
        self.master = Tk()
        self.w = Canvas(self.master, width=500, height=500)
        self.w.pack()
        self.master.update()

        # Draw a backing and lines
        x1, y1 = self._map_coords(0, 0)
        x2, y2 = self._map_coords(width, height)
        self.w.create_rectangle(x1, y1, x2, y2, fill = "white")

        # Draw white squares for open fields
        self.tiles = {}
        for i in range(width):
            for j in range(height):
                x1, y1 = self._map_coords(i, j)
                x2, y2 = self._map_coords(i + 1, j + 1)
                self.tiles[(i, j)] = self.w.create_rectangle(x1, y1, x2, y2,
                                                            fill = "white")
        # Places buildings based on buildinglist
        for i in self.buildings:
            x1 = i.getX()
            y1 = i.getY()
            x1, y1 = self._map_coords(x1, y1)
            x2, y2 = self._map_coords(i.getX() + i.getWidth(),i.getY()
                                      + i.getDepth())

            if i.width == 11:
                self.tiles[(x1, y1)] = self.w.create_rectangle(x1, y1, x2, y2,
                                                           fill = "red")
            if i.width == 8:
                self.tiles[(x1, y1)] = self.w.create_rectangle(x1, y1, x2, y2,
                                                           fill = "green")
            if i.width == 10:
                self.tiles[(x1, y1)] = self.w.create_rectangle(x1, y1, x2, y2,
                                                           fill = "orange")
                
        # Draw gridlines
        for i in range(width + 1):
            x1, y1 = self._map_coords(i, 0)
            x2, y2 = self._map_coords(i, height)
            self.w.create_line(x1, y1, x2, y2)
        for i in range(height + 1):
            x1, y1 = self._map_coords(0, i)
            x2, y2 = self._map_coords(width, i)
            self.w.create_line(x1, y1, x2, y2)

    def _map_coords(self, x, y):
        "Maps grid positions to window positions (in pixels)."
        return (250 + 450 * ((x - self.width / 2.0) / self.max_dim),
                250 + 450 * ((self.height / 2.0 - y) / self.max_dim))
    
    def done(self):
        "Indicate that the animation is done so that we allow the user to close the window."
        mainloop()

class Grid(object):
    def __init__(self, width, depth, aantalhuizen):
        self.width = width
        self.depth = depth
        self.aantalhuizen = aantalhuizen
        self.eensgezins = float(0.6)
        self.bungalows = float(0.25)
        self.maisons = float(0.15)
        self.buildings = []
        
    def findOverlap(self, building1, building2):
        return NotImplementedError
    def swapBuilding(self, building1, building2):
        return NotImplementedError
    def addBuilding(self, building):
        return self.buildings.append(building)
    
    # Starts a simulation with 60 Eengezinswoningen.
    # - Occupied_coords keeps track of all the coords the
    #   Eengezinswoningen occupy.
    def updateGrid(self):
        occupied_coords = []
        for i in range(1, self.aantalhuizen + 1):
            while True:

                # Chooses the building type
                if i <= 0.6 * self.aantalhuizen:
                    ran_x = random.randrange(0,120 - 8)
                    ran_y = random.randrange(0,140 - 8) 
                    building = EengezinsWoning(ran_x, ran_y)
                elif i > 0.6 * self.aantalhuizen and i <= 0.85 * \
                     self.aantalhuizen :
                    ran_x = random.randrange(0,120 - 10)
                    ran_y = random.randrange(0,140 - 8) 
                    building = Bungalow(ran_x, ran_y)
                else:
                    ran_x = random.randrange(0,120 - 11)
                    ran_y = random.randrange(0,140 - 10) 
                    building = Maison(ran_x, ran_y)
   
                # Gets all coordinates of the building and sees if any
                # of the coords intersect with occupied_coords. Adds building
                # if the intersection of the lists is empty.
                coordinates = [(x,y) for x in range(ran_x, ran_x +
                                                    building.width)
                               for y in range(ran_y, ran_y + building.depth)]
                intersection = set(coordinates).intersection(occupied_coords)
                
                if not intersection:
                    self.addBuilding(building)
                    print i, building
                    occupied_coords += coordinates
                    break

        # Creates the actual Grid        
        anim = GridVisualisation(120,140, self.buildings)
        anim.done()
    
class Building(object):

    def getX(self):
        return self.x
    def getY(self):
        return self.y
    def getWidth(self):
        return self.width
    def getDepth(self):
        return self.depth
    def randomPosition(self):
        return NotImplementedError
    def translate(self):
        return NotImplementedError

class EengezinsWoning(Building):
    def __init__(self,x,y):
        self.x = x
        self.y = y  
        self.width = 8
        self.depth = 8  
        self.value = 285000
        self.percentage = 3
        self.vrijstand = 2

class Bungalow(Building):
    def __init__(self,x ,y) :
        self.x = x
        self.y = y
        
        self.width = 10
        self.depth = 8
        self.value = 399000
        self.percentage = 4
        self.vrijstand = 3
        
class Maison(Building):
    def __init__(self, x, y):
        self.x = x
        self.y = y
                
        self.width = 11
        self.depth = 10
        self.value = 610000
        self.percentage = 6
        self.vrijstand = 6


#====================MAIN THREAD ===================================#
if __name__ == '__main__':
    grid = Grid(120, 140, 60)
    grid.updateGrid()



        
