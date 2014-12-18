# Authors: Patrick Vlaar, Casper Broertjes and Paul Schrijver.

from buildings import *
from visualisation import *

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
                    ran_angle = 0
                    building = Maison(ran_x, ran_y, ran_angle, self.width, self.depth)
                elif i < .4 * self.aantalhuizen:
                    ran_x = random.random() * (self.width )
                    ran_y = random.random() * (self.depth )
                    ran_angle = 0
                    building = Bungalow(ran_x, ran_y, ran_angle, self.width, self.depth)
                else:
                    ran_x = random.random() * (self.width )
                    ran_y = random.random() * (self.depth )
                    ran_angle = 0
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
