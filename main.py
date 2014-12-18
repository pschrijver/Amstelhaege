from algorithms import *

if __name__ == '__main__':
    grid = Grid(120, 160, 5)
    grid.randomPlacements()
    print grid.calcTotalValue([])
