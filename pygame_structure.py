import threading
import os, sys, time
import pygame
import color_constants
from mapcmu_data import *

if not pygame.font: print ('Warning, fonts disabled')
if not pygame.mixer: print ('Warning, sound disabled')

class MainPygame(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        pygame.init()
        pygame.display.set_caption("MapCMU")
        self.lock = threading.RLock()
        self.alive = True
        self.modes = {}
        self.modes['default'] = BootingMode()
        self.currentMode = self.modes['default']

    def __sleepFPS(self, fps, start, end):
        delta = end - start
        target = 1.0/fps
        time.sleep(target-delta if target-delta > 0 else 0)
    
    def terminate(self):
        self.alive = False
    
    def run(self):
        self.lock.acquire()
        try:
            self.screen = pygame.display.set_mode(self.currentMode.screenDims)
        finally:
            self.lock.release()

        self.__mainloop()

    def __mainloop(self):
        while self.alive:
            if (isinstance(self.currentMode, PygameMode)):
                start = time.time()
                self.lock.acquire()
                
                try:
                    #info = pygame.display.Info()
                    #if (info.current_h != self.dimQueue[1] or
                    #    info.current_w != self.dimQueue[0]):
                    #    self.screen = pygame.display.set_mode(self.dimQueue,
                    #        pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)

                    self.currentMode.drawView(self.screen)
                    self.currentMode.handleEvents(pygame.event.get())
                
                    pygame.display.flip()
                finally:
                    self.lock.release()

                end = time.time()
                self.__sleepFPS(self.currentMode.fps, start,end)
            else:
                time.sleep(.05)

    def addMode(self, pygameMode, name):
        self.modes[name] = pygameMode

    def useMode(self, name):
        self.lock.acquire()
        try:
            self.currentMode = self.modes[name]
            self.dimQueue = self.currentMode.screenDims
            self.screen = pygame.display.set_mode(self.currentMode.screenDims,
                pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)
        finally:
            self.lock.release()

    def getMode(self, name):
        return self.modes[name]

    def getPygame(self):
        return pygame

class PygameMode():
    def __init__(self, screenDims=(640,400), fps=60, 
            bkcolor=(100,100,100), changeModeFn=None):
        threading.Thread.__init__(self)
        self.fps = fps
        self.bkcolor = bkcolor
        self.screenDims = screenDims
        self.changeModeFn = changeModeFn
        self.initView()

    def initView(self):
        self.surfaces = []
        background = pygame.Surface(self.screenDims)
        background.fill(self.bkcolor)
        self.surfaces.append(background)
      
    def drawView(self, screen):        
        for surface in self.surfaces:
            #print("Mode: %s Surface: %s" % (self.currentMode, surfaceKey))
            if (isinstance(surface, pygame.Surface)):
                surface.convert()
                screen.blit(surface, (0,0))
            elif (isinstance(surface, SurfacePlus)):
                surface.surf.convert()
                screen.blit(surface.surf, (0,0)) #(surface.offset[0],surface.offset[1]))

    def mousePressed(self, event):
        # Override this!
        pass

    def keyPressed(self, event):
        # Override this! (and call super)
        ctrl = pygame.key.get_mods() & pygame.KMOD_CTRL
        if (event.key == pygame.K_c and ctrl):
            quit()
        

    def terminate(self):
        quit()

    def handleEvents(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mousePressed(event)
            if event.type == pygame.KEYDOWN:
                self.keyPressed(event)
            if event.type == pygame.QUIT:
                quit()

    def addSurface(self, surface):
        self.surfaces.append(surface)

    def removeSurface(self, surface):
        self.surfaces.remove(surface)

    def getSurface(self, i):
        return self.surfaces[i]

class PygameObject(object):
    def __init__(self, pos=(0,0), mToV=lambda *x:x[0], vToM=lambda *x:x[0]):
        self.mToV = mToV
        self.vToM = vToM
        self.objects = []
        self.pos = pos
        self.initData()
        pass

    def initData(self):
        pass

    '''Override'''
    def draw(self, surface, dims, offset=(0,0)):
        for obj in self.objects:
            obj.draw(surface, dims, offset)
    
    '''Override'''
    def mousePressed(self, surface, x, y):
        for obj in self.objects:
            obj.mousePressed(surface, x, y)

class SurfacePlus(object):
    def __init__(self):
        self.surf = None
        self.name = ""
        self.objects = []

    def drawObjects(self, offset=(0,0)):
        for obj in self.objects:
            obj.draw(self, self.surf.get_size(), offset)

    def mouseObjects(self, event, offset):
        for obj in self.objects:
            obj.mousePressed(self, event.pos[0],
                    event.pos[1])

class BootingMode(PygameMode):
    def __init__(self, screenDims=(1000,800), bkcolor=(200,200,200)):
        PygameMode.__init__(self,screenDims=screenDims,bkcolor=bkcolor)
        self.mainSurf = SurfacePlus()
        self.mainSurf.surf = pygame.Surface(self.screenDims)
        self.surfaces.append(self.mainSurf)

        self.map2image = pygame.image.load("splash.jpg")
        self.map2Rect = self.map2image.get_rect()

    def drawView(self, screen):
        #self.mainSurf.surf.fill((0,255,255))
        self.mainSurf.surf.blit(self.map2image, 
                 pygame.Rect(0, 0,
                 self.map2Rect.w, self.map2Rect.h))

        super().drawView(screen)

