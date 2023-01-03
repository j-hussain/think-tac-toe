import os
import time
import ujson as json
from math import inf

from brains.brain import Brain


class Brain_Negamax_ABP(Brain):

    def __init__(self, player, opp_player, board):
        super().__init__()
        self.player = player
        self.opp_player = opp_player
        self.board = board

        self.name = "Negamax with ABP"

        # Initialise saved scores (result from minimax)
        self.saved_scores = {}
        self.board_move = -1

        self.data_file = os.path.join(self.board.brain_data_folder,
                                      "abp_moves_{}.json".format(self.player.symbol_string))

        self.profile = False

    def get_move(self):
        depth = len(self.board.get_invalid_moves())

        self.board_move = -1

        # Pass in current player
        self.negamax(self.board, depth, self.player, None, -inf, inf)

        return self.board_move, 0

    # Player is the current player we are analysing
    def negamax(self, board, depth, player, last_played, alpha, beta):
        alpha_original = alpha

        board_identifier, state_board, board_rotate, board_flip = board.get_identifier(return_details=True)

        # Check if we have a saved score for this node
        entry = self.saved_scores.get(board_identifier, None)

        # Check if score is valid
        if entry is not None and entry["depth"] >= depth:
            if entry["flag"] == "exact":
                # Update board_move with entry's data
                self.board_move = board.state_move_to_board(entry["state_move"])

                return entry["score"]
            elif entry["flag"] == "lowerbound":
                alpha = max(alpha, entry["score"])
            elif entry["flag"] == "upperbound":
                beta = min(beta, entry["score"])

            if alpha > beta:
                # Update best_move with entry's data
                self.board_move = board.state_move_to_board(entry["state_move"])

                return entry["score"]

        if last_played is not None:
            x, y = last_played // self.board.size, last_played % self.board.size

            current_player_won = board.check_win(x, y, player)
            inactive_player_won = board.check_win(x, y, self.opp_player if player == self.player else self.player)
        else:
            current_player_won = False
            inactive_player_won = False

        # Check if node is terminal
        if depth == self.board.squares or current_player_won or inactive_player_won:
            # If our current player won, we need our score to be positive.
            if current_player_won:
                return (self.board.squares + 1) - depth
            # Otherwise, give a negative score.
            elif inactive_player_won:
                return -(self.board.squares + 1) + depth
            else:
                # It was a draw, return zero.
                return 0

        # Store all moves and their scores
        scores = {}

        # Iterate through each possible move
        for index in board.get_valid_moves():
            # Play move
            board.play(player, index)

            opp_player = self.opp_player if player == self.player else self.player

            # Save score
            scores[index] = -self.negamax(board, depth + 1, opp_player, index, -beta, -alpha)

            # Undo the move we previously added
            board.set_empty(index)

            alpha = max(alpha, scores[index])

            # If we can achieve a better score else where in the game tree, stop evaluating this branch
            if alpha > beta:
                break

        # Iterate through each of the scores and pick the maximum
        max_score = -inf

        for move, score in scores.items():
            if score > max_score:
                max_score = score
                self.board_move = move

        # Store result
        if max_score <= alpha_original:
            flag = "upperbound"
        elif max_score >= beta:
            flag = "lowerbound"
        else:
            flag = "exact"

        self.saved_scores[board_identifier] = {
            "flag": flag,
            "score": max_score,
            "depth": depth,
            "state_move": board.board_move_to_state(self.board_move)
        }

        return max_score

    def save(self):
        time_before = time.time()

        print("Saving ABP data for {}.".format(self.player.name))

        with open(self.data_file, "w") as file:
            # Dump q_table to json file
            json.dump({str(k): v for k, v in self.saved_scores.items()}, file)

        print("Saved {}'s ABP data to {}. {:.1f}s taken to save JSON file.".format(self.player.name, self.data_file,
                                                                                   time.time() - time_before))

    def load(self):
        time_before = time.time()

        print("Loading ABP data for {}.".format(self.player.name))

        try:
            with open(self.data_file, "r") as file:
                # Load ABP data from json file.
                temp = json.load(file)
        except FileNotFoundError:
            print("No ABP data found for {}.".format(self.player.name))
            return

        # Save time taken to load file.
        time_loaded = time.time()

        # Convert string keys to tuples
        self.saved_scores = {eval(k): v for k, v in temp.items()}
        time_finished = time.time()

        print(
            "Successfully loaded ABP data for {}. {:.1f}s taken to load JSON file. {:.1f}s taken to convert key tuples.".format(
                self.player.name, time_loaded - time_before, time_finished - time_loaded))
