import functools

from PyQt5 import QtWidgets, QtGui, QtCore

import tictactoe.constants as constants
from tictactoe.algorithms.q_learning import Q_Learning
from tictactoe.scoring import Scoring
from tictactoe.player import Player
from tictactoe.ui import game, menu


class Menu(QtWidgets.QMainWindow, menu.Ui_menu):

    def __init__(self, app):
        super().__init__()

        self.app = app

        # Load UI from python file
        self.setupUi(self)

        # Set windon icon
        self.setWindowIcon(QtGui.QIcon("assets/emoji_x.png"))

        # Initialise players
        self.player_x = Player(constants.CROSS, None)
        self.player_o = Player(constants.NOUGHT, None)

        self.enabled_button_stylesheet = "background-color: PaleGreen; border: 2px solid limegreen;"

        # Set icons
        self.playAsCross.setIcon(QtGui.QIcon("assets//emoji_x.png"))
        self.playAsNought.setIcon(QtGui.QIcon("assets//emoji_o.png"))
        self.play3x3.setIcon(QtGui.QIcon("assets//3x3_board.png"))
        self.play5x5.setIcon(QtGui.QIcon("assets//5x5_board.png"))
        self.play7x7.setIcon(QtGui.QIcon("assets//7x7_board.png"))

        # Setup algorithm dropdown
        self.algorithmDropdown.clear()
        for algorithm in constants.DESCRIPTIONS.keys():
            # Set the data for this item to the algorithm's name so we can update descriptions later.
            self.algorithmDropdown.addItem(algorithm, algorithm)

        # Setup button signals
        self.playAsCross.clicked.connect(functools.partial(self.select_player, self.player_x))
        self.playAsNought.clicked.connect(functools.partial(self.select_player, self.player_o))

        self.play3x3.clicked.connect(functools.partial(self.select_board_size, 3))
        self.play5x5.clicked.connect(functools.partial(self.select_board_size, 5))
        self.play7x7.clicked.connect(functools.partial(self.select_board_size, 7))

        self.algorithmDropdown.currentIndexChanged.connect(self.select_algorithm)

        self.playButton.clicked.connect(self.play_game)

        # Set defaults
        self.select_player(self.player_x)
        self.select_board_size(3)
        self.select_algorithm()

    def select_player(self, player):
        # Set play_as_player to the player they want to play as
        self.play_as_player = player
        self.ai_player = self.player_o if player == self.player_x else self.player_x

        # Set green colour for button
        if player == self.player_x:
            self.playAsCross.setStyleSheet(self.enabled_button_stylesheet)
            self.playAsNought.setStyleSheet("")
        else:
            self.playAsCross.setStyleSheet("")
            self.playAsNought.setStyleSheet(self.enabled_button_stylesheet)

    def select_board_size(self, size):
        # Set playSize to the
        self.play_board_size = size

        # Update description
        self.boardSizeDescription.setText(
            "{size}x{size}: Connect {symbols_needed} symbols in a row to win.".format(**constants.BOARD_LAYOUT[size]))

        # Set green colour for button
        if size == 3:
            self.play3x3.setStyleSheet(self.enabled_button_stylesheet)
            self.play5x5.setStyleSheet("")
            self.play7x7.setStyleSheet("")
        elif size == 5:
            self.play3x3.setStyleSheet("")
            self.play5x5.setStyleSheet(self.enabled_button_stylesheet)
            self.play7x7.setStyleSheet("")
        else:
            self.play3x3.setStyleSheet("")
            self.play5x5.setStyleSheet("")
            self.play7x7.setStyleSheet(self.enabled_button_stylesheet)

    def select_algorithm(self):
        # Update description
        self.play_algorithm = self.algorithmDropdown.itemData(self.algorithmDropdown.currentIndex())

        self.algorithmDescription.setText(constants.DESCRIPTIONS[self.play_algorithm]["description"])

    def play_game(self):
        self.hide()

        self.game_ui = GameDisplay(self.app, self, self.play_as_player, self.ai_player, self.play_algorithm,
                                   self.play_board_size)

