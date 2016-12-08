##########################################################################
# Author: Griffin Della Grotte (gdellagr@andrew.cmu.edu)
#
# This module contains two modes: 
#
# Selection Mode, which is the first mode the user enters and presents 
# them with the choice of the three operational modes
#
# Navigation Mode, which is the simple UI for entering in a desired
# destination, to which a route from the current location will be
# generated.
##########################################################################

from pygame_structure import *
import user_input
from mapcmu_data import *
import localization_engine
import time

class SelectionMode(PygameMode):
    def __init__(self, call):
        self.bk = Constants.backdrop
        PygameMode.__init__(self,screenDims=(1000,800),bkcolor=self.bk,
                changeModeFn=call)
        self.mainSurf = SurfacePlus()
        self.mainSurf.surf = pygame.Surface(self.screenDims)
        self.surfDims = self.mainSurf.surf.get_size()
        self.surfaces.append(self.mainSurf)

        self.initButtons()

    def initButtons(self):
        size = (350,100)

        pos = (self.surfDims[0]/2, 350)
        buttonNav = SelectionMode.Button(pos,size,"Navigate Mode",
                self.changeModeFn)
        buttonNav.setModeResponse("Navigate")
        self.mainSurf.objects.append(buttonNav)
        
        pos = (self.surfDims[0]/2, 500)
        buttonRoutes = SelectionMode.Button(pos,size,"Map Routes Mode",
                self.changeModeFn)
        buttonRoutes.setModeResponse("Route Planning")
        self.mainSurf.objects.append(buttonRoutes)

        pos = (self.surfDims[0]/2, 650)
        buttonMapAP = SelectionMode.Button(pos,size,"Map APs Mode",
                self.changeModeFn)
        buttonMapAP.setModeResponse("Mapping")
        self.mainSurf.objects.append(buttonMapAP)
    
    ###############################################

    class Button(PygameObject):
        # Button object that detects clicks as well as draws the button
        def __init__(self, position, size, text, call, color=Constants.marigold):
            PygameObject.__init__(self, pos=position)
            self.text = text
            self.size = size
            self.call = call
            self.buttonColor = Constants.denim
            self.txtColor = color

        def setModeResponse(self, mode):
            self.mode = mode

        def draw(self, surface, dims, offset=(0,0)):
            super().draw(surface, dims, offset)

            coords = self.mToV(self.pos, surface.surf)
            
            bX,bY = (self.pos[0] - self.size[0]/2,
                     self.pos[1] - self.size[1]/2)
            pygame.draw.rect(surface.surf, self.buttonColor,
                    (bX, bY, self.size[0], self.size[1]))
            pygame.draw.rect(surface.surf, (0,0,0),
                    (bX, bY, self.size[0], self.size[1]), 1)

            dfont = pygame.font.SysFont("arial", 40)
            sizeText = dfont.size(self.text)
            label = dfont.render(
                self.text,
                1, self.txtColor)
            surface.surf.blit(label,
                (self.pos[0] - sizeText[0]/2,
                    self.pos[1] - sizeText[1]/2))

        def mousePressed(self, surface, x, y):
            super().mousePressed(surface, x, y)

            xr, yr = self.vToM((x,y), surface.surf)
            topBound = self.pos[1] - self.size[1]/2
            bottomBound = self.pos[1] + self.size[1]/2
            leftBound = self.pos[0] - self.size[0]/2
            rightBound = self.pos[0] + self.size[0]/2

            # Check click is on box
            if (xr < rightBound and xr > leftBound and
                yr < bottomBound and yr > topBound):
                #print("%s clicked!" % self.text)
                self.call(self.mode)
            

    ###############################################

    def drawWelcome(self):
        txtColor = Constants.denim
        
        msg = "Welcome!"
        offset = 40
        margin = 15
        welcomeSize = 80

        dfont = pygame.font.SysFont("arial", welcomeSize)
        sizeText = dfont.size(msg)
        label = dfont.render(
                msg,
                1, txtColor)
        textPos = (self.surfDims[0]/2 - sizeText[0]/2,
                    sizeText[1]/2 + offset)
        self.mainSurf.surf.blit(label,textPos)
       
        msg = "Click an operation mode below to enter"
        yPos = textPos[1] + sizeText[1] + margin
        subSize = 28

        dfont = pygame.font.SysFont("arial", subSize)
        sizeText = dfont.size(msg)
        label = dfont.render(
                msg,
                1, txtColor)
        self.mainSurf.surf.blit(label,
                (self.surfDims[0]/2 - sizeText[0]/2, yPos))

    def drawView(self, screen):
        self.mainSurf.surf.fill(self.bk)
        self.drawWelcome()
        self.mainSurf.drawObjects() # This is what will draw the buttons

        super().drawView(screen)

    def mousePressed(self, event):
        self.mainSurf.mouseObjects(event, (0,0)) # Pass mouse event down

    def keyPressed(self, event):
        super().keyPressed(event)

        pass

