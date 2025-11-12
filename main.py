from controller import Controller
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore
from home import Home
import sys

class SignalReceive(QtCore.QObject):
    # Fechar aba de preferencias
    close_preferences = QtCore.pyqtSignal()



app = QApplication(sys.argv)
signals = SignalReceive()

controller = Controller("12.11.2025", signals=signals)
window = Home(controller=controller)
controller.setHomePage(home=window)
signals.close_preferences.connect( controller.close_preferences )
window.show()
sys.exit(app.exec_())
