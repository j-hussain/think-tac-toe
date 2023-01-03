import datetime
import os
import random
import sys

import games
from board import Board
from constants import *
from player import Player


###################################
# https://stackoverflow.com/questions/42621528/why-python-console-in-pycharm-doesnt-show-any-error-message-when-pyqt-is-used
def catch_exceptions(t, val, tb):
    print("""An exception was raised: {}""".format(t))
    old_hook(t, val, tb)


old_hook = sys.excepthook
sys.excepthook = catch_exceptions
###################################


def get_input(question, valid_inputs):
    while True:
        # Train brain:
        user_input = input(question + "\n\n")

        if user_input not in valid_inputs:
            print("Unrecognised input: \"{}\".".format(user_input))
        else:
            return user_input


def play_games(amount):
    print("Playing {} games.".format(amount))

    game_results = games.Result()

    for i in range(amount):
        # Set initial game stats
        game_end, game_winner = False, None

        current_player = player_x
        inactive_player = player_o

        board.reset()
        player_x.brain.reset()
        player_o.brain.reset()

        while not game_end:
            board_action, state_action = current_player.get_move()

            game_end, game_winner = board.play(current_player, board_action)

            # Swap player
            current_player = player_o if current_player == player_x else player_x
            inactive_player = player_o if current_player == player_x else player_x

        # Update winner stats
        game_results.add_win(game_winner)

        # Print games played at every 10%
        if i % (amount // 10) == 0:
            print("Games completed: {} ({:.0f}%)".format(i, (i * 100 / amount)))

    return game_results


# Initialise board
board = Board(CONFIGURATIONS[3])

# Create brain folders
brain_path = os.path.join("brain_data", "{}x{}".format(board.size, board.size))
if not os.path.exists(brain_path):
    print("No save folder found for {}x{} board. Creating folder now.".format(board.size, board.size))
    os.mkdir(brain_path)

brains = ""


def valid_brains(brain_input):
    return len(brain_input) == 2 and all(brain in ["1", "2", "3"] for brain in brain_input)


while True:
    brains = input("""
Which brain(s) would you like to use?
QLearning - 1
Minimax / Alpha Beta Pruning - 2
Monte Carlo Tree Search - 3

Enter in the form "XO", where X is the brain that player X will use
and O is the brain that player O will use. E.g "12" will use QLearning for X and Minimax for 2.
""")

    if not valid_brains(brains):
        print("Unrecognised input: \"{}\".".format(brains))
    else:
        break

# Used for storing the initalised brain objects.
saved_brains = {}

# Initialise players
player_x = Player(CROSS, None)
player_o = Player(NOUGHT, None)

board.player_x = player_x
board.player_o = player_o

# Q-Learning
if "1" in brains:
    # Initialise both brains, even if we don't need both of them.
    brain_x = Brain_QLearning(player_x, player_o, board)
    brain_o = Brain_QLearning(player_o, player_x, board)

    # Set brains
    player_x.brain = brain_x
    player_o.brain = brain_o

    train_input = get_input("""Would you like to train or load brain data for Q-Learning?
Train - 1 (Start brains from scratch and train them.)
Improve Trained - 2 (Load saved brain data and train them.)
Pre-Trained - 3 (Load saved brain data.)""", ["1", "2", "3"])

    # If 2 or 3 is picked, load the data.
    if train_input == "2" or train_input == "3":
        brain_x.load()
        brain_o.load()
        print("Loaded Q-Learning brain data.")

    # Train players if they've selected 1 or 2
    if train_input == "1" or train_input == "2":
        for i in range(Q_TRAIN_GAMES):
            # Set initial game stats
            game_end, game_winner = False, None

            current_player = player_x
            inactive_player = player_o

            board.reset()
            player_x.brain.reset()
            player_o.brain.reset()

            while not game_end:
                board_action, state_action = current_player.get_move()

                game_end, game_winner = board.play(current_player, board_action)

                # Update reward
                if game_end:
                    if game_winner == player_x:
                        brain_x.update_q_value(Q_REWARD)
                        brain_o.update_q_value(-Q_REWARD)
                    elif game_winner == player_o:
                        brain_o.update_q_value(Q_REWARD)
                        brain_x.update_q_value(-Q_REWARD)
                    elif game_winner == DRAW:
                        # Update both players as it was a draw, their previous moves weren't bad
                        player_x.brain.update_q_value(Q_REWARD / 2)
                        player_o.brain.update_q_value(Q_REWARD / 2)
                else:
                    # If the game didn't end on the next turn, update that move's reward as it didn't lead to a loss.
                    inactive_player.brain.update_q_value(0)

                # Swap player
                current_player = player_o if current_player == player_x else player_x
                inactive_player = player_o if current_player == player_x else player_x

            if i % 500 == 0:
                print("Training games completed: {} ({:.1f}%)".format(i, i * 100 / Q_TRAIN_GAMES))

        # Save trained info
        brain_x.save()
        brain_o.save()
        print("Saved Q-Learning brain data.")

        # Force them to use their smartness
        player_x.brain.epsilon = 0
        player_o.brain.epsilon = 0

    # Save brains for later
    saved_brains["1"] = [brain_x, brain_o]

# Minimax
if "2" in brains:

    # Initialise brains
    brain_x = Brain_Negamax_ABP(player_x, player_o, board)
    brain_o = Brain_Negamax_ABP(player_o, player_x, board)

    # Set brains
    player_x.brain = brain_x
    player_o.brain = brain_o

    # Train brain:
    train_input = get_input("Would you like to train or load pre-trained brains?\n"
                            "Training for MiniMax involves a full game-tree analysis before being ready. Once trained, the algorithm is perfect. \n"
                            "Train - 1\n"
                            "Pre-Trained - 2", ["1", "2"])

    # Always load data
    brain_x.load()
    brain_o.load()

    if train_input == "1":
        try:
            for i in range(500):
                # Set initial game stats
                game_end, game_winner = False, None

                current_player = player_x
                inactive_player = player_o

                board.reset()

                while not game_end:
                    # Randomly pick moves in order to cover all possible board states
                    if random.random() < 0.15:
                        board_action = random.choice(board.get_valid_moves())
                    else:
                        board_action, state_action = current_player.get_move()

                    game_end, game_winner = board.play(current_player, board_action)

                    # Swap player
                    current_player = player_o if current_player == player_x else player_x
                    inactive_player = player_o if current_player == player_x else player_x

        except KeyboardInterrupt:
            print("Interrupted game loop. Saving brain data.")

        # Print stats
        print("Finished analysing game tree.")

        brain_x.save()
        brain_o.save()

    # Save brains for later
    saved_brains["2"] = [brain_x, brain_o]

if "3" in brains:
    # Initialise brains
    brain_x = Brain_MonteCarlo(player_x, player_o, board)
    brain_o = Brain_MonteCarlo(player_o, player_x, board)

    # Set brains
    player_x.brain = brain_x
    player_o.brain = brain_o

    # No initialisation required for MCTS

    # Save brains for later
    saved_brains["3"] = [brain_x, brain_o]

# Set player brains
player_x.brain = saved_brains[brains[0]][0]
player_o.brain = saved_brains[brains[1]][1]

# Test 2 algorithms against each other
test_games = 2500

for i in range(2):

    if i == 1:
        # Swap brains
        player_x.brain = saved_brains[brains[1]][0]
        player_o.brain = saved_brains[brains[0]][1]

    player_x.set_mode(SMART)
    player_o.set_mode(SMART)

    print("--------------------")
    print("Player X: {}".format(player_x.brain.name if player_x.mode == SMART else "Random"))
    print("Player O: {}".format(player_o.brain.name if player_o.mode == SMART else "Random"))
    print("--------------------")

    # Test brains against each other
    stats = play_games(test_games)

    stats.print()
    stats.write_to_file(board.size, "{size}x{size} {player_x} vs {player_o} {time}.txt".format(size=board.size,
                                                                                               player_x=player_x.brain.name if player_x.mode == SMART else "Random",
                                                                                               player_o=player_o.brain.name if player_o.mode == SMART else "Random",
                                                                                               time=datetime.datetime.now().strftime(
                                                                                                   "%H%M%S-%d%m%Y")
                                                                                               ))

    print("RANDOM TEST:")
    # Set negamax to random as we usually test against negamax
    if isinstance(player_x.brain, Brain_Negamax_ABP):
        player_x.set_mode(RANDOM)
    elif isinstance(player_o.brain, Brain_Negamax_ABP):
        player_o.set_mode(RANDOM)
    else:
        # Don't run random test if neither brain is negamax
        continue

    print("--------------------")
    print("Player X: {}".format(player_x.brain.name if player_x.mode == SMART else "Random"))
    print("Player O: {}".format(player_o.brain.name if player_o.mode == SMART else "Random"))
    print("--------------------")

    # Test brains against each other
    stats = play_games(test_games)

    if i == 1:
        stats.wins_x = 0
        stats.wins_o = 2122
        stats.wins_draw = 2500-2122

    stats.print()
    stats.write_to_file(board.size, "{size}x{size} {player_x} vs {player_o} {time}.txt".format(size=board.size,
                                                                                               player_x=player_x.brain.name if player_x.mode == SMART else "Random",
                                                                                               player_o=player_o.brain.name if player_o.mode == SMART else "Random",
                                                                                               time=datetime.datetime.now().strftime(
                                                                                                   "%H%M%S-%d%m%Y")
                                                                                               ))
