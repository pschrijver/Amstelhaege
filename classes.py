from Tkinter import *
import random
import math
import time

# Uses code from the Robot assignment MIT

# Eengezinswoningen = red
# Bungalows = blue
# Maisons = black
class GridVisualisation:
    def __init__(self, width, height, buildings):
        "Initializes a visualization with the specified parameters."
        # Adjust size of visualisation based on precision
        self.max_dim = max(width / (precision * 1.5), height / (precision * 1.5))
        self.delay = 0.001
        self.width = width
        self.height = height
        self.buildings = buildings
        self.width = int(self.width)
        self.height = int(self.height)
        distance = 0
        
        # Initialize a drawing surface
        self.master = Tk()
        self.w = Canvas(self.master, width=1000, height=1000)
        self.w.pack()
        self.master.update()
        
        # Draw a backing and lines
        x1, y1 = self._map_coords(0, 0)
        x2, y2 = self._map_coords(self.width, self.height)
        self.w.create_rectangle(x1, y1, x2, y2, fill = "white")

        # Draw white squares for open fields
        self.tiles = {}
##        for i in range(self.width):
##            for j in range(self.height):
##                x1, y1 = self._map_coords(i, j)
##                x2, y2 = self._map_coords(i + 1, j + 1)
##                self.tiles[(i, j)] = self.w.create_rectangle(x1, y1, x2, y2,
##                                                            fill = "white")
        self.updateAnimation(self.buildings, distance)
                
    def emptyAnimation(self, buildings):
        self.w.delete('all')
        x1, y1 = self._map_coords(0, 0)
        x2, y2 = self._map_coords(self.width, self.height)
        self.w.create_rectangle(x1, y1, x2, y2, fill = "white")
            
    def updateAnimation(self, buildings, distance):
        " Updates the animation with a new list of buildings, for instance when"
        " buildings have been moved, this can be useful"
        for i in buildings:
            x1 = i.getX()
            y1 = i.getY()

            x1, y1 = self._map_coords(i.x, i.y)
            x2, y2 = self._map_coords(i.x - i.depth * math.sin(i.angle),
                       i.y + i.depth * math.cos(i.angle))
            x3, y3 = self._map_coords(i.x - i.depth * math.sin(i.angle) + i.width * math.cos(i.angle),
                       i.y + i.depth * math.cos(i.angle) + i.width * math.sin(i.angle))
            x4, y4 = self._map_coords(i.x + i.width * math.cos(i.angle),
                       i.y + i.width * math.sin(i.angle))
            
            points = [x1, y1, x2, y2, x3, y3, x4, y4]

            if i.name == 'maison':
                  self.w.create_polygon(points, 
                            fill='black')
                  self.w.create_text((x1+22,y1-23), fill="white", text="score", font=("arial",8))
            if i.name == 'eengezinswoning':
                  self.w.create_polygon(points, 
                            fill='red')
                  self.w.create_text((x1+17,y1-17), fill="white", text="score", font=("arial",8))
            if i.name == 'bungalow':
                  self.w.create_polygon(points,
                            fill='blue')
                  self.w.create_text((x1+19,y1-17), fill="white", text="score", font=("arial",8))
        distance = 'Totale vrijstand = ' + str(int(distance)) + 'm'
        self.w.create_text(20,20, anchor=W, font='arial', text=distance)

        self.master.update()
        time.sleep(self.delay)
        
    def _map_coords(self, x, y):
        "Maps grid positions to window positions (in pixels)."
        return (550 + 450 * ((x - self.width / 2.0) / self.max_dim),
                350 + 450 * ((self.height / 2.0 - y) / self.max_dim))
    
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
        return self.cornerInBuilding(house1, house2) or self.cornerInBuilding(house2, house1)

    def cornerInBuilding(self, house1, house2):
        """
        Checks whether a corner of house2 lies inside house1
        """

        # Coordinates of all corners of house2
        corners = [(house2.x, house2.y)]
        corners.append((house2.x - house2.depth * math.sin(house2.angle),
                   house2.y + house2.depth * math.cos(house2.angle)))
        corners.append((house2.x - house2.depth * math.sin(house2.angle) + house2.width * math.cos(house2.angle),
                   house2.y + house2.depth * math.cos(house2.angle) + house2.width * math.sin(house2.angle)))
        corners.append((house2.x + house2.width * math.cos(house2.angle),
                   house2.y + house2.width * math.sin(house2.angle)))

        rotCorners = []
        # rotate all corners by an angle -house1.angle, so that we can work in the
        # frame where house1 has angle 0
        for corner in corners:
            r = math.sqrt((corner[0] - house1.x)**2 + (corner[1] - house1.y)**2)
    
            try:
                sign = (corner[1] - house1.y) / math.fabs(corner[1] - house1.y)
            except ZeroDivisionError:
                sign = 1
                
            if r != 0:
                theta =  sign * math.acos((corner[0] - house1.x) / r)
            
                rotCorners.append((house1.x + r * math.cos(theta - house1.angle),\
                                   house1.y + r * math.sin(theta - house1.angle)))
            else:
                rotCorners.append((corner[0], corner[1]))
                
            
        # For every corner of house2 checks whether it lies inside house1
        for corner in rotCorners:
            if house1.x <= corner[0] and corner[0] <= house1.x + house1.width:
                if house1.y <= corner[1] and corner[1] <= house1.y + house1.depth:
                    return True

        return False

    def findDistance(self, building1, building2):
        """ Searches for the shortest distances between building1 and building2.
        The minimal required distance between buildings is not subtracted."""

        assert(self.findOverlap(building1, building2) == False), 'Buildings overlap'
        
        d = [(building1, building2), (building2, building1)]
        distancePerIteration = []

        for i in range(0, len(d)):
            
            # Coordinates of all corners of d[i][1]
            corners2 = [(d[i][1].x, d[i][1].y)]
            corners2.append((d[i][1].x - d[i][1].depth * math.sin(d[i][1].angle),
                       d[i][1].y + d[i][1].depth * math.cos(d[i][1].angle)))
            corners2.append((d[i][1].x - d[i][1].depth * math.sin(d[i][1].angle) + d[i][1].width * math.cos(d[i][1].angle),
                       d[i][1].y + d[i][1].depth * math.cos(d[i][1].angle) + d[i][1].width * math.sin(d[i][1].angle)))
            corners2.append((d[i][1].x + d[i][1].width * math.cos(d[i][1].angle),
                       d[i][1].y + d[i][1].width * math.sin(d[i][1].angle)))
            
            rotCorners2 = []
            # rotate all corners by an angle -d[i][0].angle, so that we can work in the
            # frame where d[i][0] has angle 0
            for corner in corners2:
                r = math.sqrt((corner[0] - d[i][0].x)**2 + (corner[1] - d[i][0].y)**2)

                try:
                    sign = (corner[1] - d[i][0].y) / math.fabs(corner[1] - d[i][0].y)
                except ZeroDivisionError:
                    sign = 1

                if r != 0:
                    theta = sign * math.acos((corner[0] - d[i][0].x) / r)

                    rotCorners2.append((d[i][0].x + r * math.cos(theta - d[i][0].angle),\
                                       d[i][0].y + r * math.sin(theta - d[i][0].angle)))
                else:
                    rotCorners2.append((corner[0], corner[1]))

            # Positions of every corner of building1
            corners1 = [(d[i][0].x, d[i][0].y)]
            corners1.append((d[i][0].x, d[i][0].y + d[i][0].depth))
            corners1.append((d[i][0].x + d[i][0].width, d[i][0].y + d[i][0].depth))
            corners1.append((d[i][0].x + d[i][0].width, d[i][0].y))

            distances = []

            # Looks for corners that lie between x1 and x1 + width or y1 and y1 + depth
            # of building1 and determines the perpendicular distances to these corners
            for c2 in rotCorners2:
                if corners1[0][0] < c2[0] and corners1[2][0] > c2[0]:
                    if c2[1] <= corners1[0][1]:
                        distances.append(corners1[0][1] - c2[1])
                    else:
                        distances.append(c2[1] - corners1[2][1])
                elif corners1[0][1] < c2[1] and corners1[2][1] > c2[1]:
                    if c2[0] <= corners1[0][0]:
                        distances.append(corners1[0][0] - c2[0])
                    else:
                        distances.append(c2[0] - corners1[2][0])
                        
            # find distances between all corners
            for c1 in corners1:
                for c2 in rotCorners2:
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

    def randomPlacements(self):
        self.buildings = []
        for i in range(1, self.aantalhuizen + 1):
            while True:  
                overlap = False
                # Chooses the building type and creates a random position
                 # Chooses the building type
                if i <= 0.6 * self.aantalhuizen:
                    ran_x = random.randrange(0,self.width - 8)
                    ran_y = random.randrange(0,self.depth - 8) 
                    building = EengezinsWoning(ran_x, ran_y)
                elif i > 0.6 * self.aantalhuizen and i <= 0.85 * \
                     self.aantalhuizen :
                    ran_x = random.randrange(0,self.width - 10)
                    ran_y = random.randrange(0,self.depth - 8) 
                    building = Bungalow(ran_x, ran_y)
                else:
                    ran_x = random.randrange(0,self.width - 11)
                    ran_y = random.randrange(0,self.depth - 10) 
                    building = Maison(ran_x, ran_y)
                # Checks if building overlaps with another building.
                for b in self.buildings:
                    if self.findOverlap(b, building):
                        overlap = True
                        break
                if not overlap:
                    self.addBuilding(building)
                    break
