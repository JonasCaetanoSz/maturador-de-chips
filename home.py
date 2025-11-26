import json
import shutil
import os
from urllib.parse import parse_qs, urlparse

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

from controller import Controller


class Webview(QWebEngineView):
    def __init__(self, parent=None, session_name="GUI", signals=None, inject_js=False):
        super().__init__(parent)
        self.session_name = session_name
        self.signals = signals
        self.inject_js_enabled = bool(inject_js)

        if self.inject_js_enabled:
            self.loadFinished.connect(lambda ok: self.disable_menu_options(whatsapp=True))
        else:
            self.loadFinished.connect(lambda ok: self.disable_menu_options(whatsapp=False))
        
        self.loadFinished.connect(lambda ok: self.apply_preferences_sound())

        # conectar loadFinished para injetar JS 

        if self.inject_js_enabled:
            self.loadFinished.connect(lambda ok: self.inject_js_script(ok))

    def reload(self):
        # Só tenta setar o channel se existir e se a page existir
        try:
            page = self.page()
            if page is not None and hasattr(self, "controller_channel"):
                page.setWebChannel(self.controller_channel)
        except Exception:
            # evita crash se page já foi deletada
            pass
        return super().reload()

    def inject_js_script(self, ok):
        """Injetar código javascript na página do whatsapp — somente se estiver em web.whatsapp.com"""
        self.signals.account_blocked.emit({"sessionName": self.session_name})
        if not ok:
            return

        try:
            page = self.page()
            if page is None:
                return
    
            # Só injetar quando realmente for o WhatsApp Web

            url = page.url().toString()

            if "web.whatsapp.com" not in url:
                return

            # Verifica se existe arquivo injected.js
            injected_path = os.path.abspath("injected.js")
            if not os.path.exists(injected_path):
                print(f"[Webview:{self.session_name}] injected.js não encontrado em {injected_path}")
                return

            # Lê e injeta JS
            with open(injected_path, "r", encoding="utf-8") as f:
                script = f.read().replace("@instanceName", self.session_name)

            # Protege a chamada de execução para não crashar se a página/motor sumiram
            try:
                page.runJavaScript(script)
            except RuntimeError:
                # Página provavelmente já foi deletada — ignora silenciosamente
                pass
        except Exception as e:
            # Log útil para dev
            print(f"[Webview:{self.session_name}] erro ao injetar JS: {e}")

    def apply_preferences_sound(self):
        """Aplica configurações de som e notificação webview"""

        with open("preferences.json", "r", encoding="utf8") as f:
            preferences = json.load(f)
            play_sound = preferences["PlaySound"]

        # Som

        self.page().setFeaturePermission(
                self.page().url(),
                QWebEnginePage.Feature.Notifications,
                QWebEnginePage.PermissionPolicy.PermissionGrantedByUser
        )
        self.page().setAudioMuted(not play_sound)
    
    def disable_menu_options(self, whatsapp):
        """Desativar opções do menu"""
        if not whatsapp:
            self.page().action(QWebEnginePage.Reload).setVisible(False)
        self.page().action(QWebEnginePage.Back).setVisible(False)
        self.page().action(QWebEnginePage.WebAction.SavePage).setVisible(False)
        self.page().action(QWebEnginePage.WebAction.CopyImageToClipboard).setVisible(False)
        self.page().action(QWebEnginePage.WebAction.CopyImageUrlToClipboard).setVisible(False)
        self.page().action(QWebEnginePage.WebAction.Forward).setVisible(False)
        self.page().action(QWebEnginePage.WebAction.ViewSource).setVisible(False)
        self.page().action(QWebEnginePage.WebAction.CopyLinkToClipboard).setVisible(False)
        self.page().action(QWebEnginePage.WebAction.OpenLinkInNewTab).setVisible(False)
        self.page().action(QWebEnginePage.WebAction.OpenLinkInThisWindow).setVisible(False)
        self.page().action(QWebEnginePage.WebAction.DownloadLinkToDisk).setVisible(False)
        self.page().action(QWebEnginePage.WebAction.OpenLinkInNewBackgroundTab).setVisible(False)
        self.page().action(QWebEnginePage.WebAction.OpenLinkInNewWindow).setVisible(False)

class LogCapturingPage(QWebEnginePage):
    # Qt pode chamar consoleMessage ou javaScriptConsoleMessage dependendo da versão
    def consoleMessage(self, level, message, lineNumber, sourceID):
        print(message)

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        print(message)


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
                    # Emissão do sinal com os dados recebidos pela requisição
                    self.signals.new_phone_number.emit(data)

                # bloqueia a requisição para não prosseguir no motor
                info.block(True)
        except Exception as e:
            print(f"[RequestInterceptor] erro ao interceptar: {e}")


