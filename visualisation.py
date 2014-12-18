# Authors: Patrick Vlaar, Casper Broertjes and Paul Schrijver.

from Tkinter import *
import math
import time

class GridVisualisation:

    # Eengezinswoningen = red
    # Bungalows = blue
    # Maisons = black

    def __init__(self, width, height, buildings, prijsverb):
        "Initializes a visualization with the specified parameters."
        # Adjust size of visualisation based on precision
        precision = 1.0
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