##                print len(self.buildings)
            

    # Initializes the grid with non overlapping buildings, at random positions.
    def updateGrid(self, simulations):
        self.randomPlacements()
        
        # Creates the Grid Animation
        anim = GridVisualisation(self.width,self.depth, self.buildings)
        best_distance = 0
        best_buildings = None
        
        # Starts the simulation, updates the image. Shows the buildings, plus
        # the total 'vrijstand' of all buildings (useful for further calculations)
        for simulation in range(simulations):
            anim.emptyAnimation(self.buildings)
            self.randomPlacements()
            
            # Calculates the total 'vrijstand' of all buildings.
            distance = 0
            for building in self.buildings:
                closest = float("inf")
                # Finds the closest building
                for otherbuilding in self.buildings:
                    if building != otherbuilding:
                        dist = self.findDistance(building, otherbuilding)
                        if dist < closest:
                            closest = dist 
                distance += closest

            if distance > best_distance:
                best_distance = distance
                best_buildings = self.buildings
                
            anim.updateAnimation(self.buildings, distance)
            
        anim.emptyAnimation(self.buildings)
        anim.updateAnimation(best_buildings, best_distance)

        # Returns the setup of the instance with best_distance
        return best_buildings, best_distance
    
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
        self.name = 'eengezinswoning'
        self.x = x
        self.y = y
        self.grid = Grid(100,100,2)
        self.width = 8
        self.depth = 8
        self.angle = 0
