from pygame_structure import *
from map_pygame_structure import *
import routing_engine
import user_input
from mapcmu_data import *
import math

class ForwardRoutingMode(MapPygameMode):
    def __init__(self):
        MapPygameMode.__init__(self, bkcolor=(255,255,255), screenDims=(1000,800))
        self.router = routing_engine.RoutingEngine()

        self.plannedRoute = []
        self.testRoute()

    def testRoute(self):
        nodeB = self.router.getRoomNode("Parking - 1")
        nodeA = self.router.getRoomNode("4303")

        self.plannedRoute = list(map(lambda x: x.info,
                self.router.findRoute(nodeA,nodeB)))
        print("\nRoute: %r" %self.plannedRoute)

    def drawSegments(self):
        for i in range(0, len(self.plannedRoute)-1):
            locA, locB = self.plannedRoute[i], self.plannedRoute[i+1]
            
            p1m = self.modelToView(locA, self.mainSurf.surf)
            p2m = self.modelToView(locB, self.mainSurf.surf)

            if locA[2] == locB[2] and locA[2] == self.zPos: 
                # Same floor
                pygame.draw.line(self.mainSurf.surf, (0,255,0),
                        p1m, p2m, 6)

    def drawPoints(self):
        radius = 10
        color = (0,255,0)
        for i in range(0,len(self.plannedRoute)):
            pointA = self.plannedRoute[i]
            pointB = self.plannedRoute[i+1] if (
                    i+1<len(self.plannedRoute)) else None

            coords = self.modelToView(pointA, self.mainSurf.surf)
           

            if pointA[2] == self.zPos:
                if i == 0:
                    self.drawTextPoint(coords, "Start")
                elif pointB == None:
                    self.drawTextPoint(coords, "End")
                elif pointB != None and pointA[2] > pointB[2]:
                    self.drawTextPoint(coords, "Go Down")
                elif pointB != None and pointA[2] < pointB[2]:
                    self.drawTextPoint(coords, "Go Up")
                else:
                    pygame.draw.circle(self.mainSurf.surf, color, coords, radius)

    def drawTextPoint(self, coords, text):
        radius = 25
        boxColor = (0,255,0)
        boxBuf = 5
        textColor = (255,0,0)
        fSize = 20
         
        dfont = pygame.font.SysFont("arial", fSize)
        rendSize = dfont.size(text)
        
        boxX = coords[0] - rendSize[0]/2 - boxBuf
        boxY = coords[1] - rendSize[1]/2 - boxBuf
        boxSizeX = rendSize[0] + 2*boxBuf
        boxSizeY = rendSize[1] + 2*boxBuf
        pygame.draw.rect(self.mainSurf.surf, boxColor,
                (boxX, boxY, boxSizeX, boxSizeY))
        pygame.draw.rect(self.mainSurf.surf, (0,0,0),
                (boxX, boxY, boxSizeX, boxSizeY), 1)
        
        xText = coords[0] - rendSize[0]/2
        yText = coords[1] - rendSize[1]/2 
        label = dfont.render(text, 2, textColor)
        self.mainSurf.surf.blit(label, (xText,yText))
        
    
    def drawView(self,screen):
        self.mainSurf.surf.fill((200,200,200))

        self.drawMap()
        #self.mainSurf.drawObjects(offset=tuple(self.arrowOffset))
        self.drawSegments()
        self.drawPoints()
        self.drawCornerMsg()

        #if self.textBox.enabled:
        #    self.textBox.drawBox(self.mainSurf.surf)
    
        super().drawView(screen)

    ################################################

    def keyPressed(self, event):
        super().keyPressed(event)
       
        #if self.textBox.enabled:
        #    self.textBox.keyPressed(event)
        #    return

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
