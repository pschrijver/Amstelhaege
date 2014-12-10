from Tkinter import *
from operator import itemgetter
#import matplotlib.pyplot as plt
import random
import math
import time
import csv
import multiprocessing
from multiprocessing import Manager

# Uses code from the Robot assignment MIT

# Eengezinswoningen = red
# Bungalows = blue
# Maisons = black
class GridVisualisation:
    def __init__(self, width, height, buildings, prijsverb):
        "Initializes a visualization with the specified parameters."
        # Adjust size of visualisation based on precision
        self.max_dim = max(width / (precision * 1.5), height / (precision * 1.5))
        self.delay = 0.00000001
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

        self.updateAnimation(self.buildings, '{:5,.2f}'.format(prijsverb))

    def emptyAnimation(self, buildings):
        self.w.delete('all')
        x1, y1 = self._map_coords(0, 0)
        x2, y2 = self._map_coords(self.width, self.height)
        self.w.create_rectangle(x1, y1, x2, y2, fill = "white")

    def updateAnimation(self, buildings, prijsverb):
        " Updates the animation with a new list of buildings, for instance when"
        " buildings have been moved, this can be useful"
        for i in buildings:

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
        prijsverb = 'Prijsverbetering = ' + str(prijsverb) + ' euro'
        self.w.create_text(20,20, anchor=W, font='arial', text=prijsverb)

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

    def findOverlap2(self, building):
        """
        Calculates whether a building has overlap with another building on the
        grid and if the building has a distant > vrijstand from the edges of the
        grid
        """

        corners = [(building.x, building.y)]
        corners.append((building.x - building.depth * math.sin(building.angle),
                   building.y + building.depth * math.cos(building.angle)))
        corners.append((building.x - building.depth * math.sin(building.angle) + building.width * math.cos(building.angle),
                   building.y + building.depth * math.cos(building.angle) + building.width * math.sin(building.angle)))
        corners.append((building.x + building.width * math.cos(building.angle),
                   building.y + building.width * math.sin(building.angle)))

        for x, y in corners:
            if x < building.vrijstand or y < building.vrijstand:
                return True
            elif x > self.width - building.vrijstand or y > self.depth - building.vrijstand:
                return True
        i = 0
        buildingOverlap = False

        shortestDist = float('inf')
        diagonal = math.sqrt(building.width**2 + building.depth**2) + math.sqrt(11**2 + 10.5**2)
        for neighbor in self.buildings:
            dist = math.sqrt((building.x - neighbor.x)**2 + (building.y - neighbor.y)**2)
            if dist < shortestDist:
                shortestDist = dist
        shortestDist = shortestDist + diagonal

        while i < len(self.buildings) and not buildingOverlap:
            dist = math.sqrt((building.x - self.buildings[i].x)**2 + (building.y - self.buildings[i].y)**2)

            if building != self.buildings[i] and dist <= shortestDist:
                buildingOverlap = self.findOverlap(building, self.buildings[i])
            i += 1

        return buildingOverlap

    def vrijstandMuren(self, house1):
           if house1.x - house1.vrijstand >= 0 and house1.x + house1.vrijstand + house1.width <= self.width and \
               house1.y - house1.vrijstand >= 0 and house1.y + house1.vrijstand + house1.depth <= self.depth:
               return True

    def findOverlap(self, house1, house2):
        """ Checks whether house1 and house2 overlap and makes sure there is enough vrijstand """
        if self.findDistance(house1, house2) >= house1.vrijstand and \
           self.findDistance(house1, house2) >= house2.vrijstand:
            return self.cornerInBuilding(house1, house2) or self.cornerInBuilding(house2, house1)
        else:
            return True

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

                rotCorners.append((house1.x + r * math.cos(theta - house1.angle),
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

##        assert(self.findOverlap(building1, building2) == False), 'Buildings overlap'

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

                    rotCorners2.append((d[i][0].x + r * math.cos(theta - d[i][0].angle),
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

    def findShortestDist(self, building):
        """
        Finds shortest distance from var building to another building. Returns
        this value
        """

        # Choose a distance that overestimates any possible distance
        shortestDist = math.sqrt(self.width**2 + self.depth**2)

        # Finds a radius in which the closest building lies
        maxDist = float('inf')
        diagonal = math.sqrt(building.width**2 + building.depth**2) + math.sqrt(11**2 + 10.5**2)
        for neighbor in self.buildings:
            dist = math.sqrt((building.x - neighbor.x)**2 + (building.y - neighbor.y)**2)
            if dist < maxDist and building != neighbor:
                maxDist = dist
        # Add diagonal to distance between corners to account for rotation and orientation of
        # buildings
        maxDist += diagonal

        # Calculate the distance to all buildings in the maxDist radius
        for neighbor in self.buildings:
            dist = math.sqrt((building.x - neighbor.x)**2 + (building.y - neighbor.y)**2)

            if building != neighbor and dist < maxDist:
                newDist = self.findDistance(building, neighbor)
                if newDist < shortestDist:
                    shortestDist = newDist

        return shortestDist


    def calcPrice(self, building):
        """
        Calculate the price of a single house. Returns the price and the vrijstand
        """
        extravrijstand = self.findShortestDist(building) - building.vrijstand
        prijsverb = building.percentage * extravrijstand + 1
        huisprijs = building.value * prijsverb

        return float(huisprijs), float(extravrijstand)

    def calcTotalPrice(self):
        """
        Calculates the total price for all buildings on the grid and the total
        vrijstand.
        """
        totalPrice = 0
        totalExtraVrijstand = 0

        for building in self.buildings:
            priceAndVrijstand = self.calcPrice(building)
            totalPrice += priceAndVrijstand[0]
            totalExtraVrijstand += priceAndVrijstand[1]

        return totalPrice, totalExtraVrijstand

    def randomPlacements(self):
        self.buildings = []
##        anim = GridVisualisation(self.width,self.depth, self.buildings)
        for i in range(1, self.aantalhuizen + 1):
##            anim.emptyAnimation(self.buildings)
            trials = 0
            while True:
                trials += 1
                overlap = False
                # Chooses the building type and creates a random position
                 # Chooses the building type
                if i > 0.4 * self.aantalhuizen:
                    ran_x = random.randrange(0,self.width - 8)
                    ran_y = random.randrange(0,self.depth - 8)
                    ran_angle = random.randrange(0,360)
                    building = EengezinsWoning(ran_x, ran_y, 0, self.width, self.depth)
                elif i > 0.15 * self.aantalhuizen and i <= 0.4 * \
                     self.aantalhuizen :
                    ran_x = random.randrange(0,self.width - 10)
                    ran_y = random.randrange(0,self.depth - 8)
                    building = Bungalow(ran_x, ran_y, 0, self.width, self.depth)
                else:
                    ran_x = random.randrange(0,self.width - 11 )
                    ran_y = random.randrange(0,self.depth - 10)
                    building = Maison(ran_x, ran_y, 0, self.width, self.depth)
                # Checks if building overlaps with another building.
                if self.vrijstandMuren(building):
                    for b in self.buildings:
                        if self.findOverlap(building, b ):
                            overlap = True
                            break
                    if not overlap:
                        self.addBuilding(building)
##                        anim.updateAnimation(self.buildings, 0)
##                        print i, trials
                        break

##                print len(self.buildings)

    def randomPlacements2(self):
        self.buildings = []

        trials = 0

        noConfiguration = True

        while noConfiguration:
            self. buildings = []

            trials += 1

            #if trials % 1 == 0:
                #print trials

            overlap = False
            i = 0
            randomTries = 0
            while i < self.aantalhuizen and randomTries < 1000:
                if i < .15 * self.aantalhuizen:
                    ran_x = random.random() * (self.width )
                    ran_y = random.random() * (self.depth )
                    ran_angle = 0#random.randrange(0,360)
                    building = Maison(ran_x, ran_y, ran_angle, self.width, self.depth)
                elif i < .4 * self.aantalhuizen:
                    ran_x = random.random() * (self.width )
                    ran_y = random.random() * (self.depth )
                    ran_angle = 0#random.randrange(0,360)
                    building = Bungalow(ran_x, ran_y, ran_angle, self.width, self.depth)
                else:
                    ran_x = random.random() * (self.width )
                    ran_y = random.random() * (self.depth )
                    ran_angle = 0#random.randrange(0,360)
                    building = EengezinsWoning(ran_x, ran_y, ran_angle, self.width, self.depth)

                overlap = self.findOverlap2(building)

                if not overlap:
                    self.buildings.append(building)
                    i += 1
                    randomTries = 0
                else:
                    randomTries += 1

            noConfiguration = overlap
        #anim = GridVisualisation(self.width,self.depth, self.buildings, 0)
        #anim.emptyAnimation(self.buildings)
        #anim.updateAnimation(self.buildings, 0)
        #print trials


    # Initializes the grid with non overlapping buildings, at random positions.
    def updateGrid(self, simulations):

        self.randomPlacements()

        # Creates the Grid Animation
        anim = GridVisualisation(self.width, self.depth, self.buildings, 0)
        best_buildings = None
        best_prijsverb = 0

        # Starts the simulation for calculating the prijsverbetering for
        # a randomly generated grid of buildings. Returns the building set-up
        # with the highest prijsverbetering.
        for simulation in range(simulations):
            anim.emptyAnimation(self.buildings)
            self.randomPlacements()

            # Calculates the total prijsverb for all buildings.
            totalPrice = self.calcTotalPrice()
            totalprijsverb = totalPrice[0]
            distance = totalPrice[1]

            # Remembers the best prijsverb.
            if totalprijsverb > best_prijsverb:
                best_prijsverb = totalprijsverb
                best_buildings = self.buildings

            if simulation % 10 == 0:
                print 'We ran: ', simulation, 'simulations'

            anim.updateAnimation(self.buildings, totalprijsverb)

        anim = GridVisualisation(self.width, self.depth, best_buildings, best_prijsverb)
        writer.writerow([distance, best_prijsverb])
        # Shows the best prijsverb.
##        anim.emptyAnimation(self.buildings)
##        anim.updateAnimation(best_buildings, best_prijsverb)

        # Returns the best building setup + it's prijsverb + it's distance
        return best_buildings, int(best_prijsverb), distance

    def newRandomPos(self, building, previousPrice):
        currentX = building.x
        currentY = building.y

        newX = random.random() * grid.width
        newY = random.random() * grid.depth
        building.newPosition(newX, newY)

        # If position valid calculate the new price
        if not self.findOverlap2(building):
            newPrice = self.calcTotalPrice()[0]
        else:
            newPrice = 0

        # When the new configuration has a higher total price keep it, else
        # change back to previous configuration
        if newPrice <= previousPrice:
            building.newPosition(currentX, currentY)

        return newPrice

    def newRandomPosGA(self, building, grid):
        newX = random.random() * grid.width
        newY = random.random() * grid.depth
        building.newPosition(newX, newY)



    ##def randomTrans(self, building, previousPrice):
        ##ranDist = random.random()
        ##ranAngle = random.random() * 2 * math.pi

        ##dx = ranDist * math.cos(ranAngle)
        ##dy = ranDist * math.sin(ranAngle)
        ##building.translate(dx, dy)


    def newRandomPosSA(self, building, previousPrice, t):
        currentX = building.x
        currentY = building.y

        lifetime = 1000000

        newX = random.random() * grid.width
        newY = random.random() * grid.depth
        building.newPosition(newX, newY)

        # If position valid calculate the new price
        if not self.findOverlap2(building):
            newPrice = self.calcTotalPrice()[0]
        else:
            newPrice = 0

        # When the new configuration has a higher total price keep it, else
        # change back to previous configuration. There is a chance of accepting
        # worse state depending on iteration and price difference
        if newPrice <= previousPrice:
            accept = math.exp((newPrice - previousPrice) * t / lifetime)
            if random.random() > accept or newPrice == 0:
                building.newPosition(currentX, currentY)

        return newPrice

    def swapBuildings(self, building1, building2, previousPrice):
        currentX1 = building1.x
        currentY1 = building1.y
        currentX2 = building2.x
        currentY2 = building2.y

        self.swapBuilding(building1, building2)

        if not self.findOverlap2(building1) and not self.findOverlap2(building2):
            newPrice = self.calcTotalPrice()[0]
        else:
            newPrice = 0

        if newPrice <= previousPrice:
            self.swapBuilding(building1, building2)

        return newPrice

    def SAswapBuildings(self, building1, building2, previousPrice, t):
        currentX1 = building1.x
        currentY1 = building1.y
        currentX2 = building2.x
        currentY2 = building2.y

        lifetime = 100000

        self.swapBuilding(building1, building2)

        if not self.findOverlap2(building1) and not self.findOverlap2(building2):
            newPrice = self.calcTotalPrice()[0]
        else:
            newPrice = 0

        if newPrice <= previousPrice:
            accept = math.exp((newPrice - previousPrice) * t / lifetime)
            if random.random() > accept or newPrice == 0:
                self.swapBuilding(building1, building2)

        return newPrice

    def newRandomRot(self, ID, previousPrice):
        currentAngle = self.buildings[ID].angle

        newAngle = random.random() * 360
        self.buildings[ID].newAngle(newAngle)

        if not self.findOverlap2(self.buildings[ID]):
            newPrice = self.calcTotalPrice()[0]
        else:
            newPrice = 0

        if newPrice <= previousPrice:
            self.buildings[ID].newAngle(currentAngle)

        return newPrice

def rotatingRandomSample2(aantalhuizen, gridWidth, gridDepth, step):
    """
    Uses hill climber algorithm to find optimum rotation. Does not work properly
    """
    # Define grid and place sample
    grid = Grid(gridWidth, gridDepth, aantalhuizen)
    grid.randomPlacements2()

    newPrice = grid.calcTotalPrice()[0]
    previousPrice = newPrice
    priceDevelopment = [newPrice]

    anim = GridVisualisation(gridWidth, gridDepth, grid.buildings, 0)
    anim.emptyAnimation(grid.buildings)

    i = 0
    noChange = 0

    # When over 5000 iterations the change is less than 10 per iteration the
    # loop is terminated
    while noChange < 1000:

        # Makes animation for every 1000th iteration
        if i%100==0:
            print i, previousPrice
            anim.emptyAnimation(grid.buildings)
            anim.updateAnimation(grid.buildings, 0)

        # Choose random building
        buildingID = random.randrange(0, aantalhuizen)

        newPrice = grid.newRandomRot(buildingID, previousPrice)
        priceDif = newPrice - previousPrice

        if priceDif > 0:
            previousPrice = newPrice

        if priceDif < 10:
            noChange += 1
        else:
            noChange = 0

        priceDevelopment.append(previousPrice)
        i += 1

    iterations = [x for x in xrange(len(priceDevelopment))]
    plt.plot(iterations, priceDevelopment)
    plt.show()

    anim.emptyAnimation(grid.buildings)
    anim.updateAnimation(grid.buildings, 0)

    print 'angles'
    for building in grid.buildings:
        print building.angle

    return priceDevelopment

def translatingRandomSample2(aantalhuizen, gridWidth, gridDepth, step):
    """
    Uses hillclimber algorithm to find local optimal solution. Uses translation.
    """
    # Define grid and place sample
    grid = Grid(gridWidth, gridDepth, aantalhuizen)
    grid.randomPlacements2()

    newPrice = grid.calcTotalPrice()[0]
    previousPrice = newPrice
    priceDevelopment = [newPrice]

    anim = GridVisualisation(gridWidth, gridDepth, grid.buildings, 0)
    anim.emptyAnimation(grid.buildings)

    i = 0
    noChange = 0

    # When over 5000 iterations the change is less than 10 per iteration the
    # loop is terminated
    while noChange < 5000:

        # Makes animation for every 1000th iteration
        if i%1000==0:
            print i, previousPrice
            anim.emptyAnimation(grid.buildings)
            anim.updateAnimation(grid.buildings, 0)

        # Choose random building
        building = grid.buildings[random.randrange(0, aantalhuizen)]

        newPrice = grid.newRandomPos(building, previousPrice)

        priceDif = newPrice - previousPrice

        if priceDif > 0:
            previousPrice = newPrice

        if priceDif < 10:
            noChange += 1
        else:
            noChange = 0

        priceDevelopment.append(previousPrice)
        i += 1

    iterations = [x for x in xrange(len(priceDevelopment))]
    plt.plot(iterations, priceDevelopment)
    plt.show()

    anim.emptyAnimation(grid.buildings)
    anim.updateAnimation(grid.buildings, 0)

    return priceDevelopment


def SAtranslatingRandomSample2(aantalhuizen, gridWidth, gridDepth, step):
    """
    Uses simulated annealing algorithm to find local optimal solution. Uses translation.
    """
    # Define grid and place sample
    grid = Grid(gridWidth, gridDepth, aantalhuizen)
    grid.randomPlacements2()

    newPrice = grid.calcTotalPrice()[0]
    previousPrice = newPrice
    priceDevelopment = [newPrice]

    anim = GridVisualisation(gridWidth, gridDepth, grid.buildings, 0)
    anim.emptyAnimation(grid.buildings)

    i = 0
    noChange = 0

    # When over 5000 iterations the change is less than 10 per iteration the
    # loop is terminated
    while noChange < 5000:

        # Makes animation for every 1000th iteration
        if i%1000==0:
            print i, previousPrice
            anim.emptyAnimation(grid.buildings)
            anim.updateAnimation(grid.buildings, 0)

        # Choose random building
        building = grid.buildings[random.randrange(0, aantalhuizen)]

        newPrice = grid.newRandomPosSA(building, previousPrice, i)

        priceDif = newPrice - previousPrice

        if priceDif > 0:
            previousPrice = newPrice

        if priceDif < 10:
            noChange += 1
        else:
            noChange = 0

        priceDevelopment.append(previousPrice)
        i += 1

    iterations = [x for x in xrange(len(priceDevelopment))]
    plt.plot(iterations, priceDevelopment)
    plt.show()

    anim.emptyAnimation(grid.buildings)
    anim.updateAnimation(grid.buildings, 0)

    return priceDevelopment


def swappingRandomSample2(aantalhuizen, gridWidth, gridDepth, step):
    """
    Uses hillclimber algorithm to find local optimal solution. Uses swapping.
    """
    # Define grid and place sample
    grid = Grid(gridWidth, gridDepth, aantalhuizen)
    grid.randomPlacements2()

    newPrice = grid.calcTotalPrice()[0]
    previousPrice = newPrice
    priceDevelopment = [newPrice]

    anim = GridVisualisation(gridWidth, gridDepth, grid.buildings, 0)
    anim.emptyAnimation(grid.buildings)

    i = 0
    noChange = 0

    # When over 5000 iterations the change is less than 10 per iteration the
    # loop is terminated
    while noChange < 2000:

        # Makes animation for every 1000th iteration
        if i%1000==0:
            print i, previousPrice
            anim.emptyAnimation(grid.buildings)
            anim.updateAnimation(grid.buildings, 0)

        # Choose random building
        building1 = grid.buildings[random.randrange(0, aantalhuizen)]
        building2 = grid.buildings[random.randrange(0, aantalhuizen)]


        while building1 == building2:
            building2 = grid.buildings[random.randrange(0, aantalhuizen)]

        newPrice = grid.swapBuildings(building1, building2, previousPrice)

        priceDif = newPrice - previousPrice

        if priceDif > 0:
            previousPrice = newPrice

        if priceDif < 10:
            noChange += 1
        else:
            noChange = 0

        priceDevelopment.append(previousPrice)
        i += 1

    iterations = [x for x in xrange(len(priceDevelopment))]
    plt.plot(iterations, priceDevelopment)
    plt.show()

    anim.emptyAnimation(grid.buildings)
    anim.updateAnimation(grid.buildings, 0)

    return priceDevelopment


def SAswappingRandomSample2(aantalhuizen, gridWidth, gridDepth, step):
    """
    Uses hillclimber algorithm to find local optimal solution. Uses swapping.
    """
    # Define grid and place sample
    grid = Grid(gridWidth, gridDepth, aantalhuizen)
    grid.randomPlacements2()

    newPrice = grid.calcTotalPrice()[0]
    previousPrice = newPrice
    priceDevelopment = [newPrice]

    anim = GridVisualisation(gridWidth, gridDepth, grid.buildings, 0)
    anim.emptyAnimation(grid.buildings)

    i = 0
    noChange = 0

    # When over 5000 iterations the change is less than 10 per iteration the
    # loop is terminated
    while noChange < 2000:

        # Makes animation for every 1000th iteration
        if i%1000==0:
            print i, previousPrice
            anim.emptyAnimation(grid.buildings)
            anim.updateAnimation(grid.buildings, 0)

        # Choose random building
        building1 = grid.buildings[random.randrange(0, aantalhuizen)]
        building2 = grid.buildings[random.randrange(0, aantalhuizen)]

        while building1 == building2:
            building2 = grid.buildings[random.randrange(0, aantalhuizen)]

        newPrice = grid.SAswapBuildings(building1, building2, previousPrice, i)

        priceDif = newPrice - previousPrice

        if priceDif > 0:
            previousPrice = newPrice

        if priceDif < 10:
            noChange += 1
        else:
            noChange = 0

        priceDevelopment.append(previousPrice)
        i += 1

    iterations = [x for x in xrange(len(priceDevelopment))]
    plt.plot(iterations, priceDevelopment)
    plt.show()

    anim.emptyAnimation(grid.buildings)
    anim.updateAnimation(grid.buildings, 0)

    return priceDevelopment


def combinationRandomSample2(aantalhuizen, gridWidth, gridDepth, step):
    """
    Uses hillclimber algorithm to find local optimal solution. Uses swapping.
    """
    # Define grid and place sample
    grid = Grid(gridWidth, gridDepth, aantalhuizen)
    grid.randomPlacements2()

    newPrice = grid.calcTotalPrice()[0]
    previousPrice = newPrice
    priceDevelopment = [newPrice]

    anim = GridVisualisation(gridWidth, gridDepth, grid.buildings, 0)
    anim.emptyAnimation(grid.buildings)

    i = 0
    noChange = 0

    # When over 5000 iterations the change is less than 10 per iteration the
    # loop is terminated
    while noChange < 5000:

        # Makes animation for every 1000th iteration
        if i%1000==0:
            print i, previousPrice
            anim.emptyAnimation(grid.buildings)
            anim.updateAnimation(grid.buildings, 0)

        # There is chance 0.2 to swap random buildings and 0.8 to translate
        # building
        if random.random() > 0.8:
            # Choose random building
            building1 = grid.buildings[random.randrange(0, aantalhuizen)]
            building2 = grid.buildings[random.randrange(0, aantalhuizen)]

            while building1 == building2:
                building2 = grid.buildings[random.randrange(0, aantalhuizen)]

            newPrice = grid.swapBuildings(building1, building2, previousPrice)
        else:
            # Choose random building
            building = grid.buildings[random.randrange(0, aantalhuizen)]

            newPrice = grid.newRandomPos(building, previousPrice)

        priceDif = newPrice - previousPrice

        if priceDif > 0:
            previousPrice = newPrice

        if priceDif < 10:
            noChange += 1
        else:
            noChange = 0

        priceDevelopment.append(previousPrice)
        i += 1

    iterations = [x for x in xrange(len(priceDevelopment))]
    plt.plot(iterations, priceDevelopment)
    plt.show()

    anim.emptyAnimation(grid.buildings)
    anim.updateAnimation(grid.buildings, 0)

    return priceDevelopment


def combinationRandomSample2SA(aantalhuizen, gridWidth, gridDepth, step):
    """
    Uses hillclimber algorithm to find local optimal solution. Uses swapping.
    """
    # Define grid and place sample
    grid = Grid(gridWidth, gridDepth, aantalhuizen)
    grid.randomPlacements2()

    newPrice = grid.calcTotalPrice()[0]
    previousPrice = newPrice
    priceDevelopment = [newPrice]

    anim = GridVisualisation(gridWidth, gridDepth, grid.buildings, 0)
    anim.emptyAnimation(grid.buildings)

    i = 0
    noChange = 0

    # When over 5000 iterations the change is less than 10 per iteration the
    # loop is terminated
    while noChange < 5000:

        # Makes animation for every 1000th iteration
        if i%1000==0:
            print i, previousPrice
            anim.emptyAnimation(grid.buildings)
            anim.updateAnimation(grid.buildings, 0)

        # There is chance 0.2 to swap random buildings and 0.8 to translate
        # building
        if random.random() > 0.8:
            # Choose random building
            building1 = grid.buildings[random.randrange(0, aantalhuizen)]
            building2 = grid.buildings[random.randrange(0, aantalhuizen)]

            while building1 == building2:
                building2 = grid.buildings[random.randrange(0, aantalhuizen)]

            newPrice = grid.SAswapBuildings(building1, building2, previousPrice, i)
        else:
            # Choose random building
            building = grid.buildings[random.randrange(0, aantalhuizen)]

            newPrice = grid.newRandomPosSA(building, previousPrice, i)

        priceDif = newPrice - previousPrice

        if priceDif > 0:
            previousPrice = newPrice

        if priceDif < 10:
            noChange += 1
        else:
            noChange = 0

        priceDevelopment.append(previousPrice)
        i += 1

    iterations = [x for x in xrange(len(priceDevelopment))]
    #plt.plot(iterations, priceDevelopment)
    #plt.show()

    anim.emptyAnimation(grid.buildings)
    anim.updateAnimation(grid.buildings, 0)

    return priceDevelopment


def translatingRandomSample(aantalhuizen, gridWidth, gridDepth, step):
    grid = Grid(gridWidth, gridDepth, aantalhuizen)
    grid.randomPlacements2()

    previousPrice = -1
    totalPrice = grid.calcTotalPrice()[0]
    priceDevelopment = [totalPrice]

    anim = GridVisualisation(gridWidth, gridDepth, grid.buildings, 0)
    anim.emptyAnimation(grid.buildings)

    i = 0
    while totalPrice - previousPrice > 100:
        print i, totalPrice - previousPrice

        if i%1==0:
            anim.emptyAnimation(grid.buildings)
            anim.updateAnimation(grid.buildings, 0)
        previousPrice = grid.calcTotalPrice()[0]

        for building in grid.buildings:

            # Try to move to the right
            building.translate(step, 0)
            if not grid.findOverlap2(building):
                right = grid.calcTotalPrice()[0]
            else:
                right = -1

            # Move back and move one up
            building.translate(-step, step)
            if not grid.findOverlap2(building):
                up = grid.calcTotalPrice()[0]
            else:
                up = -1

            # Move back and move to the left
            building.translate(-step, -step)
            if not grid.findOverlap2(building):
                left = grid.calcTotalPrice()[0]
            else:
                left = -1

            # Move back and move down
            building.translate(step, -step)
            if not grid.findOverlap2(building):
                down = grid.calcTotalPrice()[0]
            else:
                down = -1

            building.translate(0, step)

            if right > totalPrice or up > totalPrice or left > totalPrice or down > totalPrice:
                if right > up and right > left and right > down:
                    building.translate(step, 0)
                elif up > left and up > down:
                    building.translate(0, step)
                elif left > down:
                    building.translate(-step, 0)
                else:
                    building.translate(0, -step)

                totalPrice = grid.calcTotalPrice()[0]
        priceDevelopment.append(totalPrice)
        i += 1

    iterations = [x for x in xrange(len(priceDevelopment))]
    plt.plot(iterations, priceDevelopment)
    plt.show()

    anim.emptyAnimation(grid.buildings)
    anim.updateAnimation(grid.buildings, 0)
    return priceDevelopment


def translatingRandomSample2(aantalhuizen, gridWidth, gridDepth, step):
    """
    Uses hillclimber algorithm to find local optimal solution. Uses translation.
    """
    # Define grid and place sample
    grid = Grid(gridWidth, gridDepth, aantalhuizen)
    grid.randomPlacements2()

    newPrice = grid.calcTotalPrice()[0]
    previousPrice = newPrice
    priceDevelopment = [newPrice]

    anim = GridVisualisation(gridWidth, gridDepth, grid.buildings, 0)
    anim.emptyAnimation(grid.buildings)

    i = 0
    noChange = 0

    # When over 5000 iterations the change is less than 10 per iteration the
    # loop is terminated
    while noChange < 5000:

        # Makes animation for every 1000th iteration
        if i%1000==0:
            print i, previousPrice
            anim.emptyAnimation(grid.buildings)
            anim.updateAnimation(grid.buildings, 0)

        # Choose random building
        building = grid.buildings[random.randrange(0, aantalhuizen)]

        newPrice = grid.newRandomPos(building, previousPrice)

        priceDif = newPrice - previousPrice

        if priceDif > 0:
            previousPrice = newPrice

        if priceDif < 10:
            noChange += 1
        else:
            noChange = 0

        priceDevelopment.append(previousPrice)
        i += 1

    iterations = [x for x in xrange(len(priceDevelopment))]
    plt.plot(iterations, priceDevelopment)
    plt.show()

    anim.emptyAnimation(grid.buildings)
    anim.updateAnimation(grid.buildings, 0)

    return priceDevelopment

def geneticAlgorithm(popsize, generations, aantalhuizen, gridWidth, gridDepth):


    gencount = 0

    while gencount < generations:

        # Creating starting situation.
        if gencount == 0:
            population = createStartPopulation(popsize, aantalhuizen, gridWidth, gridDepth)
            print "Starting evolution..."

        # Sort by value (high to low).
        population = sorted(population, key=itemgetter(1), reverse=True)

        # Select fittest 50%.
        population = population[:len(population) / 2]

        # Create new generation.
        population = createGeneration(popsize, population, aantalhuizen, gridWidth, gridDepth)

        gencount += 1
        print "This is generation", gencount


    population = sorted(population, key=itemgetter(1), reverse=True)
    anim = GridVisualisation(gridWidth, gridDepth, population[0][0].buildings, population[0][1])
    anim.emptyAnimation(population[0][0].buildings)

    print "########"
    print "Evolution finished"
    print "Final value:", population[0][1]

    return population


def createStartPopulation(popsize, aantalhuizen, gridWidth, gridDepth):
    # Create initial population.
    print 'Generating start state...'
    poplist = []

    while len(poplist) < popsize:
        manager = Manager()
        return_dict = manager.dict()
        jobs = []

        for i in range(processes):
            p = multiprocessing.Process(target=createRandomCandidate, args=(aantalhuizen, gridWidth, gridDepth,return_dict))
            jobs.append(p)
            p.start()

        for proc in jobs:
            proc.join()

        for i in list(return_dict.values()):
            templist = []
            templist.append(i)
            totalprice = i.calcTotalPrice()[0]
            templist.append(totalprice)
            poplist.append(templist)

        print len(poplist), "random candidates generated."

    return poplist

def createRandomCandidate(aantalhuizen, gridWidth, gridDepth, return_dict):
    grid = Grid(gridWidth, gridDepth, aantalhuizen)
    grid.randomPlacements2()
    return_dict[grid] = grid


def createGeneration(popsize, population, aantalhuizen, gridWidth, gridDepth):
    new_pop = []
    # Builds a single candidate every iteration.
    while len(new_pop) < popsize:
        manager = Manager()
        return_dict = manager.dict()
        jobs = []

        for i in range(processes):
            p = multiprocessing.Process(target=createCandidate, args=(population, aantalhuizen, gridWidth, gridDepth,return_dict))
            jobs.append(p)
            p.start()

        for proc in jobs:
            proc.join()

        for i in list(return_dict.values()):
            templist = []
            templist.append(i)
            totalprice = i.calcTotalPrice()[0]
            templist.append(totalprice)
            new_pop.append(templist)
        print len(new_pop), "candidates evolved."

    return new_pop


def createCandidate(population, aantalhuizen, gridWidth, gridDepth, return_dict):
    candidates = []

    # Pick three random candidates from population.
    for i in range(3):
        randomcandidate = random.choice(population)

        # Candidates can't be the same.
        if randomcandidate in candidates:
            randomcandidate = random.choice(population)

        candidates.append(randomcandidate[0])

#        buildingchoices = ['b', 'e', 'm']

    grid = Grid(gridWidth, gridDepth, aantalhuizen)

    #
    # Create crossover.
    # NOT WORKING (due to overlap).

    # Adds one kind of building from each selected candidate to new candidate.
#        for candidate in candidates:

#            selectchance = random.choice(buildingchoices)
#            buildingchoices.remove(selectchance)

#            for building in candidate.buildings:

#               if selectchance == 'b' and building.name[0] == selectchance:
#                    grid.addBuilding(building)
                # Check if placing is correct.
#                    checkHouse(grid, building)

#                elif selectchance == 'e' and building.name[0] == selectchance:
#                    grid.addBuilding(building)
                # Check if placing is correct.
#                    checkHouse(grid, building)

#                elif selectchance == 'm' and building.name[0] == selectchance:
#                    grid.addBuilding(building)
                # Check if placing is correct.
#                    checkHouse(grid, building)


    #
    # Create crossover.
    #


    count = 0
    for candidate in candidates:
        if count == 0:
            for building in candidate.buildings:
                if building.name[0] == 'm':
                    grid.addBuilding(building)
                    checkHouse(grid, building)

        elif count == 1:
            for building in candidate.buildings:
                if building.name[0] == 'b':
                    grid.addBuilding(building)
                    checkHouse(grid, building)

        else:
            for building in candidate.buildings:
                if building.name[0] == 'e':
                    grid.addBuilding(building)
                    checkHouse(grid, building)

        count += 1

    #
    # Mutate the crossover.
    #

    # Choose random amount of mutations.
    mutations = random.randint(1, aantalhuizen)

    for i in range(mutations):
        # Choose a random house to mutate.
        randombuilding = grid.buildings[random.randrange(0, aantalhuizen)]

        # Mutate the house by giving it a new position.
        grid.newRandomPosGA(randombuilding, grid)

        # Change position if it doesn't meet the constraints.
        checkHouse(grid, randombuilding)

    return_dict[grid] = grid


def checkHouse(grid, building):

    while grid.findOverlap2(building) == True:
        grid.newRandomPosGA(building, grid)

    return True


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
        return self.angle
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


#====================MAIN THREAD ===================================#
if __name__ == '__main__':

    processes = 100 # Amount of simultaneous processes. Shouldn't exceed popluatie.
    precision = 1.0
    generaties = 100
    populatie = 500
    geneticAlgorithm(populatie, generaties, 60, 120, 160)
##    E = EengezinsWoning(10, 10, 0, 100, 100)
##    B = Bungalow(50, 0, 0, 100, 100)
##    M = Maison(94.0001, 50, 180, 100, 100)
##
##    grid = Grid(100, 100, 5)
##    grid.addBuilding(E)
##    grid.addBuilding(B)
##    grid.addBuilding(M)
##
##    print 'Eengezinswoning', grid.calcPrice(E)
##    print 'Bungalow', grid.calcPrice(B)
##    print 'Maison', grid.calcPrice(M)
##    print 'Total', grid.calcTotalPrice()
##    print grid.findOverlap2(M)
##
#    precision = 1.0
    #grid = Grid(120, 160, 2)


    #a = translatingRandomSample2(20, 120, 160, 0.5)
    #b = SAtranslatingRandomSample2(60, 120, 160, 0.5)
    #b = rotatingRandomSample2(20, 120, 160, 0.5)
    #c = SAswappingRandomSample2(20, 120, 160, 0.5)
    #d = combinationRandomSample2(60, 120, 160, 0.5)
    #e = combinationRandomSample2SA(20, 120, 160, 0.5)
    #grid.randomPlacements2()

##    file = open('results.csv', 'wb+')
##    writer = csv.writer(file)
##    writer.writerow(['Distance', 'Prijs'])

##    precision = 1.0
##    grid = Grid(120., 160., 60)
##    simulations = 100000
##    grid.updateGrid(simulations)


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
    #
##    'distance', grid.findDistance(b1,b2)


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
