from pygame_structure import *
from functools import reduce
from collections import Counter
import ScannerUtils
from ast import literal_eval

class TestMode(PygameMode):
    def __init__(self):
        PygameMode.__init__(self, bkcolor=(255,255,255), screenDims=(800,600))
        self.map2image= pygame.image.load("Gates-2.jpg")
        self.map2Rect = self.map2image.get_rect()
        self.map2 = SurfacePlus()
        self.map2.surf = pygame.Surface(self.screenDims)
        self.map2.offset = [+2000,+2800]

        self.surfaces.append(self.map2)

        self.recording = False
        self.finding = False
        self.resultTick = 0
        self.possiblePos = []
        self.currentPos = None

        self.apList = []
        self.scanner = ScannerUtils.APScanner(trigFunc=self.scanResult)
        self.scanner.start()

    def scanResult(self, result):
        if self.recording:
            self.resultTick += 1
            toAdd = {}
            toAdd["APs"] = result
            toAdd["FOUNDLOC"] = "(%d,%d)"%(self.map2.offset[1],self.map2.offset[0])
            self.apList.append(toAdd)
            #print("Added: %r"%toAdd)
        elif self.finding:
            self.resultTick += 1
            self.possiblePos.append(self.findBestMatch(result))
            self.currentPos = self.reducePositions(self.possiblePos)
    
    def reducePositions(self, posits):
        n = len(posits)
        #sumTup = reduce(lambda x,y: (x[0]+y[0], x[1]+y[1]), posits, (0,0))
        #return tuple(map(lambda x: x/n, sumTup))
        intList = list(map(lambda x: (int(x[0]),int(x[1])), posits))
        return Counter(intList).most_common(1)[0][0]

    def findBestMatch(self, result):
        def findBSSIDMatch(bssid, a):
            for i in range(len(a)):
                if bssid == a[i]["BSSID"]:
                    return a[i]
            return None

        def dbToScore(db):
            return dbOffset(db)**(3/2)
        
        def dbOffset(db):
            return db + 90

        byLoc = {}
        for val in self.apList:
            loc = val["FOUNDLOC"]
            if loc in byLoc:
                byLoc[loc] = byLoc[loc] + tuple([ap for ap in val["APs"]])
            else:
                byLoc[loc] = tuple([ap for ap in val["APs"]])

        avgByLoc = {}
        for loc in byLoc:
            bssids = set([ap['BSSID'] for ap in byLoc[loc]])

            for bssid in bssids:
                apsWithBssid = list(filter(lambda x: x["BSSID"] == bssid, byLoc[loc]))
                apNum = len(apsWithBssid)
                if apNum < 1: continue
                
                averageRssi = reduce(lambda x,y: x + int(y["RSSI"]), apsWithBssid, 0)
                averageRssi /= apNum

                if loc in avgByLoc:
                    avgByLoc[loc] = avgByLoc[loc] + ({"BSSID":bssid, "RSSI":averageRssi},)
                else:
                    avgByLoc[loc] = ({"BSSID":bssid, "RSSI":averageRssi},)
                    

        bestScore = 100000000000
        bestLoc = self.apList[0]["FOUNDLOC"] 
        for loc in avgByLoc:
            apsAtLoc = avgByLoc[loc]
            score = 0
            apsHit = []
            bothLists = reduce(lambda x,y: x + 
                    ((y,) if findBSSIDMatch(y["BSSID"], apsAtLoc) == None else tuple()),
                    result,
                    apsAtLoc)

            #for ap in result:
            for ap in bothLists: 
                matchResult = findBSSIDMatch(ap["BSSID"], result)
                matchLoc = findBSSIDMatch(ap["BSSID"], apsAtLoc)
                
                if matchResult != None:
                    print ("BSSIDResult: %s" % matchResult["BSSID"], end=' ')
                    mRScore = dbToScore(int(matchResult["RSSI"]))
                else: 
                    print ("BSSIDResult: %s" % "None", end=' ')
                    mRScore = dbToScore(-70)

                if matchLoc != None:
                    print ("BSSIDLoc: %s" % matchLoc["BSSID"], end=' ')
                    mLScore = dbToScore(int(matchLoc["RSSI"]))
                else: 
                    print ("BSSIDLoc: %s" % "None", end=' ')
                    mLScore = dbToScore(-70)

                if matchResult == None and matchLoc == None:
                    assert(False)

                print("RSSI1: %d RSSI2: %d"%(mRScore,mLScore))
                score += abs(mRScore - mLScore)
                
                #if (match != None):
                #    print("RSSI1: %s RSSI2: %s"%(match["RSSI"],ap["RSSI"]))
                #    score += (dbToScore(int(match["RSSI"])) - 
                #              dbToScore(int(ap["RSSI"])))**2
                #else:
                #    print("RSSI1: %s RSSI2: %s"%(-70,ap["RSSI"]))
                #    score += (dbToScore(-70) - dbToScore(int(ap["RSSI"])))**2 
                #    # What to make this...
            print("Score at %s: %s" % (loc,score))
            if score < bestScore:
                bestScore = score
                bestLoc = loc

        return literal_eval(bestLoc)



    def drawView(self, screen):
        self.map2.surf.fill((255,255,255))
        self.map2.surf.blit(self.map2image,
                 pygame.Rect(self.map2Rect.x - self.map2.offset[0],
                 self.map2Rect.y - self.map2.offset[1],
                 self.map2Rect.w, self.map2Rect.h))
        
        pygame.draw.circle(self.map2.surf, (255,0,0),
                (self.screenDims[0]//2, self.screenDims[1]//2),
                8)
        
        dfont = pygame.font.SysFont("monospace", 15)
        label = dfont.render(
                "Position (x,y): (%d,%d)" % (self.map2.offset[1], self.map2.offset[0]),
                1, (10,10,10))
        self.map2.surf.blit(label, (0, 0))

        if (self.recording or self.finding):
            label = dfont.render(
                    "RECORDING (%d)" % self.resultTick if self.recording \
                        else "FINDING (%d): %s" % (self.resultTick,self.currentPos),
                    1, (255,0,0))
            self.map2.surf.blit(label, (0, 20))


        super().drawView(screen)

    def keyPressed(self, event):
        mult = .1 if pygame.key.get_mods() & pygame.KMOD_SHIFT else 1
        ctrl = pygame.key.get_mods() & pygame.KMOD_CTRL 
        if event.key == pygame.K_UP:
            self.map2.offset[1] -= 100 * mult
        elif event.key == pygame.K_DOWN:
            self.map2.offset[1] += 100 * mult
        elif event.key == pygame.K_LEFT:
            self.map2.offset[0] -= 100 * mult
        elif event.key == pygame.K_RIGHT:
            self.map2.offset[0] += 100 * mult
        elif event.key == pygame.K_r:
            self.resultTick = 0
            self.recording = not self.recording
            self.finding = False
            self.possiblePos = []
            self.currentPos = None
        elif event.key == pygame.K_p:
            self.resultTick = 0
            self.finding = not self.finding
            self.recording = False
            self.possiblePos = []
            self.currentPos = None
        elif event.key == pygame.K_ESCAPE or (event.key == pygame.K_c and ctrl):
            quit()


        
