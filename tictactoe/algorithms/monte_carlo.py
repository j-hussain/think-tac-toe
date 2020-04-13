# MCTS algorithm

from random import choice
from tictactoe.algorithms.algorithm import Algorithm
from tictactoe.constants import MONTE_CARLO_COUNT
from tictactoe.scoring import Scoring
from math import log as ln
from math import sqrt
from tictactoe.board import Board
from numpy import argmax as get_index_largest_value


class Node:

    def __init__(self, algorithm, current_move, current_board, terminal_state=False, winning_state=None, parent_node=None):
        # Initialise
        self.algorithm = algorithm
        self.current_move = current_move
        self.current_board = current_board
        self.parent_node = parent_node
        self.children_nodes = []
        self.is_terminal_state = terminal_state
        self.winning_state = winning_state
        self.game_score = Scoring()
        self.nodes_visited = 0
        self._possible_moves = current_board.valid_moves()

    def terminal_node(self):
        return self.is_terminal_state

    def traverse_complete(self):
        return len(self._possible_moves) == 0

    def highest_scoring_node(self):
        # Implementation of the Markov Decision Process by Auer, Cesa-Bianchi, and Fischer
        c_bias = 1.41421356
        values = []
        for each_node in self.children_nodes:
            wins = each_node.game_score.return_scores(self.current_board.check_current_player())
            losses = each_node.game_score.return_scores(self.current_board.current_opponent())

            ucb_value = ((wins - losses) / self.nodes_visited) + (c_bias * sqrt(ln(self.nodes_visited)/self.nodes_visited))
            values.append(ucb_value)

        return self.children_nodes[get_index_largest_value(values)]

    def expand_node(self):

        next_state = Board(self.current_board.BOARD_LAYOUT)
        next_state.player_nought, next_state.player_cross = self.current_board.player_nought, self.current_board.player_cross
        next_state.current_state = self.current_board.current_state

        next_move = self._possible_moves.pop()
        final_state, winner = next_state.play(next_state.check_current_player(), next_move)
        new_node = Node(self.algorithm, next_state, next_move, final_state, winner, self)
        self.children_nodes.append(new_node)

        return new_node

    def backpropagate(self, winner):
        self.nodes_visited += 1
        self.game_score.increment_win(winner)

        if self.parent_node is not None:
            self.parent_node.backpropogate(winner)

    def simulate_board(self):
        if self.is_terminal_state:
            return self.is_terminal_state, self.winning_state

        simulated_moves = []
        final_state = False

        while not final_state:
            next_move = choice(self.current_board.valid_moves())
            simulated_moves.append(next_move)
            final_state, winner = self.current_board.play_move(self.current_board.check_current_player(), next_move)

        for each_move in simulated_moves:
            self.current_board.fill_empty_state(each_move)

        return final_state, winner


class MCTS(Algorithm):

    def __init__(self, current_state, current_player, current_opponent):
        super().__init__()

        # Initialise and import variables/constants
        self.current_state = current_state
        self.current_player = current_player
        self.current_opponent = current_opponent
        self.tree_nodes = {}

        self.algorithm_name = "Monte Carlo Tree Search Algorithm"

    @staticmethod
    def select_node(current_node):
        while current_node.terminal_node() is False:
            if current_node.traverse_complete():
                current_node = current_node.highest_scoring_node()
            else:
                return current_node.expand_node()

        return current_node

    def analyse_move(self):
        current_node = Node(self, self.current_state, None)
        for simulation in range(MONTE_CARLO_COUNT):
            child_node = self._select_node(current_node)

            _, winning_move = child_node.simulate_board()
            child_node.backpropagate(winning_move)