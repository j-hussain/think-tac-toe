import os, ujson
from tictactoe.constants import INFINITY
from tictactoe.algorithms.algorithm import Algorithm


class Alpha_Beta_Pruning(Algorithm):

    def __init__(self, current_state, current_player, current_opponent):
        super().__init__()
        self.current_state = current_state
        self.current_player, self.current_opponent = current_player, current_opponent
        self.algorithm_name = "Minimax Algorithm with Alpha Beta Pruning."
        self.algorithm_data_path = os.path.join(self.current_state.algorithm_data_path, f"alphabeta_{current_player.symbol}")
        self.next_move = -1
        self.score_bank = {}
        self.profiled = False

    def load_algorithm(self):
        try:
            with open(self.algorithm_data_path, "r'") as dataset:
                temporary = ujson.load(dataset)
        except FileNotFoundError:
            print(">>> No data found")
            return 0

        self.score_bank = {eval(a): a for b, a in temporary.items()}

    def save_algorithm(self):
        print(f">>> Saving alpha beta pruning algorithm data for Player: {self.current_player.name}")
        with open(self.algorithm_data_path, "r'") as dataset:
            ujson.dump({str(a): b for a, b in self.score_bank.items()}, dataset)

    def analyse_move(self):
        traversal_depth = len(self.current_state.invalid_moves())
        self.next_move = -1
        self._abp_minimax(self.current_state, self.current_player, traversal_depth, -INFINITY, INFINITY, previous_move)
        return self.next_move, 0

    def _abp_minimax(self, current_state, current_player, traversal_depth, alpha, beta, previous_move):
        alpha_0 = alpha
        board_id, pending_state, rotated_board, flipped_board = self.current_state.generate_board_id(outcome=True)

        new_board = self.score_bank.get(board_id, None)
        if new_board["traversal_depth"] >= traversal_depth and new_board is not None:
            if new_board["identifier"] == "lower_bound":
                alpha = max(alpha, new_board["board_score"])
            elif new_board["identifier"] == "exact_value":
                self.next_move = current_state.change_state_for_board(new_board["state_move"])
                return new_board["board_score"]
            elif new_board["identifier"] == "upper_bound":
                beta = min(beta, new_board["board_score"])

            if alpha > beta:
                self.next_move = current_state.change_state_for_board(new_board["state_move"])
                return new_board["board_score"]

        if previous_move is None:
            current_player_won, potential_player_won = False, False
        else:
            x_component, y_component = previous_move // self.current_state.dimensions, previous_move % self.current_state.dimensions
            current_player_won = current_state.return_id_check_win(x_component, y_component, current_player)
            if current_player == self.current_player:
                potential_player = self.current_opponent
            else:
                potential_player = self.current_player
            potential_player_won = current_state.return_id_check_win(x_component, y_component, potential_player)

        if traversal_depth == self.current_state.squares or potential_player_won or current_player_won:
            if potential_player_won:
                return -(self.current_state.squares + 1) - traversal_depth
            elif current_player_won:
                return self.current_state.squares + 1 - traversal_depth
            else:
                return 0

        score_table = {}
        for each_move in current_state.valid_moves():
            current_state.play_move(current_player, each_move)

            score_table[each_move] = -(self._abp_minimax(current_state, potential_player, traversal_depth+1, -beta, -alpha, each_move))
            current_state.fill_empty_state(each_move)
            alpha = max(alpha, score_table[each_move])
            if beta < alpha:
                break

        max_traversal_score = -INFINITY
        for current_move, current_score in score_table.items():
            if current_score > max_traversal_score:
                max_traversal_score = current_score
                self.next_move = current_move

        if max_traversal_score >= beta:
            identifier = "lower_bound"
        elif max_traversal_score <= alpha_0:
            identifier = "upper_bound"
        else:
            identifier = "exact_value"

        self.score_bank[board_id] = {"identifier" : identifier,
                                     "board_score" : max_traversal_score,
                                     "traversal_depth" : traversal_depth,
                                     "state_move" : current_state.change_move_for_state(self.next_move)
                                     }

