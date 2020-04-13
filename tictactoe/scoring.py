import os
from tictactoe.constants import GAME_DRAW, NOUGHT, RL_CONSTANTS

class Scoring:

    def __init__(self):
        self.draws = 0
        self.noughts_wins = 0
        self.crosses_wins = 0

    def increment_win(self, winner):
        if winner.symbol == NOUGHT:
            self.noughts_wins += 1
        elif winner == GAME_DRAW:
            self.draws += 1
        else:
            self.crosses_wins += 1

    def display_results(self):
        print(f"""
        - - - - - - - - - - - - - -
        | Draws | Noughts | Cross |
        | {self.draws} | {self.noughts_wins} | {self.crosses_wins} |
        - - - - - - - - - - - - - -
        """)

    def output_results_to_file(self, filename, dimensions):
        with open(os.path.join("Scores", filename), "w") as f:
            f.write("\n".join([
                "Configuration:",
                f"Dimensions: {dimensions}x{dimensions}",
                f"Number of Q-Learning Training Games: {RL_CONSTANTS['TRAINING_GAMES']}",
                f"Draws, Noughts, Crosses",
                f"{self.draws}, {self.noughts_wins}, {self.crosses_wins}"
            ]))

    def reset_scores(self):
        self.draws, self.noughts_wins, self.crosses_wins = 0, 0, 0

    def return_scores(self, winner):
        if winner.symbol == NOUGHT:
            return self.noughts_wins
        elif winner == GAME_DRAW:
            return self.draws
        else:
            return self.crosses_wins
