
import pygame
from settings import *
from game import Game

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Monopoly")

clock = pygame.time.Clock()

game = Game(screen)

running = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

        if event.type == pygame.MOUSEBUTTONDOWN:

            if game.roll_btn.clicked(event.pos):
                game.roll()

            if game.buy_btn.clicked(event.pos):
                game.buy_property()

            if game.house_btn.clicked(event.pos):
                game.build_house()

    game.update()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
