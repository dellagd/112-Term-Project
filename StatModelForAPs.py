import math
from functools import reduce

class ProbabilisticMap(object):
    def __init__(self, apScanner, mapTable):
        self.scanner = apScanner
        
        self.mapTable = mapTable
        #self.mapTable.nukeTable()

        self.addingToMap = False
        self.pdfsPerLocation = None

        self.regenerateModel()

    def addResultRow(self, loc, bssid, rssi, timeStamp):
        self.mapTable.addAP(loc, bssid, rssi, timeStamp)

    def regenerateModel(self):
        # Generate histogram for each ap at each location
        # Try just estimateing with normal-ish distribution
        self.pdfsPerLocation = self.generateProbFuncs()
           
    def findLocation(self, report):
        q = 4 # Get Strongest 4
        if len(report) <= 2:
            print("Report from wifi adapter too small")
            return None
        elif len(report) <= 4:
            topQ = report
        else:
            topQ = sorted(report, key=lambda x: int(x["RSSI"]))
            topQ = topQ[-q:]
        
        possibleLocs = self.mapTable.collection.distinct("Location")
        bestLoc, bestProb = None, -1
        for loc in possibleLocs:
            #print("Trying loc: %r" % loc)
            res = self.probOfResult(loc, topQ) * 10**8 # Better visibility

            if res > bestProb:
                #print("%f better than %f" % (res,bestProb))
                bestLoc = loc
                bestProb = res

        return bestLoc


    def probOfResult(self, loc, topQ):
        def findBSSIDMatch(bssid, a):
            for i in range(len(a)):
                if bssid == a[i]["BSSID"]:
                    return a[i]
            return None
        
        pdfsHere = self.pdfsPerLocation[loc]
        #print (pdfsHere)
        #print("*********")
        #print(topQ)
        if len(pdfsHere) < 4:
            print("Not enough data at %r" % loc)
            return 0.0
        
        totalProb = 1
        for i in range(len(topQ)):
            ap = topQ[i]

            match = findBSSIDMatch(ap["BSSID"], pdfsHere)
            if match != None:
                probFromPDF = match["PDF"](int(ap["RSSI"]))
                #print("Found Prob: %f" % probFromPDF)
                totalProb *= probFromPDF
            else:
                #print("None found: 0.0001")
                totalProb *= 0.0001
        
        return totalProb
            

    def generateProbFuncs(self):
        def getGaussianFunc(center, stdev):
            height = 1 / (2 * math.pi * stdev**2) # Lock integral = 1
            return lambda x: max(
                    height * (math.exp(-((x-center)**2)/(2*(stdev**2)))),
                    0.001)

        # Generate the probability function per each bssid per loc
        # Do this for just the strongest 4
        possibleLocs = self.mapTable.collection.distinct("Location")
        mapByLoc = {}

        for loc in possibleLocs:
            mapByLoc[loc] = []

            apsAtLoc = self.mapTable.getAPsAtLoc(loc)
            possibleBSSIDs = self.mapTable.collection.distinct("BSSID" , {"Location" : loc})

            for bssid in possibleBSSIDs:
                samples = self.mapTable.getAPsAtLocWithBSSID(loc, bssid)
                
                amount = len(list(samples))
                sumOfRSSI = reduce(lambda x,y: x+int(y["RSSI"]), samples, 0)
                
                avg = sumOfRSSI / amount

                mapByLoc[loc].append({"BSSID" : bssid, "RSSI" : avg})

            # Find k Strongest APs
            k = 4
            exampleStdev = 1.5 # Eventually calculate this
            topK = sorted(mapByLoc[loc], key=lambda a:a["RSSI"])
            topK = topK[-k:]
            mapByLoc[loc] = topK[:]

            for i in range(len(mapByLoc[loc])):
                #print("Making function centered at %r" % mapByLoc[loc][i]["RSSI"])
                mapByLoc[loc][i]["PDF"] = getGaussianFunc(
                        mapByLoc[loc][i]["RSSI"],
                        exampleStdev)

        return mapByLoc