class GameDisplay(QtWidgets.QMainWindow, game.Ui_board):

    def __init__(self, app, menu, human_player, ai_player, algorithm, board_configuration):
        super(GameDisplay, self).__init__()

        print("Loading gui.")

        from tictactoe.board import Board

        self.app = app
        self.menu = menu

        # Setup UI from python files
        self.setupUi(self)

        # Set windon icon
        self.setWindowIcon(QtGui.QIcon("assets/emoji_x.png"))

        # Load GUI and display loading message
        self.show()
        self.loadingMessage.show()
        self.app.processEvents()

        # Initialise board & algorithms
        self.board = Board(constants.BOARD_LAYOUT[board_configuration])
        self.board.player_x = human_player if human_player.symbol == constants.CROSS else ai_player
        self.board.player_o = human_player if human_player.symbol == constants.NOUGHT else ai_player

        # Initialise brain for AI
        ai_player.brain = constants.DESCRIPTIONS[algorithm]["brain"](ai_player, human_player, self.board)
        ai_player.brain.load()
        ai_player.set_playing_tactic(constants.PLAYING_TACTIC[1][1])

        # For Q-Learning, ensure epsilon is set to 0 so that we exploit
        if isinstance(ai_player.brain, Q_Learning):
            ai_player.algorithm.EPSILON = 0

        self.loadingMessage.hide()

        self.human_player = human_player
        self.ai_player = ai_player

        # Setup table for playing
        self.boardWidget.setRowCount(self.board.dimensions)
        self.boardWidget.setColumnCount(self.board.dimensions)

        self.boardWidget.setShowGrid(False)

        self.boardWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.boardWidget.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.boardWidget.horizontalHeader().hide()
        self.boardWidget.verticalHeader().hide()

        self.buttons = []

        self.delegate = DrawBorderDelegate(self.board.dimensions)

        self.boardWidget.setItemDelegate(self.delegate)

        # Create buttons for each of the moves
        for move in range(self.board.squares):
            button = QtWidgets.QPushButton()

            self.buttons.append(button)
            self.boardWidget.setCellWidget(move // self.board.dimensions, move % self.board.dimensions, button)

            button.clicked.connect(functools.partial(self.button_clicked, move))

        # Initialise another thread to calculate AI's move so we don't freeze our program.
        self.thread = QtCore.QThread()
        self.thread.start()

        # Move the worker to the new thread.
        self.worker = AI_Worker(self.ai_player)
        self.worker.moveToThread(self.thread)

        # After the move has been calculated, call play_ai_move which will then interact with the board object
        self.worker.finished.connect(self.play_ai_move)

        # Update scoreboard
        self.scores = Scoring()
        self.update_scores()

        # Reset & start game
        self.reset_game()
        self.resetButton.clicked.connect(self.reset_game)
        self.returnToMenu.clicked.connect(self.return_to_menu)

    def reset_game(self):
        # Clear board
        self.board.reset_board()

        # Disable reset button
        self.resetButton.setEnabled(False)

        self.game_end = False

        # Reversed as evaluate_game swaps players when called
        # i.e user player will be swapped to AI player for the next move.
        self.current_player = self.ai_player if self.human_player.symbol == constants.CROSS else self.human_player

        # Begin game
        self.evaluate_game(False, False)

    def return_to_menu(self):
        # Show menu
        self.menu.show()

        # Exit thread
        self.thread.exit()

        # Close game display
        self.close()

    def update_table(self):
        for index, symbol in enumerate(self.board.current_state.flatten()):
            if symbol == constants.NULL:
                image = "assets//blank.png"
            elif symbol == constants.CROSS:
                image = "assets//emoji_x.png"
            else:
                image = "assets//emoji_o.png"

            self.buttons[index].setStyleSheet("QPushButton {{ border: 3px solid red; border-image: url(\"{}\")}}".format(image))

    def button_clicked(self, move):
        # Check that it's the human's turn
        if self.current_player == self.ai_player:
            return

        # If the game has already ended, ignore their move
        if self.game_end:
            return

        # If they've picked a move that has already been played, ignore it
        if move not in self.board.valid_moves():
            return

        # Play and evaluate
        game_end, game_winner = self.board.play_move(self.human_player, move)

        self.evaluate_game(game_end, game_winner)

    def ai_play(self):
        # Start thread to get AI move
        self.worker.run()

    def play_ai_move(self, board_move, state_move):
        if board_move == -1 and state_move == -1:
            return

        # Play and evaluate
        game_end, game_winner = self.board.play_move(self.ai_player, board_move)

        self.evaluate_game(game_end, game_winner)

    def evaluate_game(self, game_end, game_winner):
        # Display the new board
        self.update_table()

        self.app.processEvents()

        # Check whether the game has finished
        if game_end:
            self.game_end = True

            # Add to winner statS
            self.scores.increment_win(game_winner)

            self.update_scores()

            # Update label and set enabled
            if game_winner != constants.GAME_DRAW:
                self.statusLabel.setText("Game over! {} wins.".format(game_winner.name))
            else:
                self.statusLabel.setText("Game over! It's a draw.")

            self.resetButton.setEnabled(True)
        else:
            # Otherwise, swap the current player and if it's the AI's turn, get their move.
            self.current_player = self.ai_player if self.current_player == self.human_player else self.human_player

            if self.current_player == self.ai_player:
                self.statusLabel.setText("Computer is thinking...")

                # Update UI before beginning move calculation
                self.app.processEvents()

                self.ai_play()
            else:
                # Wait for the human to press a button
                self.statusLabel.setText("Your turn...")

    def update_scores(self):
        self.scoreX.setText(str(self.scores.crosses_wins))
        self.scoreO.setText(str(self.scores.noughts_wins))
        self.scoreD.setText(str(self.scores.draws))


class AI_Worker(QtCore.QObject):

    def __init__(self, player, *args, **kwargs):
        QtCore.QObject.__init__(self, *args, **kwargs)
        self.player = player

    def run(self):
        try:
            # Get move
            self.board_move, self.state_move = self.player.get_move()
        except:
            # Print error in the event something goes wrong
            import traceback
            self.error.emit(traceback.format_exc())
            self.finished.emit(-1, -1)
        else:
            # Emit the calculated move so we can make the move
            self.finished.emit(self.board_move, self.state_move)

    error = QtCore.pyqtSignal(str)
    finished = QtCore.pyqtSignal(int, int)


class DrawBorderDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, board_size):
        super(DrawBorderDelegate, self).__init__()

        self.board_size = board_size

    def paint(self, painter, option, index):
        column = index.column()
        row = index.row()

        # Set width of the edges to 3
        rect = QtCore.QRect(option.rect)
        pen = painter.pen()
        pen.setWidth(3)
        painter.setPen(pen)

        # Draw left side of the cell
        if column - 1 >= 0:
            painter.drawLine(rect.topLeft(), rect.bottomLeft())

        # Draw right side of the cell
        if column + 1 < self.board_size:
            painter.drawLine(rect.topRight(), rect.bottomRight())

        # Draw top side of cell
        if row - 1 >= 0:
            painter.drawLine(rect.topLeft(), rect.topRight())

        # Draw bottom side of cell
        if row + 1 < self.board_size:
            painter.drawLine(rect.bottomLeft(), rect.bottomRight())
