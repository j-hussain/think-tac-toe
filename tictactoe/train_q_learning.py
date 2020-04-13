import os
from tictactoe.player import Player
from tictactoe.board import Board
from tictactoe.algorithms.q_learning import Q_Learning
from tictactoe.constants import *

# Train on a 3x3 board by default
current_board = Board(BOARD_LAYOUT[3])
# Bind a path to save the data to
algorithm_data_path = os.path.join("q_learning_trained_data", f"{current_board.dimensions}x{current_board.dimensions}")
previous_algorithms = {}
# Instantiation of Player objects with their respective pieces
nought_player, cross_player = Player(NOUGHT, None), Player(CROSS, None)
# Linking the board with the Players
current_board.player_nought, current_board.player_cross = nought_player, cross_player
# We assign each player a Q-Learning algorithm, in case we are training AI against one another
# Or if we're training it against a live player
algorithm_nought, algorithm_cross = Q_Learning(nought_player, cross_player, current_board), Q_Learning(cross_player, nought_player, current_board)
# Assign algorithms to players so data can be saved respectively
nought_player.algorithm, cross_player.algorithm = algorithm_nought, algorithm_cross

while True:
    7
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
        nought_player.algorithm.EPSILON, cross_player.algorithm.epsilon = 0, 0

    # 1 signifies Q_Learning - easier to deal with integer identifiers
    previous_algorithms["1"] = [nought_player, cross_player]