
import pygame

class Button:
    def __init__(self, x,y,w,h,text,color=(70,130,180)):
        self.rect = pygame.Rect(x,y,w,h)
        self.text = text
        self.color = color

    def draw(self, screen, font):
        pygame.draw.rect(screen, self.color, self.rect)
        txt = font.render(self.text, True, (255,255,255))
        screen.blit(txt, (self.rect.x+10, self.rect.y+10))

    def clicked(self, pos):
        return self.rect.collidepoint(pos)
