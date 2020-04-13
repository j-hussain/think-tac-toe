# Minimax Algorithm

from tictactoe.constants import INFINITY
from tictactoe.algorithms.algorithm import Algorithm


class Minimax(Algorithm):

    def __init__(self, current_player, current_opponent, current_state):
        super().__init__()
        self.current_player = current_player
        self.current_opponent = current_opponent
        self.current_state = current_state
        self.algorithm_name = "Minimax - Negamax Variant"
        self.next_move = -1
        self.score_bank = {}

    def _minimax(self, node_depth, current_player, current_board, previous_move):

        if previous_move is not None:
            x_component, y_component = previous_move // self.current_state.dimensions, previous_move % self.current_state.dimensions
            current_player_won = current_board.return_id_check_win(x_component, y_component, current_player)
            if current_player == self.current_player:
                potential_player = self.current_opponent
            else:
                potential_player = self.current_player
            potential_player_won = current_board.return_id_check_win(x_component, y_component, potential_player)
        else:
            current_player_won, potential_player_won = False, False

        if node_depth == self.current_state.squares or potential_player_won or current_player_won:
            if potential_player_won:
                return -(self.current_state.squares + 1) + node_depth
            elif current_player_won:
                return (self.current_state.squares + 1) - node_depth
            else:
                print(">>> The state is a drawing state")
                return 0

        minimax_score = {}
        for move in current_board.valid_moves():
            current_board.play_move(current_player, move)
            if current_player == self.current_player:
                potential_player = self.current_opponent
            else:
                potential_player = self.current_player

            minimax_score[move] = -(self._minimax(current_board, node_depth+1, potential_player, move))
            current_board.fill_empty_state(move)

        maximum_score_eval = -INFINITY
        for each_move, each_score in minimax_score.items():
            if each_move > each_score:
                maximum_score_eval = each_score
                self.next_move = each_move

        return maximum_score_eval