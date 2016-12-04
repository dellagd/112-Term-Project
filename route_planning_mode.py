from pygame_structure import *
import routing_engine
import user_input
from mapcmu_data import *
import math

class RoutePlanningMode(PygameMode):
    def __init__(self):
        PygameMode.__init__(self, bkcolor=(255,255,255), screenDims=(1000,800))
        self.router = routing_engine.RoutingEngine()
        #self.router.testTable() # Temp for testing!
        self.mainSurf = SurfacePlus()
        self.mainSurf.surf = pygame.Surface(self.screenDims)
        self.surfaces.append(self.mainSurf)
        
        self.textBox = user_input.TextInputBox()
        self.arrowOffset = [2300,3200]

        self.initData()
        self.initFloorData()
        self.initMap()
        self.initRouteNodes()
        self.newFloor(self.selFloor)

        self.testRoute()
        
    def initMap(self):
        self.map2image = pygame.image.load(
                Constants.buildings[self.selBuilding].getFloor(self.selFloor))
        self.map2Rect = self.map2image.get_rect()

    def initRouteNodes(self):
        self.routeNodes = self.RouteNodeHandler(mToV=self.modelToView,
                vToM=self.viewToModel)
        self.refreshNodes()
        self.mainSurf.objects.append(self.routeNodes)

    def initData(self):
        self.pointQueue = []
        self.lastPoint = None

    def initFloorData(self):
        self.selFloor = 2
        self.selBuilding = "GHC"

    def testRoute(self):
        nodeA = self.router.getRoomNode("Parking - 1")
        nodeB = self.router.getRoomNode("4303")

        print("\nRoute: %r" % self.router.findRoute(nodeA,nodeB))

    def upAFloor(self):
        if self.selFloor < Constants.buildings[self.selBuilding].maxFloor:
            self.newFloor(self.selFloor+1)

    def downAFloor(self):
        if self.selFloor > Constants.buildings[self.selBuilding].minFloor:
            self.newFloor(self.selFloor-1)
    
    def newFloor(self, floor):
        self.selFloor = floor
        self.zPos = (self.selFloor-1) * Constants.floorHeight

        self.initData()
        self.initMap()
        self.refreshNodes()

    def removeLastAddedSegment(self):
        if len(self.pointQueue) < 1: return False
        else:
            point = self.pointQueue.pop()
            self.router.segTable.collection.remove({"_id" : point[0]})
            self.routeNodes.removeNode(point[1])

            findNode = [point[2][0],point[2][1],self.zPos,self.selBuilding]
            q = { '$or' : [{"LOC_A" : findNode}, {"LOC_B" : findNode}]}
            conn = self.router.segTable.collection.find(q)
            if len(list(conn)) < 1:
                self.routeNodes.removeNode(point[2])
                self.lastPoint = None
            else:
                self.lastPoint = point[2]

    def checkAndAddSegment(self, aLoc, bLoc):
        print("This point: %r   Last point: %r" % (aLoc, bLoc))
            
        if aLoc != None and bLoc != None:
            aLocDB = [aLoc[0],aLoc[1],self.zPos,self.selBuilding]
            bLocDB = [bLoc[0],bLoc[1],self.zPos,self.selBuilding]

            q = { '$or' : [
                {"LOC_A" : aLocDB, "LOC_B" : bLocDB},
                {"LOC_B" : aLocDB, "LOC_A" : bLocDB}
                ]}
            conn = self.router.segTable.collection.find(q)

            if len(list(conn)) > 0: # This segment already exists
                return
            
            rId = self.addSegmentToMap(aLoc, bLoc)
            self.pointQueue.append((rId,aLoc,bLoc))
            
            if pygame.key.get_mods() & pygame.KMOD_CTRL:
                self.textBox.doPopup("Enter room", self.textBoxCallback,
                        args=(rId,))
            
            return rId

    def addSegmentToMap(self, pos1, pos2):
        return self.router.segTable.addSegment(
            [pos1[0],pos1[1],self.zPos,self.selBuilding],
            [pos2[0],pos2[1],self.zPos,self.selBuilding]
            ) # Returns entry id
    
    def textBoxCallback(self, text, rId):
        print(text, rId)
        self.router.segTable.collection.update({"_id" : rId},
                {"$set" : {"NOTE" : text}})

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
       
        def removeNode(self, remNode):
            for node in self.objects:
                if node.pos == remNode:
                    self.objects.remove(node)

        def purgeNodes(self, dbNodes):
            self.objects = []

            for node in dbNodes:
                self.addNode((node[0],node[1]))
        
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

    def refreshNodes(self):
        self.routeNodes.purgeNodes(
                self.router.getAllNodes(onFloor=self.selFloor))

    #############################################

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
        segs = self.router.getAllSegments(onFloor=self.selFloor)

        for seg in segs:
            pos1, pos2 = seg["LOC_A"], seg["LOC_B"]
            pos1, pos2 = pos1[:2], pos2[:2]
            p1m = self.modelToView(pos1, self.mainSurf.surf)
            p2m = self.modelToView(pos2, self.mainSurf.surf)

            pygame.draw.line(self.mainSurf.surf, (0,0,255),
                    p1m, p2m)

    def drawCornerMsg(self):
        boxSize = (0,0,140,30)
        pygame.draw.rect(self.mainSurf.surf, (255,255,255),
                boxSize)
        pygame.draw.rect(self.mainSurf.surf, (0,0,0),
                boxSize,1)

        dfont = pygame.font.SysFont("monospace", 25)
        label = dfont.render(
                "Floor: %d" % self.selFloor,
                1, (10,10,10))
        self.mainSurf.surf.blit(label, (3, 0))


    def drawView(self,screen):
        self.mainSurf.surf.fill((200,200,200))

        self.drawMap()
        self.drawRoutes()
        self.mainSurf.drawObjects(offset=tuple(self.arrowOffset))
        self.drawCornerMsg()

        if self.textBox.enabled:
            self.textBox.drawBox(self.mainSurf.surf)
    
        super().drawView(screen)

#######################################

    def mousePressed(self, event):
        if self.textBox.enabled: return
        
        # Do events for contained pygameobjects first
        self.mainSurf.mouseObjects(event, self.arrowOffset)
        
        xm, ym = self.viewToModel(event.pos, self.mainSurf.surf)

        clickPos = self.routeNodes.getSelectedPosition()
        if clickPos != None:
            xm, ym = clickPos
        else:
            self.routeNodes.addNode((xm, ym))

        segId = self.checkAndAddSegment((xm,ym), self.lastPoint)

        self.lastPoint = (xm, ym)

    def keyPressed(self, event):
        super().keyPressed(event)
       
        if self.textBox.enabled:
            self.textBox.keyPressed(event)
            return

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
        elif event.key == pygame.K_PAGEUP:
            self.upAFloor()
        elif event.key == pygame.K_PAGEDOWN:
            self.downAFloor()
        elif event.key == pygame.K_u:
            self.removeLastAddedSegment()
            self.refreshNodes() 
        if event.key == pygame.K_SPACE:
            print("Space!")
            self.refreshNodes()
            self.routeNodes.clearSelection()
            self.lastPoint = None

        if event.key == pygame.K_a:
            # TESTING POPUP
            self.textBox.doPopup("Room", self.textBoxCallback)

