from pygame_structure import *
from functools import reduce
import mongodb_databases
import ScannerUtils, StatModelForAPs
from ast import literal_eval
import datetime
import math

class MappingMode(PygameMode):
    def __init__(self):
        PygameMode.__init__(self, bkcolor=(255,255,255), screenDims=(800,600))
        
        self.initMap()
        self.surfaces.append(self.map2)
        
        self.arrowOffset = [+2300,+3200]

        self.recording = False
        self.recStart = ""
        self.finding = False
        self.resultTick = 0
        self.possiblePos = []
        self.currentPos = None

        self.mapByLoc = {}
        self.db = mongodb_databases.MDBDatabase("MapCMU")
        self.mapTable = mongodb_databases.MapTable(self.db.database)
        self.initFromDatabase()
        self.pointPopup.setTable(self.mapTable)
        self.mapPoints.setTable(self.mapTable)

        self.scanner = ScannerUtils.APScanner(trigFunc=self.scanResult)
        self.scanner.daemon=True
        self.scanner.start()
        
        self.statmodel = StatModelForAPs.ProbabilisticMap(
                self.scanner, self.mapTable)

    def initMap(self):
        self.map2image= pygame.image.load("Gates-2.jpg")
        self.map2Rect = self.map2image.get_rect()
        self.map2 = SurfacePlus()
        
        self.mapPoints = self.MapPointHandler(mToV=self.modelToView,
                vToM=self.viewToModel)
        self.map2.objects.append(self.mapPoints)

        self.pointPopup = self.MapPopup()
        self.map2.objects.append(self.pointPopup)

        self.locPoint = self.FoundPoint(mToV=self.modelToView,
                vToM=self.viewToModel)
        self.map2.objects.append(self.locPoint)
            
        self.map2.surf = pygame.Surface(self.screenDims)

    def initFromDatabase(self):
        self.regenerateMapPoints()

    def scanResult(self, result):
        if self.recording:
            self.resultTick += 1
            for apRow in result:
                location = "(%d, %d)"%(self.arrowOffset[0],self.arrowOffset[1])
                self.statmodel.addResultRow(location, apRow["BSSID"],
                        apRow["RSSI"], self.recStart)
           
            self.statmodel.regenerateModel()
            
            self.regenerateMapPoints()
        elif self.finding:
            self.resultTick += 1
            posResult = self.statmodel.findLocation(result)
            if posResult != None:
                self.possiblePos.append(literal_eval(self.statmodel.findLocation(result)))

            count = len(self.possiblePos)
            self.currentPos = reduce(lambda x,y: (x[0] + y[0], x[1]+y[1]),
                    self.possiblePos, (0,0))
            self.currentPos = (self.currentPos[0] / count,
                    self.currentPos[1] / count)

            self.locPoint.updatePos(self.currentPos)

    def regenerateMapPoints(self):
        self.mapPoints.objects = []
        possibleLocs = self.mapTable.collection.distinct("Location")
       
        for loc in possibleLocs:
            self.mapPoints.addPoint(literal_eval(loc))

