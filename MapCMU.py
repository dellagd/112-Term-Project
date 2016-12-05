import threading
import os, sys, time
import pygame
import color_constants
from pygame_structure import *
from mapping_mode import *
from route_planning_mode import *
from forward_routing_mode import *
from control_modes import *

if not pygame.font: print ('Warning, fonts disabled')
if not pygame.mixer: print ('Warning, sound disabled')

class MainProgram(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.myPygame = MainPygame()

        self.modeStack = []

        #self.myPygame.daemon=True
        self.myPygame.start()

    def run(self):
        self.__mainloop()

    def upAMode(self):
        self.modeStack.pop() # Pop twice because mode will be re-added
        mode = self.modeStack.pop()

        self.changeMode(mode)

    def changeMode(self, mode=None, args=None):
        if mode == None:
            self.upAMode()
            return
        else:
            del self.myPygame.modes[mode]
            if mode == "Mapping":
                self.modeMapping = MappingMode(self.changeMode)
                self.myPygame.addMode(self.modeMapping, mode)
            elif mode == "Route Planning":
                self.modeRoutePlan = RoutePlanningMode(self.changeMode)
                self.myPygame.addMode(self.modeRoutePlan, mode)
            elif mode == "Routing":
                self.modeRouting = ForwardRoutingMode(self.changeMode, args=args)
                self.myPygame.addMode(self.modeRouting, mode)
            elif mode == "Select":
                self.modeSelect = SelectionMode(self.changeMode)
                self.myPygame.addMode(self.modeSelect, mode)
            elif mode == "Navigate":
                self.modeNav = NavigateMode(self.changeMode)
                self.myPygame.addMode(self.modeNav, mode)

            self.modeStack.append(mode)
            self.myPygame.useMode(mode)

    def __mainloop(self):
        call = self.changeMode
        modeMapping = MappingMode(call)
        modeRoutePlan = RoutePlanningMode(call)
        modeRouting = ForwardRoutingMode(call)
        modeSelect = SelectionMode(call)
        modeNav = NavigateMode(call)
        self.myPygame.addMode(modeMapping, "Mapping")
        self.myPygame.addMode(modeRoutePlan, "Route Planning")
        self.myPygame.addMode(modeRouting, "Routing")
        self.myPygame.addMode(modeSelect, "Select")
        self.myPygame.addMode(modeNav, "Navigate")
        
        self.modeStack.append("Select")
        self.myPygame.useMode("Select")

mu = MainProgram()
mu.run()
