# Authors: Patrick Vlaar, Casper Broertjes and Paul Schrijver.

# This software has been written to solve the 'AmstelHeage' case.
# http://wiki.phoib.net/wiki/index.php?title=Amstelhaege

# This code has been tested with both Python 2.7 and Pypy 2.4.0.
# For best performance it is recommended to use Pypy.
# http://pypy.org/download.html

from buildings import *
from visualisation import *
from grid import *

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

def combinationRandomSample(aantalhuizen, gridWidth, gridDepth, optVar, noChangeParam, valueDifParam):
    """
    Uses hillclimber algorithm to find local optimal solution. Uses swapping.
    """
    print 'Starting hill climbing algorithm...'
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
            print "Current iteration = ",i, " with value: ", previousValue
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

    anim.emptyAnimation(grid.buildings)
    anim.updateAnimation(grid.buildings, 0)
    
    return grid.calcTotalValue([]) + (grid,)


def combinationRandomSampleSA(aantalhuizen, gridWidth, gridDepth, lifetimeNewPos, lifetimeSwap, optVar, noChangeParam, valueDifParam):
    """
    Uses simulated annealing algorithm to find local optimal solution. Uses swapping and translating.
    """
    print "Starting simulated annealing algorithm..."
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
            print "Current iteration = ", i, "with value = ",previousValue
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


def swappingRandomSample(aantalhuizen, gridWidth, gridDepth, optVar, noChangeParam, valueDifParam):
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




