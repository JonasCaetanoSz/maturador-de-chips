from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile , QWebEnginePage
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QUrl
import os

class MainWindow(QMainWindow):
    def __init__(self, accounts_page, signals):
        super().__init__()
        self.accounts_page = accounts_page
        self.signals = signals
        self.setWindowTitle("Maturador de chips - Dashboard")
        self.main_engine:QWebEnginePage
        self.setFixedSize(769, 660)
        self.webview = QWebEngineView(self)
        cache_dir = os.getcwd() + "/sessions/cache"
        profile = QWebEngineProfile("gui_cache", self.webview)
        profile.setCachePath(cache_dir)
        profile.setPersistentStoragePath(cache_dir)
        profile.setDownloadPath(cache_dir)
        profile.setPersistentCookiesPolicy(QWebEngineProfile.AllowPersistentCookies)
        profile.setHttpAcceptLanguage("pt-br")
        self.webview.page().action(QWebEnginePage.Back).setVisible(False)
        self.webview.page().action(QWebEnginePage.Reload).setVisible(False)
        self.webview.page().action(QWebEnginePage.WebAction.SavePage).setVisible(False)
        self.webview.page().action(QWebEnginePage.WebAction.CopyImageToClipboard).setVisible(False)
        self.webview.page().action(QWebEnginePage.WebAction.CopyImageUrlToClipboard).setVisible(False)
        engine = QWebEnginePage(profile, self.webview)
        self.webview.setPage(engine)
        self.webview.load(QUrl("http://127.0.0.1:5025/dashboard"))
        self.webview.page().setZoomFactor(0.92)
        self.setWindowIcon(QIcon("pages/assets/medias/icon.ico"))
        self.setCentralWidget(self.webview)
        self.main_engine = engine
    
    def closeEvent(self, event):
        self.signals.stop_maturation.emit()
        {engine.deleteLater() for engine in self.accounts_page.webs_engine}
        self.accounts_page.close()
        self.main_engine.deleteLater()
        event.accept()