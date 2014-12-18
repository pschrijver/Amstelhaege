# Authors: Patrick Vlaar, Casper Broertjes and Paul Schrijver.

# This software has been written to solve the 'AmstelHeage' case.
# http://wiki.phoib.net/wiki/index.php?title=Amstelhaege

# This code has been tested with both Python 2.7 and Pypy 2.4.0.
# For best performance it is recommended to use Pypy.
# http://pypy.org/download.html


from algorithms import *
from buildings import *

if __name__ == '__main__':
    # Define precision of movements
    precision = 1.0
    # Width of the building site.
    gridWidth = 120
    # Depth of the building site.
    gridDepth = 160
    # Amount of houses
    houses = 60
    # Precision of house placement
    precision = 1.0


    
    ### Random solution. ###

    #UNCOMMENT THIS SECTION TO RUN A RANDOM PLACEMENT
    
    #grid = Grid(gridWidth, gridDepth, houses)
    #grid.randomPlacements()

    # Visualize map with score: price.
    #GridVisualisation(gridWidth, gridDepth, grid.buildings, grid.calcTotalValue(grid.buildings)[0])

    ### End ###
    



    ### Run Genetic algorithm. ###

    # Amount of generations
    generations = 500
    # Population size
    population = 5000

    # UNCOMMENT TO RUN GENETIC ALGORITHM
    #geneticAlgorithm(population, generations, houses, gridWidth, gridDepth, 'v')

    ### End ###




    ### Hill Climbing Algorithm ###

    # How many times no significant improvement may occur
    noChangeParam = 10000

    # Below this param is considered an insignificant improvement
    valueDifParam = 1000

    # Choose optVar (0 = Price, 1 = Vrijstand)
    optVar = 0
    
    # UNCOMMENT TO RUN HILL CLIMBING ALGORITHM
    #combinationRandomSample(houses, gridWidth, gridDepth, optVar, noChangeParam, valueDifParam)




    ### Simulated Annealing Algorithm ###

    # How many times no significant improvement may occur
    noChangeParam = 20000

    # Below this param is considered an insignificant improvement
    valueDifParam = 1000

    # Simulated Annealing Temperatures
    lifetimeNewPos = 400000000
    lifetimeSwap = 200000000

    # Choose optVar (0 = Price, 1 = Vrijstand)
    optVar = 0

    # UNCOMMENT TO RUN SIMULATED ANNEALING
    combinationRandomSampleSA(houses, gridWidth, gridDepth, lifetimeNewPos, lifetimeSwap, optVar, noChangeParam, valueDifParam)
   
