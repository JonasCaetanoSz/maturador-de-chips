from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QLabel, QVBoxLayout, QInputDialog, QMessageBox
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineSettings, QWebEngineUrlRequestInterceptor
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import Qt, QUrl, QSettings
from PyQt6.QtGui import QAction, QIcon
from urllib.parse import parse_qs, urlparse
from controller import Controller

import shutil
import json
import os

class Webview(QWebEngineView):
    def __init__(self, parent=None, session_name="GUI", signals=None, inject_js=False):
        super().__init__(parent)
        self.session_name = session_name
        self.signals = signals
        self.inject_js_enabled = bool(inject_js)

        if self.inject_js_enabled:
            self.loadFinished.connect(lambda ok: self.disable_menu_options(whatsapp=True))
            self.loadFinished.connect(lambda ok: self.inject_js_script(ok))
        else:
            self.loadFinished.connect(lambda ok: self.disable_menu_options(whatsapp=False))
        
        self.loadFinished.connect(lambda ok: self.apply_preferences_sound())

    def reload(self):
        try:
            page = self.page()
            if page is not None and hasattr(self, "controller_channel"):
                page.setWebChannel(self.controller_channel)
        except Exception:
            pass
        return super().reload()

    def inject_js_script(self, ok):
        """Injetar código javascript na página do whatsapp — somente se estiver em web.whatsapp.com"""
        if self.signals:
            self.signals.account_blocked.emit({"sessionName": self.session_name})
        if not ok:
            return

        try:
            page = self.page()
            if page is None:
                return

            url = page.url().toString()
            if "web.whatsapp.com" not in url:
                return

            injected_path = os.path.abspath("injected.js")
            if not os.path.exists(injected_path):
                return

            with open(injected_path, "r", encoding="utf-8") as f:
                script = f.read().replace("@instanceName", self.session_name)

            try:
                page.runJavaScript(script)
            except RuntimeError:
                pass
        except Exception as e:
            print(f"[Webview:{self.session_name}] erro ao injetar JS: {e}")

    def apply_preferences_sound(self):
        """Aplica configurações de som e notificação webview"""
        try:
            if os.path.exists("preferences.json"):
                with open("preferences.json", "r", encoding="utf8") as f:
                    preferences = json.load(f)
                    play_sound = preferences.get("PlaySound", False)
            else:
                play_sound = False

            if self.page():
                self.page().setFeaturePermission(
                    self.page().url(),
                    QWebEnginePage.Feature.Notifications,
                    QWebEnginePage.PermissionPolicy.PermissionGrantedByUser
                )
                self.page().setAudioMuted(not play_sound)
        except Exception:
            pass

    def disable_menu_options(self, whatsapp):
        """Desativar opções do menu"""
        try:
            if not whatsapp and self.page():
                self.page().action(QWebEnginePage.WebAction.Reload).setVisible(False)
            
            if self.settings():
                self.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
            
            if self.page():
                for action in [
                    QWebEnginePage.WebAction.Back, QWebEnginePage.WebAction.SavePage,
                    QWebEnginePage.WebAction.CopyImageToClipboard, QWebEnginePage.WebAction.CopyImageUrlToClipboard,
                    QWebEnginePage.WebAction.Forward, QWebEnginePage.WebAction.ViewSource,
                    QWebEnginePage.WebAction.CopyLinkToClipboard, QWebEnginePage.WebAction.OpenLinkInNewTab,
                    QWebEnginePage.WebAction.OpenLinkInThisWindow, QWebEnginePage.WebAction.DownloadLinkToDisk,
                    QWebEnginePage.WebAction.OpenLinkInNewBackgroundTab, QWebEnginePage.WebAction.OpenLinkInNewWindow
                ]:
                    self.page().action(action).setVisible(False)
        except Exception:
            pass

class LogCapturingPage(QWebEnginePage):
    def consoleMessage(self, level, message, lineNumber, sourceID):
        pass

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        pass

class RequestInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, parent=None, signals=None):
        super().__init__(parent)
        self.signals = signals

    def interceptRequest(self, info):
        try:
            url = info.requestUrl().toString()
            if "/maturador/api/account-added" in url:
                parsed = urlparse(url)
                params = parse_qs(parsed.query)

                data = {
                    "sessionName": params.get("sessionName", [""])[0],
                    "phone": params.get("phone", [""])[0],
                    "photo": params.get("photo", [""])[0],
                }
                if self.signals:
                    self.signals.new_phone_number.emit(data)

                info.block(True)
        except Exception as e:
            print(f"[RequestInterceptor] erro ao interceptar: {e}")

class Home(QMainWindow):
    def __init__(self, controller: Controller):
        super().__init__()
        self.setWindowTitle(f"Maturador PRO - 20.07.2026")
        self.setWindowIcon(QIcon("assets/medias/icon.ico"))
        self.setGeometry(100, 100, 1200, 700)
        self.controller = controller
        self.webviews = {}

        settings = QSettings("MaturadorChips", "MainWindow")
        geometry = settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

        self.menubar = self.menuBar()
        self.options_menu = self.menubar.addMenu("Opções")
        
        self.action_start_maturation = QAction("Iniciar Privado", self)
        self.action_start_maturation.triggered.connect(lambda: self.controller.signals.start_maturation.emit())
        self.menubar.addAction(self.action_start_maturation)

        self.action_start_group = QAction("Iniciar Grupos", self)
        self.action_start_group.triggered.connect(lambda: self.controller.signals.start_group_maturation.emit())
        self.menubar.addAction(self.action_start_group)
        
        self.config_action = QAction("Configurações", self)
        self.config_action.triggered.connect(self.open_preferences)
        self.options_menu.addAction(self.config_action)

        self.add_account_action = QAction("Adicionar conta", self)
        self.add_account_action.triggered.connect(self.add_account)
        self.options_menu.addAction(self.add_account_action)

        self.remove_account_action = QAction("Remover conta", self)
        self.remove_account_action.setEnabled(True)
        self.remove_account_action.triggered.connect(self.delete_session)
        
        central_widget = QWidget()
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.sidebar = Webview(self, session_name="sidebar", signals=None, inject_js=False)
        profile = QWebEngineProfile("cache_list_view", self.sidebar)
        engine = LogCapturingPage(profile, self.sidebar)
        channel = QWebChannel(engine)
        channel.registerObject("controller", self.controller)
        self.sidebar.controller_channel = channel
        engine.setWebChannel(channel)
        sidebar_path = os.path.abspath("whatsapp_list.html")
        engine.loadFinished.connect(lambda ok: self.load_sessions() if ok else None)
        engine.setUrl(QUrl.fromLocalFile(sidebar_path))
        self.sidebar.setPage(engine)

        self.stacked = QStackedWidget()

        self.no_account_widget = QWidget()
        self.no_account_layout = QVBoxLayout(self.no_account_widget)
        self.no_account_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label = QLabel("Nenhuma conta conectada")
        label.setStyleSheet("font-size: 24px; color: #555;")
        self.no_account_layout.addWidget(label)

        cache_dir = os.path.join(os.getcwd(), "cache")

        self.settings_view = Webview(self, session_name="settings", inject_js=False)
        profile = QWebEngineProfile("cache_configs_view", self.settings_view)
        profile.setCachePath(cache_dir)
        profile.setPersistentStoragePath(cache_dir)
        profile.setDownloadPath(cache_dir)
        profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies)
        profile.setHttpAcceptLanguage("pt-br")
        engine = LogCapturingPage(profile, self.settings_view)
        channel = QWebChannel(engine)
        channel.registerObject("controller", self.controller)
        self.settings_view.controller_channel = channel
        engine.setWebChannel(channel)
        settings_path = os.path.abspath("settings.html")
        engine.setUrl(QUrl.fromLocalFile(settings_path))
        self.settings_view.setPage(engine)

        self.status_view = Webview(self, session_name="status", inject_js=False)
        profile = QWebEngineProfile("cache_status_view", self.status_view)
        profile.setCachePath(cache_dir)
        profile.setPersistentStoragePath(cache_dir)
        profile.setDownloadPath(cache_dir)
        profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies)
        profile.setHttpAcceptLanguage("pt-br")
        engine = LogCapturingPage(profile, self.status_view)
        channel = QWebChannel(engine)
        channel.registerObject("controller", self.controller)
        self.status_view.controller_channel = channel
        engine.setWebChannel(channel)
        status_path = os.path.abspath("status.html")
        engine.setUrl(QUrl.fromLocalFile(status_path))
        self.status_view.setPage(engine)

        self.stacked.addWidget(self.no_account_widget)   # índice 0
        self.stacked.addWidget(self.settings_view)       # índice 1
        self.stacked.addWidget(self.status_view)         # índice 2

        layout.addWidget(self.sidebar, 25)
        layout.addWidget(self.stacked, 75)
        self.setCentralWidget(central_widget)

    def open_preferences(self):
        try:
            self.options_menu.removeAction(self.remove_account_action)
        except Exception:
            pass

        try:
            self.settings_view.reload()
        except Exception:
            pass

        self.stacked.setCurrentIndex(1)

    def close_preferences(self):
        js = """
        (function(){
            const activeButton = document.querySelector('.contact-item.active');
            return activeButton ? activeButton.getAttribute('webview') : null;
        })();
        """
        def callback(webview_name):
            if webview_name and webview_name in self.webviews:
                self.stacked.setCurrentWidget(self.webviews[webview_name]["webview"])
                self.options_menu.addAction(self.remove_account_action)
            else:
                self.stacked.setCurrentIndex(0)

        self.sidebar.page().runJavaScript(js, callback)

    def close_status(self):
        js = """
        (function(){
            const activeButton = document.querySelector('.contact-item.active');
            return activeButton ? activeButton.getAttribute('webview') : null;
        })();
        """
        def callback(webview_name):
            if webview_name and webview_name in self.webviews:
                self.stacked.setCurrentWidget(self.webviews[webview_name]["webview"])
            else:
                self.stacked.setCurrentIndex(0)

        self.sidebar.page().runJavaScript(js, callback)

    def add_account(self):
        while True:
            name, _continue = QInputDialog.getText(self, "Maturador de chips", "Escolha um nome para essa sessão: ")
            if not _continue:
                return

            if not name or name.isspace():
                QMessageBox.about(self, "Maturador de chips", "O nome da sessão não pode estar vazio!")
                continue

            session_path = os.path.join(os.getcwd(), f"sessions/{name}.session")
            if os.path.exists(session_path):
                QMessageBox.about(self, "Maturador de chips", "Já existe um sessão com esse nome, por favor escolha outro.")
                continue

            break

        webview = Webview(self, session_name=name, signals=self.controller.signals, inject_js=True)
        interceptor = RequestInterceptor(webview, self.controller.signals)
        profile = QWebEngineProfile(f"{name}", webview)
        profile.setUrlRequestInterceptor(interceptor)
        profile.setCachePath(session_path)
        profile.setPersistentStoragePath(session_path)
        profile.setDownloadPath(session_path)
        profile.setHttpUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
        profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies)
        profile.setHttpAcceptLanguage("pt-br")
        engine = LogCapturingPage(profile, webview)
        webview.setPage(engine)
        webview.load(QUrl("https://web.whatsapp.com"))

        self.stacked.addWidget(webview)
        self.webviews.update({name: {"webview": webview, "page": engine, "connected": False}})
        self.create_session_button(name)
        self.stacked.setCurrentWidget(webview)

        if self.remove_account_action not in self.options_menu.actions():
            self.options_menu.addAction(self.remove_account_action)

    def create_session_button(self, name):
        script = f"""
        function create_button(){{
            const container = document.createElement("div");
            container.className = "contact-item";
            container.setAttribute("webview", "{name}");

            const icon = document.createElement("img");
            icon.className = "contact-icon";
            icon.src = "assets/medias/contact.jpg";
            icon.alt = "{name}";

            const number = document.createElement("div");
            number.className = "contact-number";
            number.textContent = "{name} (Desconectado)";

            container.appendChild(icon);
            container.appendChild(number);

            container.onclick = (event) => {{
                window.change_current_webview(event);
            }};

            document.querySelector(".contact-list").appendChild(container);
            const fakeEvent = {{ currentTarget: container }};
            window.change_current_webview(fakeEvent);
        }}
        create_button();
        """
        try:
            if self.sidebar and self.sidebar.page():
                self.sidebar.page().runJavaScript(script)
        except Exception as e:
            print(f"[create_session_button] erro: {e}")

    def load_sessions(self):
        sessions_dir = os.path.join(os.getcwd(), "sessions")
        if not os.path.exists(sessions_dir):
            try:
                os.mkdir(sessions_dir)
            except Exception:
                return

        for filename in os.listdir(sessions_dir):
            if ".session" not in filename:
                continue

            name = filename[:-8] if filename.endswith(".session") else filename
            session_path = os.path.join(sessions_dir, filename)
            service_worker_path = os.path.join(session_path, "Service Worker")
            if os.path.exists(service_worker_path):
                try:
                    shutil.rmtree(service_worker_path)
                except Exception:
                    pass

            webview = Webview(self, name, self.controller.signals, inject_js=True)
            interceptor = RequestInterceptor(webview, self.controller.signals)
            profile = QWebEngineProfile(f"{name}", webview)
            profile.setUrlRequestInterceptor(interceptor)
            profile.setCachePath(session_path)
            profile.setPersistentStoragePath(session_path)
            profile.setDownloadPath(session_path)
            profile.setHttpUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
            profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies)
            profile.setHttpAcceptLanguage("pt-br")
            engine = LogCapturingPage(profile, webview)
            webview.setPage(engine)
            webview.load(QUrl("https://web.whatsapp.com"))

            self.stacked.addWidget(webview)
            self.webviews.update({name: {"webview": webview, "page": engine, "connected": False, "phone": None}})
            self.create_session_button(name)
            self.stacked.setCurrentWidget(webview)

        if len(self.webviews) > 0 and self.remove_account_action not in self.options_menu.actions():
            self.options_menu.addAction(self.remove_account_action)

    def delete_session(self):
        """Remove a sessão atual e libera explicitamente a memória do Chromium."""
        webview = self.stacked.currentWidget()
        if webview is None:
            return

        session_path = None
        try:
            if webview.page() and webview.page().profile():
                session_path = webview.page().profile().cachePath()
        except Exception:
            pass

        name_to_delete = None
        obj_to_delete = None
        for name, obj in list(self.webviews.items()):
            if obj.get("webview") == webview:
                name_to_delete = name
                obj_to_delete = obj
                break

        if not name_to_delete:
            return

        del self.webviews[name_to_delete]

        current_index = self.stacked.currentIndex()
        self.stacked.removeWidget(webview)

        total_sessions = len(self.webviews)
        if total_sessions == 0:
            try:
                self.options_menu.removeAction(self.remove_account_action)
            except Exception:
                pass
            self.stacked.setCurrentIndex(0)
        else:
            new_index = min(self.stacked.count() - 1, max(0, current_index - 1))
            if new_index < 3:
                new_index = 3 if self.stacked.count() > 3 else 0
            self.stacked.setCurrentIndex(new_index)

        try:
            if session_path:
                self.controller.setSessionTobeDelete(session_path)
        except Exception:
            pass

        script = f"""
        (function(){{
            try {{
                const el = document.querySelector('[webview="{name_to_delete}"]');
                if (el) el.remove();
                const first = document.querySelector(".contact-item");
                if (first) first.classList.add("active");
            }} catch(e) {{}}
        }})();
        """
        try:
            if self.sidebar and self.sidebar.page():
                self.sidebar.page().runJavaScript(script)
        except Exception:
            pass

        # OTIMIZAÇÃO CRÍTICA DE RAM: Parar o carregamento e desalocar explicitamente a página e o webview
        try:
            webview.stop()
            if obj_to_delete and obj_to_delete.get("page"):
                obj_to_delete["page"].deleteLater()
            webview.deleteLater()
        except Exception:
            pass

    def closeEvent(self, event):
        """Desligar todos web engine e fechar o programa"""
        try:
            if self.sidebar and self.sidebar.page():
                self.sidebar.page().deleteLater()
        except Exception:
            pass

        try:
            if self.settings_view and self.settings_view.page():
                self.settings_view.page().deleteLater()
        except Exception:
            pass

        for key, value in list(self.webviews.items()):
            try:
                engine = value.get("page")
                if engine:
                    engine.deleteLater()
            except Exception:
                pass

        settings = QSettings("MaturadorChips", "MainWindow")
        settings.setValue("geometry", self.saveGeometry())
        
        try:
            super().closeEvent(event)
        except Exception:
            pass