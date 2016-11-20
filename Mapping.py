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
        modeA = PygameMode(fps=30)
        modeB = PygameMode(screenDims=(800,800), fps=60, bkcolor=(255,0,0))
        modeC = TestMode()
        self.myPygame.addMode(modeA, "A")
        self.myPygame.addMode(modeB, "B")
        self.myPygame.addMode(modeC, "C")

        modeB.addSurface(pygame.Surface(modeB.screenDims))
        pygame.draw.rect(modeB.getSurface(1), (0,255,0), (0,0,20,20))

        self.myPygame.useMode("C")

mu = MappingUtility()
mu.run()
