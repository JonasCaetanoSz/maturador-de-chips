from PyQt5 import QtWidgets

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QAction, QStackedWidget, QLabel, QVBoxLayout
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import Qt, QUrl
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
        pass
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        pass
    

class Home(QMainWindow):
    def __init__(self, controller:Controller):
        super().__init__()
        self.setWindowTitle("Maturador de chips 2025.11.12")
        self.setGeometry(100, 100, 1200, 700)
        self.controller = controller

        # === Cria o menu ===
        menubar = self.menuBar()
        options_menu = menubar.addMenu("Opções")

        # Ação de configurações
        config_action = QAction("Configurações", self)
        config_action.triggered.connect(self.abrir_configuracoes)
        options_menu.addAction(config_action)

        # Ação de adicionar conta
        add_account_action = QAction("Adicionar conta", self)
        add_account_action.triggered.connect(self.adicionar_conta)
        options_menu.addAction(add_account_action)

        # === Layout central ===
        central_widget = QWidget()
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # === WebView menor (sidebar 25%) ===
        self.sidebar = Webview(self)
        sidebar_path = os.path.abspath("whatsapp_list.html")
        self.sidebar.setUrl(QUrl.fromLocalFile(sidebar_path))

        # === QStackedWidget para o webview maior (75%) ===
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
        profile = QWebEngineProfile("cache", self.settings_view)
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

    def abrir_configuracoes(self):
        """Muda o webview maior para configurações"""
        self.settings_view.reload()
        self.stacked.setCurrentIndex(1)


    def adicionar_conta(self):
        """Muda o webview maior para adicionar conta"""
        pass
