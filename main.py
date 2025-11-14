from PyQt5.QtWidgets import QApplication
from controller import Controller
from PyQt5 import QtCore
from home import Home
import sys

class SignalReceive(QtCore.QObject):
    # Fechar aba de preferencias
    close_preferences = QtCore.pyqtSignal()

# Instanciar o app e classes

app = QApplication(sys.argv)
signals = SignalReceive()
controller = Controller("12.11.2025", signals=signals)
window = Home(controller=controller, app=app)
window.sidebar.page().loadStarted.connect(lambda: window.show )
controller.setHomePage(home=window)

# Connectar eventos PyQt Signal

signals.close_preferences.connect( controller.close_preferences )

# Exibir janela

window.show()

sys.exit(app.exec_())
