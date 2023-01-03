import copy
import os
import random
import time
import ujson as json

from brains.brain import Brain


class Brain_QLearning(Brain):

    def __init__(self, player, opp_player, board):
        super().__init__()
        self.player = player
        self.opp_player = opp_player
        self.board = board

        self.name = "QLearning"

        from constants import Q_ALPHA, Q_EPSILON, Q_GAMMA

        # Initialise learning values
        self.alpha = Q_ALPHA
        self.epsilon = Q_EPSILON
        self.gamma = Q_GAMMA

        # Initialise Q-Table
        self.q_table = {}

        self.data_file = os.path.join(self.board.brain_data_folder, "q_table_{}.json".format(self.player.symbol_string))

        self.reset()

    def reset(self):
        self.last_state_action = None
        self.last_state = None

    def get_move(self):
        # Check key exists for current board
        board_identifier, state_board, board_rotate, board_flip = self.board.get_identifier(return_details=True)

        if board_identifier not in self.q_table:
            self.q_table[board_identifier] = [0] * self.board.squares

        # Check whether we want to explore or exploit
        if random.random() < self.epsilon:
            # Explore, pick random move
            board_action = random.choice(self.board.get_valid_moves())

            # Store our state action to update Q-Table
            state_action = self.board.board_move_to_state(board_action)
        else:
            # Exploit, get best move
            state_action = self.max_index(self.q_table[board_identifier], state_board.get_invalid_moves())

            # Store our board action to update Q-Table
            board_action = self.board.state_move_to_board(state_action)

        # Store our current board & action so we can update Q-Table later on
        self.last_state_action = state_action
        self.last_state = board_identifier

        return board_action, state_action

    def update_q_value(self, reward):
        if self.last_state is None:
            return

        # Get old value for our last action
        old_value = self.q_table[self.last_state][self.last_state_action]

        board_identifier = self.board.get_identifier()
        if board_identifier not in self.q_table:
            self.q_table[board_identifier] = [0] * self.board.squares

        # Get the next maximum value for our new state
        new_board_max = self.max_value(self.q_table[board_identifier], self.board.get_invalid_moves())

        # Set new value
        new_value = old_value + (self.alpha * ((reward + self.gamma*new_board_max) - old_value))

        self.q_table[self.last_state][self.last_state_action] = new_value

    def max_value(self, array, ignore_indexes):
        # Remove ignore indexes
        new_list = copy.copy(array)

        # Sort as to not throw off the other values
        for index in sorted(ignore_indexes, reverse=True):
            del new_list[index]

        if len(new_list) == 0:
            return 0

        return max(new_list)

    def max_index(self, array, ignore_indexes):
        max_value = self.max_value(array, ignore_indexes)

        return random.choice(
            list(index for index, value in enumerate(array) if value == max_value and index not in ignore_indexes))

    def save(self):
        time_before = time.time()

        print("Saving Q-Table data for {}.".format(self.player.name))

        with open(self.data_file, "w") as file:
            # Dump q_table to json file
            json.dump({str(k): v for k, v in self.q_table.items()}, file, double_precision=16)

        print("Saved {}'s Q-Table data to {}. {:.1f}s taken to save JSON file.".format(self.player.name, self.data_file,
                                                                                       time.time() - time_before))

    def load(self):
        time_before = time.time()

        print("Loading Q-Table data for {}.".format(self.player.name))

        try:
            with open(self.data_file, "r") as file:
                # Load q_table from json file.
                temp = json.load(file)
        except FileNotFoundError:
            print("No Q-Table data found for {}.".format(self.player.name))
            return

        # Save time taken to load file.
        time_loaded = time.time()

        # Convert string keys to tuples
        self.q_table = {eval(k): v for k, v in temp.items()}
        time_finished = time.time()

        print(
            "Successfully loaded Q-Table data for {}. {:.1f}s taken to load JSON file. {:.1f}s taken to convert key tuples.".format(
                self.player.name, time_loaded - time_before, time_finished - time_loaded))
