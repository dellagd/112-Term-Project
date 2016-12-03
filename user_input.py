import pygame

class TextInputBox(object):
    def __init__(self):
        self.size = 400,150
        self.bSize = 360,40
        self.bOffset = 20
        self.color = (180,255,180)
    
    def drawBox(self, surface):
        surfSize = surface.get_size()
        xMid, yMid = surfSize[0]//2, surfSize[1]//2
        pygame.draw.rect(surface,self.color,
                (xMid-self.size[0]//2, yMid-self.size[1]//2,
                    self.size[0], self.size[1]))

        pygame.draw.rect(surface,(0,0,0),
                (xMid-self.bSize[0]//2, yMid-self.bSize[1]//2 + self.bOffset,
                    self.bSize[0], self.bSize[1]), 1)


                

