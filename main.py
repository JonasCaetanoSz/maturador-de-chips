from PyQt6.QtWidgets import QApplication
from PyQt6 import QtCore
from controller import Controller
from whatsapp import WhatsApp
from home import Home
import sys

class SignalReceive(QtCore.QObject):
    # Fechar aba de preferencias
    close_preferences = QtCore.pyqtSignal()
    # novo numero adicionado
    new_phone_number = QtCore.pyqtSignal(dict)
    # conta do WhatsApp bloqueada ou desconectada
    account_blocked = QtCore.pyqtSignal(dict)
    # iniciar maturação (Privado)
    start_maturation = QtCore.pyqtSignal()
    # iniciar maturação (Grupos)
    start_group_maturation = QtCore.pyqtSignal()
    # parar maturação
    stop_maturation = QtCore.pyqtSignal()
    # inserir campo no table de status da maturação
    inject_message_row = QtCore.pyqtSignal(dict)
    # Enviar mensagem de texto no whatsapp (Privado)
    send_whatsapp_text_message = QtCore.pyqtSignal(dict)
    # Enviar mensagem de texto e figurinha no whatsapp (Grupos)
    send_whatsapp_group_message = QtCore.pyqtSignal(dict)
    # trocar para uma aba no stacked principal
    change_current_stacked_index = QtCore.pyqtSignal(int)


ripening: WhatsApp = None


def start_maturation(signals, controller):
    global ripening, window
    window.status_view.reload()
    ripening = WhatsApp(signals=signals, controller=controller)
    ripening.prepare(mode="private")


def start_group_maturation_handler(signals, controller):
    global ripening, window
    window.status_view.reload()
    ripening = WhatsApp(signals=signals, controller=controller)
    ripening.prepare(mode="group")


# Instanciar o app e classes  

app = QApplication(sys.argv)
signals = SignalReceive()
# A data já foi atualizada na sua fonte para 17.07.2026
controller = Controller("17.07.2026", signals=signals)
window = Home(controller=controller)
# window.sidebar.page().loadStarted.connect(lambda: window.show)
controller.setHomePage(home=window)

# Connectar eventos PyQt Signal

signals.close_preferences.connect(controller.close_preferences)
signals.new_phone_number.connect(lambda data: controller.accountAuthenticated(data))
signals.account_blocked.connect(lambda data: controller.accountDisconnected(data))
signals.change_current_stacked_index.connect(lambda idx: window.stacked.setCurrentIndex(idx))

# Conexões de Start/Stop da Maturação
signals.start_maturation.connect(lambda: start_maturation(signals=signals, controller=controller))
signals.start_group_maturation.connect(lambda: start_group_maturation_handler(signals=signals, controller=controller))
signals.stop_maturation.connect(lambda: controller.stop_maturation(whatsapp=ripening))

# Conexões de Mensagens JS
signals.inject_message_row.connect(lambda data: controller.inject_message_row(data=data))
signals.send_whatsapp_text_message.connect(lambda data: controller.send_whatsapp_text_message(**data) )
signals.send_whatsapp_group_message.connect(lambda data: controller.send_whatsapp_group_message(data) )


# Exibir janela

window.show()

sys.exit(app.exec())