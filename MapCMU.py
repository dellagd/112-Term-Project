import threading
import os, sys, time
import pygame
import color_constants
from pygame_structure import *
from mapping_mode import *
from route_planning_mode import *

if not pygame.font: print ('Warning, fonts disabled')
if not pygame.mixer: print ('Warning, sound disabled')

class MainProgram(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.myPygame = MainPygame()
        #self.myPygame.daemon=True
        self.myPygame.start()

    def run(self):
        self.__mainloop()

    def __mainloop(self):
        modeMapping = MappingMode()
        modeRouting = RoutePlanningMode()
        self.myPygame.addMode(modeMapping, "Mapping")
        self.myPygame.addMode(modeRouting, "Routing")

        self.myPygame.useMode("Routing")

mu = MainProgram()
mu.run()
