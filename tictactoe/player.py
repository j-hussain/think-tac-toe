from random import choice
from tictactoe.constants import PLAYING_TACTIC, NOUGHT, CROSS

class Player:

    def __init__(self, algorithm, player_piece):
        """
        :param algorithm: the algorithm that the computer will be using
        :param player_piece: whether the computer is a nought or a cross

        playing_tactic uses the following: PLAYING_TACTIC = ["LEARN", "EXPLOIT", "RANDOM MOVE"]
        """
        self.algorithm = algorithm
        self.player_piece = player_piece
        self.playing_tactic = PLAYING_TACTIC[0]

        if self.player_piece == NOUGHT:
            self.player_piece = "O"
            self.player_name = "Nought"
        else:
            self.player_piece = "X"
            self.player_name = "Cross"

    def _set_playing_tactic(self, playing_tactic):
        self.playing_tactic = playing_tactic

    def analyse_move(self):
        """
        This function checks whether or not the AI will be randomly allocating moves. If it isn't,
        then it runs the analyse_move function for the respective algorithm
        :return:
        """
        if self.playing_tactic == PLAYING_TACTIC[2]:
            return choice(self.algorithm.current_state.valid_moves()), 0
        else:
            return self.algorithm.analyse_move()