from PyQt5.QtWidgets import (
    QStackedWidget,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QInputDialog,
    QHBoxLayout,
    QScrollArea,
    QMessageBox,
    QWidget
    )

from PyQt5.QtWebEngineWidgets import (QWebEngineView, QWebEngineProfile, QWebEnginePage)
from PyQt5.QtWebEngineCore import (QWebEngineUrlRequestInterceptor)
from PyQt5.QtGui import (QIcon, QCursor)
from PyQt5.QtCore import (QUrl, Qt)

import shutil                                          
import json
import os

SIGNALS = None

# sobrescreve as funções de log javascript para que, todas as saídas geradas sejam escritas no arquivo de log do maturador

class LogCapturingPage(QWebEnginePage):
    def consoleMessage(self, level, message, lineNumber, sourceID):
        try:
            log_message = f"{level} - {message}"
            with open("MaturadorLogs.txt", "a", encoding="utf-8") as log_file:
                log_file.write(log_message + "\n")
        except:
            pass
    
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        try:
            log_message = f"{level} - {message}"
            with open("MaturadorLogs.txt", "a", encoding="utf-8") as log_file:
                log_file.write(log_message + "\n")
        except:
            pass


# interceptar as requisições que vem do WhatsApp web para filtrar 
# as que são feitas para enviar dados ao maturador, isso é necessário 
# pois o WhatsApp web bloqueia requisições feitas para domínios
# diferente do deles através do content security policy (CSP).

class RequestInterceptor(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info):
        
        # novo numero adicionado
        
        if "/maturador/api/account-added" in info.requestUrl().path():
            url_path = info.requestUrl().path()
            json_string = url_path[url_path.find("{"):url_path.find("}") + 1]
            data = json.loads(json_string)
            global SIGNALS
            SIGNALS.new_phone_number.emit(data)
            info.block(True)
        
        # conta bloqueada

        elif "/maturador/api/account-blocked" in info.requestUrl().path():
            url_path = info.requestUrl().path()
            json_string = url_path[url_path.find("{"):url_path.find("}") + 1]
            data = json.loads(json_string)
            SIGNALS.account_blocked.emit(data)
            info.block(True)


