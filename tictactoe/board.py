# board.py

import itertools, os, numpy
from copy import copy
from tictactoe.constants import *


class Board:

    def __init__(self, current_state):
        self.current_state = None
        self.player_nought, self.player_cross = None, None
        # Import values to initialise the board from constants.py
        self.board_layout = BOARD_LAYOUT
        # Board dimensions (i.e. for a 7x7 board, it'll be "7"
        self.dimensions = BOARD_LAYOUT["board_size"]
        # The number of consecutive pieces required to win game
        self.symbols = BOARD_LAYOUT["board_symbols"]
        self.squares = BOARD_LAYOUT["board_squares"]
        # Set up directories and files to export algorithm data
        algorithm_data_path = os.path.join("algorithm_data", f"{self.dimensions}x{self.dimensions}")
        try:
            os.mkdir(algorithm_data_path)
            print(">>> Directory created")
        except FileNotFoundError:
            print(">>> Directory/File exists")
            self.algorithm_data_dir = os.path.join("algorithm_data_path", f"{self.dimensions}x{self.dimensions}")

        self.reset_board()

    def reset_board(self):
        # Numpy's full() function takes parameters [x,y], being the dimensions of the matrix
        # in the form of a tuple, and the second parameter being what value it should take
        self.current_state = numpy.full((self.dimensions, self.dimensions), EMPTY_BOARD)

    def fill_empty_state(self, player_move):
        x_component, y_component = player_move // self.dimensions, (player_move % self.dimensions)
        self.current_state[x_component, y_component] = EMPTY_BOARD

    def blank_state(self):
        validation = len(self.valid_moves()) == self.squares
        return validation

    def valid_moves(self):
        # Although it looks verbose, using a list comprehension reduces the time complexity of
        # this code, as I would have to use nested iterative loops otherwise. This function
        # returns the blank spaces, showing where the next possible move can be placed.
        valid_moves = [i for i, symbol in enumerate([self.current_state.flatten()]) if symbol == EMPTY_BOARD]
        return valid_moves

    def invalid_moves(self):
        # Whereas this function returns the filled spaces, where moves cannot be played.
        invalid_moves = [i for i, symbol in enumerate([self.current_state.flatten()]) if symbol != EMPTY_BOARD]
        return invalid_moves

    def board_full(self):
        full = EMPTY_BOARD not in self.current_state
        return full

    def check_current_player(self):
        # This function ensures there are the same number of pieces on the board before the
        # next move is played
        nought_count, cross_count = 0, 0
        for element in list(self.current_state.flatten()):
            if element == NOUGHT:
                nought_count += 1
            elif element == CROSS:
                cross_count += 1
            else:
                pass
        return self.player_nought if cross_count == nought_count else self.player_cross

    def current_opponent(self):
        # Returns the opponent piece (i.e. If current player is X, then this will return O
        return self.player_nought if self.check_current_player() == self.player_cross else self.player_cross

    def play_move(self, current_player, current_move):
        """
        :param current_player: player making current move
        :param current_move: move to be played
        :return: current_player (winner), game_ended -> BOOL:

        This function splits the index components into two separate variables, checking whether
        moves are eligible (i.e. placing a piece where it isn't blank)
        """
        x_component, y_component = current_move // self.dimensions, (current_move % self.dimensions)
        game_ended = False
        game_won = None

        if self.current_state[x_component, y_component] is not EMPTY_BOARD:
            raise IndexError(f"The following invalid move was attempted: {current_move}")

        self.current_state[x_component, y_component] = current_player.symbol

        if self.board_full():
            game_ended = True
            game_won = GAME_DRAW
        elif self.return_id_check_win(x_component, y_component, current_player):
            game_won = current_player
            game_ended = True

        return game_won, game_ended

    def display_board(self):
        rows = []
        for x in range(self.dimensions):
            row_array = [" {} "] * self.dimensions
            rows.append("|".join(row_array) + "\n")

    @staticmethod
    def symbol_convert(player_symbol):
        if player_symbol == CROSS:
            return "X"
        elif player_symbol == NOUGHT:
            return "O"
        else:
            return " "

    def return_id_check_win(self, current_player, x_component, y_component):
        """

        :param current_player:
        :param x_component:
        :param y_component:
        :return:

        In this function, I itemise each column, diagonal and row and see if there's a consecutive set of
        values (I.e. a row of 'XXXXX' on a 5x5 grid means the current player has won. I then change the
        coordinates of the board to rotate it, and check for any other diagonals. This is further explained in
        the project documentation -  see section 3.0.2.
        """
        def check_pieces(pieces):
            """
            :param pieces: an array with the number of pieces in
            :return: BOOL
            """
            # The following list comprehension, as denoted by the identifier name, produces a quantified list.
            # It iterates through the list and it quantifies how much of each element there is but moves onwards
            # Consider the following array -> [0,0,0,0,4,5,4,4,7]
            # The function would return (0,4),(4,1),(5,1),(4,2),(7,1)

            quantified_list = [(x, sum(1 for i in j)) for x, j in itertools.groupby(pieces)]
            for current_tuple in quantified_list:
                if current_tuple[1] >= self.symbols and current_tuple[0] == current_player.symbol:
                    return True

        column_values = list(self.current_state[:, y_component])
        if check_pieces(column_values):
            return True
        diagonal_values = list(numpy.diag(self.current_state, (y_component - x_component)))
        if check_pieces(diagonal_values):
            return True
        row_values = list(self.current_state[x_component, :])
        if check_pieces(row_values):
            return True

        # Numpy module can only do a 180 degree rotation, so we reorder the diagonal format and
        # Create a list to iterate across it
        rotated_state = numpy.flip(self.current_state, 1)
        diagonal_format = list(numpy.diag(rotated_state, (self.dimensions - 1 - y_component - x_component)))
        if check_pieces(diagonal_format):
            return True
        # If no winning number of consecutive values are found, return False.
        return False

    def generate_board_id(self, outcome=False):

        # See section 3.0.x for further explanation

        nought_sum, cross_sum = INFINITY, INFINITY
        rotated_state, flipped_state = 0, 0

        ideal_state = None

        for number_of_flips in range(2):
            initial_state = copy(self.current_state)
            if number_of_flips == 1:
                initial_state = numpy.flip(initial_state, 0)

            for current_rotation in range(0, 4):
                # The greek letter Sigma denotes sum in mathematics, to prevent repeated
                # identifier names I used these variable names
                sigma_nought, sigma_cross = 0, 0
                state_analysed = False

                for key, sym in enumerate(initial_state.flatten()):
                    if sym == -1:
                        sigma_nought += 0.5 ** (1+key)
                    elif sym == 1:
                        sigma_cross += 0.5 ** (1+key)

            if sigma_cross == cross_sum:
                if sigma_nought < nought_sum:
                    state_analysed = True
            elif sigma_cross < cross_sum:
                state_analysed = True

            if state_analysed:
                nought_sum, cross_sum = sigma_nought, sigma_cross
                flipped_state = number_of_flips
                rotated_state = current_rotation
                ideal_state = copy(initial_state)

            initial_state = numpy.rot90(initial_state)

        if outcome:
            current_board = Board(self.board_layout)
            current_board.current_state = ideal_state

            return (nought_sum, cross_sum), current_board, rotated_state, flipped_state
        else:
            return (nought_sum, cross_sum)

    def change_state_for_board(self, current_move):
        # Check the validity of the attempted move before we attempt a state change
        if current_move < 0: raise Exception(f"Attempted move isn't possible: {current_move}")
        # List comprehension to provide an array of zeroes which will change relatively to the board
        # We replace the moves 0 with a 1, and get the index of its position
        state = [0 for i in range(self.squares)]
        board_id, current_board, current_board_rotated, current_board_flipped = generate_board_id(outcome=True)
        state[current_move] = 1
        # We then convert this array into a Numpy array to allow us to manipulate the board
        state = numpy.array(state)
        state.resize((self.dimensions, self.dimensions))
        state = numpy.rot90(state, -current_board_rotated)

        if current_board_flipped:
            state = numpy.flip(state, 0)

        state = [state.flatten()]
        return state.index(1)

    def change_board_for_state(self, current_move):

        if current_move < 0: raise Exception(f"Attempted move isn't possible: {current_move}")
        state = [0 for i in range(self.squares)]

        board_id, current_board, current_board_rotated, current_board_flipped = generate_board_id(outcome=True)
        state[current_move] = 1
        state = numpy.array(state)
        state.resize((self.dimensions, self.dimensions))
        state = numpy.rot90(state, current_board_rotated)

        if current_board_flipped:
            state = numpy.flip(state, 0)

        state = [state.flatten()]
        return state.index(1)

    def generate_display(self):
        grid = list()
        for x in range(self.dimensions):
            space = [" {} "] * self.dimensions
            grid.append("|".join(space) + "\n")

        state_space = (("----" * self.dimensions) + "\n").join(grid)

        symbols_converted = (self.symbol_convert(each_symbol) for each_symbol in [self.current_state.flatten()])
        print(state_space.format(*symbols_converted))