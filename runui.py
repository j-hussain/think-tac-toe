import sys


###################################
# https://stackoverflow.com/questions/42621528/why-python-console-in-pycharm-doesnt-show-any-error-message-when-pyqt-is-used
# Used to catch PyQt5 exceptions in PyCharm.
def catch_exceptions(t, val, tb):
    print("""An exception was raised: {}""".format(t))
    old_hook(t, val, tb)


old_hook = sys.excepthook
sys.excepthook = catch_exceptions
###################################

print("Loading UI for Noughts and Crosses.")

# Load UI for player
from PyQt5 import QtWidgets
from ui_controller import Menu
import sys

app = QtWidgets.QApplication(sys.argv)

menu_ui = Menu(app)
menu_ui.show()

app.exec()
