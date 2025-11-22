from PyQt5.QtWidgets import QApplication
from controller import Controller
from whatsapp import WhatsApp
from PyQt5 import QtCore
from home import Home
import sys

class SignalReceive(QtCore.QObject):
    # Fechar aba de preferencias
    close_preferences = QtCore.pyqtSignal()
    # novo numero adicionado
    new_phone_number = QtCore.pyqtSignal(dict)
    # conta do WhatsApp bloqueada ou desconectada
    account_blocked = QtCore.pyqtSignal(dict)
    # iniciar maturação
    start_maturation = QtCore.pyqtSignal()
    # parar maturação
    stop_maturation = QtCore.pyqtSignal()
    # inserir campo no table de status da maturação
    inject_message_row =  QtCore.pyqtSignal(dict)
    
ripening :WhatsApp = None

def start_maturation(signals, controller):
    global ripening
    ripening = WhatsApp(signals=signals, controller=controller)
    ripening.prepare()

# Instanciar o app e classes

app = QApplication(sys.argv)
signals = SignalReceive()
controller = Controller("12.11.2025", signals=signals)
window = Home(controller=controller)
#window.sidebar.page().loadStarted.connect(lambda: window.show )
controller.setHomePage(home=window)

# Connectar eventos PyQt Signal

signals.close_preferences.connect( controller.close_preferences )
signals.new_phone_number.connect( lambda data: controller.accountAuthenticated(data) )
signals.account_blocked.connect( lambda  data: controller.accountDisconnected(data) )
signals.start_maturation.connect(lambda: start_maturation(signals=signals, controller=controller) )
signals.inject_message_row.connect(lambda data: controller.inject_message_row(data=data))

# Exibir janela

window.show()

sys.exit(app.exec_())
