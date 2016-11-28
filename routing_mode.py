from pygame_structure import *
import routing_engine

class RoutingMode(PygameMode):
    def __init__(self):
        PygameMode.__init__(self, bkcolor=(255,255,255), screenDims=(1000,800))
        self.router = routing_engine.RoutingEngine()
        self.router.testTable()
        self.path = (self.router.findRoute([10,10,0,"GHC"], [200,220,0,"GHC"]))
        self.mainSurf = SurfacePlus()
        self.mainSurf.surf = pygame.Surface(self.screenDims)
        self.surfaces.append(self.mainSurf)
    
    ##################################################
    
    def drawRoutes(self):
        segs = self.router.getAllSegments()

        for seg in segs:
            pos1, pos2 = seg["LOC_A"], seg["LOC_B"]
            pos1, pos2 = pos1[:2], pos2[:2]

            pygame.draw.line(self.mainSurf.surf, (0,0,255),
                    pos1, pos2)

        nodes = self.router.getAllNodes()

        pointRadius = 5
        print(self.path)
        for node in nodes:
            if node in self.path: color = (0,255,255)
            else: color = (0,0,255)
            pygame.draw.circle(self.mainSurf.surf, color,
                    node[:2], pointRadius)

    def drawView(self,screen):
        self.mainSurf.surf.fill((200,200,200))

        self.drawRoutes()

        super().drawView(screen)    

