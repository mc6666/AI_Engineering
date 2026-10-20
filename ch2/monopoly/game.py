
import pygame
from settings import *
from board import Board
from player import Player
from dice import Dice
from ui import Button

class Game:

    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("arial", 22)

        self.board = Board()
        self.dice = Dice()

        self.players = [
            Player("P1", (255,0,0)),
            Player("P2", (0,0,255))
        ]

        self.current = 0
        self.message = "Monopoly Started"

        self.roll_btn = Button(900,200,200,60,"ROLL")
        self.buy_btn = Button(900,300,200,60,"BUY")
        self.house_btn = Button(900,400,200,60,"BUILD")

    def current_player(self):
        return self.players[self.current]

    def next_turn(self):
        self.current = (self.current + 1) % len(self.players)

    def roll(self):
        player = self.current_player()
        steps = self.dice.roll()
        player.move(steps, len(self.board.tiles))
        self.message = f"{player.name} rolled {steps}"
        self.next_turn()

    def buy_property(self):
        self.message = "Buy property feature"

    def build_house(self):
        self.message = "Build house feature"

    def draw_board(self):
        margin = 50
        size = 100

        for i in range(len(self.board.tiles)):
            x = margin + (i % 4) * size
            y = margin + (i // 4) * size

            pygame.draw.rect(self.screen, (180,180,180), (x,y,size,size))
            txt = self.font.render(self.board.tiles[i], True, (0,0,0))
            self.screen.blit(txt, (x+5,y+5))

        for p in self.players:
            x = margin + (p.position % 4) * size
            y = margin + (p.position // 4) * size

            pygame.draw.circle(self.screen, p.color, (x+50,y+50), 15)

    def draw_ui(self):
        self.roll_btn.draw(self.screen, self.font)
        self.buy_btn.draw(self.screen, self.font)
        self.house_btn.draw(self.screen, self.font)

        msg = self.font.render(self.message, True, (255,255,0))
        self.screen.blit(msg, (50,700))

    def update(self):
        self.screen.fill((30,30,30))
        self.draw_board()
        self.draw_ui()