class Home(QMainWindow):
    def __init__(self, controller: Controller):
        super().__init__()
        self.setWindowTitle("Maturador de chips 2025.11.12")
        self.setWindowIcon(QIcon("assets/medias/icon.ico"))
        self.setGeometry(100, 100, 1200, 700)
        self.controller = controller
        self.webviews = {}

        # Cria o menu
        menubar = self.menuBar()
        self.options_menu = menubar.addMenu("Opções")
        # Ação solta na barra
        self.action_start_maturation = QtWidgets.QAction("Iniciar", self)
        # note: emitir diretamente no controller.signals
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

        # Sidebar (lista) - NÃO injeta JS
        self.sidebar = Webview(self, session_name="sidebar", signals=None, inject_js=False)
        profile = QWebEngineProfile("cache_list_view", self.sidebar)
        engine = LogCapturingPage(profile, self.sidebar)
        channel = QWebChannel(engine)
        channel.registerObject("controller", self.controller)
        self.sidebar.controller_channel = channel
        engine.setWebChannel(channel)
        sidebar_path = os.path.abspath("whatsapp_list.html")
        # carrega lista e, ao terminar, chama load_sessions
        engine.loadFinished.connect(lambda ok: self.load_sessions() if ok else None)
        engine.setUrl(QUrl.fromLocalFile(sidebar_path))
        self.sidebar.setPage(engine)

        # QStackedWidget para o webview maior
        self.stacked = QStackedWidget()

        # Página 0 (index 0): Nenhuma conta conectada
        self.no_account_widget = QWidget()
        self.no_account_layout = QVBoxLayout(self.no_account_widget)
        self.no_account_layout.setAlignment(Qt.AlignCenter)
        label = QLabel("Nenhuma conta conectada")
        label.setStyleSheet("font-size: 24px; color: #555;")
        self.no_account_layout.addWidget(label)

        # Página 1 (index 1): Configurações (NÃO injeta JS)
        self.settings_view = Webview(self, session_name="settings", inject_js=False)
        cache_dir = os.path.join(os.getcwd(), "cache")
        profile = QWebEngineProfile("cache_configs_view", self.settings_view)
        profile.setCachePath(cache_dir)
        profile.setPersistentStoragePath(cache_dir)
        profile.setDownloadPath(cache_dir)
        profile.setPersistentCookiesPolicy(QWebEngineProfile.AllowPersistentCookies)
        profile.setHttpAcceptLanguage("pt-br")

        engine = LogCapturingPage(profile, self.settings_view)
        channel = QWebChannel(engine)
        channel.registerObject("controller", self.controller)
        self.settings_view.controller_channel = channel
        engine.setWebChannel(channel)
        settings_path = os.path.abspath("settings.html")
        engine.setUrl(QUrl.fromLocalFile(settings_path))
        self.settings_view.setPage(engine)

        # Página 2 (index 2): atualizações/status (NÃO injeta JS)
        self.status_view = Webview(self, session_name="status", inject_js=False)
        profile = QWebEngineProfile("cache_status_view", self.status_view)
        profile.setCachePath(cache_dir)
        profile.setPersistentStoragePath(cache_dir)
        profile.setDownloadPath(cache_dir)
        profile.setPersistentCookiesPolicy(QWebEngineProfile.AllowPersistentCookies)
        profile.setHttpAcceptLanguage("pt-br")

        engine = LogCapturingPage(profile, self.status_view)
        channel = QWebChannel(engine)
        channel.registerObject("controller", self.controller)
        self.status_view.controller_channel = channel
        engine.setWebChannel(channel)
        status_path = os.path.abspath("status.html")
        engine.setUrl(QUrl.fromLocalFile(status_path))
        self.status_view.setPage(engine)

        # Adiciona as páginas no stacked widget
        self.stacked.addWidget(self.no_account_widget)   # índice 0
        self.stacked.addWidget(self.settings_view)       # índice 1
        self.stacked.addWidget(self.status_view)         # índice 2

        # Adiciona sidebar e stacked widget ao layout
        layout.addWidget(self.sidebar, 25)
        layout.addWidget(self.stacked, 75)

        # Define o layout central da janela
        self.setCentralWidget(central_widget)

    def open_preferences(self):
        """Muda o webview maior para configurações"""
        # garante que o botão remover exista apenas quando relevante
        try:
            self.options_menu.removeAction(self.remove_account_action)
        except Exception:
            pass

        # recarrega as configurações de forma segura
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
            else:
                self.stacked.setCurrentIndex(0)

        self.sidebar.page().runJavaScript(js, callback)
        self.options_menu.addAction(self.remove_account_action)

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
        """Adicionar nova conta/webview"""
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

        # Cria webview da sessão - AQUI ativamos injeção porque é um web.whatsapp.com
        webview = Webview(self, session_name=name, signals=self.controller.signals, inject_js=True)
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
        self.webviews.update({name: {"webview": webview, "page": engine, "connected": False}})
        self.create_session_button(name)
        self.stacked.setCurrentWidget(webview)

        # ativa menu remover (há ao menos 1 sessão)
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

            // Cria um objeto evento "fake" para ativar o botão via função
            const fakeEvent = {{ currentTarget: container }};
            window.change_current_webview(fakeEvent);
        }}
        create_button();
        """

        # Protege a chamada para evitar exceções se sidebar.page() sumiu
        try:
            if self.sidebar and self.sidebar.page():
                self.sidebar.page().runJavaScript(script)
        except Exception as e:
            print(f"[create_session_button] erro: {e}")

    def load_sessions(self):
        """Carregar sessões salvas no sistema"""
        sessions_dir = os.path.join(os.getcwd(), "sessions")
        if not os.path.exists(sessions_dir):
            try:
                os.mkdir(sessions_dir)
            except Exception:
                return

        for filename in os.listdir(sessions_dir):
            # corrige bug: usar substring check em vez de find()
            if ".session" not in filename:
                continue

            # determina o nome
            if filename.endswith(".session"):
                name = filename[:-8]
            else:
                name = filename

            session_path = os.path.join(sessions_dir, filename)
            service_worker_path = os.path.join(session_path, "Service Worker")
            if os.path.exists(service_worker_path):
                try:
                    shutil.rmtree(service_worker_path)
                except Exception:
                    pass

            # Cria webview da sessão (injeta JS)
            webview = Webview(self, name, self.controller.signals, inject_js=True)
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
            self.webviews.update({name: {"webview": webview, "page": engine, "connected": False, "phone": None}})
            self.create_session_button(name)
            # não muda o currentWidget repetidamente para cada sessão; apenas define a última adicionada
            self.stacked.setCurrentWidget(webview)

        # Se houver sessões, garante que o botão remover esteja visível
        if len(self.webviews) > 0 and self.remove_account_action not in self.options_menu.actions():
            self.options_menu.addAction(self.remove_account_action)

    def delete_session(self):
        """Remove a sessão atual, exclui o botão da sidebar e define o próximo webview ativo."""
        webview = self.stacked.currentWidget()
        if webview is None:
            return

        # tenta obter session_path de forma segura
        try:
            session_path = webview.page().profile().cachePath()
        except Exception:
            session_path = None

        name_to_delete = None
        for name, obj in list(self.webviews.items()):
            if obj.get("webview") == webview:
                name_to_delete = name
                break

        if not name_to_delete:
            return

        # remove do dicionário
        try:
            del self.webviews[name_to_delete]
        except KeyError:
            pass

        # Remove o widget do stacked e determina novo índice seguro
        try:
            current_index = self.stacked.currentIndex()
            self.stacked.removeWidget(webview)
        except Exception:
            current_index = 0

        # Atualiza menu remover se não houver mais sessões
        total_sessions = len(self.webviews)
        if total_sessions == 0:
            try:
                self.options_menu.removeAction(self.remove_account_action)
            except Exception:
                pass
            self.stacked.setCurrentIndex(0)
        else:
            # Escolhe um widget válido para setCurrentIndex: pega o último widget (se possível)
            new_index = min(self.stacked.count() - 1, max(0, current_index - 1))
            # evita escolher índices reservados (0..2 são widgets não-sessão)
            if new_index < 3:
                new_index = 3 if self.stacked.count() > 3 else 0
            try:
                self.stacked.setCurrentIndex(new_index)
            except Exception:
                self.stacked.setCurrentIndex(0)

        # Chama controller para marcar a sessão pra remoção (se aplicável)
        try:
            if session_path:
                self.controller.setSessionTobeDelete(session_path)
        except Exception:
            pass

        # Remove botão da sidebar via JS, protegido com try/except
        script = f"""
        (function(){{
            try {{
                const el = document.querySelector('[webview="{name_to_delete}"]');
                if (el) {{
                    el.remove();
                }}
                const first = document.querySelector(".contact-item");
                if (first) {{
                    first.classList.add("active");
                }}
            }} catch(e) {{ console.log(e) }}
        }})();
        """
        try:
            if self.sidebar and self.sidebar.page():
                self.sidebar.page().runJavaScript(script)
        except Exception as e:
            print(f"[delete_session] erro ao executar JS na sidebar: {e}")

        # Tenta executar logout na webview se possível
        try:
            if webview and webview.page():
                webview.page().runJavaScript("if(window.WTools && window.WTools.logout){ window.WTools.logout(); }")
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

        # chama o fechamento padrão
        try:
            super().closeEvent(event)
        except Exception:
            pass
