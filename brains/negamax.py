from math import inf

from brains.brain import Brain


class Brain_Negamax(Brain):

    def __init__(self, player, opp_player, board):
        super().__init__()
        self.player = player
        self.opp_player = opp_player
        self.board = board

        self.name = "Negamax"

        self.board_move = -1

        # Initialise saved scores (result from minimax)
        self.saved_scores = {}

    def get_move(self):
        depth = len(self.board.get_invalid_moves())

        # Pass in current player
        self.board_move = -1

        self.negamax(self.board, depth, self.player, None)

        return self.board_move, 0

    # Player is the current player we are analysing
    def negamax(self, board, depth, player, last_played):
        # Check for win/end of game
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
            scores[index] = -self.negamax(board, depth + 1, opp_player, index)

            # Undo the move we previously added
            board.set_empty(index)

        # Iterate through each of the scores and pick the maximum
        max_score = -inf

        for move, score in scores.items():
            if score > max_score:
                max_score = score
                self.board_move = move

        return max_score
