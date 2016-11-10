import threading
import os, sys, time
import pygame
import color_constants

if not pygame.font: print ('Warning, fonts disabled')
if not pygame.mixer: print ('Warning, sound disabled')

class MainPygame(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        pygame.init()
        self.lock = threading.RLock()
        self.alive = True
        self.modes = {}
        self.modes['default'] = PygameMode()
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
            self.screen = pygame.display.set_mode(self.currentMode.screenDims,
                    pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)
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
    def __init__(self, screenDims=(640,400), fps=60, bkcolor=(100,100,100)):
        threading.Thread.__init__(self)
        self.fps = fps
        self.bkcolor = bkcolor
        self.screenDims = screenDims
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
        # Override this!
        pass

    def terminate(self):
        quit()

    def handleEvents(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mousePressed(event)
            if event.type == pygame.KEYDOWN:
                self.keyPressed(event)

    def addSurface(self, surface):
        self.surfaces.append(surface)

    def removeSurface(self, surface):
        self.surfaces.remove(surface)

    def getSurface(self, i):
        return self.surfaces[i]

class SurfacePlus(object):
    def __init__(self):
        self.surf = None
        self.offset = [0,0]
        self.name = ""
