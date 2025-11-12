import os
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QMenuBar, QAction
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl


class Home(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JonasCaetano • WebView Dashboard")
        self.setGeometry(100, 100, 1200, 700)

        # === Cria o menu ===
        menubar = self.menuBar()
        opcoes_menu = menubar.addMenu("Opções")

        # Ação de configurações
        config_action = QAction("Configurações", self)
        config_action.triggered.connect(self.abrir_configuracoes)
        opcoes_menu.addAction(config_action)

        # === Layout central ===
        central_widget = QWidget()
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # === WebView menor (25%) ===
        self.sidebar = QWebEngineView()
        sidebar_path = os.path.abspath("whatsapp_list.html")
        self.sidebar.setUrl(QUrl.fromLocalFile(sidebar_path))

        # === WebView maior (75%) ===
        self.main_view = QWebEngineView()
        self.main_view.setUrl(QUrl("https://web.whatsapp.com/"))

        # Adiciona as views ao layout
        layout.addWidget(self.sidebar, 25)
        layout.addWidget(self.main_view, 75)

        # Define o layout central da janela
        self.setCentralWidget(central_widget)

    def abrir_configuracoes(self):
        """Abre o settings.html no WebView maior"""
        settings_path = os.path.abspath("settings.html")
        if os.path.exists(settings_path):
            self.main_view.setUrl(QUrl.fromLocalFile(settings_path))
        else:
            self.main_view.setHtml(
                "<h3 style='color:white;text-align:center;margin-top:40px;'>Arquivo settings.html não encontrado</h3>"
            )
