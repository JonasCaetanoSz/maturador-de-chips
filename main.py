from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore
import dashboard
import accounts

from whatssap import Whatssap
from api import Api
import threading
import sys


# recebe sinais para fazer alguma ação

class SignalReceive(QtCore.QObject):
    # mostrar a pagina de contas conectadas
    viewer_accounts = QtCore.pyqtSignal()
    # novo numero adicionado, atualizar a pagina
    new_phone_number = QtCore.pyqtSignal()
    # conta dowhatssap bloqueada ou desconectada
    account_blocked = QtCore.pyqtSignal(str)
    # parar maturação
    stop_maturation = QtCore.pyqtSignal()
    # iniciar maturação
    start_maturation = QtCore.pyqtSignal(dict, list)
    # fechar a pagina de contas conectadas
    close_accounts_page = QtCore.pyqtSignal()


# iniciar maturação

wapp:Whatssap = None

def start_maturation(window, messages_file, phones,signals):
    global wapp
    wapp = Whatssap(window=window, messages_file=messages_file, phones=phones,signals=signals, webviews=accounts_page.webviews)
    wapp.start()


# iniciar a aplicação

VERSION = "30.06.2023"

if __name__ == "__main__":

    app = QApplication(sys.argv)
    signals = SignalReceive()
    api = Api(VERSION, signals)
    accounts_page = accounts.MainWindow(api_instance=api)
    signals.viewer_accounts.connect(lambda: api.set_account_page_state(True, accounts_page) == accounts_page.show())
    threading.Thread(target=api.start,daemon=True).start()
    window = dashboard.MainWindow(accounts_page, signals)
    
    # conectar os sinais pyqtsignal

    signals.new_phone_number.connect(lambda: window.webview.reload() if "/dashboard" in window.webview.url().toString() else None) 
    signals.start_maturation.connect(lambda messages_file, phones: start_maturation(window=window, messages_file=messages_file, phones=phones,signals=signals))
    signals.stop_maturation.connect(lambda: threading.Thread(target=wapp.stop() if wapp else None, daemon=True).start())
    signals.account_blocked.connect(lambda phone: wapp.set_account_block(phone=phone))
    signals.close_accounts_page.connect(lambda: accounts_page.close() )
    
    # iniciar o programa na interface dashboard

    window.show()   
    app.exec()