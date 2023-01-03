import copy
import itertools
import os
from math import inf

import numpy as np

import constants


class Board:

    def __init__(self, configuration):
        self.board = None

        self.player_x = None
        self.player_o = None

        self.configuration = configuration
        self.size = configuration["size"]
        self.squares = configuration["squares"]
        self.symbols_needed = configuration["symbols_needed"]

        # Create brain folders
        brain_path = os.path.join("brain_data", "{}x{}".format(self.size, self.size))
        if not os.path.exists(brain_path):
            print("No save folder found for {}x{} board. Creating folder now.".format(self.size, self.size))
            os.mkdir(brain_path)

        self.brain_data_folder = os.path.join("brain_data", "{size}x{size}".format(size=self.size))

        # Reset board
        self.reset()

    def reset(self):
        self.board = np.full((self.size, self.size), constants.EMPTY)

    def play(self, player, move):
        # Split index components into x & y
        x, y = move // self.size, move % self.size

        # If there is already a piece in this place, throw an error.
        if self.board[x, y] != constants.EMPTY:
            raise IndexError("Invalid board move passed. Attempted move: {}".format(move))

        # Set board symbol in internal array
        self.board[x, y] = player.symbol

        # Initialise return parameters
        game_winner = None
        game_end = False
        
        # Check if this move has resulted in a win
        if self.check_win(x, y, player):
            game_end = True
            game_winner = player
        # Check whether the board is now full, if so, the game is a draw.
        elif self.is_full():
            game_end = True
            game_winner = constants.DRAW

        # Return whether the game has ended and the winner.
        return game_end, game_winner

    def set_empty(self, move):
        # Split index components into x & y
        x, y = move // self.size, move % self.size

        self.board[x, y] = constants.EMPTY

    def check_win(self, x, y, player):
        # Check for win

        def check_consecutive(piece_list):
            # Converts 0, 2, 2, 1, 2, 2, 2
            # Into
            # (0, 1), (2, 2), (1, 1), (2, 3)
            # (Symbol, Amount)
            grouped_list = [(k, sum(1 for i in g)) for k, g in itertools.groupby(piece_list)]

            for consecutive_tuple in grouped_list:
                if consecutive_tuple[0] == player.symbol and consecutive_tuple[1] >= self.symbols_needed:
                    return True

        # Check row
        row_list = list(self.board[x, :])
        if check_consecutive(row_list):
            return True

        # Check vertical
        column_list = list(self.board[:, y])
        if check_consecutive(column_list):
            return True

        # Check diagonals
        # Check left to right
        diagonal = list(np.diag(self.board, y - x))
        # indices = list(np.diag_indices(self.board, y-x))
        if check_consecutive(diagonal):
            return True

        # Flip the board as we can only check left to right
        board_flip = np.flip(self.board, 1)

        # Also calculate board_index for new board
        # The row remains the same, however the column is now board_size - current column - 1
        y = self.size - 1 - y

        diagonal = list(np.diag(board_flip, y - x))
        if check_consecutive(diagonal):
            return True

        return False

    def is_full(self):
        return constants.EMPTY not in self.board

    def is_empty(self):
        return len(self.get_valid_moves()) == (self.squares)

    def symbol_formatter(self, symbol):
        if symbol == constants.EMPTY:
            return " "
        elif symbol == constants.NOUGHT:
            return "O"
        else:
            return "X"

    def display(self):
        # Form rows of formatting {}s connected by |
        rows = []
        for i in range(self.size):
            row = [" {} "] * self.size
            rows.append("|".join(row) + "\n")

        # Add in-between lines
        board = (("----" * self.size) + "\n").join(rows)

        # Convert CROSS to X etc.
        board_symbols = (self.symbol_formatter(symbol) for symbol in list(self.board.flatten()))

        # Print the string with the symbols then formatted
        print(board.format(*board_symbols))

    def get_identifier(self, return_details = False):
        # Calculate the SUM_X/SUM_Y for board and return in tuple form
        # Rotate board 4 times and find minimum value for state
        # Implementation of Sebestian Siegel's "ECE 539 Term Project" algorithm

        # State board information
        sum_x = inf
        sum_o = inf
        board_flip = 0
        board_rotate = 0
        best_board = None

        # Consider unflipped & flipped
        for flip in range(2):
            # Clone board so that we do not modify object's board
            board_copy = copy.copy(self.board)

            # On second iteration of loop, flip the board
            if flip == 1:
                board_copy = np.flip(board_copy, 0)

            # Consider 4 rotations
            for rotation in range(0, 4):
                # Board information
                board_sum_x = 0
                board_sum_o = 0

                # Whether we should change state board variables
                set_board = False

                # Determine sum_x & sum_o
                for index, value in enumerate(board_copy.flatten()):
                    if value == 1:
                        board_sum_x += 0.5 ** (index + 1)
                    elif value == -1:
                        board_sum_o += 0.5 ** (index + 1)

                # Check whether the sum for this board is lower than the previous smallest sum
                if board_sum_x < sum_x:
                    set_board = True
                elif sum_x == board_sum_x:
                    # Sum X and temp are the same, check O values
                    if board_sum_o < sum_o:
                        set_board = True

                if set_board:
                    # This board is the new reference
                    sum_x = board_sum_x
                    sum_o = board_sum_o
                    board_rotate = rotation
                    board_flip = flip
                    best_board = copy.copy(board_copy)

                # Rotate board
                board_copy = np.rot90(board_copy)

        # Determine whether to return all state information or just the ID
        if return_details:
            state_board = Board(self.configuration)
            state_board.board = best_board

            return (sum_x, sum_o), state_board, board_rotate, board_flip
        else:
            return (sum_x, sum_o)
        
    def get_current_player(self):
        # If it's X's turn, there will be the same amount of Xs as Os

        x_count, o_count = 0, 0
        for symbol in list(self.board.flatten()):
            if symbol == constants.CROSS:
                x_count += 1
            elif symbol == constants.NOUGHT:
                o_count += 1

        return self.player_x if o_count == x_count else self.player_o

    def get_inactive_player(self):
        return self.player_x if self.get_current_player() == self.player_o else self.player_o
    
    def get_valid_moves(self):
        # Return moves that do not contain a player
        return list(index for index, symbol in enumerate(list(self.board.flatten())) if symbol == constants.EMPTY)

    def get_invalid_moves(self):
        # Return moves that already contain a player
        return list(index for index, symbol in enumerate(list(self.board.flatten())) if symbol != constants.EMPTY)

    def board_move_to_state(self, move):
        # Check if valid move is passed
        if move < 0:
            raise Exception("Invalid board move passed: {}".format(move))

        moves = [0] * self.squares

        # Action 2 does not mean move 2 for our state board
        board_identifier, state_board, board_rotate, board_flip = self.get_identifier(return_details=True)

        # In our temporary array, set our move to be converted to 1. We will then later get the index of this 1 to
        # return our new move.
        moves[move] = 1
        moves = np.array(moves)
        moves.resize((self.size, self.size))

        # Flip board if needed
        if board_flip:
            moves = np.flip(moves, 0)

        # Rotate however many times required
        moves = np.rot90(moves, board_rotate)

        # Convert moves back into a list then return index of the 1
        moves = list(moves.flatten())
        return moves.index(1)

    def state_move_to_board(self, move):
        # Check if valid move is passed
        if move < 0:
            raise Exception("Invalid state move passed: {}".format(move))

        moves = [0] * self.squares

        # State move 2 does not mean move 2 for our current board
        board_identifier, state_board, board_rotate, board_flip = self.get_identifier(return_details=True)

        # In our temporary array, set our move to be converted to 1. We will then later get the index of this 1 to
        # return our new move.
        moves[move] = 1
        moves = np.array(moves)
        moves.resize((self.size, self.size))

        # Rotate the board in the other direction (as we're doing the inverse of the board -> state moves)
        moves = np.rot90(moves, -board_rotate)

        # Flip board if needed after rotations (as we're doing the inverse of the board -> state moves)
        if board_flip:
            moves = np.flip(moves, 0)

        # Convert moves back into a list then return index of the 1
        moves = list(moves.flatten())
        return moves.index(1)
