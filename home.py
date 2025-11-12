from PyQt5.QtWidgets import QWidget, QHBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import os

class Home(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JonasCaetano • WebView Dashboard")
        self.setGeometry(100, 100, 1200, 700)

        # Layout horizontal principal
        layout = QHBoxLayout(self)

        # Remove margens e espaçamento entre os widgets
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # === WebView menor (25%) ===
        self.sidebar = QWebEngineView()
        sidebar_path = os.path.abspath("whatsapp_list.html")
        self.sidebar.setUrl(QUrl.fromLocalFile(sidebar_path))

        # === WebView maior (75%) ===
        self.main_view = QWebEngineView()
        self.main_view.setUrl(QUrl("https://web.whatsapp.com/"))

        # Adiciona ao layout com proporção 25/75
        layout.addWidget(self.sidebar, 25)
        layout.addWidget(self.main_view, 75)

        self.setLayout(layout)
