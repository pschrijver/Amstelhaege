import Tkinter as tk

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()

    def createWidgets(self):
        self.quitButton = tk.Button(self, text='Quit',
            command=self.quit)
        self.quitButton.grid()

app = Application()
app.master.title('Sample application')
app.mainloop()

class Grid(object):
    def __init__(self, width, depth, aantalhuizen):
        self.width = width
        self.depth = depth
        self.aantalhuizen = aantalhuizen
        self.eensgezins = float(0.6)
        self.bungalows = float(0.25)
        self.maisons = float(0.15)
        buildings = []
        
    def findOverlap(self, building1, building2):
        return NotImplementedError
    def swapBuilding(self, building1, building2):
        return NotImplementedError
    
class Building(object):
    def _init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 8
        self.depth = 8
        self.value = 285000
        self.percentage = 3
        self.vrijstand = 2

class Bungalow(Building):
    def _init__(self):
        self.width = 10
        self.depth = float(7.5)
        self.value = 399000
        self.percentage = 4
        self.vrijstand = 3
        
class Maison(Building):
    def _init__(self):
        self.width = 11
        self.depth = float(10.5)
        self.value = 610000
        self.percentage = 6
        self.vrijstand = 6

    def getX(self):
        return self.x
    def getY(self):
        return self.y
    def randomPosition(self):
        return NotImplementedError
    def translate(self):
        return NotImplementedError

class EengezinsWoning(Building):
    def _init__(self):
        self.width = 8
        self.depth = 8
        self.value = 285000
        self.percentage = 3
        self.vrijstand = 2

class Bungalow(Building):
    def _init__(self):
        self.width = 10
        self.depth = float(7.5)
        self.value = 399000
        self.percentage = 4
        self.vrijstand = 3
        
class Maison(Building):
    def _init__(self):
        self.width = 11
        self.depth = float(10.5)
        self.value = 610000
        self.percentage = 6
        self.vrijstand = 6




        
