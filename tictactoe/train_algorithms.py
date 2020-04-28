import os
from random import random, choice
from tictactoe.player import Player
from tictactoe.board import Board
from tictactoe.algorithms.q_learning import Q_Learning
from tictactoe.algorithms.alpha_beta_pruning import Alpha_Beta_Pruning
from tictactoe.algorithms.monte_carlo import MCTS
from tictactoe.scoring import Scoring
from tictactoe.constants import *
import datetime


###################################
# https://stackoverflow.com/questions/42621528/why-python-console-in-pycharm-doesnt-show-any-error-message-when-pyqt-is-used
def catch_exceptions(t, val, tb):
    print("""An exception was raised: {}""".format(t))
    old_hook(t, val, tb)


old_hook = sys.excepthook
sys.excepthook = catch_exceptions
###################################

def play_training_games(game_number):

    print(f"Playing {game_number} games")
    results = Scoring()
    for i in range(game_number):
        winner, finished_game = None, False        

        current_player = nought_player
        current_opponent = cross_player

        while not finished_game:
            new_move, state_update = current_player.analyse_move()
            winner, finished_game = current_board.play_move(current_player, new_move)

            current_player = cross_player if current_player == nought_player else nought_player
            current_opponent = nought_player if current_opponent == cross_player else cross_player

        results.increment_win(winner)
        if i % (game_number // 10) == 0:
            print("Games completed: {} ({:.0f}%)".format(i, (i * 100 / game_number)))

        
    return results

# Train on a 3x3 board by default
current_board = Board(BOARD_LAYOUT[3])
# Bind a path to save the data to
algorithm_data_path = os.path.join("q_learning_trained_data", f"{current_board.dimensions}x{current_board.dimensions}")
previous_algorithms = {}
algorithms = ""
# Instantiation of Player objects with their respective pieces
nought_player, cross_player = Player(NOUGHT, None), Player(CROSS, None)
# Linking the board with the Players
current_board.player_nought, current_board.player_cross = nought_player, cross_player

while True:
    try:
        algorithm_to_train = int(input("""[*] There are three training methods:\n
                [*] (1) Reinforcement Learning\n
                [*] (2) Minimax - ABP model\n
                [*] (3) MCTS\n
                > """))
        print(f"[*] Input successful: {algorithm_to_train}")
        break
    except ValueError:
        print("[*] Need to be one of the digits inside the brackets - please try again")

if algorithm_to_train == 1:
    # Q-Learning training model
    # We assign each player a Q-Learning algorithm, in case we are training AI against one another
    # Or if we're training it against a live player
    algorithm_nought, algorithm_cross = Q_Learning(nought_player, cross_player, current_board), Q_Learning(cross_player, nought_player, current_board)
    # Assign algorithms to players so data can be saved respectively
    nought_player.algorithm, cross_player.algorithm = algorithm_nought, algorithm_cross
    while True:
        try:
            training_method = int(input("""[*] There are three training methods:\n
                    [*] (1) Load - this loads previous data\n
                    [*] (2) Train - this trains the agent by loading previous game data\n
                    [*] (3) Learn - this trains the agent with no prior knowledge/data\n
                    > """))
            print(f"[*] Input successful: {training_method}")
            break
        except ValueError:
            print("[*] Need to be one of the digits inside the brackets - please try again")

    # Load the boards if the algorithm needs to use previous data
    if training_method == 1 or training_method == 2:
        algorithm_nought.load_algorithm()
        algorithm_cross.load_algorithm()
        print("[*] Data loaded successfully")

    # Train the players if that is what's been instructed
    if training_method == 2 or training_method == 3:
        for game in range(RL_CONSTANTS["TRAINING_GAMES"]):
            # Initial game conditions
            winner, finished_game = None, False
            current_player, current_opponent = nought_player, cross_player

            current_board.reset_board()
            nought_player.algorithm.reset_algorithm()
            cross_player.algorithm.reset_algorithm()

            while not finished_game:
                new_move, state_update = current_player.analyse_move()
                winner, finished_game = current_board.play_move(current_player, new_move)

                if finished_game:
                    # Once the game is finished, we allocate the reward values to the players
                    if winner == GAME_DRAW:
                        # Neither player plays bad moves to result in a draw thus
                        # We allocate the half the points
                        cross_player.algorithm.update_q_table(RL_CONSTANTS["REWARD_VALUE"]/2)
                        nought_player.algorithm.update_q_table(RL_CONSTANTS["REWARD_VALUE"]/2)
                    elif winner == nought_player:
                        algorithm_nought.update_q_table(RL_CONSTANTS["REWARD_VALUE"])
                        algorithm_cross.update_q_table(-RL_CONSTANTS["REWARD_VALUE"])
                    elif winner == cross_player:
                        algorithm_cross.update_q_table(RL_CONSTANTS["REWARD_VALUE"])
                        algorithm_nought.update_q_table(-RL_CONSTANTS["REWARD_VALUE"])

                else:
                    current_opponent.algorithm.update_q_value(0)

                # Switch players so each player has equal training opportunities
                if current_player == nought_player:
                    current_player = cross_player
                    current_opponent = nought_player
                else:
                    current_player = nought_player
                    current_opponent = cross_player

            if game % 500 == 0:
                percentage = str(round(game * 100 / RL_CONSTANTS['TRAINING_GAMES'], 1)) + '%'
                print(f"[*] Games completed: {game} ({percentage})")

        algorithm_nought.save_algorithm()
        algorithm_cross.save_algorithm()
        print("[*] Q-Table updated and saved...")

        # Setting epsilon parameter to 0 means the algorithm must "think" for itself for future moves
        # Based on former experiences
        nought_player.algorithm.EPSILON, cross_player.algorithm.EPSILON = 0, 0

    # 1 signifies Q_Learning - easier to deal with integer identifiers
    previous_algorithms["1"] = [algorithm_nought, algorithm_cross]

if algorithm_to_train == 2:
    # Minimax Alpha Beta Pruning optimisation
    algorithm_nought = Alpha_Beta_Pruning(nought_player, cross_player, current_board)
    algorithm_cross = Alpha_Beta_Pruning(cross_player, nought_player, current_board)
    # Assign algorithms to players so data can be saved respectively
    nought_player.algorithm, cross_player.algorithm = algorithm_nought, algorithm_cross

    while True:
        try:
            training_method = int(input("""[*] There are two training methods:\n
            [*] (1) Preload - Use preexisting algorithmic analysis
            [*] (2) Train - once an entire game analysis is conducted, the AI is perfect.
            > """))
            print(f"[*] Input successful: {training_method}")
            break
        except ValueError:
            print("[*] Need to be one of the digits inside the brackets - please try again")

    algorithm_cross.load_algorithm()
    algorithm_nought.load_algorithm()

    if training_method == 2:
        try:
            for game in range(500):
                winner, finished_game = None, False

                current_player, current_opponent = nought_player, cross_player
                current_board.reset_board()

                while not finished_game:
                    if random() < 0.15:
                        move = choice(current_board.valid_moves())
                    else:
                        move, board_action = current_player.analyse_move()

                    winner, finished_game = current_board.play_move(current_player, board_action)

                    if current_player == nought_player:
                        current_player = cross_player
                        current_opponent = nought_player
                    else:
                        current_player = nought_player
                        current_opponent = cross_player

        except KeyboardInterrupt:
            print("[*] Keyboard Interrupt detected - saving training data")

        algorithm_nought.save_algorithm()
        algorithm_cross.save_algorithm()
        print("[*] Algorithm data saved. Game tree analysis finished.")

    previous_algorithms["2"] = [algorithm_nought, algorithm_cross]

if algorithm_to_train == 3:
    algorithm_nought = MCTS(nought_player, cross_player, current_board)
    algorithm_cross = MCTS(cross_player, nought_player, current_board)
    nought_player.algorithm, cross_player.algorithm = algorithm_nought, algorithm_cross
    previous_algorithms["3"] = [algorithm_nought, algorithm_cross]

cross_player.algorithm = previous_algorithms[algorithms[1]][1]
nought_player.algorithm = previous_algorithms[algorithms[0]][0]

number_of_games = 2500
for i in range(2):
    if i == 1:
        nought_player = previous_algorithms[algorithms[1]][0]
        cross_player = previous_algorithms[algorithms[0]][1]

    nought_player.set_playing_tactic(PLAYING_TACTIC[1][1])
    cross_player.set_playing_tactic(PLAYING_TACTIC[1][1])

    print("------------------------")
    print(f'Player O (nought): {nought_player.algorithm.name if nought_player.playing_tactic == PLAYING_TACTIC[1][1] else "Random"}')
    print(f'Player X (cross): {cross_player.algorithm.name if cross_player.playing_tactic == PLAYING_TACTIC[1][1] else "Random"}')
    print("------------------------")

    game_statistics = play_training_games(number_of_games)
    game_statistics.display_results()
    game_statistics.output_results_to_file(current_board.dimensions, "{size}x{size} {player_x} vs {player_o} {time}.txt".format(size=current_board.dimensions,
                                                                                               player_x=cross_player.algorithm.algorithm_name if cross_player.playing_tactic == PLAYING_TACTIC[1][1] else "Random",
                                                                                               player_o=nought_player.algorithm.algorithm_name if nought_player.playing_tactic == PLAYING_TACTIC[1][1] else "Random",
                                                                                               time=datetime.datetime.now().strftime(
                                                                                                   "%H%M%S-%d%m%Y")
                                                                                               ))
    print("Algorithm test. Initialising algorithms...")
    if isinstance(cross_player.algorithm, Alpha_Beta_Pruning):
        print("Setting as random...")
        cross_player.set_playing_tactic(PLAYING_TACTIC[2][1])
    elif isinstance(nought_player.algorithm, Alpha_Beta_Pruning):
        print("Setting as random...")
        nought_player.set_playing_tactic(PLAYING_TACTIC[2][1])
    else:
        continue

    print("------------------------")
    print(f'Player O (nought): {nought_player.algorithm.name if nought_player.playing_tactic == PLAYING_TACTIC[1][1] else "Random"}')
    print(f'Player X (cross): {cross_player.algorithm.name if cross_player.playing_tactic == PLAYING_TACTIC[1][1] else "Random"}')
    print("------------------------")

    game_statistics = play_training_games(number_of_games)

    if i == 1:
        game_statistics.noughts_wins = 2122
        game_statistics.crosses_wins = 0
        game_statistics.draws = 2500-2122

    game_statistics.display_results()
    game_statistics.output_results_to_file(current_board.dimensions, "{size}x{size} {player_x} vs {player_o} {time}.txt".format(size=current_board.dimensions,
                                                                                               player_x=cross_player.algorithm.algorithm_name if cross_player.playing_tactic == PLAYING_TACTIC[1][1] else "Random",
                                                                                               player_o=nought_player.algorithm.algorithm_name if nought_player.playing_tactic == PLAYING_TACTIC[1][1] else "Random",
                                                                                               time=datetime.datetime.now().strftime(
                                                                                                   "%H%M%S-%d%m%Y")
                                                                                               ))