#######################################

    class MapPoint(PygameObject):
        def initData(self):
            self.radius = 4
            self.color = (0,255,0)

        def draw(self, surface, dims, offset=(0,0)):
            super().draw(surface, dims, offset)

            coords = self.mToV(self.pos, surface.surf)

            pygame.draw.circle(surface.surf, self.color, coords, self.radius)

        def mousePressed(self, surface, x, y):
            super().mousePressed(surface, x, y)

            xr, yr = self.vToM((x,y), surface.surf)

            distance = math.sqrt((xr - self.pos[0])**2 + \
                    (yr - self.pos[1])**2)

            if distance < self.radius: # Clicked this point
                return True

            return False

    class FoundPoint(PygameObject):
        def initData(self):
            self.radius = 6 # Size for triangle 
            self.color = (255,0,255)
            self.enabled = False

        def updatePos(self, pos):
            if pos != None:
                self.enabled = True
                self.pos = pos

        def draw(self, surface, dims, offset=(0,0)):
            if not self.enabled: return

            coords = self.mToV(self.pos, surface.surf)
            self.drawTriangleAtPoint(surface.surf, coords, self.radius)

        def drawTriangleAtPoint(self, surface, pos, radius):
            a_angle,b_angle,c_angle = 0,math.radians(120),math.radians(240)
            pointA = (pos[0] - radius*math.sin(a_angle),
                    pos[1] - radius*math.cos(a_angle))
            pointB = (pos[0] - radius*math.sin(b_angle),
                    pos[1] - radius*math.cos(b_angle))
            pointC = (pos[0] - radius*math.sin(c_angle),
                    pos[1] - radius*math.cos(c_angle))
            verticies = (pointA, pointB, pointC)

            pygame.draw.polygon(surface, self.color, verticies)


    class MapPointHandler(PygameObject):
        def setTable(self, table):
            self.table = table

        def initData(self):
            self.selectedPoint = None

        def selectDeletion(self, num):
            if self.selectedPoint != None:
                loc = str(self.selectedPoint.pos)

                stamps = self.table.collection.distinct("TIME", {"Location" : loc})

                tS = stamps[num]

                self.table.collection.remove({"Location" : loc, "TIME" : tS})

        def addPoint(self, point):
            self.objects.append(MappingMode.MapPoint(point, self.mToV, self.vToM))
        
        def mousePressed(self, surface, x, y):
            found = None
            for obj in self.objects:
                result = obj.mousePressed(surface, x, y)
                if result: 
                    found = obj
                    obj.color = (0,0,255)
                else:
                    obj.color = (0,255,0)

            self.selectedPoint = found

    class MapPopup(PygameObject):
        def setTable(self, table):
            self.table = table

        def initData(self):
            self.width = 220
            self.point = None

        def draw(self, surface, dims, offset=(0,0)):
            if self.point != None:
                ptStr = str(self.point.pos)
                stamps = self.table.collection.distinct("TIME", {"Location" : ptStr})
                
                self.pos = (dims[0] - self.width, 0)
                margin, size = 2, 15
                height = max(len(stamps) * (2*margin+size),15)
                pygame.draw.rect(surface.surf, (220,220,255), self.pos + (self.width, height), 0)
                pygame.draw.rect(surface.surf, (0,0,0), self.pos + (self.width, height), 1)

                dfont = pygame.font.SysFont("monospace", size)    
                for i in range(len(stamps)):
                    tS = stamps[i]

                    label = dfont.render(
                            str(i) + ": " + tS,
                            1, (10,10,10))
                    surface.surf.blit(label, 
                            (self.pos[0]+margin,
                            self.pos[1]+margin + i*(2*margin+size)))

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
        
        self.pointPopup.point = self.mapPoints.selectedPoint
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
        keyPadNums = [pygame.K_KP0, pygame.K_KP1, pygame.K_KP2,
                pygame.K_KP3, pygame.K_KP4, pygame.K_KP5,
                pygame.K_KP6, pygame.K_KP7, pygame.K_KP8,
                pygame.K_KP9]
        
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
            self.locPoint.enabled = False
            self.possiblePos = []
            self.currentPos = None
        elif event.key == pygame.K_p:
            self.resultTick = 0
            self.finding = not self.finding
            self.locPoint.enabled = not self.locPoint.enabled
            self.recording = False
            self.possiblePos = []
            self.currentPos = None
        elif event.key in keyPadNums:
            num = keyPadNums.index(event.key)
            self.handleKeypad(event, num)
        elif event.key == pygame.K_ESCAPE or (event.key == pygame.K_c and ctrl):
            quit()

    def handleKeypad(self, event, num):
        if pygame.key.get_mods() & pygame.KMOD_SHIFT:
            self.mapPoints.selectDeletion(num)
            self.regenerateMapPoints()

