# board_constants.py

# General constants used throughout Tic-Tac-Toe
import math

CROSS = 1
NOUGHT = -1
NULL = 0
GAME_DRAW = 2
EMPTY_BOARD = 0
INFINITY = math.inf
DIMENSIONS = 3

BOARD_LAYOUT = {
    3 : {
        "board_size" : 3,
        "board_squares" : 9,
        "board_symbols" : 3
    },
    5 : {
        "board_size" : 5,
        "board_squares" : 25,
        "board_symbols" : 4
    },
    7 : {
        "board_size" : 7,
        "board_squares" : 49,
        "board_symbols" : 4
    }
}

PLAYING_TACTIC = ["LEARN", "EXPLOIT", "RANDOM MOVE"]

# Constants used for Q-Learning
RL_CONSTANTS = {
    "TRAINING_GAMES": 2500,
    "REWARD_VALUE": 1,
    "ALPHA": 0.1,
    "GAMMA": 0.6,
    "EPSILON": 0.135
}

