import shutil
from PyQt5 import QtWidgets

from PyQt5.QtWidgets import (
    QMainWindow, QWidget,
     QHBoxLayout, QAction, QStackedWidget, QLabel, QVBoxLayout, QInputDialog, QMessageBox
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon

import os

from controller import Controller

class Webview(QWebEngineView):
    def __init__(self, parent=None , session_name = "GUI", signals = None):
        super().__init__(parent)
        self.session_name = session_name
        self.signals = signals
        self.loadFinished.connect(lambda _: self.inject_js_script() )

    def reload(self):
        self.page().setWebChannel(self.controller_channel)
        return super().reload()

    def inject_js_script(self):
        """Injetar codigo javascript na pagina do whatsapp"""
        if self.signals:
            self.signals.account_blocked.emit({"sessionName": self.session_name})
            with open("injected.js", "r", encoding="utf-8") as f:
                self.page().runJavaScript( f.read().replace("@instanceName", self.session_name ) )

    
class LogCapturingPage(QWebEnginePage):
    def consoleMessage(self, level, message, lineNumber, sourceID):
        print(message)
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        print(message)

from urllib.parse import parse_qs, urlparse

class RequestInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, parent=None, signals=None):
        super().__init__(parent)
        self.signals = signals

    def interceptRequest(self, info):
        url = info.requestUrl().toString()

        if "/maturador/api/account-added" in url:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)

            data = {
                "sessionName": params.get("sessionName", [""])[0],
                "phone": params.get("phone", [""])[0],
                "photo": params.get("photo", [""])[0],
            }

            self.signals.new_phone_number.emit(data)
            info.block(True)

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
        self.options_menu = menubar.addMenu("Opções")
        # Ação solta na barra
        self.action_start_maturation = QtWidgets.QAction("Iniciar", self)
        self.action_start_maturation.triggered.connect(lambda: self.controller.signals.start_maturation.emit())
        menubar.addAction(self.action_start_maturation)
        # Ação de configurações
        config_action = QAction("Configurações", self)
        config_action.triggered.connect(self.open_preferences)
        self.options_menu.addAction(config_action)

        # Ação de adicionar conta
        add_account_action = QAction("Adicionar conta", self)
        add_account_action.triggered.connect(self.add_account)
        self.options_menu.addAction(add_account_action)

        # Ação de remover conta
        self.remove_account_action = QAction("Remover conta", self)
        self.remove_account_action.setEnabled(True)
        self.remove_account_action.triggered.connect(self.delete_session)
        
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
        engine.loadFinished.connect(lambda x: self.load_sessions() )
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

        # Página 2 (index 2): atualizações

        self.status_view = Webview(self)
        cache_dir = os.getcwd() + "/cache"
        profile = QWebEngineProfile("cache_status_view", self.status_view)
        profile.setCachePath(cache_dir)
        profile.setPersistentStoragePath(cache_dir)
        profile.setDownloadPath(cache_dir)
        profile.setPersistentCookiesPolicy(QWebEngineProfile.AllowPersistentCookies)
        profile.setHttpAcceptLanguage("pt-br")

        engine = LogCapturingPage(profile, self.status_view)
        channel = QWebChannel(engine)
        channel.registerObject("controller",self.controller)
        self.status_view.controller_channel = channel
        engine.setWebChannel(channel)
        status_path = os.path.abspath("status.html")
        engine.setUrl(QUrl.fromLocalFile(status_path))
        self.status_view.setPage(engine)

        # Adiciona as páginas no stacked widget

        self.stacked.addWidget(self.no_account_widget)  # índice 0
        self.stacked.addWidget(self.settings_view)      # índice 1
        self.stacked.addWidget(self.status_view)      # índice 2

        # Adiciona sidebar e stacked widget ao layout

        layout.addWidget(self.sidebar, 25)
        layout.addWidget(self.stacked, 75)

        # Define o layout central da janela

        self.setCentralWidget(central_widget)

    def open_preferences(self):
        """Muda o webview maior para configurações"""
        self.options_menu.removeAction(self.remove_account_action)
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

        webview = Webview(self, name, self.controller.signals)
        interceptor = RequestInterceptor(webview, self.controller.signals)
        profile = QWebEngineProfile(f"{name}", webview)
        profile.setUrlRequestInterceptor(interceptor)
        profile.setCachePath(session_path)
        profile.setPersistentStoragePath(session_path)
        profile.setDownloadPath(session_path)
        profile.setHttpUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
        profile.setPersistentCookiesPolicy(QWebEngineProfile.AllowPersistentCookies)
        profile.setHttpAcceptLanguage("pt-br")
        engine = LogCapturingPage(profile, webview)
        webview.setPage(engine)
        webview.load(QUrl("https://web.whatsapp.com"))
        self.stacked.addWidget(webview)
        self.webviews.update({name: {"webview":webview, "page": engine , "connected": False} })
        self.create_session_button(name)
        self.stacked.setCurrentWidget(webview)


    def create_session_button(self, name):
        script = f"""
        function create_button(){{
            const container = document.createElement("div");
            container.className = "contact-item";
            container.setAttribute("webview", "{name}");
            container.onclick = () => {{ window.change_current_webview(event) }};

            const icon = document.createElement("img");
            icon.className = "contact-icon";
            icon.src = "assets/medias/contact.jpg";
            icon.alt = "{name}";

            const number = document.createElement("div");
            number.className = "contact-number";
            number.textContent = "{name} (Desconectado)";

            container.appendChild(icon);
            container.appendChild(number);

            container.addEventListener("click", () => {{
                document.querySelectorAll(".contact-item").forEach(el => {{
                    el.classList.remove("active");
                }})

                container.classList.add("active");
            }});

            document.querySelector(".contact-list").appendChild(container);
            document.querySelectorAll(".contact-item").forEach(el => el.classList.remove("active"));
            container.classList.add("active"); 
            container.click();
        }}
        create_button();
        """

        self.sidebar.page().runJavaScript(script)
    
    def load_sessions(self):
        """Carregar sessões salvas no sistema"""

        sessions_dir = os.path.join( os.getcwd() , "sessions")
        if not os.path.exists(sessions_dir):
            os.mkdir(sessions_dir)

        for session_path in os.listdir(sessions_dir):

            if not session_path.find(".session"):
                continue

            if session_path.endswith(".session"):
                name = session_path[:-8] 
            else:
                name = session_path

            session_path = os.path.join(sessions_dir, session_path)
            service_Worker_path = os.path.join(session_path, "Service Worker")
            if os.path.exists(path=service_Worker_path):
                shutil.rmtree(path=service_Worker_path)

            webview = Webview(self, name, self.controller.signals)
            interceptor = RequestInterceptor(webview, self.controller.signals)
            profile = QWebEngineProfile(f"{name}", webview)
            profile.setUrlRequestInterceptor(interceptor)
            profile.setCachePath(session_path)
            profile.setPersistentStoragePath(session_path)
            profile.setDownloadPath(session_path)
            profile.setHttpUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
            profile.setPersistentCookiesPolicy(QWebEngineProfile.AllowPersistentCookies)
            profile.setHttpAcceptLanguage("pt-br")
            engine = LogCapturingPage(profile, webview)
            webview.setPage(engine)
            webview.load(QUrl("https://web.whatsapp.com"))
            self.stacked.addWidget(webview)
            self.webviews.update({name: {"webview":webview, "page": engine , "connected": False, "phone": None} })
            self.create_session_button(name)
            self.stacked.setCurrentWidget(webview)


    def delete_session(self):
        """Remove a sessão atual, exclui o botão da sidebar e define o próximo webview ativo."""

        webview: Webview = self.stacked.currentWidget()
        session_path = webview.page().profile().cachePath()

        name_to_delete = None
        for name, obj in self.webviews.items():
            if obj["webview"] == webview:
                name_to_delete = name
                break

        if not name_to_delete:
            return
        
        if name_to_delete in self.webviews:
            del self.webviews[name_to_delete]

        current_index = self.stacked.currentIndex()
        total_sessions = len(self.webviews)

        if total_sessions <= 1:
            self.options_menu.removeAction(self.remove_account_action)
            self.stacked.setCurrentIndex(0)
        else:
            previous_index = current_index - 1
            if previous_index < 3:
                previous_index = 3
            self.stacked.setCurrentIndex(previous_index)

        self.controller.setSessionTobeDelete(session_path)

        script = f"""
            {{
                const el = document.querySelector('[webview="{name_to_delete}"]');
                if (el) {{
                    el.remove();
                }}

                const first = document.querySelector(".contact-item");
                if (first) {{
                    first.classList.add("active");
                }}
            }}
        """

        self.sidebar.page().runJavaScript(script)

        self.stacked.removeWidget(webview)
        webview.page().runJavaScript("window.WTools.logout()")


    def closeEvent(self, event):
        """Desligar todos web engine e fechar o programa"""
        self.sidebar.page().deleteLater()
        self.settings_view.page().deleteLater()
        for key, value in self.webviews.items():
            engine:QWebEnginePage = value["page"]
            engine.deleteLater()