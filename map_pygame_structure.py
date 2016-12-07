from pygame_structure import *
from mapcmu_data import *

class MapPygameMode(PygameMode):
    def __init__(self, bkcolor=(255,255,255), screenDims=(1000,800),
            changeModeFn=None):
        PygameMode.__init__(self, bkcolor=bkcolor, screenDims=screenDims,
                changeModeFn=changeModeFn)
        #self.router.testTable() # Temp for testing!
        self.mainSurf = SurfacePlus()
        self.mainSurf.surf = pygame.Surface(self.screenDims)
        self.surfaces.append(self.mainSurf)
        
        self.arrowOffset = [2300,3200]

        self.showHelp = False

        self.initFloorData()
        MapPygameMode.newFloor(self, self.selFloor)

    def initMap(self):
        self.map2image = pygame.image.load(
                Constants.buildings[self.selBuilding].getFloor(self.selFloor))
        self.map2Rect = self.map2image.get_rect()

    def initFloorData(self):
        self.selFloor = 2
        self.selBuilding = "GHC"

    def upAFloor(self):
        if self.selFloor < Constants.buildings[self.selBuilding].maxFloor:
            self.newFloor(self.selFloor+1)

    def downAFloor(self):
        if self.selFloor > Constants.buildings[self.selBuilding].minFloor:
            self.newFloor(self.selFloor-1)
    
    def newFloor(self, floor):
        self.selFloor = floor
        self.zPos = (self.selFloor-1) * Constants.floorHeight

        self.initMap()
    
    ##################################################

    def modelToView(self, coords, surf):
        return (coords[0] - self.arrowOffset[0] + surf.get_size()[0]//2,
                coords[1] - self.arrowOffset[1] + surf.get_size()[1]//2)

    def viewToModel(self, coords, surf):
        return (coords[0] + self.arrowOffset[0] - surf.get_size()[0]//2,
                coords[1] + self.arrowOffset[1] - surf.get_size()[1]//2) 

    def drawTextAt(self, text, pos, size=18, color=Constants.steel, bold=False):
        dfont = pygame.font.SysFont("arial", size, bold=bold)
        label = dfont.render(
                text,
                1, color)
        self.mainSurf.surf.blit(label, pos)

        return dfont.size(text)

    def drawHelpOverlay(self, mlString):
        surfSize = self.mainSurf.surf.get_size()
        mlString = mlString.strip()

        border = 80
        pygame.draw.rect(self.mainSurf.surf, Constants.backdrop,
                (border,border,surfSize[0]-border*2,surfSize[1]-border*2))
        pygame.draw.rect(self.mainSurf.surf, (0,0,0),
                (border,border,surfSize[0]-border*2,surfSize[1]-border*2),
                1)

        posX = border + 10

        sizeHelp = self.drawTextAt("HELP", (posX,border+10),
                color=(255,0,0), size=35, bold=True)

        if len(mlString) < 1: return

        startY = border + sizeHelp[1] + 30
        posX += 30
        margin = 7
        lines = mlString.splitlines()
        sizeLine = self.drawTextAt(lines[0], (posX,startY))
        for i in range(1,len(lines)):
            line = lines[i]
            lineY = startY + i*(sizeLine[1] + margin)
            
            self.drawTextAt(line, (posX, lineY))
            

    def drawFooterHelp(self):
        surfSize = self.mainSurf.surf.get_size()
        boxH = 30

        pygame.draw.rect(self.mainSurf.surf, Constants.backGray,
                (0, surfSize[1] - boxH, surfSize[0], boxH))
        pygame.draw.rect(self.mainSurf.surf, (0,0,0),
                (0, surfSize[1] - boxH, surfSize[0], boxH),
                1)

        msg = Constants.footerHelp
        dfont = pygame.font.SysFont("arial", 18)
        msgSize = dfont.size(msg)
        boxY = msgSize[1]/2 + boxH/2 
        label = dfont.render(
                msg,
                1, (10,10,10))
        self.mainSurf.surf.blit(label, 
                (surfSize[0]/2 - msgSize[0]/2, surfSize[1]-boxY))

    def drawMap(self):
        coords = self.modelToView(self.map2Rect, self.mainSurf.surf)

        self.mainSurf.surf.blit(self.map2image, 
                 pygame.Rect(coords[0], coords[1],
                 self.map2Rect.w, self.map2Rect.h))

    def drawCornerMsg(self):
        boxSize = (0,0,100,35)
        txtPos = (10,2)
        pygame.draw.rect(self.mainSurf.surf, Constants.backdrop,
                boxSize)
        pygame.draw.rect(self.mainSurf.surf, (0,0,0),
                boxSize,1)

        dfont = pygame.font.SysFont("arial", 25)
        label = dfont.render(
                "Floor %d" % self.selFloor,
                1, (10,10,10))
        self.mainSurf.surf.blit(label, txtPos)

