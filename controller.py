from PyQt5.QtCore import QUrl, pyqtSlot, QObject
import webbrowser
import os

class Controller(QObject):
    def __init__(self, accounts_page):
        super().__init__()
        self.accounts_page_instance = accounts_page

    # bot de numerosa virtuais no telegram
         
    @pyqtSlot()
    def telegram_bot_virtual_number_open(self):
        try:
            if os.path.exists(
                    os.path.join(
                    os.environ["APPDATA"],
                    "Telegram Desktop"
                )):
                telegram_url = "tg://resolve?domain=NotzSMSBot&start=6455672508"
            
            else:
                raise FileNotFoundError("telegram não encontrado")
        except:
            telegram_url = "https://t.me/NotzSMSBot?start=6455672508"

        webbrowser.open(url=telegram_url)

    # exibir contas conectadas
        
    @pyqtSlot()
    def accounts_viewer(self):
        if self.accounts_page_instance._opened:
            self.accounts_page_instance.activateWindow()
        self.accounts_page_instance._opened = True
        self.accounts_page_instance.show()

    # relatar problema 
    
    @pyqtSlot()
    def open_insues_link(self):
        webbrowser.open(url="https://github.com/JonasCaetanoSz/maturador-de-chips/issues")


    
    # abrir o link do repositório do projeto no github

    @pyqtSlot()
    def open_github_repository(self):
        webbrowser.open(url="https://github.com/JonasCaetanoSz/maturador-de-chips")    

    # abrir o link da licença do código

    @pyqtSlot()
    def open_license_repository(self):
        webbrowser.open(url="https://github.com/JonasCaetanoSz/maturador-de-chips/blob/main/LICENSE")

    # selecionar o arquivo de conversas

    @pyqtSlot()
    def selected_file(self):
        pass