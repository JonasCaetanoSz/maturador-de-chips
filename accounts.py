from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QStackedWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtCore import QUrl, Qt, QTimer
from PyQt5.QtGui import QIcon, QCursor

import requests
import shutil
import json
import os

# intercptar as request para conseguir encontrar as que é feita para o programa
# isso é nescesario pois o whatssap web bloqueia requisições feitas para dominios
# diferente do deles atráves do content security policy (CSP).

class RequestInterceptor(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info):
        
        # novo numero adicionado

        if "/maturador/api/account-added" in info.requestUrl().path():
            url_path = info.requestUrl().path()
            json_string = url_path[url_path.find("{"):url_path.find("}") + 1]
            data = json.loads(json_string)
            requests.post(
                url="http://127.0.0.1:5025/api/account-added",
                json=data
            )
            info.block(True)
        
        # conta bloqueada

        elif "/maturador/api/account-blocked" in info.requestUrl().path():
            url_path = info.requestUrl().path()
            json_string = url_path[url_path.find("{"):url_path.find("}") + 1]
            data = json.loads(json_string)
            requests.post(
                url="http://127.0.0.1:5025/api/account-blocked",
                json=data
            )
            info.block(True)


class MainWindow(QMainWindow):
    def __init__(self, api_instance):
        super().__init__()
        self.all_webview_load_finish = []
        self.API_INSTANCE = api_instance
        self.ACCOUNTS_AMOUNT = 1
        self.webs_engine = []
        self.setWindowTitle("Maturador de chips - Contas conectadas")
        self.setWindowIcon(QIcon("pages/assets/medias/icon.ico"))
        self.setFixedSize(950, 700)
        with open(file="user-agent", mode="r", encoding="utf8") as f: self.USER_AGENT = f.read()
        self.webviews = []
        self.create_webviews()

        # criar o QStackedWidget para alternar entre os webviews

        self.stacked_widget = QStackedWidget()
        for webview in self.webviews:
            self.stacked_widget.addWidget(webview)

        self.buttons_widget = QWidget()
        self.buttons_widget.setFixedHeight(50)

        # configura o layout dos botoes

        buttons_layout = QHBoxLayout()
        self.buttons_widget.setLayout(buttons_layout)
        self.create_buttons(buttons_layout)

        # configurar o layout principal

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.buttons_widget)
        main_layout.addWidget(self.stacked_widget)

        # configurar o wiget central da janela

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def closeEvent(self, event):
        #[webview.close() for webview in self.webviews]
        #{engine.deleteLater() for engine in self.webs_engine if self.webs_engine.remove(engine) != int}
        self.API_INSTANCE.set_account_page_state(False)
        event.accept()
    
    # cria e carrega os webview e o site do whatssap,além de apagar a pasta worker service

    def create_webviews(self):

        for i in range(0, 10):
            webview = QWebEngineView()
            profile = QWebEngineProfile(f"storage{i}", webview)
            session_dir = os.getcwd() + f"/sessions/M0{i}"
            # apaga Service Worker porque está causando problema com a sessão
            if os.path.exists(path=session_dir + "/Service Worker"): shutil.rmtree(path=session_dir + "/Service Worker")
            profile.setCachePath(session_dir)
            profile.setPersistentStoragePath(session_dir)
            profile.setDownloadPath(session_dir)
            profile.setPersistentCookiesPolicy(QWebEngineProfile.AllowPersistentCookies)
            profile.setHttpUserAgent(self.USER_AGENT)
            profile.setHttpAcceptLanguage("pt-br")
            interceptor = RequestInterceptor(webview)
            profile.setUrlRequestInterceptor(interceptor)
            engine = QWebEnginePage(profile, webview)
            webview.setPage(engine)
            self.webs_engine.append(engine)
            webview.load(QUrl("https://web.whatsapp.com/"))
            #webview.load(QUrl("https://example.com/"))
            self.webviews.append(webview)
            webview.page().loadFinished.connect(lambda ok: self.run_scripts(ok))
    
    # injeta script  login.js

    def run_scripts(self, ok):

        if ok:
            self.all_webview_load_finish.append(ok)
            if len(self.all_webview_load_finish) == self.ACCOUNTS_AMOUNT:
                self.all_webview_load_finish.clear()
                for i in self.webviews:
                    with open(file="scripts/login.js", mode="r") as file:
                        script = file.read()
                        i.page().runJavaScript(script.replace('@INSTANCE', str(self.webviews.index(i)) ))
    
    # criar os botões de cada webview

    def create_buttons(self, layout):
        
        self.buttons = []
        for i in range(len(self.webviews)):
            button = QPushButton(f"M{(i + 1):02d}")
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
            button.clicked.connect(lambda _, idx=i: self.switch_tab(idx))
            layout.addWidget(button)
            self.buttons.append(button)
            if i == 0:
                button.click()
    
    # troca o webview padrão

    def switch_tab(self, idx):
        if idx < len(self.webviews):
            self.stacked_widget.setCurrentIndex(idx)
            self.highlight_current_button(idx)

    # destaca o botão do webview atual

    def highlight_current_button(self, idx):
        for i, button in enumerate(self.buttons):
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