class NavigateMode(PygameMode):
    def __init__(self, call):
        self.bk = Constants.backdrop
        PygameMode.__init__(self,screenDims=(1000,800),bkcolor=self.bk,
                changeModeFn=call)
        self.mainSurf = SurfacePlus()
        self.mainSurf.surf = pygame.Surface(self.screenDims)
        self.surfDims = self.mainSurf.surf.get_size()
        self.surfaces.append(self.mainSurf)

        self.localize = localization_engine.LocalizationEngine()
        self.localize.daemon = True
        self.localize.start()

        self.waiting = False
        self.startWaiting = 0

        self.entryText = ""

    ###############################################

    def requestRouteTo(self):
        # Check if valid location
        dests = self.localize.router.segTable.collection.distinct("NOTE")
        if (self.entryText not in dests):
            return

        self.localize.beginLocalization(3, self.route)
        # Now wait for localization engine to complete and do callback
        self.waiting = True
        self.startWaiting = time.time()

    def route(self, fromPos):
        locA = fromPos
        locB = self.entryText

        self.waiting = False

        floor = (int(fromPos[2]/Constants.floorHeight) + 1)
        viewPos = (fromPos[0], fromPos[1], floor)
        self.changeModeFn("Routing", args=(locA,locB,viewPos))
        

    ###############################################

    def drawTextBox(self):
        prompt = "Room"
        pos = (0,50)
        bSize = (500,40)

        surfSize = self.mainSurf.surf.get_size()
        xMid, yMid = surfSize[0]//2-pos[0], surfSize[1]//2-pos[1]
        pygame.draw.rect(self.mainSurf.surf,(255,255,255),
                (xMid-bSize[0]//2, yMid-bSize[1]//2,
                    bSize[0], bSize[1]))
        
        pygame.draw.rect(self.mainSurf.surf,(0,0,0),
                (xMid-bSize[0]//2, yMid-bSize[1]//2,
                    bSize[0], bSize[1]), 1)

        fSize = 20
        buf = (bSize[1] - fSize)/2
        dfont = pygame.font.SysFont("monospace", fSize)
        xText = xMid - bSize[0]//2 + buf
        yText = yMid - bSize[1]//2 + fSize / 2 
        # Center text in box
        label = dfont.render(
                "%s: %s" % (prompt,self.entryText),
                1, (10,10,10))
        self.mainSurf.surf.blit(label, (xText,yText))

    def drawWelcome(self):
        msg = "Navigate"
        offset = 40
        margin = 15
        navSize = 80

        dfont = pygame.font.SysFont("arial", navSize)
        sizeText = dfont.size(msg)
        label = dfont.render(
                msg,
                1, Constants.titleText)
        textPos = (self.surfDims[0]/2 - sizeText[0]/2,
                    sizeText[1]/2 + offset)
        self.mainSurf.surf.blit(label,textPos)
       
        msg = "Type your intended destination below"
        yPos = textPos[1] + sizeText[1] + margin
        subSize = 28

        dfont = pygame.font.SysFont("arial", subSize)
        sizeText = dfont.size(msg)
        label = dfont.render(
                msg,
                1, Constants.titleText)
        self.mainSurf.surf.blit(label,
            (self.surfDims[0]/2 - sizeText[0]/2, yPos))

    def drawWaiting(self):
        msg = "Localizing"
        curTime = time.time() - self.startWaiting
        dots = (int(curTime))%3
        msg += '.'*(dots+1)
        fSize = 50

        offset = 100
        dfont = pygame.font.SysFont("arial", fSize)
        sizeText = dfont.size(msg)
        label = dfont.render(
                msg,
                1, Constants.titleText)
        textPos = (self.surfDims[0]/2 - sizeText[0]/2,
                    self.surfDims[1] - sizeText[1] - offset)
        self.mainSurf.surf.blit(label,textPos)

    def drawView(self, screen):
        self.mainSurf.surf.fill(self.bk)
        self.drawWelcome()
        self.drawTextBox()
        if self.waiting:
            self.drawWaiting()

        super().drawView(screen)

    def mousePressed(self, event):
        self.mainSurf.mouseObjects(event, (0,0))

    def keyPressed(self, event):
        super().keyPressed(event)

        shift = pygame.key.get_mods() & pygame.KMOD_SHIFT
        if event.key == pygame.K_ESCAPE:
            self.changeModeFn()
        elif event.key == pygame.K_BACKSPACE:
            self.entryText = self.entryText[:-1]
        elif event.key == pygame.K_RETURN:
            self.requestRouteTo()
        elif event.key < 127: # Put this char into the text box
            char = event.key
            if shift: char -= 32
            self.entryText += chr(char)

