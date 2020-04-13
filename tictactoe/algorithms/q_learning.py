# Q - Learning Algorithm

import os, ujson
from copy import copy
from random import random, choice
from tictactoe.algorithms.algorithm import Algorithm
from tictactoe.constants import RL_CONSTANTS


class Q_Learning(Algorithm):

    def __init__(self, current_player, current_opponent, current_state):
        super().__init__()
        # Initialise player objects
        self.current_player = current_player
        self.current_opponent = current_opponent
        self.current_state = current_state
        # Import Q-Learning constants as described in documentation
        self.ALPHA = RL_CONSTANTS["ALPHA"]
        self.GAMMA = RL_CONSTANTS["GAMMA"]
        self.EPSILON = RL_CONSTANTS["EPSILON"]
        # Set up Q-Table
        self._qtable = {}
        self._previous_state = None
        self._previous_state_transition = None

        self.algorithm_name = "Q-Learning Algorithm"
        self.record_file = os.path.join(self.current_state.algorithm_data_dir, f"q_table_{self.current_player}.json")

        self.reset_algorithm()

    def reset_algorithm(self):
        # Resets the previous state status
        self._previous_state = None
        self._previous_state_transition = None

    def save_algorithm(self):
        print(f">>> Writing Q-Table data to JSON file for {self.current_player}")
        with open(self.record_file, "w") as f:
            # This list comprehension essentially iterates through the Q-Table values
            # And dumps it in the relevant JSON file
            ujson.dumps({str(i): j for i, j in self._qtable.items()}, f, double_precision=16)

        print(">>> Data saved.")

    def load_algorithm(self):
        print(f">>> Loading JSON files and Q-Table data for {self.current_player.name}")
        try:
            with open(self.record_file, "r") as f:
                temporary_dict = ujson.load(f)
        except FileNotFoundError:
            print(f"No Q-Table data for {self.current_player.name}")
            return

        self._qtable = {eval(i): j for i, j in temporary_dict.items()}
        print(f">>> Q-Table loaded for {self.current_player.name}")

    def get_max_index(self, state_array, indices):
        maximum = self.get_max_index(state_array, indices)
        return choice([i for i, j in enumerate(state_array) if j == maximum and i not in indices])

    @staticmethod
    def get_max_value(state_array, indices):
        temporary_array = copy(state_array)
        for current_index in sorted(indices, reverse=True):
            del temporary_array[current_index]
        if len(temporary_array) == 0:
            return 0
        else:
            print(f"The maximum is {max(temporary_array)}")
        return max(temporary_array)g

    def update_q_table(self, current_reward):
        if self._previous_state is None:
            return

        board_id = self.current_state.return_id_check_win()
        if board_id not in self._qtable:
            # If the algorithm hasn't encountered the new board, we generate an empty set of 0's in an
            # array and append it to our Q-Table
            self._qtable[board_id] = [0 for i in range(self.squares)]

        previous_q_value = self._qtable[self._previous_state][self._previous_state_transition]c
        maximum_value = self.get_max_value(self._qtable[board_id], self.current_state._invalid_moves())
        # Using Equation 1.2 in the documentation
        updated_q_value = previous_q_value + (self.ALPHA * (current_reward + maximum_value*self.GAMMA) - previous_q_value)
        self._qtable[self._previous_state][self._previous_state_transition] = updated_q_value

    def analyse_move(self):
        # Get board details
        board_id, current_board, current_board_rotated, current_board_flipped = self.return_id_check_win(outcome=True)
        # Has this state been played before?
        if board_id not in self._qtable:
            # In this block of conditional code, the program decides whether to exploit or explore
            # We compare it to our Epsilon parameter, and the outcome is based on the difference
            # between the numbers
            if random() >= self.EPSILON:
                new_move = self.get_max_index(self._qtable[board_id], current_board.invalid_moves())
                state_update = self.current_state.change_state_for_board(new_move)
            else:
                new_move = choice(self.current_state.valid_moves())
                state_update = self.current_state.change_board_for_state(new_move)

        self._previous_state_transition = new_move
        self._previous_state = board_id

        return new_move, state_update
