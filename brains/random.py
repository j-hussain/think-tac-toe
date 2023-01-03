import random

from brains.brain import Brain


class Brain_Random(Brain):

    def __init__(self, player, opp_player, board):
        super().__init__()
        self.player = player
        self.opp_player = opp_player
        self.board = board

        self.name = "Random"

    def get_move(self):
        # Pick random move
        board_action = random.choice(self.board.get_valid_moves())

        return board_action, self.board.board_move_to_state(board_action)
