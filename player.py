import random

from constants import *


class Player:

    def __init__(self, symbol, brain):
        self.symbol = symbol
        self.brain = brain
        self.mode = SMART

        if self.symbol == CROSS:
            self.name = "Cross"
            self.symbol_string = "x"
        else:
            self.name = "Nought"
            self.symbol_string = "o"
            
    def get_move(self):
        if self.mode == SMART or self.mode == TRAIN:
            return self.brain.get_move()
        elif self.mode == RANDOM:
            return random.choice(self.brain.board.get_valid_moves()), 0

    def set_mode(self, mode):
        self.mode = mode
        