class MainWindow(QMainWindow):
    def __init__(self):
        self.controller = None
        self._is_open = False
        super().__init__()
        self.webs_engine = []
        self.setWindowTitle("Maturador de chips - Contas conectadas")
        self.setWindowIcon(QIcon("pages/assets/medias/icon.ico"))
        self.setFixedSize(1060, 650)
        with open(file="user-agent", mode="r", encoding="utf8") as f: self.USER_AGENT = f.read()
        self.sessions_waiting_to_be_disconnected = []
        self.webviews:QWebEngineView = []
        self.buttons_layout = QHBoxLayout()
        self.stacked_widget = QStackedWidget()
        self.buttons = {}
        self.selected_button = None
        self.load_webviews()

        # criar o QStackedWidget para alternar entre os webviews

        for webview in self.webviews:
            self.stacked_widget.addWidget(webview)

        self.buttons_widget = QWidget()
        self.buttons_widget.setFixedHeight(50)

        # configura o layout dos botoes de alternar entre instancias

        buttons_scroll_area = QScrollArea()
        buttons_scroll_area.setWidgetResizable(True)
        buttons_scroll_area.setFixedHeight(50)
        buttons_container = QWidget()
        buttons_container.setLayout(self.buttons_layout)
        buttons_scroll_area.setWidget(buttons_container)

        #o layout principal como QVBoxLayout

        main_layout = QVBoxLayout()

        # configurar widget central da janela

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # adicionar o QScrollArea dentro layout principal

        main_layout.addWidget(buttons_scroll_area)

        # adicionar o QStackedWidget ao layout principal

        main_layout.addWidget(self.stacked_widget)
        
        # botões "adicionar" e "remover" layout

        buttons_container = QWidget()
        buttons_container.setLayout(main_layout)
        button_layout = QHBoxLayout()
        add_instance_button = QPushButton("Adicionar")
        add_instance_button.clicked.connect(self.create_session)
        remove_instance_button = QPushButton("Remover")
        remove_instance_button.clicked.connect(self.delete_session)

        # personaliza os dois botões "adicionar" e "remover"

        add_instance_button.setCursor(QCursor(Qt.PointingHandCursor))
        remove_instance_button.setCursor(QCursor(Qt.PointingHandCursor))
        add_instance_button.setStyleSheet(
        '''
            QPushButton {
                background-color: #f56642;
                color: white;
                font-size: 13px;
                width: 23px;
                height: 23px; 
                margin-right: 0x;
                border-radius: 0px;
            }
            QPushButton:hover {
                background-color: #fc4f23;
            }
        '''
        )
        remove_instance_button.setStyleSheet(
        '''
            QPushButton {
                background-color: #ed4a47;
                color: white;
                font-size: 13px;
                width: 23px;
                height: 23px; 
                margin-right: 0x;
                border-radius: 0px;
            }
            QPushButton:hover {
                background-color: #fa2420;
            }
        '''
        )

        button_layout.addWidget(add_instance_button)
        button_layout.addWidget(remove_instance_button)
        buttons_container.layout().addLayout(button_layout)

        # configurar o widget central da janela

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def closeEvent(self, event):
        self._is_open = False
        event.accept()
    
    # criar nova sessão/webview

    def create_session(self):
        
        while True:
            session_name, want_continue = QInputDialog.getText(self, "Maturador de chips" ,"qual o nome você quer definir para essa instância?")

            if not want_continue:
                return

            elif not session_name or session_name.isspace():
                QMessageBox.critical(self, "Maturador de chips","o nome da instância não pode estar vazio")
            
            elif len(session_name) > 11:
                QMessageBox.critical(self, "Maturador de chips","o nome da instância não pode ter mais de 11 dígitos")
            
            elif os.path.exists(os.path.join("sessions", f"@{session_name}")):
                QMessageBox.critical(self, "Maturador de chips", f"já existe uma instância com o nome {session_name}, escolha outro.")
            
            else:
                session_name = "@" + session_name
                break

        webview = QWebEngineView()
        profile = QWebEngineProfile(f"storage{session_name}", webview)
        session_dir = os.getcwd() + f"/sessions/{session_name}"
        profile.setCachePath(session_dir)
        profile.setPersistentStoragePath(session_dir)
        profile.setDownloadPath(session_dir)
        profile.setPersistentCookiesPolicy(QWebEngineProfile.AllowPersistentCookies)
        profile.setHttpUserAgent(self.USER_AGENT)
        profile.setHttpAcceptLanguage("pt-br")
        interceptor = RequestInterceptor(webview)
        profile.setUrlRequestInterceptor(interceptor)
        engine = LogCapturingPage(profile, webview)
        webview.setPage(engine)
        self.webs_engine.append(engine)
        webview.load(QUrl("https://web.whatsapp.com/"))
        self.stacked_widget.addWidget(webview)
        self.webviews.append(webview)
        self.create_button(session_name).click()
        webview.page().loadFinished.connect(lambda ok, sessionname=session_name : self.run_script(sessionname))
    
    # carregar sessões de webviews já existentes

    def load_webviews(self):
        try:
            sessions = [session for session in os.listdir("sessions") if session.startswith("@")]
        except FileNotFoundError: # a pasta de sessões ainda não existe
            return 
        for sessionname in sessions:

            webview = QWebEngineView()
            profile = QWebEngineProfile(f"storage{sessionname}", webview)
            session_dir = os.getcwd() + f"/sessions/{sessionname}"

            # apaga Service Worker porque está causando problema com a sessão

            service_Worker_path = os.path.join(session_dir, "Service Worker")
            if os.path.exists(path=service_Worker_path):
                shutil.rmtree(path=service_Worker_path)
            
            profile.setCachePath(session_dir)
            profile.setPersistentStoragePath(session_dir)
            profile.setDownloadPath(session_dir)
            profile.setPersistentCookiesPolicy(QWebEngineProfile.AllowPersistentCookies)
            profile.setHttpUserAgent(self.USER_AGENT)
            profile.setHttpAcceptLanguage("pt-br")
            interceptor = RequestInterceptor(webview)
            profile.setUrlRequestInterceptor(interceptor)
            engine = LogCapturingPage(profile, webview)
            webview.setPage(engine)
            self.webs_engine.append(engine)
            webview.load(QUrl("https://web.whatsapp.com/"))
            self.create_button(sessionname)
            self.webviews.append(webview)
            webview.page().loadFinished.connect(lambda ok, session_name=sessionname : self.run_script(session_name))
    
    # injeta script login.js

    def run_script(self, session_name:str):
        for idx, key in enumerate(start=0, iterable=self.buttons.keys()):
            if key == session_name:
                script = open(
                    file="scripts/login.js",
                    mode="r",
                    encoding="utf8"
                )
                webview:QWebEngineView = self.webviews[idx]
                webview.page().runJavaScript(script.read().replace('@INSTANCE', str(idx) ).replace("@SESSIONNAME", session_name))
                script.close()
    
    # criar botão para alternar entre o webview 

    def create_button(self, session_name:str) -> QPushButton:
    
        button = QPushButton(session_name.replace('@', ''))
        button.setMinimumWidth(000)
        button.setStyleSheet('''
                QPushButton {
                    background-color: #6ab8b8;
                    color: white;
                    font-size: 13px;
                    width: 50px;
                    height: 20px;
                    margin-right: 5px;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            ''')
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.clicked.connect(lambda _, name=session_name: self.switch_tab(name))
        self.buttons_layout.addWidget(button)
        self.buttons.update(
            {
            session_name:button
            }
        )
        if len(self.buttons) == 1:
            button.click()
        return button
    
    # troca o webview padrão

    def switch_tab(self, session_name):
        for idx, key in enumerate(start=0, iterable=self.buttons.keys()):
            if session_name == key:
                self.selected_button = str(session_name)
                self.stacked_widget.setCurrentIndex(idx)
                self.highlight_current_button(idx)

    # destaca o botão do webview atual

    def highlight_current_button(self, idx):
        for i, button in enumerate(self.buttons):
            button = self.buttons[button]
            if i == idx:
                button.setStyleSheet('''
                    QPushButton {
                        background-color: #4f6b6b;
                        color: white;
                        font-size: 13px;
                        width: 50px;
                        height: 20px;
                        margin-right: 5px;
                        border-radius: 10px;
                    }
                ''')
            else:
                button.setStyleSheet('''
                    QPushButton {
                        background-color: #6ab8b8;
                        color: white;
                        font-size: 13px;
                        width: 50px;
                        height: 20px;
                        margin-right: 5px;
                        border-radius: 10px;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
         ''')
    
    # apagar uma instancia

    def delete_session(self):
        if not self.selected_button:
            return QMessageBox.critical(self, "Maturador de chips","nenhuma instância aberta, impossível apagar.")
        
        confirm = QMessageBox.question(
            self,
            "Maturador de chips",
            f"""você tem certeza que quer apagar a instância "{self.selected_button.replace("@", "")}" ?""",
            QMessageBox.StandardButton.Apply,
            QMessageBox.StandardButton.Abort
        )

        if confirm == QMessageBox.StandardButton.Abort:
            return
        
        for idx, key in enumerate(start=0, iterable=self.buttons.keys()):
            if key == self.selected_button:
                self.buttons_layout.removeWidget(self.buttons[key])
                self.stacked_widget.removeWidget(self.webviews[idx])
                try:
                    self.switch_tab(
                        list(self.buttons.keys())[idx - 1]
                    )            
                except (KeyError, IndexError):
                    self.selected_button = None
                self.webviews.pop(idx)   
                self.webs_engine.pop(idx)
                self.buttons.pop(key)
                self.sessions_waiting_to_be_disconnected.append(
                    os.path.join(
                    "sessions",
                    key
                )
                )
                try:
                    self.controller.connected_numbers.pop(key)
                    SIGNALS.new_phone_number.emit({})
                except KeyError:
                    pass
                break

        if not self.buttons:
            self.selected_button = None