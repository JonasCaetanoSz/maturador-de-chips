from PyQt5.QtWebEngineWidgets import QWebEngineView
from plyer import notification
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QUrl, QThread
from gpt import GptGenerateMessage
from controller import Controller
from dashboard import MainWindow
import datetime
import random
import json
import time
import os

class WhatsApp(QThread):

    def __init__(self, window:MainWindow, messages_file:dict, phones:dict, signals, webviews:list, controller:Controller) -> None:
        super().__init__()
        self.messages = [i.rstrip("\r").rstrip("\n") for i in messages_file["content"]]
        self.configs = json.load(open(file="state.json", mode="r", encoding="utf8"))
        self.OPEN_CHAT_SCRIPT = open(file="scripts/open_chat.js", mode="r", encoding="utf8").read()
        self.CHECK_BLOCK_SCRIPT = open(file="scripts/check_block.js", mode="r", encoding="utf8").read()
        self.SEND_MESSAGE_SCRIPT = open(file="scripts/send_message.js", mode="r", encoding="utf8").read()
        self.CLOSE_CHAT_SCRIPT = open(file="scripts/close_chat.js", mode="r", encoding="utf8").read()
        self.gpt_random_message:GptGenerateMessage = None
        self.have_a_blocked_account = False
        self.controller = controller
        self.phones = list(set(phones.values()))
        self.window = window
        self.webviews = webviews
        self.signals = signals

        self.phones_sender_control = []
        self.phones_receiver_control = []
        self.used_accounts = []
        self.current_sending_account = None
        self.current_receiver_account = None
        self.messages_send_count = 0
        self.sending = tuple()

    def start(self) -> None:

        if len(self.phones) < 2:
            return QMessageBox.about(
            self.window,
            "Maturador de Chips",
            "número de contas insuficiente para iniciar a maturação."
        )

        elif not self.configs["openAIToken"] and self.configs["messageInputMethod"] == "byOpenAI":
            return QMessageBox.about(
            self.window,
            "Maturador de Chips",
            "token de acesso á API openIA invalida"
        )

        elif not self.configs["AIUnofficialToken"] and self.configs["messageInputMethod"] == "byOpenAIUnofficial":
            return QMessageBox.about(
            self.window,
            "Maturador de Chips",
            "cookie ou token de acesso á API não oficial invalida"
        )

        elif not self.messages and self.configs["messageInputMethod"] == "byFile":
            return QMessageBox.about(
            self.window,
            "Maturador de Chips",
            "o arquivo de mensagens base não foi escolhido ou está vazio."
        )
        if self.configs["messageInputMethod"] != "byFile":
            self.gpt_random_message = GptGenerateMessage()
            self.gpt_random_message.set_bing_cookie(cookie=self.configs["AIUnofficialToken"]) if self.configs["messageInputMethod"] == "byOpenAIUnofficial" \
                else self.gpt_random_message.ininialize_openai_client(token=self.configs["openAIToken"])

        self.window.setFixedSize(749, 560)
        self.window.webview.load(QUrl.fromLocalFile("/pages/updates.html"))
        self.window.setWindowTitle("Maturador de chips - maturação em andamento ")
        super().start()

    # finalizar a thread de maturação
        
    def stop(self) -> None:
        super().terminate()
    
    # aquecendo os chips em uma segunda thread para não travar a interface gráfica
        
    def run(self) -> None:
        # inicializar as variáveis de controle para cada execução
        phones_copy = self.phones.copy()
        random.shuffle(phones_copy)  # embaralhar para garantir aleatoriedade

        for execution_count in range(0, int(self.configs["StopAfterMessages"])):
            self.messages_send_count += 1

            if len(self.phones_sender_control) == len(self.phones):
                self.phones_sender_control.clear()

            if len(self.phones_receiver_control) == len(self.phones):
                self.phones_receiver_control.clear()

            if len(self.used_accounts) == len(self.phones):
                self.used_accounts.clear()

            # escolher a conta que envia mensagem
            while not self.current_sending_account or \
                self.current_sending_account in self.phones_sender_control or \
                self.current_sending_account in self.used_accounts:
                self.current_sending_account = phones_copy.pop()
                if not phones_copy:  # se não houver mais números de telefone, reiniciar a lista
                    phones_copy = self.phones.copy()
                    random.shuffle(phones_copy)

            # escolher a conta que vai receber
            while not self.current_receiver_account or \
                self.current_receiver_account in self.phones_receiver_control or \
                self.current_sending_account == self.current_receiver_account or \
                self.current_receiver_account in self.used_accounts:
                self.current_receiver_account = phones_copy.pop()
                if not phones_copy:  # se não houver mais números de telefone, reiniciar a lista
                    phones_copy = self.phones.copy()
                    random.shuffle(phones_copy)

            # atualizar as listas de controle
                    
            self.phones_sender_control.append(self.current_sending_account)
            self.phones_receiver_control.append(self.current_receiver_account)
            self.used_accounts.extend([self.current_sending_account, self.current_receiver_account])

            # escolhendo mensagem
                
            message = random.choice(self.messages) if self.configs["messageInputMethod"] == "byFile" else \
                self.gpt_random_message.by_official() if self.configs["messageInputMethod"] == "byOpenAI" else self.gpt_random_message.by_unnoficial()

            if isinstance(message, tuple):
                notification.notify(
                    title="Maturador de chips",
                    message=f"erro ao gerar mensagem com GPT: {message[1] if len(message[1]) < (255 - 32) else  message[1][:(255 - 32)]}"  ,
                    app_icon="pages/assets/medias/icon.ico", 
                    timeout=5,
                )
                continue

            # checando bloqueio e enviando mensagem
            account_sender_webview:QWebEngineView = self.webviews[ self.phones.index( self.current_sending_account ) ]
            account_is_blocked = self.check_block(self.current_sending_account, account_webview=account_sender_webview)
            if account_is_blocked == -1:
                continue
            elif account_is_blocked:
                return
            account_sender_webview.page().runJavaScript(self.OPEN_CHAT_SCRIPT.replace("@PHONE", self.current_receiver_account))
            time.sleep(2)
            account_sender_webview.page().runJavaScript(self.SEND_MESSAGE_SCRIPT.replace("@MESSAGE", message))
            time.sleep(2)
            account_sender_webview.page().runJavaScript(self.CLOSE_CHAT_SCRIPT)
            time.sleep(1)
    
            self.controller.notifications.append({
                "enviadoDe": self.current_sending_account,
                "recebidoPor": self.current_receiver_account,
                "mensagem": message,
                "horario":  datetime.datetime.now().strftime("%H:%M:%S") 
            })

            # aguardando o fim do intervalo definido pelo usuário

            time.sleep( random.randint( int(self.configs["MinimumMessageInterval"]) ,  int(self.configs["MaximumMessageInterval"]) ))

        # maturação concluída
            
        if self.configs["ShutdownAfterCompletion"]:
            os.system("shutdown /s /t 30")
        self.signals.message_box.emit(
                "Maturador de chips",
                "maturação concluída com sucesso!")
        self.signals.stop_maturation.emit()
        
    # parar maturação
            
    def stop(self):
        super().terminate()
        self.window.setFixedSize(767, 620)
        self.window.webview.load(QUrl.fromLocalFile("/pages/dashboard.html"))
        self.window.setWindowTitle("Maturador de chips - Dashboard")
    
    # definir que uma conta foi bloqueada
        
    def set_account_block(self, phone:str):
        self.have_a_blocked_account = True

    # checar se a conta que esta enviando mensagem foi bloqueada os desconectada

    def check_block(self, phone:str, account_webview:QWebEngineView) -> bool|int:

        account_webview.page().runJavaScript(self.CHECK_BLOCK_SCRIPT.replace("@PHONE", phone)) 
        time.sleep(3)
        
        if self.have_a_blocked_account and not self.configs["ContinueOnBlock"]:
            self.signals.message_box.emit(
            "Maturador de Chips",
            f"o número {phone} foi desconectado ou banido. parando maturação!")
            self.signals.stop_maturation.emit()
            return True
        
        elif self.have_a_blocked_account and len(self.phones) == 2:
            self.signals.message_box.emit(
                "Maturador de Chips",
                f"o número {phone} foi desconectado ou banido e agora o número de contas conectadas é insuficiente para continuar. parando maturação!")
            self.signals.stop_maturation.emit()
            return True

        elif self.have_a_blocked_account:
            notification.notify(
                    title="Maturador de chips",
                    message="conta desconectada ou banida: " + phone,
                    app_icon="pages/assets/medias/icon.ico", 
                    timeout=5,
                )
            self.phones.remove(phone)
            self.have_a_blocked_account = False
            return -1
        
        return False