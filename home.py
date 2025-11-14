from PyQt5 import QtWidgets

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QAction, QStackedWidget, QLabel, QVBoxLayout, QInputDialog, QMessageBox
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon

import os

from controller import Controller

class Webview(QWebEngineView):
    def __init__(self, parent: QtWidgets.QWidget | None = ...) -> None:
        self.controller_channel:QWebChannel = None
        super().__init__(parent)
    
    def reload(self) -> None:
        self.page().setWebChannel(self.controller_channel)
        return super().reload()
    
class LogCapturingPage(QWebEnginePage):
    def consoleMessage(self, level, message, lineNumber, sourceID):
        print(message)
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        print(message)
    
class Home(QMainWindow):
    def __init__(self, controller:Controller):
        super().__init__()
        self.setWindowTitle("Maturador de chips 2025.11.12")
        self.setWindowIcon( QIcon("assets/medias/icon.ico") )
        self.setGeometry(100, 100, 1200, 700)
        self.controller = controller
        self.webviews = {}
        # Cria o menu
        menubar = self.menuBar()
        options_menu = menubar.addMenu("Opções")

        # Ação de configurações
        config_action = QAction("Configurações", self)
        config_action.triggered.connect(self.open_preferences)
        options_menu.addAction(config_action)

        # Ação de adicionar conta
        add_account_action = QAction("Adicionar conta", self)
        add_account_action.triggered.connect(self.add_account)
        options_menu.addAction(add_account_action)

        # Layout central
        central_widget = QWidget()
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        #  WebView menor (sidebar 25%)

        self.sidebar = Webview(self)
        profile = QWebEngineProfile("cache_list_view", self.sidebar)
        engine = LogCapturingPage(profile, self.sidebar)
        channel = QWebChannel(engine)
        channel.registerObject("controller",self.controller)
        self.sidebar.controller_channel = channel
        engine.setWebChannel(channel)
        sidebar_path = os.path.abspath("whatsapp_list.html")
        engine.setUrl(QUrl.fromLocalFile(sidebar_path))
        self.sidebar.setPage(engine)

        # QStackedWidget para o webview maior (75%)

        self.stacked = QStackedWidget()

        # Página 0 (index 0): Nenhuma conta conectada (widget simples com QLabel)

        self.no_account_widget = QWidget()
        self.no_account_layout = QVBoxLayout(self.no_account_widget)
        self.no_account_layout.setAlignment(Qt.AlignCenter)
        label = QLabel("Nenhuma conta conectada")
        label.setStyleSheet("font-size: 24px; color: #555;")
        self.no_account_layout.addWidget(label)

        # Página 1 (index 1): Configurações

        self.settings_view = Webview(self)
        cache_dir = os.getcwd() + "/cache"
        profile = QWebEngineProfile("cache_configs_view", self.settings_view)
        profile.setCachePath(cache_dir)
        profile.setPersistentStoragePath(cache_dir)
        profile.setDownloadPath(cache_dir)
        profile.setPersistentCookiesPolicy(QWebEngineProfile.AllowPersistentCookies)
        profile.setHttpAcceptLanguage("pt-br")

        engine = LogCapturingPage(profile, self.settings_view)
        channel = QWebChannel(engine)
        channel.registerObject("controller",self.controller)
        self.settings_view.controller_channel = channel
        engine.setWebChannel(channel)
        settings_path = os.path.abspath("settings.html")
        engine.setUrl(QUrl.fromLocalFile(settings_path))
        self.settings_view.setPage(engine)

        # Adiciona as páginas no stacked widget

        self.stacked.addWidget(self.no_account_widget)  # índice 0
        self.stacked.addWidget(self.settings_view)      # índice 1

        # Adiciona sidebar e stacked widget ao layout

        layout.addWidget(self.sidebar, 25)
        layout.addWidget(self.stacked, 75)

        # Define o layout central da janela

        self.setCentralWidget(central_widget)

    def open_preferences(self):
        """Muda o webview maior para configurações"""
        self.settings_view.reload()
        self.stacked.setCurrentIndex(1)


    def add_account(self):
        """Adicionar nova conta/webview"""
        
        while True:
            name , _continue = QInputDialog.getText(self, "Maturador de chips", "Escolha um nome para essa sessão: ")
            session_path = os.getcwd() + f"/sessions/{name}.session"

            if not _continue:
                return
            
            if not name or name.isspace():
                QMessageBox.about(self, "Maturador de chips", "O nome da sessão não pode estar vazio!" )
                continue

            if os.path.exists(session_path):
                QMessageBox.about(self, "Maturador de chips", "Já existe um sessão com esse nome, por favor escolha outro." )
                continue

            break

        webview = Webview(self)
        profile = QWebEngineProfile(f"{name}", webview)
        profile.setCachePath(session_path)
        profile.setPersistentStoragePath(session_path)
        profile.setDownloadPath(session_path)
        profile.setPersistentCookiesPolicy(QWebEngineProfile.AllowPersistentCookies)
        profile.setHttpAcceptLanguage("pt-br")
        engine = LogCapturingPage(profile, webview)
        webview.setPage(engine)
        webview.load(QUrl("https://web.whatsapp.com/"))
        self.stacked.addWidget(webview)
        self.webviews.update({name: {"webview":webview, "page": engine } })
        self.create_session_button(name)
        self.stacked.setCurrentWidget(webview)

    
    def create_session_button(self, name):
        script = f"""
        function create_button(){{
        const container = document.createElement("div");
        container.className = "contact-item";
        container.setAttribute("webview", "{name}")
        container.onclick = () => {{ window.change_current_webview(event) }};
        const icon = document.createElement("div");
        icon.className = "contact-icon";
        icon.textContent = "{name[0].upper()}";

        const number = document.createElement("div");
        number.className = "contact-number";
        number.textContent = "{name} (Desconectado)";

        container.appendChild(icon);
        container.appendChild(number);

        container.addEventListener("click", () => {{
            document.querySelectorAll(".contact-item").forEach(el => {{
                el.classList.remove("active");
            }});

            container.classList.add("active");
        }});

        document.querySelector(".contact-list").appendChild(container);
        document.querySelectorAll(".contact-item").forEach(el => el.classList.remove("active"));
        container.classList.add("active");}}
        create_button();

        """

        self.sidebar.page().runJavaScript(script)