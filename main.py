# Authors: Patrick Vlaar, Casper Broertjes and Paul Schrijver.

# This software has been written to solve the 'AmstelHeage' case.
# http://wiki.phoib.net/wiki/index.php?title=Amstelhaege

# This code has been tested with both Python 2.7 and Pypy 2.4.0.
# For best performance it is recommended to use Pypy.
# http://pypy.org/download.html


from algorithms import *

if __name__ == '__main__':
    # Define precision of movements
    precision = 1.0
    # Width of the building site.
    gridWidth = 120
    # Depth of the building site.
    gridDepth = 160
    # Amount of houses
    houses = 60



    ### Random solution. ###

    grid = Grid(gridWidth, gridDepth, house)
    grid.randomPlacements()

    # Visualize map with score: price.
    #GridVisualisation(gridWidth, gridDepth, grid.buildings, grid.calcTotalValue(grid.buildings)[0])


    ### Run Genetic algorithm. ###

    # Amount of generations
    generations = 500
    # Population size
    population = 5000

    # Uncomment to run
    #geneticAlgorithm(population, generations, houses, gridWidth, gridDepth, 'v')