##########################################################################
# Author: Griffin Della Grotte (gdellagr@andrew.cmu.edu)
#
# This module is the highest level script that of MapCMU. It facilitates
# the initialization of the software as well as the transition between
# modes.
##########################################################################

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
        self.myPygame.start() # Start the PyGame wrapper thread

    def run(self):
        self.go()

    def upAMode(self):
        self.modeStack.pop() # Pop twice because mode will be re-added
        mode = self.modeStack.pop()

        self.changeMode(mode)

    def changeMode(self, mode=None, args=None):
        # This function will be passed down to the modes so they can use it to
        # call a mode change
        if mode == None:
            self.upAMode()
            return
        else:
            if mode == "Mapping":
                self.myPygame.modes[mode].scanner.kill = True
                del self.myPygame.modes[mode]
                self.modeMapping = MappingMode(self.changeMode)
                self.myPygame.addMode(self.modeMapping, mode)
            elif mode == "Route Planning":
                del self.myPygame.modes[mode]
                self.modeRoutePlan = RoutePlanningMode(self.changeMode)
                self.myPygame.addMode(self.modeRoutePlan, mode)
            elif mode == "Routing":
                del self.myPygame.modes[mode]
                self.modeRouting = ForwardRoutingMode(self.changeMode, args=args)
                self.myPygame.addMode(self.modeRouting, mode)
            elif mode == "Select":
                del self.myPygame.modes[mode]
                self.modeSelect = SelectionMode(self.changeMode)
                self.myPygame.addMode(self.modeSelect, mode)
            elif mode == "Navigate":
                self.myPygame.modes[mode].localize.kill = True
                del self.myPygame.modes[mode]
                self.modeNav = NavigateMode(self.changeMode)
                self.myPygame.addMode(self.modeNav, mode)

            self.modeStack.append(mode)
            self.myPygame.useMode(mode)

    def go(self):
        # Initialize modes
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
