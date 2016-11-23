import threading
import os, sys, time
import pygame
import color_constants
from pygame_structure import *
from mapping_modes import *

if not pygame.font: print ('Warning, fonts disabled')
if not pygame.mixer: print ('Warning, sound disabled')

class MappingUtility(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.myPygame = MainPygame()
        #self.myPygame.daemon=True
        self.myPygame.start()

    def run(self):
        self.__mainloop()

    def __mainloop(self):
        modeMapping = MappingMode()
        self.myPygame.addMode(modeMapping, "Mapping")

        self.myPygame.useMode("Mapping")

mu = MappingUtility()
mu.run()