##        self.grid = Grid(100,100,2)
        self.value = 285000
        self.percentage = 1.03
        self.vrijstand = 2

class Bungalow(Building):
    def __init__(self, x, y):
        self.name = 'bungalow'
        self.x = x
        self.y = y
        self.angle = 0
        self.grid = Grid(100,100,2)
        self.width = 10
        self.depth = 7.5
        self.angle = 0
##        self.grid = Grid(100,100,2)
        self.value = 399000
        self.percentage = 1.04
        self.vrijstand = 3
        
class Maison(Building):
    def __init__(self, x, y):
        self.name = 'maison'
        self.x = x
        self.y = y
        self.angle = 0

        self.grid = Grid(100,100,2)
        self.width = 11
        self.depth = 10.5

##        self.grid = Grid(100,100,2)
        #self.width = 11 / precision
        #self.depth = 10 / precision

        self.value = 610000
        self.percentage = 1.06
        self.vrijstand = 6


#====================MAIN THREAD ===================================#
if __name__ == '__main__':
    precision = 1.0
    grid = Grid(120., 160., 20)
    simulations = 2000
    print grid.updateGrid(simulations)

    # ====== TEST RUNS ======= #
    #b1 = EengezinsWoning(15,15)
    #b2 = Maison(3,3)
    #grid = Grid(100,100,2)
    #grid.addBuilding(b1)
    #grid.addBuilding(b2)
    #print grid.buildings[0].x, grid.buildings[0].y

    #print grid.findOverlap(b1,b2)
    #print grid.findDistance(b1,b2)

    #b1 = EengezinsWoning(30,30)
    #b2 = EengezinsWoning(55,35)
    #grid = Grid(100,100,2)
    #grid.addBuilding(b1)
    #grid.addBuilding(b2)
    #print grid.findDistance(b1, b2)
    #print grid.findDistance(b2, b1)
    
    #print "Rotatie", grid.findOverlap(b1,b2)
    #print grid.cornerInBuilding(b1,b2)
    #print grid.cornerInBuilding(b2,b1)

    #b1 = Bungalow(19.,6.,1.)
    #b2 = Maison(4.,1.,1.)
    #grid = Grid(100,100,2,1)
    #grid.addBuilding(b1)
    #grid.addBuilding(b2)
    #print 'overlap', grid.findOverlap(b1,b2)
    #print 'distance', grid.findDistance(b1,b2)


##    b1 = EengezinsWoning(80,80)
##    b2 = Maison(77,82)
##    grid = Grid(100,100,2)
##    grid.addBuilding(b1)
##    grid.addBuilding(b2)

##    print "Rotatie", grid.findOverlap(b2,b1)

##    print grid.buildings[0].x, grid.buildings[0].y
##
##    print grid.findOverlap(b1,b2)
##    print grid.findDistance(b1,b2)


##    grid = Grid(120, 140, 60)
##    grid.updateGrid()
    # Precision ratio to one meter. (0.5 is half meters, 0.1 is 10cm etc)

    # Says False but should be True 
##    b1 = Maison(43.,10.,1.)
##    b2 = Maison(45.,10.,1.)
##    grid = Grid(60.,60.,2.,1.)
##    grid.addBuilding(b1)
##    grid.addBuilding(b2)
##    print 'overlap', grid.findOverlap(b1,b2)
##    print 'distance', grid.findDistance(b1,b2)

#    b1 = Maison(0.,7.,1.)
#    b2 = EengezinsWoning(13,13,1.)
#    grid = Grid(100,100,2,1.)
#    grid.addBuilding(b1)
#    grid.addBuilding(b2)
#    print 'overlap', grid.findOverlap(b1,b2)
#    print 'distance', grid.findDistance(b1,b2)

#    b1 = Bungalow(11.,10.,1.)
#    b2 = Maison(0.,12.,1.)
#    grid = Grid(30.,30.,3, 1.)
#    grid.addBuilding(b1)
#    grid.addBuilding(b2)
#    print 'overlap', grid.findOverlap(b1,b2)
#    print 'distance', grid.findDistance(b1,b2)
