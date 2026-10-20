
class Player:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.money = 500
        self.position = 0
        self.properties = []
        self.in_jail = False
        self.free_jail_cards = 0
        self.alive = True

    def move(self, steps, board_size):
        self.position = (self.position + steps) % board_size
