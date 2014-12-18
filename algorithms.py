# Authors: Patrick Vlaar, Casper Broertjes and Paul Schrijver.

# This software has been written to solve the 'AmstelHeage' case.
# http://wiki.phoib.net/wiki/index.php?title=Amstelhaege

# This code has been tested with both Python 2.7 and Pypy 2.4.0.
# For best performance it is recommended to use Pypy.
# http://pypy.org/download.html


from Tkinter import *
from operator import itemgetter
import matplotlib.pyplot as plt
import random
import math
import time
import csv
import os
import sys
import codecs
import errno
import cStringIO
import multiprocessing
from multiprocessing import Manager
import copy

class GridVisualisation:

    # Eengezinswoningen = red
    # Bungalows = blue
    # Maisons = black

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
        self.w.postscript(file="map.ps", colormode='color')

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
                  #self.w.create_text((x1+22,y1-23), fill="white", text="score", font=("arial",8))
            if i.name == 'eengezinswoning':
                  self.w.create_polygon(points,
                            fill='red')
                  #self.w.create_text((x1+17,y1-17), fill="white", text="score", font=("arial",8))
            if i.name == 'bungalow':
                  self.w.create_polygon(points,
                            fill='blue')
                  #self.w.create_text((x1+19,y1-17), fill="white", text="score", font=("arial",8))
        prijsverb = 'Score = ' + str(prijsverb)
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
        grid and if the building has a distance > vrijstand from the edges of the
        grid
        @param building: building for which overlap with other buildings is checked
        @return buildingOverlap: boolean (True: building has overlap with other building /
            False: building has no overlap with other building)
        """

        # Coordinates of all corners of the building
        corners = [(building.x, building.y)]
        corners.append((building.x - building.depth * math.sin(building.angle),
                   building.y + building.depth * math.cos(building.angle)))
        corners.append((building.x - building.depth * math.sin(building.angle) + building.width * math.cos(building.angle),
                   building.y + building.depth * math.cos(building.angle) + building.width * math.sin(building.angle)))
        corners.append((building.x + building.width * math.cos(building.angle),
                   building.y + building.width * math.sin(building.angle)))

        # Check whether the building has a distance larger than the mandatory vrijstand
        # from the edge of the grid
        for x, y in corners:
            if x < building.vrijstand or y < building.vrijstand:
                return True
            elif x > self.width - building.vrijstand or y > self.depth - building.vrijstand:
                return True

        i = 0
        buildingOverlap = False

        shortestDist = float('inf')  # Radius in which the closest building must lie

        # Find an overestimate of the shortest distance to the closest neighbor

        # The diagonal of the building and an overestimate of the diagonal of the
        # neighboring building must be added to the distance between the corners to
        # correct for possible rotations of buildings
        diagonal = math.sqrt(building.width**2 + building.depth**2) + math.sqrt(11**2 + 10.5**2)
        for neighbor in self.buildings:
            if neighbor != building:
                dist = math.sqrt((building.x - neighbor.x)**2 + (building.y - neighbor.y)**2)
                if dist < shortestDist:
                    shortestDist = dist
                    
        shortestDist += diagonal

        # Only check for overlap with buildings lying inside the shortestDist radius
        while i < len(self.buildings) and not buildingOverlap:
            dist = math.sqrt((building.x - self.buildings[i].x)**2 + (building.y - self.buildings[i].y)**2)

            if building != self.buildings[i] and dist <= shortestDist:
                buildingOverlap = self.findOverlap(building, self.buildings[i])
            i += 1

        return buildingOverlap
    

    def findOverlap(self, house1, house2):
        """ Checks whether house1 and house2 overlap and makes sure there is enough vrijstand
        @param house1: building for which overlap with house2 is checked
        @param house2: building for which overlap with house1 is checked
        @return: boolean (True: buildings overlap / False: buildings don't overlap)
        """
        # First check whether the houses have enough vrijstand
        if self.findDistance(house1, house2) >= house1.vrijstand and self.findDistance(house1, house2) >= house2.vrijstand:
            # findDistance might return False when two buildings lie inside each other, therefore
            # also check for overlap
            return self.cornerInBuilding(house1, house2) or self.cornerInBuilding(house2, house1)
        else:
            return True


    def cornerInBuilding(self, house1, house2):
        """
        Checks whether a corner of house2 lies inside house1
        @param house1: building for which it is checked whether a corner of house2 lies inside
        @param house2: building for which it is checked whether a corner lies in house1
        @return: boolean (True: Corner of house2 lies inside house1 / False: No corners of house2 lie inside house1)
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
        # Rotate all corners by an angle -house1.angle, so that we can work in the
        # frame where house1 has angle 0
        for corner in corners:
            # Change to polar coordinates
            r = math.sqrt((corner[0] - house1.x)**2 + (corner[1] - house1.y)**2)

            # Because the cosine is an even function, we need to add a minus sign
            # when house2 has a lower value for y
            try:
                sign = (corner[1] - house1.y) / math.fabs(corner[1] - house1.y)
            except ZeroDivisionError:
                sign = 1

            # When r = 0, the corner is at the origin, so the x and y coordinates
            # don't change
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
        """
        Searches for the shortest distances between building1 and building2.
        The minimal required distance between buildings is not subtracted.
        @param building1:
        @param building2:
        @return: distance between building1 and building2
        """

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
        """
        Swaps the positions of two buildings
        @param building1: building that swaps with second building
        @param building2: building that swaps with first building
        """
        x1 = building1.getX()
        y1 = building1.getY()

        x2 = building2.getX()
        y2 = building2.getY()

        building1.newPosition(x2, y2)
        building2.newPosition(x1, y1)


    def addBuilding(self, building):
        """
        Adds a building to the grid.
        @param building: building that becomes added to the grid
        """
        return self.buildings.append(building)


    def findShortestDist(self, building):
        """
        Finds shortest distance from building to another building. The new
        shortest dist and the corresponding neighbor with the shortest dist is
        stored in the building object.
        @param building: building for which shortest dist is calculated
        """

        # Choose a distance that overestimates any possible distance
        shortestDist = math.sqrt(self.width**2 + self.depth**2)

        maxDist = float('inf')  # Radius in which the closest building must lie

        # Find an overestimate of the shortest distance to the closest neighbor.
        
        # The diagonal of the building and an overestimate of the diagonal of the neighboring building
        # must be added to the distance between the corners to correct for possible rotations of buildings
        diagonal = math.sqrt(building.width**2 + building.depth**2) + math.sqrt(11**2 + 10.5**2)

        for neighbor in self.buildings:
            dist = math.sqrt((building.x - neighbor.x)**2 + (building.y - neighbor.y)**2)
            if dist < maxDist and building != neighbor:
                maxDist = dist

        # Add diagonal to distance between corners to account for rotation and orientation of
        # buildings
        maxDist += diagonal

        # Calculate the distance to all buildings within the maxDist radius
        for neighbor in self.buildings:
            dist = math.sqrt((building.x - neighbor.x)**2 + (building.y - neighbor.y)**2)

            if building != neighbor and dist < maxDist:
                newDist = self.findDistance(building, neighbor)
                if newDist < shortestDist:
                    shortestDist = newDist
                    shortestNeighbor = neighbor

        building.changeShortestDist(shortestDist, shortestNeighbor)

    def calcValue(self, building):
        """
        Calculate the price of a single house. Returns the price and the vrijstand
        @param building: building for which the price is calculated
        @return float(huisprijs): building price
        @return float(vrijstand): vrijstand of building
        """
        vrijstand = building.shortestDist
        extravrijstand = vrijstand - building.vrijstand
        
        prijsverb = building.percentage * extravrijstand + 1
        huisprijs = building.value * prijsverb

        return float(huisprijs), float(vrijstand)

    def calcTotalValue(self, buildingsMoved):
        """
        Calculates the total price for all buildings on the grid and the total
        vrijstand. Also updates shortest distances and shortest neighbors.
        @param buildingMoved: list of all moved buildings
        @return totalPrice: total price of the grid
        @return totalVrijstand: total vrijstand of the grid
        """
        totalPrice = 0
        totalVrijstand = 0

        
        noCheck = []
        # If the building had the moved building as shortest neighbor, the
        # shortest dist needs to be recalculated. This building can be omitted
        # in the next loop
        for building in self.buildings:
            if building.getShortestNeighbor() in buildingsMoved:
                self.findShortestDist(building)
                noCheck.append(building)

        # Searches buildings that have the moved building as closest neighbor now
        # and calculates the new shortest dist of the moved building
        for building in buildingsMoved:  
            for posNeighbor in self.buildings:
                if posNeighbor not in noCheck:
                    dist = self.findDistance(building, posNeighbor)

                    if dist < posNeighbor.shortestDist:
                        posNeighbor.changeShortestDist(dist, building)

            # Find the shortest dist for the moved bu
            self.findShortestDist(building)

        # Calculate the total price and vrijstand for all buildings and add them
        for building in self.buildings:
            priceAndVrijstand = self.calcValue(building)
            totalPrice += priceAndVrijstand[0]
            totalVrijstand += priceAndVrijstand[1]

        return totalPrice, totalVrijstand

    def randomPlacements(self):
        """
        Removes the old configuration (if present) and makes a new randomly filled grid
        """

        # Empty the current grid
        self.buildings = []

        trials = 0

        # Boolean variable indicating whether a configuration is found
        noConfiguration = True  

        while noConfiguration:
            self.buildings = []

            trials += 1

            overlap = False
            i = 0
            randomTries = 0

            # Starts adding Maisons to the grid, then Bungalows and finally Eengezinswoningen
            # to give an optimum chance of finding space to place the building. When a new building
            # does not fit initially, it tries to find a new random position for at most 1000 trials
            while i < self.aantalhuizen and randomTries < 1000:
                if i < .15 * self.aantalhuizen:
                    ran_x = random.random() * (self.width )
                    ran_y = random.random() * (self.depth )
                    ran_angle = random.randrange(0,360)
                    building = Maison(ran_x, ran_y, ran_angle, self.width, self.depth)
                elif i < .4 * self.aantalhuizen:
                    ran_x = random.random() * (self.width )
                    ran_y = random.random() * (self.depth )
                    ran_angle = random.randrange(0,360)
                    building = Bungalow(ran_x, ran_y, ran_angle, self.width, self.depth)
                else:
                    ran_x = random.random() * (self.width )
                    ran_y = random.random() * (self.depth )
                    ran_angle = random.randrange(0,360)
                    building = EengezinsWoning(ran_x, ran_y, ran_angle, self.width, self.depth)

                overlap = self.findOverlap2(building)

                if not overlap:
                    self.buildings.append(building)
                    i += 1
                    randomTries = 0
                else:
                    randomTries += 1

            # When no valid configuration is found noConfiguration stays True, otherwise it switches to False
            noConfiguration = overlap

        # Initialize values for shortestDist and shortestNeighbor for all buildings
        for building in self.buildings:
            self.findShortestDist(building)

    def newRandomPosGA(self, building, grid):
        """
        Assigns a random position to a building.
        :param building: Building.
        :param grid:  Map
        :return: none.
        """
        newX = random.random() * grid.width
        newY = random.random() * grid.depth
        building.newPosition(newX, newY)


    def newRandomPos(self, building, previousValue, optVar):
        """
        Places input building on new random position, determines whether this
        position is available and determines the new value. When this value is
        better than the old value it is kept, otherwise it is rejected.
        @param building: object that is placed at a random position
        @param previousValue: value determined in previous iteration
        @param optVar: variable that is used as value ('0' for price and '1'
        for vrijstand)
        @return newValue: new value of the configuration
        """
        currentX = building.getX()
        currentY = building.getY()

        # Store current shortest distance and closest neighbor for every object
        shortestDists = {}
        for i in self.buildings:
            shortestDists[i] = (i.shortestDist, i.shortestNeighbor)

        # Place building at a new random position
        newX = random.random() * self.width
        newY = random.random() * self.depth
        building.newPosition(newX, newY)

        # If position valid calculate the new value
        if not self.findOverlap2(building):
            newValue = self.calcTotalValue([building])[optVar]
        else:
            newValue = 0

        # When the new configuration has a higher total price keep it, else
        # change back to previous configuration
        if newValue <= previousValue:
            building.newPosition(currentX, currentY)

            # Change distance variables back to previous values
            for i in self.buildings:
                i.shortestDist = shortestDists[i][0]
                i.shortestNeighbor = shortestDists[i][1]

        return newValue


    def newRandomPosSA(self, building, previousValue, t, lifetime, optVar):
        """
        Places input building on new random position, determines whether this
        position is available and determines the new value. When this value is
        better than the old value it is kept. When the value is lower it has a
        probability to be kept. This probability declines with
        subsequent iterations.
        @param building: object that is placed at a random position
        @param previousValue: value determined in previous iteration
        @param t: current iteration
        @param lifetime: number of iterations over which probability declines
        with exp(-1)
        @param optVar: variable that is used as value ('0' for price and '1'
        for vrijstand)
        @return newValue: new value of the configuration
        """
        currentX = building.getX()
        currentY = building.getY()

        # Store current shortest distance and closest neighbor for every object
        shortestDists = {}
        for i in self.buildings:
            shortestDists[i] = (i.shortestDist, i.shortestNeighbor)

        # Place building at a new random position
        newX = random.random() * self.width
        newY = random.random() * self.depth
        building.newPosition(newX, newY)

        # If position valid calculate the new price
        if not self.findOverlap2(building):
            newValue = self.calcTotalValue([building])[optVar]
        else:
            newValue = 0

        # When the new configuration has a higher total price keep it, else
        # change back to previous configuration. There is a chance of accepting
        # worse state depending on the number of iterations and price difference
        if newValue <= previousValue:
            accept = math.exp((newValue - previousValue) * t / lifetime)
            if random.random() > accept or newValue == 0:
                building.newPosition(currentX, currentY)

                for i in self.buildings:
                    i.shortestDist = shortestDists[i][0]
                    i.shortestNeighbor = shortestDists[i][1]

                newValue = previousValue

        return newValue


    def swapBuildings(self, building1, building2, previousValue, optVar):
        """
        Interchanges the positions of two input buildings. Subsequently
        determines the new value. When this value is better than the old
        value it is kept, otherwise the old configuration is restored.
        @param building1: building that is interchanged with the second building
        @param building2: building that is interchanged with the first building
        @param previousValue: value determined in previous iteration
        @param optVar: variable that is used as value ('0' for price and '1'
        for vrijstand)
        @return newValue: new value of the configuration
        """
        currentX1 = building1.getX()
        currentY1 = building1.getY()
        currentX2 = building2.getX()
        currentY2 = building2.getY()

        # Store current shortest distance and closest neighbor for every object
        shortestDists = {}
        for i in self.buildings:
            shortestDists[i] = (i.shortestDist, i.shortestNeighbor)

        # Interchange the positions of the buildings
        self.swapBuilding(building1, building2)

        # If position valid calculate the new value
        if not self.findOverlap2(building1) and not self.findOverlap2(building2):
            newValue = self.calcTotalValue([building1, building2])[optVar]
        else:
            newValue = 0

        # When the new configuration has a higher total price keep it, otherwise
        # change back to previous configuration
        if newValue <= previousValue:
            self.swapBuilding(building1, building2)

            # Change distance variables back to previous values
            for i in self.buildings:
                i.shortestDist = shortestDists[i][0]
                i.shortestNeighbor = shortestDists[i][1]

        return newValue


    def swapBuildingsSA(self, building1, building2, previousValue, t, lifetime, optVar):
        """
        Interchanges the positions of two input buildings. Subsequently
        determines the new value. When this value is better than the old
        value it is kept. Otherwise the new configuration is kept with a
        certain probability.
        @param building1: building that is interchanged with the second building
        @param building2: building that is interchanged with the first building
        @param previousValue: value determined in previous iteration
        @param t: current iteration
        @param lifetime: number of iterations over which probability declines
        with exp(-1)
        @param optVar: variable that is used as value ('0' for price and '1'
        for vrijstand)
        @return newValue: new value of the configuration
        """

        currentX1 = building1.getX()
        currentY1 = building1.getY()
        currentX2 = building2.getX()
        currentY2 = building2.getY()

        # Store current shortest distance and closest neighbor for every object
        shortestDists = {}
        for i in self.buildings:
            shortestDists[i] = (i.shortestDist, i.shortestNeighbor)

        # Interchange the positions of the buildings
        self.swapBuilding(building1, building2)

        # If position valid calculate the new value
        if not self.findOverlap2(building1) and not self.findOverlap2(building2):
            newValue = self.calcTotalValue([building1, building2])[optVar]
        else:
            newValue = 0


        # When the new configuration has a higher total price keep it, else
        # change back to previous configuration. There is a chance of accepting
        # worse state depending on the number of iterations and price difference
        if newValue <= previousValue:
            accept = math.exp((newValue - previousValue) * t / lifetime)
            if random.random() > accept or newValue == 0:
                self.swapBuilding(building1, building2)

                # Change distance variables back to previous values
                for i in self.buildings:
                    i.shortestDist = shortestDists[i][0]
                    i.shortestNeighbor = shortestDists[i][1]

                newValue = previousValue

        return newValue


    def newRandomRot(self, building, previousValue, optVar):
        """
        Gives input building a new random angle, determines whether the position
        is available and determines the new value. When this value is better than
        the old value it is kept, otherwise it is rejected.
        @param building: object that is placed at a random position
        @param previousValue: value determined in previous iteration
        @param optVar: variable that is used as value ('0' for price and '1'
        for vrijstand)
        @return newValue: new value of the configuration
        """

        currentAngle = building.getAngle()

        # Store current shortest distance and closest neighbor for every object
        shortestDists = {}
        for i in self.buildings:
            shortestDists[i] = (i.shortestDist, i.shortestNeighbor)

        newAngle = random.random() * 360

        # Give the building a new random angle
        building.newAngle(newAngle)

        # If position valid calculate the new value
        if not self.findOverlap2(building):
            newValue = self.calcTotalValue([building])[optVar]
        else:
            newValue = 0

        # When the new configuration has a higher total price keep it, else
        # change back to previous configuration.
        if newValue <= previousValue:
            building.newAngle(currentAngle)

            # Change distance variables back to previous values
            for i in self.buildings:
                i.shortestDist = shortestDists[i][0]
                i.shortestNeighbor = shortestDists[i][1]

        return newValue


    def newRandomRotSA(self, building, previousValue, t, lifetime, optVar):
        """
        Gives input building a new random angle, determines whether the position
        is available and determines the new value. When this value is better than
        the old value it is kept. Otherwise it is accepted with a certain
        probability.
        @param building: object that is placed at a random position
        @param previousValue: value determined in previous iteration
        @param t: current iteration
        @param lifetime: number of iterations over which probability declines
        with exp(-1)
        @param optVar: variable that is used as value ('0' for price and '1'
        for vrijstand)
        @return newValue: new value of the configuration
        """

        currentAngle = building.getAngle()

        # Store current shortest distance and closest neighbor for every object
        shortestDists = {}
        for i in self.buildings:
            shortestDists[i] = (i.shortestDist, i.shortestNeighbor)

        newAngle = random.random() * 360

        # Give the building a new random angle
        building.newAngle(newAngle)

        # If position valid calculate the new value
        if not self.findOverlap2(building):
            newValue = self.calcTotalValue([building])[optVar]
        else:
            newValue = 0

        # When the new configuration has a higher total price keep it, else
        # change back to previous configuration. There is a change of accepting
        # worse state depending on the number of iterations and price difference
        if newValue <= previousValue:
            accept = math.exp((newValue - previousValue) * t / lifetime)
            if random.random() > accept or newValue == 0:
                building.newAngle(currentAngle)

                # Change distance variables back to previous values
                for i in self.buildings:
                    i.shortestDist = shortestDists[i][0]
                    i.shortestNeighbor = shortestDists[i][1]

                newValue = previousValue

        return newValue

    def newTranslatedPosSA(self, building, previousValue, t, lifetime, optVar):
        currentX = building.getX()
        currentY = building.getY()

        # Store current shortest distance and closest neighbor for every object
        shortestDists = {}
        for i in self.buildings:
            shortestDists[i] = (i.shortestDist, i.shortestNeighbor)

        distance = random.random() * 15
        angle = random.randrange(0, 360)
        ##if t%100==0:
            ##print 'DISTANCE', distance


        newY = currentY + (math.sin(angle) * distance)
        newX = currentX + (float(1.3) / math.cos(angle))

        building.newPosition(newX, newY)

         # If position valid calculate the new price
        if not self.findOverlap2(building):
            newValue = self.calcTotalValue([building])[optVar]
        else:
            newValue = 0

        # When the new configuration has a higher total price keep it, else
        # change back to previous configuration. There is a chance of accepting
        # worse state depending on iteration and price difference
        if newValue <= previousValue:
            accept = math.exp((newValue - previousValue) * t / lifetime)
            if random.random() > accept or newValue == 0:
                building.newPosition(currentX, currentY)

                # Change distance variables back to previous values
                for i in self.buildings:
                    i.shortestDist = shortestDists[i][0]
                    i.shortestNeighbor = shortestDists[i][1]

                newValue = previousValue

        return newValue

    def newTranslatedPos(self, building, previousValue, optVar):
        currentX = building.getX()
        currentY = building.getY()

        # Store current shortest distance and closest neighbor for every object
        shortestDists = {}
        for i in self.buildings:
            shortestDists[i] = (i.shortestDist, i.shortestNeighbor)

        distance = random.random() * 25
        angle = random.randrange(0, 360)

        newY = currentY + (math.sin(angle) * distance)
        newX = currentX + (float(1.3) / math.cos(angle))

        building.newPosition(newX, newY)

         # If position valid calculate the new price
        if not self.findOverlap2(building):
            newValue = self.calcTotalValue([building])[optVar]
        else:
            newValue = 0

        # When the new configuration has a higher total price keep it, else
        # change back to previous configuration
        if newValue <= previousValue:
            building.newPosition(currentX, currentY)

            # Change distance variables back to previous values
            for i in self.buildings:
                i.shortestDist = shortestDists[i][0]
                i.shortestNeighbor = shortestDists[i][1]

        return newValue


def rotatingRandomSample(aantalhuizen, gridWidth, gridDepth, optVar, noChangeParam, valueDifParam):
    """
    Uses hill climber algorithm to find optimum rotation.
    @param optVar: variable that is used as value ('0' for price and '1'
        for vrijstand)
    """
    # Define grid and place sample
    grid = Grid(gridWidth, gridDepth, aantalhuizen)
    grid.randomPlacements()

    newValue = grid.calcTotalValue([])[optVar]
    previousValue = newValue
    #valueDevelopment = [newValue]

    #anim = GridVisualisation(gridWidth, gridDepth, grid.buildings, 0)
    #anim.emptyAnimation(grid.buildings)

    i = 0
    noChange = 0

    # When over 5000 iterations the change is less than 10 per iteration the
    # loop is terminated
    while noChange < noChangeParam:

        # Makes animation for every 1000th iteration
        #if i%100==0:
            #print i, previousValue
            #anim.emptyAnimation(grid.buildings)
            #anim.updateAnimation(grid.buildings, 0)

        # Choose random building
        building = grid.buildings[random.randrange(0, aantalhuizen)]

        newValue = grid.newRandomRot(building, previousValue, optVar)
        valueDif = newValue - previousValue

        if valueDif > 0:
            previousValue = newValue

        if valueDif < valueDifParam:
            noChange += 1
        else:
            noChange = 0

        #valueDevelopment.append(previousValue)
        i += 1

    #iterations = [x for x in xrange(len(valueDevelopment))]
    #plt.plot(iterations, valueDevelopment)
    #plt.show()

    #anim.emptyAnimation(grid.buildings)
    #anim.updateAnimation(grid.buildings, 0)

    return grid.calcTotalValue([]) + (grid,)


def rotatingRandomSampleSA(aantalhuizen, gridWidth, gridDepth, lifetime, optVar, noChangeParam, valueDifParam):
    """
    Uses hill climber algorithm to find optimum rotation.
    @param optVar: variable that is used as value ('0' for price and '1'
        for vrijstand)
    """
    # Define grid and place sample
    grid = Grid(gridWidth, gridDepth, aantalhuizen)
    grid.randomPlacements()

    newValue = grid.calcTotalValue([])[optVar]
    previousValue = newValue
    #valueDevelopment = [newValue]

    #anim = GridVisualisation(gridWidth, gridDepth, grid.buildings, 0)
    #anim.emptyAnimation(grid.buildings)

    i = 0
    noChange = 0

    # When over 5000 iterations the change is less than 10 per iteration the
    # loop is terminated
    while noChange < noChangeParam:

        # Makes animation for every 1000th iteration
        #if i%100==0:
            #print i, previousValue
            #anim.emptyAnimation(grid.buildings)
            #anim.updateAnimation(grid.buildings, 0)

        # Choose random building
        building = grid.buildings[random.randrange(0, aantalhuizen)]

        newValue = grid.newRandomRotSA(building, previousValue, i, lifetime, optVar)
        valueDif = newValue - previousValue

        previousValue = newValue

        if valueDif < valueDifParam:
            noChange += 1
        else:
            noChange = 0

        #valueDevelopment.append(previousValue)
        i += 1

    #iterations = [x for x in xrange(len(valueDevelopment))]
    #plt.plot(iterations, valueDevelopment)
    #plt.show()

    #anim.emptyAnimation(grid.buildings)
    #anim.updateAnimation(grid.buildings, 0)

    return grid.calcTotalValue([]) + (grid,)

def translatingRandomSample2(aantalhuizen, gridWidth, gridDepth, optVar, noChangeParam, valueDifParam):
    """
    Uses hillclimber algorithm to find local optimal solution. Uses translation.
    """
    # Define grid and place sample
    grid = Grid(gridWidth, gridDepth, aantalhuizen)
    grid.randomPlacements()

    newValue = grid.calcTotalValue([])[optVar]
    previousValue = newValue
    #valueDevelopment = [newValue]

    #anim = GridVisualisation(gridWidth, gridDepth, grid.buildings, 0)
    #anim.emptyAnimation(grid.buildings)

    i = 0
    noChange = 0

    # When over 5000 iterations the change is less than 10 per iteration the
    # loop is terminated
    while noChange < noChangeParam:

        # Makes animation for every 1000th iteration
        #if i%1000==0:
            #print i, previousValue
            #anim.emptyAnimation(grid.buildings)
            #anim.updateAnimation(grid.buildings, 0)

        # Choose random building
        building = grid.buildings[random.randrange(0, aantalhuizen)]

        newValue = grid.newRandomPos(building, previousValue, optVar)

        valueDif = newValue - previousValue

        if valueDif > 0:
            previousValue = newValue

        if valueDif < valueDifParam:
            noChange += 1
        else:
            noChange = 0

        #valueDevelopment.append(previousValue)
        i += 1

    #iterations = [x for x in xrange(len(valueDevelopment))]
    #plt.plot(iterations, valueDevelopment)
    #plt.show()

    #anim.emptyAnimation(grid.buildings)
    #anim.updateAnimation(grid.buildings, 0)

    return grid.calcTotalValue([]) + (grid,)


def SAtranslatingRandomSample2(aantalhuizen, gridWidth, gridDepth, optVar, lifetime, noChangeParam, valueDifParam):
    """
    Uses simulated annealing algorithm to find local optimal solution. Uses translation.
    """
    # Define grid and place sample
    grid = Grid(gridWidth, gridDepth, aantalhuizen)
    grid.randomPlacements()

    newValue = grid.calcTotalValue([])[optVar]
    previousValue = newValue
    #valueDevelopment = [newValue]    

    #anim = GridVisualisation(gridWidth, gridDepth, grid.buildings, 0)
    #anim.emptyAnimation(grid.buildings)

    i = 0
    noChange = 0

    # When over 5000 iterations the change is less than 10 per iteration the
    # loop is terminated
    while noChange < noChangeParam:

        # Makes animation for every 1000th iteration
        #if i%1000==0:
            #print i, previousValue
            #anim.emptyAnimation(grid.buildings)
            #anim.updateAnimation(grid.buildings, 0)

        # Choose random building
        building = grid.buildings[random.randrange(0, aantalhuizen)]

        newValue = grid.newRandomPosSA(building, previousValue, i, lifetime, optVar)

        valueDif = newValue - previousValue

        previousValue = newValue

        if valueDif < valueDifParam:
            noChange += 1
        else:
            noChange = 0

        #valueDevelopment.append(previousValue)
        i += 1

    #iterations = [x for x in xrange(len(valueDevelopment))]
    #plt.plot(iterations, valueDevelopment)
    #plt.show()

    #anim.emptyAnimation(grid.buildings)
    #anim.updateAnimation(grid.buildings, 0)

    return grid.calcTotalValue([]) + (grid,)


def swappingRandomSample2(aantalhuizen, gridWidth, gridDepth, optVar, noChangeParam, valueDifParam):
    """
    Uses hillclimber algorithm to find local optimal solution. Uses swapping.
    """
    # Define grid and place sample
    grid = Grid(gridWidth, gridDepth, aantalhuizen)
    grid.randomPlacements()

    newValue = grid.calcTotalValue([])[optVar]
    previousValue = newValue
    #valueDevelopment = [newValue]

    #anim = GridVisualisation(gridWidth, gridDepth, grid.buildings, 0)
    #anim.emptyAnimation(grid.buildings)

    i = 0
    noChange = 0

    # When over 5000 iterations the change is less than 10 per iteration the
    # loop is terminated
    while noChange < noChangeParam:

        # Makes animation for every 1000th iteration
        #if i%1000==0:
            #print i, previousValue
            #anim.emptyAnimation(grid.buildings)
            #anim.updateAnimation(grid.buildings, 0)

        # Choose random building
        building1 = grid.buildings[random.randrange(0, aantalhuizen)]
        building2 = grid.buildings[random.randrange(0, aantalhuizen)]


        while building1 == building2:
            building2 = grid.buildings[random.randrange(0, aantalhuizen)]

        newValue = grid.swapBuildings(building1, building2, previousValue, optVar)

        valueDif = newValue - previousValue

        if valueDif > 0:
            previousValue = newValue

        if valueDif < valueDifParam:
            noChange += 1
        else:
            noChange = 0

        #valueDevelopment.append(previousValue)
        i += 1

    #iterations = [x for x in xrange(len(valueDevelopment))]
    #plt.plot(iterations, valueDevelopment)
    #plt.show()

    #anim.emptyAnimation(grid.buildings)
    #anim.updateAnimation(grid.buildings, 0)

    return grid.calcTotalValue([]) + (grid,)

def translatingRandomSample3(aantalhuizen, gridWidth, gridDepth, optVar, noChangeParam, valueDifParam):
    """
    Uses hillclimber algorithm to find local optimal solution. Uses translation.
    """
    # Define grid and place sample
    grid = Grid(gridWidth, gridDepth, aantalhuizen)
    grid.randomPlacements()

    newValue = grid.calcTotalValue([])[optVar]
    previousValue = newValue
    #valueDevelopment = [newValue]

    #anim = GridVisualisation(gridWidth, gridDepth, grid.buildings, 0)
    #anim.emptyAnimation(grid.buildings)

    i = 0
    noChange = 0

    # When over 5000 iterations the change is less than 10 per iteration the
    # loop is terminated
    while noChange < noChangeParam:

        # Makes animation for every 1000th iteration
        if i%1000==0:
            print i, previousValue
            anim.emptyAnimation(grid.buildings)
            anim.updateAnimation(grid.buildings, 0)

        # Choose random building
        building = grid.buildings[random.randrange(0, aantalhuizen)]
        newValue = grid.newTranslatedPos(building, previousValue, optVar)

        valueDif = newValue - previousValue

        if valueDif > 0:
            previousValue = newValue

        if valueDif < valueDifParam:
            noChange += 1
        else:
            noChange = 0

        #valueDevelopment.append(previousValue)
        i += 1

    #iterations = [x for x in xrange(len(valueDevelopment))]
    #plt.plot(iterations, valueDevelopment)
    #plt.show()

    #anim.emptyAnimation(grid.buildings)
    #anim.updateAnimation(grid.buildings, 0)

    return grid.calcTotalValue([]) + (grid,)

def SAtranslatingRandomSample3(aantalhuizen, gridWidth, gridDepth, optVar, lifetime, noChangeParam, valueDifParam):
    """
    Uses simulated annealing algorithm to find local optimal solution. Uses translation.
    """
    # Define grid and place sample
    grid = Grid(gridWidth, gridDepth, aantalhuizen)
    grid.randomPlacements()

    newValue = grid.calcTotalValue([])[optVar]
    previousValue = newValue
    valueDevelopment = [newValue]    

    anim = GridVisualisation(gridWidth, gridDepth, grid.buildings, 0)
    anim.emptyAnimation(grid.buildings)

    i = 0
    noChange = 0

    # When over 5000 iterations the change is less than 10 per iteration the
    # loop is terminated
    while noChange < noChangeParam:

        # Makes animation for every 1000th iteration
        if i%1000==0:
            print i, previousValue
            anim.emptyAnimation(grid.buildings)
            anim.updateAnimation(grid.buildings, 0)

        # Choose random building
        building = grid.buildings[random.randrange(0, aantalhuizen)]
        newValue = grid.newTranslatedPosSA(building, previousValue, i, lifetime, optVar)

        valueDif = newValue - previousValue

        previousValue = newValue

        if valueDif < valueDifParam:
            noChange += 1
        else:
            noChange = 0

        valueDevelopment.append(previousValue)
        i += 1

    iterations = [x for x in xrange(len(valueDevelopment))]
    plt.plot(iterations, valueDevelopment)
    plt.show()

    anim.emptyAnimation(grid.buildings)
    anim.updateAnimation(grid.buildings, 0)

    return grid.calcTotalValue([]) + (grid,)

def SAswappingRandomSample2(aantalhuizen, gridWidth, gridDepth, lifetime, optVar, noChangeParam, valueDifParam):
    """
    Uses hillclimber algorithm to find local optimal solution. Uses swapping.
    """
    # Define grid and place sample
    grid = Grid(gridWidth, gridDepth, aantalhuizen)
    grid.randomPlacements()

    newValue = grid.calcTotalValue([])[optVar]
    previousValue = newValue
    #valueDevelopment = [newValue]

    #anim = GridVisualisation(gridWidth, gridDepth, grid.buildings, 0)
    #anim.emptyAnimation(grid.buildings)

    i = 0
    noChange = 0

    # When over 5000 iterations the change is less than 10 per iteration the
    # loop is terminated
    while noChange < noChangeParam:

        # Makes animation for every 1000th iteration
        #if i%1000==0:
            #print i, previousValue
            #anim.emptyAnimation(grid.buildings)
            #anim.updateAnimation(grid.buildings, 0)

        # Choose random building
        building1 = grid.buildings[random.randrange(0, aantalhuizen)]
        building2 = grid.buildings[random.randrange(0, aantalhuizen)]

        while building1 == building2:
            building2 = grid.buildings[random.randrange(0, aantalhuizen)]

        newValue = grid.swapBuildingsSA(building1, building2, previousValue, i, lifetime, optVar)

        valueDif = newValue - previousValue

        previousValue = newValue

        if valueDif < valueDifParam:
            noChange += 1
        else:
            noChange = 0

        #valueDevelopment.append(previousValue)
        i += 1

    #iterations = [x for x in xrange(len(valueDevelopment))]
    #plt.plot(iterations, valueDevelopment)
    #plt.show()

    #anim.emptyAnimation(grid.buildings)
    #anim.updateAnimation(grid.buildings, 0)

    return grid.calcTotalValue([]) + (grid,)


def combinationRandomSample2(aantalhuizen, gridWidth, gridDepth, optVar, noChangeParam, valueDifParam):
    """
    Uses hillclimber algorithm to find local optimal solution. Uses swapping.
    """
    # Define grid and place sample
    grid = Grid(gridWidth, gridDepth, aantalhuizen)
    grid.randomPlacements()

    newValue = grid.calcTotalValue([])[optVar]
    previousValue = newValue
    #valueDevelopment = [newValue]

    anim = GridVisualisation(gridWidth, gridDepth, grid.buildings, 0)
    anim.emptyAnimation(grid.buildings)

    i = 0
    noChange = 0

    # When over 5000 iterations the change is less than 10 per iteration the
    # loop is terminated
    while noChange < noChangeParam:

        # Makes animation for every 1000th iteration
        if i%1000==0:
            print i, previousValue
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

            newValue = grid.swapBuildings(building1, building2, previousValue, optVar)
        else:
            # Choose random building
            building = grid.buildings[random.randrange(0, aantalhuizen)]

            newValue = grid.newTranslatedPos(building, previousValue, optVar)

        valueDif = newValue - previousValue

        if valueDif > 0:
            previousValue = newValue

        if valueDif < valueDifParam:
            noChange += 1
        else:
            noChange = 0

        #valueDevelopment.append(previousValue)
        i += 1

    #iterations = [x for x in xrange(len(valueDevelopment))]
    #plt.plot(iterations, valueDevelopment)
    #plt.show()

    #anim.emptyAnimation(grid.buildings)
    #anim.updateAnimation(grid.buildings, 0)

    return grid.calcTotalValue([]) + (grid,)


def combinationRandomSample2SA(aantalhuizen, gridWidth, gridDepth, lifetimeNewPos, lifetimeSwap, optVar, noChangeParam, valueDifParam):
    """
    Uses hillclimber algorithm to find local optimal solution. Uses swapping.
    """
    # Define grid and place sample
    grid = Grid(gridWidth, gridDepth, aantalhuizen)
    grid.randomPlacements()

    newValue = grid.calcTotalValue([])[optVar]
    previousValue = newValue
    valueDevelopment = [newValue]

    anim = GridVisualisation(gridWidth, gridDepth, grid.buildings, 0)
    anim.emptyAnimation(grid.buildings)

    i = 0
    noChange = 0

    # When over 5000 iterations the change is less than 10 per iteration the
    # loop is terminated
    while noChange < noChangeParam:

        # Makes animation for every 1000th iteration
        if i%1000==0:
            print i, previousValue
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

            newValue = grid.swapBuildingsSA(building1, building2, previousValue, i, lifetimeSwap, optVar)

        else:
            # Choose random building
            building = grid.buildings[random.randrange(0, aantalhuizen)]

            newValue = grid.newTranslatedPosSA(building, previousValue, i, lifetimeNewPos, optVar)

        valueDif = newValue - previousValue

        previousValue = newValue

        if valueDif < valueDifParam:
            noChange += 1
        else:
            noChange = 0

        #valueDevelopment.append(previousValue)
        i += 1

    #iterations = [x for x in xrange(len(valueDevelopment))]
    #plt.plot(iterations, valueDevelopment)
    #plt.show()

    #anim.emptyAnimation(grid.buildings)
    #anim.updateAnimation(grid.buildings, 0)

    return grid.calcTotalValue([])


def translatingRandomSample(aantalhuizen, gridWidth, gridDepth, step, optVar, valueDifParam):
    grid = Grid(gridWidth, gridDepth, aantalhuizen)
    grid.randomPlacements()

    previousValue = -1
    totalPrice = grid.calcTotalValue([])[optVar]
    #valueDevelopment = [totalPrice]

    #anim = GridVisualisation(gridWidth, gridDepth, grid.buildings, 0)
    #anim.emptyAnimation(grid.buildings)

    i = 0
    while totalPrice - previousValue > valueDifParam:
        #print i, totalPrice - previousValue

        #if i%1==0:
            #anim.emptyAnimation(grid.buildings)
            #anim.updateAnimation(grid.buildings, 0)
        previousValue = grid.calcTotalValue()[optVar]

        for building in grid.buildings:

            # Try to move to the right
            building.translate(step, 0)
            if not grid.findOverlap2(building):
                right = grid.calcTotalValue()[optVar]
            else:
                right = -1

            # Move back and move one up
            building.translate(-step, step)
            if not grid.findOverlap2(building):
                up = grid.calcTotalValue()[optVar]
            else:
                up = -1

            # Move back and move to the left
            building.translate(-step, -step)
            if not grid.findOverlap2(building):
                left = grid.calcTotalValue()[optVar]
            else:
                left = -1

            # Move back and move down
            building.translate(step, -step)
            if not grid.findOverlap2(building):
                down = grid.calcTotalValue()[optVar]
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

                totalPrice = grid.calcTotalValue()[optVar]
        #valueDevelopment.append(totalPrice)
        i += 1

    #iterations = [x for x in xrange(len(valueDevelopment))]
    #plt.plot(iterations, valueDevelopment)
    #plt.show()

    #anim.emptyAnimation(grid.buildings)
    #anim.updateAnimation(grid.buildings, 0)
    return grid.calcTotalValue([])




def geneticAlgorithm(popsize, generations, aantalhuizen, gridWidth, gridDepth, score):
    """
    This function uses a genetic algorithm to produce an 'optimized' map.
    :param int popsize: Size of population.
    :param int generations: Amount of generations that should be generated.
    :param int aantalhuizen: Amount of buildings in a candidate
    :param int gridWidth: Width of the candidate.
    :param int gridDepth: Depth of candidate
    :param str score: Kind of score that should be optimized.
            'v' = optimal vrijstand. 'p' = optimal price.
    :return: List containing final population, sorted on score from high to low.
    """

    filename = score + str(aantalhuizen)
    gencount = 0

    while gencount < generations:

        # Create starting situation.
        if gencount == 0:
            population = createStartPopulation(popsize, aantalhuizen, gridWidth, gridDepth, score)
            print "Starting evolution..."

        # Sort population by fitness (score from high to low).
        population = sorted(population, key=itemgetter(1), reverse=True)

        # Select fittest 50%.
        population = population[:len(population) / 2]

        # Create new generation.
        population = createGeneration(popsize, population, aantalhuizen, gridWidth, gridDepth, score)

        gencount += 1
        print "This is generation", gencount

    # Sort final population.
    population = sorted(population, key=itemgetter(1), reverse=True)

    # Visualize best candidate.
    GridVisualisation(gridWidth, gridDepth, population[0][0].buildings, population[0][1])

    # Store best candidate.
    storeMap(population[0][0], filename)

    print "########"
    print "Evolution finished"
    print "Final value:", population[0][1]

    return population


def createStartPopulation(popsize, aantalhuizen, gridWidth, gridDepth, score):
    """
    Creates initial population.
    :param int popsize: Size of population.
    :param int aantalhuizen: Amount of buildings in a candidate
    :param int gridWidth: Width of the candidate.
    :param int gridDepth: Depth of candidate
    :param str score: Kind of score that should be optimized.
            'v' = optimal vrijstand. 'p' = optimal price.
    :return: list containing population
    """

    print 'Generating start state...'
    poplist = []

    while len(poplist) < popsize:

        grid = createRandomCandidate(aantalhuizen, gridWidth, gridDepth)

        templist = []
        templist.append(grid)

        if score == 'p':
            totalscore = grid.calcTotalValue(grid.buildings)[0]
        elif score == 'v':
            totalscore = grid.calcTotalValue(grid.buildings)[1]

        templist.append(totalscore)
        poplist.append(templist)

        if len(poplist) % 100 == 0:
            print len(poplist), "random candidates generated."
    return poplist

def createRandomCandidate(aantalhuizen, gridWidth, gridDepth):
    """
    Creates a single random candidate.
    :param int aantalhuizen: Amount of buildings in a candidate
    :param int gridWidth: Width of the candidate.
    :param int gridDepth: Depth of candidate
    :return: grid, contains a random candidate.
    """
    grid = Grid(gridWidth, gridDepth, aantalhuizen)
    grid.randomPlacements()
    return grid

def createGeneration(popsize, population, aantalhuizen, gridWidth, gridDepth, score):
    """
    Creates a generation of the size that was chosen as initial population size.
    :param int popsize: Size of population.
    :param list population: List containing candidates.
    :param int aantalhuizen: Amount of buildings in a candidate
    :param int gridWidth: Width of the candidate.
    :param int gridDepth: Depth of candidate
    :param str score: Kind of score that should be optimized.
            'v' = optimal vrijstand. 'p' = optimal price.
    :return: returns a list containing new population
    """
    new_pop = []
    # Builds a single candidate every iteration.
    while len(new_pop) < popsize:
        grid = createCandidate(population, aantalhuizen, gridWidth, gridDepth, score)
        templist = []
        templist.append(grid)
        if score == 'p':
            totalscore = grid.calcTotalValue(grid.buildings)[0]
        elif score == 'v':
            totalscore = grid.calcTotalValue(grid.buildings)[1]

        templist.append(totalscore)
        new_pop.append(templist)

        if len(new_pop) % 100 == 0:
            print len(new_pop), "candidates evolved."

    return new_pop


def createCandidate(population, aantalhuizen, gridWidth, gridDepth, score):
    """
    Creates a single candidate (crosover with mutation).
    :param list population: List containing candidates.
    :param int aantalhuizen: Amount of buildings in a candidate
    :param int gridWidth: Width of the candidate.
    :param int gridDepth: Depth of candidate
    :param str score: Kind of score that should be optimized.
            'v' = optimal vrijstand. 'p' = optimal price.
    :return: returns a single candidate.
    """
    # Create a crossover.
    grid = createCrossover(population, aantalhuizen, gridWidth, gridDepth)

    for building in grid.buildings:
        grid.findShortestDist(building)

    # Fully random mutation of crossover.
    #grid = mutatecandidate(aantalhuizen, grid)

    # Hillclimb random mutation.
    grid = mutatecandidateHC(aantalhuizen, grid, score)

    return grid



def createCrossover(population, aantalhuizen, gridWidth, gridDepth):
    """
    Creates a crossover.
    :param list population: List containing candidates.
    :param int aantalhuizen: Amount of buildings in a candidate
    :param int gridWidth: Width of the candidate.
    :param int gridDepth: Depth of candidate
    :return: returns single candidate.
    """
    currentcandidate = False
    coattempt = 0

    # A broken crossover will be returned if repair fails.
    # This candiate will be automatically discarded in next fitness selection.

    while currentcandidate == False and coattempt < 10:
        coattempt += 1

        candidates = []
        # Pick two random candidates from population.
        for i in range(2):
            randomcandidate = random.choice(population)

            # Candidates can't be the same.
            while randomcandidate in candidates:
                randomcandidate = random.choice(population)

            candidates.append(randomcandidate[0])

        candidate1 = candidates[0]
        candidate2 = candidates[1]

        grid = Grid(gridWidth, gridDepth, aantalhuizen)

        maison = 0
        bungalow = 0
        eensgezins = 0

        stop = False

        # Add buildings from first candidate.
        for building in candidate1.buildings:
            if building.y > gridDepth /2:
                if building.name[0] == 'm' and maison < aantalhuizen * grid.maisons:
                    maison += 1
                    #grid.addBuilding(building)
                    newbuilding = Maison(building.x, building.y, building.angle, grid.width, grid.depth)
                    grid.addBuilding(newbuilding)
                if building.name[0] == 'b' and bungalow < aantalhuizen * grid.bungalows:
                    bungalow += 1
                    newbuilding = Bungalow(building.x, building.y, building.angle, grid.width, grid.depth)
                    grid.addBuilding(newbuilding)
                if building.name[0] == 'e' and eensgezins < aantalhuizen * grid.eensgezins:
                    eensgezins += 1
                    newbuilding = EengezinsWoning(building.x, building.y, building.angle, grid.width, grid.depth)
                    grid.addBuilding(newbuilding)

        # Add buildings from second candiate.
        for building in candidate2.buildings:
            if building.y < gridDepth /2:
                attempts = 0
                if building.name[0] == 'm' and maison < aantalhuizen * grid.maisons:
                    maison += 1
                    newbuilding = Maison(building.x, building.y, building.angle, grid.width, grid.depth)
                    grid.addBuilding(newbuilding)

                    while grid.findOverlap2(newbuilding) == True:
                        grid.newRandomPosGA(newbuilding, grid)
                        attempts += 1
                        if attempts > 1000:
                            stop = True
                            break


                attempts = 0
                if building.name[0] == 'b' and bungalow < aantalhuizen * grid.bungalows:
                    bungalow += 1
                    newbuilding = Bungalow(building.x, building.y, building.angle, grid.width, grid.depth)
                    grid.addBuilding(newbuilding)

                    while grid.findOverlap2(newbuilding) == True:
                        grid.newRandomPosGA(newbuilding, grid)
                        attempts += 1
                        if attempts > 1000:
                            stop = True
                            break


                attempts = 0
                if building.name[0] == 'e' and eensgezins < aantalhuizen * grid.eensgezins:
                    eensgezins += 1
                    #grid.addBuilding(building)
                    newbuilding = EengezinsWoning(building.x, building.y, building.angle, grid.width, grid.depth)
                    grid.addBuilding(newbuilding)

                    while grid.findOverlap2(newbuilding) == True:
                        grid.newRandomPosGA(newbuilding, grid)
                        attempts += 1
                        if attempts > 1000:
                            stop = True
                            break

                if stop == True:
                    break

        stop = False


        # Add missing buildings.
        while maison < aantalhuizen * grid.maisons:
            maison += 1
            ran_x = random.random() * (grid.width )
            ran_y = random.random() * (grid.depth )
            ran_angle = 0 #random.randrange(0,360)
            building = Maison(ran_x, ran_y, ran_angle, grid.width, grid.depth)
            grid.addBuilding(building)
            attempts = 0
            while grid.findOverlap2(building) == True:
                grid.newRandomPosGA(building, grid)
                attempts += 1
                if attempts > 1000:
                    stop = True
                    break

        while bungalow < aantalhuizen * grid.bungalows:
            bungalow += 1
            ran_x = random.random() * (grid.width )
            ran_y = random.random() * (grid.depth )
            ran_angle = 0 #random.randrange(0,360)
            building = Bungalow(ran_x, ran_y, ran_angle, grid.width, grid.depth)
            grid.addBuilding(building)
            attempts = 0
            while grid.findOverlap2(building) == True:
                grid.newRandomPosGA(building, grid)
                attempts += 1
                if attempts > 1000:
                    stop = True
                    break

        while eensgezins < aantalhuizen * grid.eensgezins:
            eensgezins += 1
            ran_x = random.random() * (grid.width )
            ran_y = random.random() * (grid.depth )
            ran_angle = 0 #random.randrange(0,360)
            building = EengezinsWoning(ran_x, ran_y, ran_angle, grid.width, grid.depth)
            grid.addBuilding(building)
            attempts = 0
            while grid.findOverlap2(building) == True:
                grid.newRandomPosGA(building, grid)
                attempts += 1
                if attempts > 1000:
                    stop = True
                    break


        # Try again if crossover failed.
        if stop == True:
            currentcandidate = False
        else:
            currentcandidate = True

    return grid


def mutatecandidate(aantalhuizen, grid):
    """
    Random mutation of candidate.
    :param int aantalhuizen: Amount of buildings in a candidate
    :param grid: object containing candidate
    :return: object containing mutated candidate
    """
    # Choose random amount of mutations.
    mutations = random.randint(1, aantalhuizen / 5)

    for i in range(mutations):
        # Choose a random house to mutate.
        randombuilding = grid.buildings[random.choice(range(len(grid.buildings)))]

        # Mutate the house by giving it a new position.
        grid.newRandomPosGA(randombuilding, grid)

        # Change position if it doesn't meet the constraints.
        while grid.findOverlap2(randombuilding) == True:
            grid.newRandomPosGA(randombuilding, grid)

    return grid

def mutatecandidateHC(aantalhuizen, grid, score):
    """
    Random mutation of candidate with hill climbing.
    :param int aantalhuizen: Amount of buildings in a candidate
    :param grid: object containing candidate
    :param str score: Kind of score that should be optimized.
            'v' = optimal vrijstand. 'p' = optimal price.
    :return: object containing mutated candidate
    """
    if score == 'p':
        grid = HillClimberGA(grid, 0, 10, 200, aantalhuizen)
    elif score == 'v':
        grid = HillClimberGA(grid, 1, 10, 200, aantalhuizen)

    return grid


def HillClimberGA(grid, optVar, noChangeParam, valueDifParam, aantalhuizen):
    """
    Uses hillclimber algorithm to find local optimal solution. Uses swapping.
    """
    newValue = grid.calcTotalValue([])[optVar]
    previousValue = newValue

    i = 0
    noChange = 0

    # When over chosen amount of iterations the change is less than chosen
    # amount per iteration the loop is terminated.
    while noChange < noChangeParam:
        # There is chance 0.2 to swap random buildings and 0.8 to translate
        # building
        if random.random() > 0.8:
            # Choose random building
            building1 = grid.buildings[random.randrange(0, aantalhuizen)]
            building2 = grid.buildings[random.randrange(0, aantalhuizen)]

            while building1 == building2:
                building2 = grid.buildings[random.randrange(0, aantalhuizen)]

            newValue = grid.swapBuildings(building1, building2, previousValue, optVar)
        else:
            # Choose random building
            building = grid.buildings[random.randrange(0, aantalhuizen)]

            newValue = grid.newTranslatedPos(building, previousValue, optVar)

        valueDif = newValue - previousValue

        if valueDif > 0:
            previousValue = newValue

        if valueDif < valueDifParam:
            noChange += 1
        else:
            noChange = 0
        i += 1
    return grid



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


def storeMap(grid, filename):
    """
    Stores width and depth of a grid and the positions, rotations and types of all buildings on a grid in a file
    @param grid: an object of type grid
    @param filename: name for the created file
    """
    
    f = open(filename, 'w')
    f.write(str(grid.width) + ' ' + str(grid.depth) + '\n')

    for building in grid.buildings:
        f.write(str(building.getX()) + ' ' + str(building.getY()) + ' ' + str(building.getAngle()) + ' ' + str(building.name) + '\n')

    f.close()


def readMap(filename):
    """
    Reads files created by function storeMap and returns the corresponding grid. Also makes an animation
    @param filename: name of the file to read
    @return: grid stored in the file
    """
    f = open(filename, 'r')
    line = f.readline()[:-1]      # Read the line and remove the '\n' part
    
    gridWidth, gridDepth = line.split(' ')

    buildings = []
    while line != '':
        line = f.readline()[:-1]
        buildings.append((line.split(' ')))

    grid = Grid(float(gridWidth), float(gridDepth), len(buildings))

    for building in buildings:
        if building != ['']:
            if building[3] == 'eengezinswoning':
                instant = EengezinsWoning(float(building[0]), float(building[1]), float(building[2]), float(gridWidth), float(gridDepth))
            elif building[3] == 'bungalow':
                instant = Bungalow(float(building[0]), float(building[1]), float(building[2]), float(gridWidth), float(gridDepth))
            elif building[3] == 'maison':
                instant = Maison(float(building[0]), float(building[1]), float(building[2]), float(gridWidth), float(gridDepth))
         
            grid.addBuilding(instant)

    anim = GridVisualisation(float(gridWidth), float(gridDepth), grid.buildings, 0)
    anim.emptyAnimation(grid.buildings)
    
    return grid




