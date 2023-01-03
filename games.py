import os

import constants


class Result:

    def __init__(self):
        self.wins_x = 0
        self.wins_o = 0
        self.draws = 0

    def reset(self):
        self.wins_x = 0
        self.wins_o = 0
        self.draws = 0

    def add_win(self, player):
        if player == constants.DRAW:
            self.draws += 1
        elif player.symbol == constants.CROSS:
            self.wins_x += 1
        else:
            self.wins_o += 1

    def get_wins(self, player):
        if player == constants.DRAW:
            return self.draws
        elif player.symbol == constants.CROSS:
            return self.wins_x
        else:
            return self.wins_o

    def print(self):
        print("""
+--------------------------------+
|{:^10}|{:^10}|{:^10}|
+--------------------------------+
|{:^10}|{:^10}|{:^10}|
+--------------------------------+
""".format("Cross", "Nought", "Draw", self.wins_x, self.wins_o, self.draws))

    def write_to_file(self, board_size, file_name):
        with open(os.path.join("results", file_name), "w") as file:
            file.write("\n".join(["Game Settings:",
                                  "Size: {size}x{size}".format(size=board_size),
                                  "Q-Learning Games: {}".format(constants.Q_TRAIN_GAMES),
                                  "MCTS Simulations: {}".format(constants.MCTS_SIMULATION_COUNT),
                                  "Cross,Nought,Draw",
                                  "{},{},{}".format(self.wins_x, self.wins_o, self.draws)]))
