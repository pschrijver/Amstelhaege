from Tkinter import *
import random
import math

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
        
    def findOverlap(self, house1, house2):
        """ Checks whether house1 and house2 overlap """
        return self.cornerInBuilding(house1, house2) and \
    self.cornerInBuilding(house2, house1)

    def cornerInBuilding(self, house1, house2):
        """
        Checks whether a corner of house2 lies inside house1
        """

        # Coordinates of all corners of house2
        corners = [(house2.x, house2.y)]
        corners.append((house2.x + house2.depth * math.sin(house2.angle),
                   house2.y + house2.depth * math.cos(house2.angle)))
        corners.append((house2.x + house2.depth * math.sin(house2.angle) + house2.width * math.cos(house2.angle),
                   house2.y + house2.depth * math.cos(house2.angle) - house2.width * math.sin(house2.angle)))
        corners.append((house2.x + house2.width * math.cos(house2.angle),
                   house2.y - house2.width * math.sin(house2.angle)))

        rotCorners = []
        # rotate all corners by an angle -house1.angle, so that we can work in the
        # frame where house1 has angle 0
        for corner in corners:
            r = math.sqrt(corner[0]**2 + corner[1]**2)

            rotCorners.append((r * math.cos(math.atan(corner[1] / corner[0]) - house1.angle), r * math.sin(math.atan(corner[1] / corner[0]) - house1.angle)))

        # For every corner of house2 checks whether it lies inside house1
        for corner in rotCorners:
            if house1.x < corner[0] and corner[0] < house1.x + house1.width:
                if house1.y < corner[1] and corner[1] < house1.y + house1.depth:
                    return True

        return False

    def findDistance(self, building1, building2):
        """ Searches for the shortest distances between building1 and building2 """

        d = [(building1, building2), (building2, building1)]
        distancePerIteration = []

        for i in range(0, len(d)):
            # Positions of every corner of building2
            corners2 = [(d[i][1].x, d[i][1].y)]
            corners2.append((d[i][1].x + d[i][1].depth * math.sin(d[i][1].angle),
                       d[i][1].y + d[i][1].depth * math.cos(d[i][1].angle)))
            corners2.append((d[i][1].x + d[i][1].depth * math.sin(d[i][1].angle) + d[i][1].width * math.cos(d[i][1].angle),
                       d[i][1].y + d[i][1].depth * math.cos(d[i][1].angle) - d[i][1].width * math.sin(d[i][1].angle)))
            corners2.append((d[i][1].x + d[i][1].width * math.cos(d[i][1].angle),
                       d[i][1].y - d[i][1].width * math.sin(d[i][1].angle)))

            rotCorners2 = []

            # rotate all corners by an angle -house1.angle, so that we can work in the
            # frame where house1 has angle 0
            for corner in corners2:
                r = math.sqrt(corner[0]**2 + corner[1]**2)

                rotCorners2.append((r * math.cos(math.atan(corner[1] / corner[0]) - d[i][0].angle), r * math.sin(math.atan(corner[1] / corner[0]) - d[i][0].angle)))

            # Positions of every corner of building1
            corners1 = [(d[i][0].x, d[i][0].y)]
            corners1.append((d[i][0].x, d[i][0].y + d[i][0].depth))
            corners1.append((d[i][0].x + d[i][0].width, d[i][0].y + d[i][0].depth))
            corners1.append((d[i][0].x + d[i][0].width, d[i][0].y))

            distances = []

            # Looks for corners that lie between x1 and x1 + width or y1 and y1 + depth
            # of building1 and determines the perpendicular distances to these corners
            for c2 in corners2:
                if d[i][0].x < c2[0] and d[i][0].x + d[i][0].width > c2[0]:
                    if c2[1] < d[i][0].y:
                        distances.append(d[i][0].y - c2[1])
                    else:
                        distances.append(c2[1] - d[i][0].y - d[i][0].depth)
                elif d[i][0].y < c2[1] and d[i][0].y + d[i][0].depth > c2[1]:
                    if c2[0] < d[i][0].x:
                        distances.append(d[i][0].x - c2[1])
                    else:
                        distances.append(c2[0] - d[i][0].y - d[i][0].depth)

            # find distances between all corners
            for c1 in corners1:
                for c2 in corners2:
                    distances.append(math.sqrt((c2[0] - c1[0])**2 + (c2[1] - c1[1])**2))

            distancePerIteration.append(min(distances))

        # Returns the shortest distance between the buildings
        return min(distancePerIteration)

    def swapBuilding(self, building1, building2):
        """ Swaps the positions of two buildings """
        x1 = building1.x
        y1 = building1.y

        x2 = building2.x
        y2 = building2.y

        building1.newPosition(x2, y2)
        building2.newPosition(x1, y1)
        
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
    def __init__(self):
        pass

    def getX(self):
        return self.x
    def getY(self):
        return self.y
    def getAngle(self):
        return self.angle
    def getWidth(self):
        return self.width
    def getDepth(self):
        return self.depth
    def randomPosition(self):
        # Places the building at a random place on the grid
        self.x = random.random() * (self.grid.width - self.width)
        self.y = random.random() * (self.grid.depth - self.depth)
        self.angle = random.random() * 2 * math.pi
    def translate(self, dx, dy):
        # Translate building to place (x + dx, y + dy)
        self.x += dx
        self.y += dy
    def newPosition(self, x, y):
        # Place building at another place
        self.x = x
        self.y = y

# !!!!!!!! x and y need to go to superclass, also add angle and grid !!!!!!!!!!!!!!!
class EengezinsWoning(Building):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.grid = Grid(100,100,2)
        self.width = 8
        self.depth = 8  
        self.value = 285000
        self.percentage = 1.03
        self.vrijstand = 2

class Bungalow(Building):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.grid = Grid(100,100,2)
        self.width = 10
        self.depth = 8
        self.value = 399000
        self.percentage = 1.04
        self.vrijstand = 3
        
class Maison(Building):
    def __init__(self, x, y):                
        self.x = x
        self.y = y
        self.angle = 0
        self.grid = Grid(100,100,2)
        self.width = 11
        self.depth = 10
        self.value = 610000
        self.percentage = 1.06
        self.vrijstand = 6


#====================MAIN THREAD ===================================#
if __name__ == '__main__':
    b1 = EengezinsWoning(15,15)
    b2 = Maison(3,3)
    grid = Grid(100,100,2)
    grid.addBuilding(b1)
    grid.addBuilding(b2)
    print grid.buildings[0].x, grid.buildings[0].y

    print grid.findOverlap(b1,b2)
    print grid.findDistance(b1,b2)

    
#    grid = Grid(120, 140, 60)
#    grid.updateGrid()



        
