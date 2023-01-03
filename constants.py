from brains.montecarlo import Brain_MonteCarlo
from brains.negamax_abp import Brain_Negamax_ABP
from brains.qlearning import Brain_QLearning
from brains.random import Brain_Random

# Symbol definition

NOUGHT = -1
CROSS = 1
EMPTY = 0
DRAW = 2

GAME_SIZE = 3
CONFIGURATIONS = {
    3: {
        "size": 3,
        "symbols_needed": 3,
        "squares": 9
    },
    5: {
        "size": 5,
        "symbols_needed": 4,
        "squares": 25
    },
    7: {
        "size": 7,
        "symbols_needed": 4,
        "squares": 49
    }
}


ALGORITHMS = {
    "Negamax":
        {
            "name": "Negamax",
            "description": "Negamax is an algorithm that will evaluate all possible boards to search for a best move. Negamax is a variant to Minimax.",
            "brain": Brain_Negamax_ABP
        },
    "MCTS":
        {
            "name": "Monte Carlo Tree Search",
            "description": "Monte Carlo Tree Search is an algorithm that selects a best move based on simulations of playing that move. After many simulations, the algorithm selects a best move through analysing win-rate.",
            "brain": Brain_MonteCarlo
        },
    "QLearning":
        {
            "name": "Reinforcement Learning",
            "description": "Reinforcement Learning is a machine learning algorithm that learns the best move through analysing which moves results in positive outcomes for the AI for thousands of test games.",
            "brain": Brain_QLearning
        },
    "Random":
        {
            "name": "Random",
            "description": "Random moves picked.",
            "brain": Brain_Random
        }
}

# Modes
SMART = 0
TRAIN = 1
RANDOM = 2

# Q-Learning parameters
Q_ALPHA = 0.1
Q_EPSILON = 0.135
Q_GAMMA = 0.6
Q_TRAIN_GAMES = 3500
Q_REWARD = 1

# MCTS parameters
MCTS_SIMULATION_COUNT = 1250
