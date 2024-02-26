from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore
import dashboard
import accounts

from controller import Controller
from whatsapp import WhatsApp
import threading
import sys

# redireciona saídas de logs e erros para o arquivo de log

sys.stdout = open("MaturadorLogs.txt", "a", encoding="utf-8")
sys.stderr = open("MaturadorLogs.txt", "a", encoding="utf-8")

# recebe sinais para fazer alguma ação

class SignalReceive(QtCore.QObject):
    # novo numero adicionado
    new_phone_number = QtCore.pyqtSignal(dict)
    # conta do WhatsApp bloqueada ou desconectada
    account_blocked = QtCore.pyqtSignal(dict)
    # parar maturação
    stop_maturation = QtCore.pyqtSignal()
    # iniciar maturação
    start_maturation = QtCore.pyqtSignal(dict, dict)
    # exibir um Qmessagebox 
    message_box = QtCore.pyqtSignal(str, str)

# iniciar maturação

wapp:WhatsApp = None

def start_maturation(window, messages_file, phones,signals):
    global wapp, controller_instance
    wapp = WhatsApp(window=window, messages_file=messages_file, phones=phones,signals=signals, webviews=accounts_page.webviews, controller=controller_instance)
    wapp.start()

# iniciar a aplicação

VERSION = "24.02.2024"

if __name__ == "__main__":

    app = QApplication(sys.argv)
    signals = SignalReceive()
    accounts.SIGNALS = signals
    accounts_page = accounts.MainWindow()
    controller_instance = Controller(accounts_page, VERSION, signals)
    window = dashboard.MainWindow(accounts_page, signals, app, controller_instance)
    accounts_page.controller = controller_instance
    controller_instance.dashboard_window = window
    
    # conectar os sinais de pyqtsignal

    signals.new_phone_number.connect(lambda account_data: [controller_instance.account_added(account_data), window.webview.reload()] if account_data else window.webview.reload())
    signals.start_maturation.connect(lambda messages_file, phones: start_maturation(window=window, messages_file=messages_file, phones=phones,signals=signals))
    signals.stop_maturation.connect(lambda: threading.Thread(target=wapp.stop() if wapp else None, daemon=True).start())
    signals.account_blocked.connect(lambda account_data: ( controller_instance.account_blocked(account_data) == wapp.set_account_block(phone=account_data["phone"]) ))
    signals.message_box.connect(lambda title, message: controller_instance.message_box(message=message, title=title))
    
    # iniciar o programa na interface dashboard
    
    window.show()   
    app.exec()