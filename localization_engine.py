##########################################################################
# Author: Griffin Della Grotte (gdellagr@andrew.cmu.edu)
#
# The localization engine wraps both the APScanner and StatModel into
# a simple interface that more easily permits the implementation
# of WiFi localization. This class is used by the Navigation Mode in
# order to find the user's initial location
##########################################################################

import threading
import time
from mapcmu_data import *
import mongodb_databases
import routing_engine
import ScannerUtils
import StatModelForAPs
from ast import literal_eval
from functools import reduce

class LocalizationEngine(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.db = mongodb_databases.MDBDatabase(Constants.database)
        self.mapTable = mongodb_databases.MapTable(self.db.database)
        self.router = routing_engine.RoutingEngine()

        self.results = []

        # Set up the scanner
        self.scanner = ScannerUtils.APScanner(trigFunc=self.scanResult)
        self.scanner.daemon = True # Quit when the parent thread quits
        self.scanner.start()

        self.statmodel = StatModelForAPs.ProbabilisticMap(
                self.scanner, self.mapTable)
        
        self.samples = None
        self.callback = None

        self.enabled = False

        self.kill = False

        self.selBuilding = "GHC"

    def run(self):
        self.__mainloop()

    def __mainloop(self):
        while True:
            if self.kill:
                # If I'm dead, kill the scanner too
                self.scanner.kill = True
                return

            if not self.enabled: 
                time.sleep(0.05)
                continue
            else:
                if len(self.results) >= self.samples:
                    position = self.reduceToPosition()
                    self.callback(self.findClosestNode(position))
                    self.enabled = False
                time.sleep(0.1)
                    
    def scanResult(self, result):
        if self.enabled:
            print("Sample Received")
            posResult = self.statmodel.findLocation(result)
            if posResult != None:
                self.results.append(literal_eval(self.statmodel.findLocation(result)))

    def reduceToPosition(self):
        # Average out possible positions down to one
        count = len(self.results)
        self.currentPos = reduce(lambda x,y: (
                x[0]+y[0], x[1]+y[1], x[2]+y[2]),
                self.results, (0,0,0))

        self.currentPos = (self.currentPos[0] / count,
                self.currentPos[1] / count,
                self.coerceZPos(self.currentPos[2] / count))

        return (self.currentPos)


    def coerceZPos(self, z):
        # Snap z position to a valid floor
        maxFloor = Constants.buildings[self.selBuilding].maxFloor
        minFloor = Constants.buildings[self.selBuilding].minFloor

        for floor in range(minFloor, maxFloor+1):
            zPos = (floor-1) * Constants.floorHeight
            zRange = (zPos - Constants.floorHeight/2,
                      zPos + Constants.floorHeight/2)

            if z > zRange[0] and z <= zRange[1]:
                return zPos
        print("Out of range floor position (this should not be possible)")


    def beginLocalization(self, samples, callback):
        self.samples = samples
        self.callback = callback
        self.results = []

        self.enabled = True

    def euclDist(self, posA, posB):
        return ((posA[0] - posB[0])**2 + \
                (posA[1] - posB[1])**2)**0.5

    def findClosestNode(self, position):
        print(position)
        floorP = (position[2] // Constants.floorHeight) + 1
        nodes = self.router.getAllNodes(onFloor=floorP)

        bestNode = None
        bestDist = 10e42
        for node in nodes:
            dist = self.euclDist(node, position)
            
            if dist < bestDist:
                bestNode = node
                bestDist = dist

        return bestNode

    
