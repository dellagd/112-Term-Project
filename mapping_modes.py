from pygame_structure import *
from functools import reduce
from collections import Counter
import mongodb_databases
import ScannerUtils, StatModelForAPs
from ast import literal_eval

class TestMode(PygameMode):
    def __init__(self):
        PygameMode.__init__(self, bkcolor=(255,255,255), screenDims=(800,600))
        self.map2image= pygame.image.load("Gates-2.jpg")
        self.map2Rect = self.map2image.get_rect()
        self.map2 = SurfacePlus()
        self.map2.surf = pygame.Surface(self.screenDims)

        self.surfaces.append(self.map2)
        
        self.arrowOffset = [+2000,+2800]

        self.recording = False
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
                apRow["Location"] = "(%d,%d)"%(self.map2.offset[1],self.map2.offset[0]) 
                self.statmodel.addResultRow(
                        apRow["Location"], apRow["BSSID"], apRow["RSSI"])
           
            self.statmodel.regenerateModel()    
        elif self.finding:
            self.resultTick += 1
            self.currentPos = self.statmodel.findLocation(result)

#######################################

    def modelToView(self, coords):
        return (coords[0] - self.arrowOffset[0],
                coords[1] - self.arrowOffset[1])

    def drawMap(self):
        self.map2.surf.fill((255,255,255))
        self.map2.surf.blit(self.map2image, 
                 pygame.Rect(self.map2Rect.x - self.arrowOffset[0],
                 self.map2Rect.y - self.arrowOffset[1],
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

        dfont = pygame.font.SysFont("monospace", 15)
        label = dfont.render(
                "Position (x,y): (%d,%d)" % (self.arrowOffset[1], self.arrowOffset[0]),
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

    def keyPressed(self, event):
        mult = .1 if pygame.key.get_mods() & pygame.KMOD_SHIFT else 1
        ctrl = pygame.key.get_mods() & pygame.KMOD_CTRL 
        if event.key == pygame.K_UP:
            self.arrowOffset[1] -= 100 * mult
        elif event.key == pygame.K_DOWN:
            self.arrowOffset[1] += 100 * mult
        elif event.key == pygame.K_LEFT:
            self.arrowOffset[0] -= 100 * mult
        elif event.key == pygame.K_RIGHT:
            self.arrowOffset[0] += 100 * mult
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


        
