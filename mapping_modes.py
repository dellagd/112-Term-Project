from pygame_structure import *
from functools import reduce
import mongodb_databases
import ScannerUtils, StatModelForAPs
from ast import literal_eval
import datetime
import math

class TestMode(PygameMode):
    def __init__(self):
        PygameMode.__init__(self, bkcolor=(255,255,255), screenDims=(800,600))
        self.map2image= pygame.image.load("Gates-2.jpg")
        self.map2Rect = self.map2image.get_rect()
        self.map2 = SurfacePlus()
        self.mapPoints = self.MapPointHandler(mToV=self.modelToView,
                vToM=self.viewToModel)
        self.map2.objects.append(self.mapPoints)
        self.map2.surf = pygame.Surface(self.screenDims)

        self.surfaces.append(self.map2)
        
        self.arrowOffset = [+2300,+3200]

        self.recording = False
        self.recStart = ""
        self.finding = False
        self.resultTick = 0
        self.currentPos = None

        self.mapByLoc = {}
        self.db = mongodb_databases.MDBDatabase("MapCMU_test")
        self.mapTable = mongodb_databases.MapTable(self.db.database)

        self.scanner = ScannerUtils.APScanner(trigFunc=self.scanResult)
        self.scanner.daemon=True
        self.scanner.start()
        
        self.statmodel = StatModelForAPs.ProbabilisticMap(
                self.scanner, self.mapTable)

    def scanResult(self, result):
        if self.recording:
            self.resultTick += 1
            for apRow in result:
                location = "(%d,%d)"%(self.arrowOffset[0],self.arrowOffset[1])
                self.statmodel.addResultRow(location, apRow["BSSID"],
                        apRow["RSSI"], self.recStart)
           
            self.statmodel.regenerateModel()
            
            self.regenerateMapPoints()
        elif self.finding:
            self.resultTick += 1
            self.currentPos = self.statmodel.findLocation(result)

    def regenerateMapPoints(self):
        self.mapPoints.objects = []
        possibleLocs = self.mapTable.collection.distinct("Location")
       
        for loc in possibleLocs:
            print("Adding %r" % loc)
            self.mapPoints.addPoint(literal_eval(loc))

#######################################

    class MapPoint(PygameObject):
        def initData(self):
            self.radius = 4 

        def draw(self, surface, dims, offset=(0,0)):
            super().draw(surface, dims, offset)

            coords = self.mToV(self.pos, surface.surf)

            pygame.draw.circle(surface.surf, (0,255,0), coords, self.radius)

        def mousePressed(self, surface, x, y):
            super().mousePressed(surface, x, y)

            xr, yr = self.vToM((x,y), surface.surf)

            distance = math.sqrt((xr - self.pos[0])**2 + \
                    (yr - self.pos[1])**2)

            if distance < self.radius: # Clicked this point
                print("Clicked! I am at %r" % (self.pos,))

    class MapPointHandler(PygameObject):
        def addPoint(self, point):
            self.objects.append(TestMode.MapPoint(point, self.mToV, self.vToM))    

    def modelToView(self, coords, surf):
        return (coords[0] - self.arrowOffset[0] + surf.get_size()[0]//2,
                coords[1] - self.arrowOffset[1] + surf.get_size()[1]//2)

    def viewToModel(self, coords, surf):
        return (coords[0] + self.arrowOffset[0] - surf.get_size()[0]//2,
                coords[1] + self.arrowOffset[1] - surf.get_size()[1]//2) 

    def drawMap(self):
        self.map2.surf.fill((200,200,200))
    
        coords = self.modelToView(self.map2Rect, self.map2.surf)

        self.map2.surf.blit(self.map2image, 
                 pygame.Rect(coords[0], coords[1],
                 self.map2Rect.w, self.map2Rect.h))
       
    def drawCursor(self):
        mid = (self.screenDims[0]//2, self.screenDims[1]//2)
        cursorSize = min(self.screenDims[0]//15, self.screenDims[1]//15)
        cursorVert = (mid[1] - cursorSize//2, mid[1] + cursorSize//2)
        cursorHorz = (mid[0] - cursorSize//2, mid[0] + cursorSize//2)

        pygame.draw.line(self.map2.surf, (255,0,0), # Vertical Line
                (mid[0], cursorVert[1]), (mid[0], cursorVert[0]))
        pygame.draw.line(self.map2.surf, (255,0,0), # Horizontal Line
                (cursorHorz[1], mid[1]), (cursorHorz[0], mid[1]))
        
    def drawView(self, screen):
        self.drawMap() # Draws the map image
        self.drawCursor() # Draws cursor in screen center

        self.map2.drawObjects(offset=tuple(self.arrowOffset))

        dfont = pygame.font.SysFont("monospace", 15)
        label = dfont.render(
                "Position (x,y): (%d,%d)" % (self.arrowOffset[0], self.arrowOffset[1]),
                1, (10,10,10))
        self.map2.surf.blit(label, (0, 0))

        if (self.recording or self.finding):
            label = dfont.render(
                    "RECORDING (%d)" % self.resultTick if self.recording \
                        else "FINDING (%d): %s" % (self.resultTick,self.currentPos),
                    1, (255,0,0))
            self.map2.surf.blit(label, (0, 20))


        super().drawView(screen)

#######################################

    def mousePressed(self, event):
        self.map2.mouseObjects(event, self.arrowOffset)

    def keyPressed(self, event):
        mult = .1 if pygame.key.get_mods() & pygame.KMOD_SHIFT else 1
        ctrl = pygame.key.get_mods() & pygame.KMOD_CTRL 
        if event.key == pygame.K_UP:
            self.arrowOffset[1] -= int(100 * mult)
        elif event.key == pygame.K_DOWN:
            self.arrowOffset[1] += int(100 * mult)
        elif event.key == pygame.K_LEFT:
            self.arrowOffset[0] -= int(100 * mult)
        elif event.key == pygame.K_RIGHT:
            self.arrowOffset[0] += int(100 * mult)
        elif event.key == pygame.K_r:
            self.resultTick = 0
            self.recording = not self.recording
            self.recStart = ( 
                '{:%Y-%b-%d %H:%M:%S}'.format(datetime.datetime.now()))
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


        
