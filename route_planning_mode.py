from pygame_structure import *
import routing_engine
from mapcmu_data import *
import math

class RoutePlanningMode(PygameMode):
    def __init__(self):
        PygameMode.__init__(self, bkcolor=(255,255,255), screenDims=(1000,800))
        self.router = routing_engine.RoutingEngine()
        self.router.testTable() # Temp for testing!
        self.mainSurf = SurfacePlus()
        self.mainSurf.surf = pygame.Surface(self.screenDims)
        self.surfaces.append(self.mainSurf)

        self.arrowOffset = [2300,3200]
        self.selFloor = 2
        self.selBuilding = "GHC"
        self.floorHeight = 600

        self.lastPoint = None

        self.initMap()
        
    def initMap(self):
        self.map2image = pygame.image.load(
                Constants.buildings[self.selBuilding].getFloor(self.selFloor))
        self.map2Rect = self.map2image.get_rect()

        self.routeNodes = self.RouteNodeHandler(mToV=self.modelToView,
                vToM=self.viewToModel)
        self.mainSurf.objects.append(self.routeNodes)


    def addSegmentToMap(self, pos1, pos2):
        self.router.segTable.addSegment(
            [pos1[0],pos1[1],self.floorHeight*self.selFloor,self.selBuilding],
            [pos2[0],pos2[1],self.floorHeight*self.selFloor,self.selBuilding]
            )
    
    ##################################################
    
    class RouteNode(PygameObject):
        def initData(self):
            self.radius = 5
            self.color = (0,0,255)

        def draw(self, surface, dims, offset=(0,0)):
            super().draw(surface, dims, offset)

            coords = self.mToV(self.pos, surface.surf)

            pygame.draw.circle(surface.surf, self.color, coords, self.radius)

        def getCoords(self):
            return self.pos

        def mousePressed(self, surface, x, y):
            super().mousePressed(surface, x, y)

            xr, yr = self.vToM((x,y), surface.surf)

            distance = math.sqrt((xr - self.pos[0])**2 + \
                    (yr - self.pos[1])**2)

            if distance < self.radius: # Clicked this point
                return True

            return False
   
    class RouteNodeHandler(PygameObject):
        def setTable(self, table):
            self.table = table

        def initData(self):
            self.selectedPoint = None
            self.NOT_SEL = (0,0,255)
            self.SEL = (255,0,255)

        def addNode(self, point):
            self.objects.append(RoutePlanningMode.RouteNode(
                point, self.mToV, self.vToM))
        
        def getSelectedPosition(self):
            if self.selectedPoint == None:
                return None
            else:
                return self.selectedPoint.getCoords()

        def clearSelection(self):
            self.selectedPoint = None
            for obj in self.objects:
                obj.color = self.NOT_SEL

        def mousePressed(self, surface, x, y):
            found = None
            for obj in self.objects:
                result = obj.mousePressed(surface, x, y)
                if result: 
                    found = obj
                    obj.color = self.SEL
                else:
                    obj.color = self.NOT_SEL

            self.selectedPoint = found


    def modelToView(self, coords, surf):
        return (coords[0] - self.arrowOffset[0] + surf.get_size()[0]//2,
                coords[1] - self.arrowOffset[1] + surf.get_size()[1]//2)

    def viewToModel(self, coords, surf):
        return (coords[0] + self.arrowOffset[0] - surf.get_size()[0]//2,
                coords[1] + self.arrowOffset[1] - surf.get_size()[1]//2) 

    def drawMap(self):
        coords = self.modelToView(self.map2Rect, self.mainSurf.surf)

        self.mainSurf.surf.blit(self.map2image, 
                 pygame.Rect(coords[0], coords[1],
                 self.map2Rect.w, self.map2Rect.h))
    
    def drawRoutes(self):
        segs = self.router.getAllSegments()

        for seg in segs:
            pos1, pos2 = seg["LOC_A"], seg["LOC_B"]
            pos1, pos2 = pos1[:2], pos2[:2]
            p1m = self.modelToView(pos1, self.mainSurf.surf)
            p2m = self.modelToView(pos2, self.mainSurf.surf)

            pygame.draw.line(self.mainSurf.surf, (0,0,255),
                    p1m, p2m)

        nodes = self.router.getAllNodes()

        #pointRadius = 5
        #for node in nodes:
        #    color = (0,0,255)
        #    nm = self.modelToView(node, self.mainSurf.surf)
        #    pygame.draw.circle(self.mainSurf.surf, color,
        #            nm[:2], pointRadius)

    def drawCornerMsg(self):
        dfont = pygame.font.SysFont("monospace", 15)
        label = dfont.render(
                "Floor: %d" % self.selFloor,
                1, (10,10,10))
        self.mainSurf.surf.blit(label, (0, 0))


    def drawView(self,screen):
        self.mainSurf.surf.fill((200,200,200))

        self.drawMap()
        self.drawRoutes()
        self.mainSurf.drawObjects(offset=tuple(self.arrowOffset))
        self.drawCornerMsg()

        super().drawView(screen)  

#######################################

    def mousePressed(self, event):
        # Do events for contained pygameobjects first
        self.mainSurf.mouseObjects(event, self.arrowOffset)
        
        xm, ym = self.viewToModel(event.pos, self.mainSurf.surf)

        clickPos = self.routeNodes.getSelectedPosition()
        if clickPos != None:
            xm, ym = clickPos
        else:
            self.routeNodes.addNode((xm, ym))

        print("This point: %d, %d   Last point: %r" % (xm,ym,self.lastPoint)) 
        if (xm, ym) != None and self.lastPoint != None:
            self.addSegmentToMap((xm,ym),self.lastPoint)

        self.lastPoint = (xm, ym)

    def keyPressed(self, event):
        super().keyPressed(event)
        
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
        
        if event.key == pygame.K_SPACE:
            print("Space!")
            self.routeNodes.clearSelection()
            self.lastPoint = None

