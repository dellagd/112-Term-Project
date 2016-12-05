import pygame

class TextInputBox(object):
    def __init__(self, pos=(0,0), color=(180,255,180)):
        self.enabled = False
        self.pos = pos

        self.size = 400,150
        self.bSize = 360,40
        self.bOffset = 20
        self.color = color
    
        self.text = ""
        self.prompt = ""

        self.callback = None

    def doPopup(self, question, callback, args=()):
        self.prompt = question
        self.callback = callback
        self.callArgs = args
        self.enabled = True

    def drawBox(self, surface):
        surfSize = surface.get_size()
        xMid, yMid = surfSize[0]//2-self.pos[0], surfSize[1]//2-self.pos[1]
        pygame.draw.rect(surface,self.color,
                (xMid-self.size[0]//2, yMid-self.size[1]//2,
                    self.size[0], self.size[1]))

        pygame.draw.rect(surface,(255,255,255),
                (xMid-self.bSize[0]//2, yMid-self.bSize[1]//2 + self.bOffset,
                    self.bSize[0], self.bSize[1]))
        
        pygame.draw.rect(surface,(0,0,0),
                (xMid-self.bSize[0]//2, yMid-self.bSize[1]//2 + self.bOffset,
                    self.bSize[0], self.bSize[1]), 1)

        fSize = 20
        buf = (self.bSize[1] - fSize)/2
        dfont = pygame.font.SysFont("monospace", fSize)
        xText = xMid - self.bSize[0]//2 + buf
        yText = yMid - self.bSize[1]//2 + self.bOffset + fSize / 2 
        # Center text in box
        label = dfont.render(
                "%s: %s" % (self.prompt,self.text),
                1, (10,10,10))
        surface.blit(label, (xText,yText))

        fSize = 20
        buf = 10
        instr = "Please type your response"
        dfont = pygame.font.SysFont("monospace", fSize)
        xText = xMid - dfont.size(instr)[0]/2
        yText = yMid - self.bSize[1]//2 - self.bOffset 
        label = dfont.render(
                instr,
                1, (10,10,10))
        surface.blit(label, (xText,yText))
       
    def doCallback(self):
        args = (self.text,) + self.callArgs
        self.callback(*args)
        self.text = ""
        self.prompt = ""
        self.enabled = False

    def keyPressed(self, event):
        shift = pygame.key.get_mods() & pygame.KMOD_SHIFT
        if event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        elif event.key == pygame.K_RETURN:
            self.doCallback()
        elif event.key < 127: # An alpha key
            char = event.key
            if shift: char -= 32
            self.text += chr(char)
        



                

