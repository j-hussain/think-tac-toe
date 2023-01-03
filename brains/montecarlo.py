import random

import numpy as np

import constants
from board import Board
from brains.brain import Brain


class Brain_MonteCarlo(Brain):

    def __init__(self, player, opp_player, board):
        super().__init__()
        self.player = player
        self.opp_player = opp_player
        self.board = board

        self.name = "MCTS"

        self.nodes = {}

    def get_move(self):

        current_node = Node(self, self.board, None)

        for i in range(constants.MCTS_SIMULATION_COUNT):
            leaf = self.selection(current_node)

            # Simulate out this node
            _, game_winner = leaf.simulation()

            leaf.backpropagate(game_winner)

        # Exploit
        return current_node.best_child(c=0).move_played, None

    def selection(self, current_node):

        while not current_node.is_terminal_node():
            # If the node has not been fully expanded, expand the node
            if not current_node.is_fully_expanded():
                return current_node.expand()
            else:
                # Select best node to return
                current_node = current_node.best_child()

        # If we're a terminal node, just return ourself
        return current_node


class Node:

    def __init__(self, brain, board, move, terminal=False, winner=None, parent=None):
        from games import Result

        self.brain = brain

        self.board = board
        self.parent = parent
        self.children = []
        # Store game_end & game_winner as we can't retrieve them from the board state
        self.terminal = terminal
        self.winner = winner
        self.results = Result()

        self.visit_count = 0

        self.move_played = move

        self.unexplored_moves = board.get_valid_moves()

    def best_child(self, c=1.41):
        ucb_values = []

        for node in self.children:
            # Get wins for this child node
            wins = node.results.get_wins(self.board.get_current_player())
            losses = node.results.get_wins(self.board.get_inactive_player())

            # Calculate win-rate
            node_value = (wins - losses) / node.visit_count

            # Calculate sqrt() part of UCB formula
            root = np.sqrt(np.log(self.visit_count) / node.visit_count)

            # Calculate value
            val = node_value + (c * root)

            # Add value
            ucb_values.append(val)

        return self.children[np.argmax(ucb_values)]

    def is_fully_expanded(self):
        return len(self.unexplored_moves) == 0

    def is_terminal_node(self):
        return self.terminal

    def expand(self):
        # Return one of our unexplored moves
        new_board = Board(self.board.configuration)
        new_board.player_x = self.board.player_x
        new_board.player_o = self.board.player_o
        new_board.board = self.board.board.copy()

        board_move = self.unexplored_moves.pop()
        game_end, game_winner = new_board.play(new_board.get_current_player(), board_move)

        # Create new node
        node = Node(self.brain, new_board, board_move, game_end, game_winner, self)
        self.children.append(node)

        return node

    def simulation(self):
        # If we're a terminal node, just return our winner already
        if self.terminal:
            return self.terminal, self.winner

        # Record moves so we can undo them
        moves = []

        # Play the rest of the game out from this board state
        game_end = False

        # Random playout
        while not game_end:
            board_move = random.choice(self.board.get_valid_moves())
            moves.append(board_move)
            game_end, game_winner = self.board.play(self.board.get_current_player(), board_move)

        # Undo moves
        for move in moves:
            self.board.set_empty(move)

        return game_end, game_winner

    def backpropagate(self, game_winner):
        # Add to statistics
        self.visit_count += 1
        self.results.add_win(game_winner)

        # Apply result recursively to parent node
        if self.parent is not None:
            self.parent.backpropagate(game_winner)
