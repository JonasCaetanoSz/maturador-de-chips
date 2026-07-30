import os
import sys

sys.argv.extend([
    "--disable-gpu",                      # Desativa aceleração de GPU desnecessária em background
    "--disable-software-rasterizer",
    "--no-sandbox",                       # Reduz overhead de processos
    "--disable-dev-shm-usage",            # Evita estouro de memória compartilhada
    "--disable-accelerated-2d-canvas",
    "--js-flags=--max-old-space-size=256" # Limita a memória JS do Chromium por aba/conta a 256MB
])

from PyQt6.QtWidgets import QApplication
from PyQt6 import QtCore
from controller import Controller
from whatsapp import WhatsApp
from home import Home

class SignalReceive(QtCore.QObject):
    close_preferences = QtCore.pyqtSignal()
    new_phone_number = QtCore.pyqtSignal(dict)
    account_blocked = QtCore.pyqtSignal(dict)
    start_maturation = QtCore.pyqtSignal()
    start_group_maturation = QtCore.pyqtSignal()
    stop_maturation = QtCore.pyqtSignal()
    inject_message_row = QtCore.pyqtSignal(dict)
    send_whatsapp_text_message = QtCore.pyqtSignal(dict)
    send_whatsapp_group_message = QtCore.pyqtSignal(dict)
    change_current_stacked_index = QtCore.pyqtSignal(int)
    show_alert = QtCore.pyqtSignal(str, str)

ripening: WhatsApp = None

def start_maturation(signals, controller):
    global ripening, window
    window.status_view.reload()
    
    # Encerra instância anterior se ainda estiver rodando para liberar recursos
    if ripening and ripening.isRunning():
        ripening.stop()
        
    ripening = WhatsApp(signals=signals, controller=controller)
    ripening.prepare(mode="private")

def start_group_maturation_handler(signals, controller):
    global ripening, window
    window.status_view.reload()
    
    # Encerra instância anterior se ainda estiver rodando para liberar recursos
    if ripening and ripening.isRunning():
        ripening.stop()
        
    ripening = WhatsApp(signals=signals, controller=controller)
    ripening.prepare(mode="group")

# Instanciar o app e classes  
app = QApplication(sys.argv)
signals = SignalReceive()
controller = Controller("20.07.2026", signals=signals)
window = Home(controller=controller)
controller.setHomePage(home=window)

# Conectar eventos PyQt Signal
signals.close_preferences.connect(controller.close_preferences)
signals.new_phone_number.connect(lambda data: controller.accountAuthenticated(data))
signals.account_blocked.connect(lambda data: controller.accountDisconnected(data))
signals.change_current_stacked_index.connect(lambda idx: window.stacked.setCurrentIndex(idx))
signals.show_alert.connect(lambda t, m: controller.show_alert(title=t, message=m))

# Conexões de Start/Stop da Maturação
signals.start_maturation.connect(lambda: start_maturation(signals=signals, controller=controller))
signals.start_group_maturation.connect(lambda: start_group_maturation_handler(signals=signals, controller=controller))
signals.stop_maturation.connect(lambda: controller.stop_maturation(whatsapp=ripening))

# Conexões de Mensagens JS
signals.inject_message_row.connect(lambda data: controller.inject_message_row(data=data))
signals.send_whatsapp_text_message.connect(lambda data: controller.send_whatsapp_text_message(**data))
signals.send_whatsapp_group_message.connect(lambda data: controller.send_whatsapp_group_message(data))

# Exibir janela
window.show()

sys.exit(app.exec())