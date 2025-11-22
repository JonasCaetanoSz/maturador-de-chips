import os
import json
import shutil
from typing import Optional

from PyQt5.QtWidgets import QMessageBox, QSystemTrayIcon
from PyQt5.QtCore import pyqtSlot, QObject
from PyQt5.QtGui import QIcon
from tkinter import filedialog


class Controller(QObject):
    def __init__(self, version: str, signals):
        super().__init__()
        self.signals = signals
        self.window = None
        self.home = None
        self.messages_base = {"filename": "Selecionar arquivo", "path": ""}
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QIcon("assets/medias/icon.ico"))
        self.tray.show()

        # Garante que delete.json existe e tenta limpar sessões marcadas para exclusão
        self._cleanup_deleted_sessions()

    def _cleanup_deleted_sessions(self):
        """Remove past session folders listadas em delete.json (executado na inicialização)."""
        path = "delete.json"
        try:
            if not os.path.exists(path):
                # cria arquivo vazio com a estrutura esperada
                with open(path, "w", encoding="utf-8") as f:
                    json.dump({"deleteLaster": []}, f, indent=4, ensure_ascii=False)
                return

            with open(path, "r+", encoding="utf-8") as file:
                content = file.read().strip()
                if not content:
                    json_content = {"deleteLaster": []}
                else:
                    try:
                        json_content = json.loads(content)
                    except json.JSONDecodeError:
                        json_content = {"deleteLaster": []}

                delete_list = json_content.get("deleteLaster", [])[:]
                for session_path in delete_list:
                    try:
                        if os.path.exists(session_path):
                            shutil.rmtree(session_path)
                    except Exception as e:
                        print(f"[Controller] erro ao remover sessão '{session_path}': {e}")
                    # remove sempre, mesmo se não existia mais
                    try:
                        json_content["deleteLaster"].remove(session_path)
                    except ValueError:
                        pass

                # reescreve o arquivo com a lista atualizada
                file.seek(0)
                json.dump(json_content, file, indent=4, ensure_ascii=False)
                file.truncate()
        except Exception as e:
            print(f"[Controller] erro ao limpar delete.json: {e}")

    def setHomePage(self, home):
        """Definir instancia da janela principal (Home)."""
        self.home = home

    @pyqtSlot()
    def close_preferences_signal(self):
        """Evento chamado pelo JS da página de preferências para fechar a aba."""
        if hasattr(self, "signals") and self.signals:
            try:
                self.signals.close_preferences.emit()
            except Exception:
                pass

    def close_preferences(self):
        """Fechar preferencias"""
        self.home.close_preferences()

    @pyqtSlot(result=str)
    def get_user_configs(self) -> str:
        """Retorna o conteúdo de preferences.json (ou string vazia se não existir)."""
        try:
            with open("preferences.json", "r", encoding="utf-8") as configs:
                return configs.read()
        except FileNotFoundError:
            return ""
        except Exception as e:
            print(f"[Controller] erro ao ler preferences.json: {e}")
            return ""

    @pyqtSlot(str)
    def update_user_configs(self, new_configs: str):
        """Atualiza preferences.json com o conteúdo recebido do JS, acrescentando o caminho do arquivo selecionado."""
        try:
            json_data = json.loads(new_configs) if new_configs else {}
        except json.JSONDecodeError:
            json_data = {}

        # garante a chave seleciona e atualiza
        json_data.update({"seletedFilePath": self.messages_base.get("path", "")})
        try:
            with open("preferences.json", "w", encoding="utf-8") as file:
                json.dump(json_data, file, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Controller] erro ao escrever preferences.json: {e}")

    @pyqtSlot(str, str)
    def show_alert(self, title: str, message: str):
        """Mostrar caixa de diálogo alternativa ao alert do JS."""
        try:
            parent = self.home if self.home is not None else None
            QMessageBox.about(parent, title, message)
        except Exception as e:
            print(f"[Controller] erro ao mostrar alert: {e}")

    @pyqtSlot(result=str)
    def select_file(self) -> Optional[str]:
        """Selecionar arquivo de mensagens via filedialog (tkinter). Retorna caminho ou None."""
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("Arquivos de Texto", "*.txt")],
                title="Maturador de Chips - selecione o arquivo de mensagens"
            )
            if not file_path:
                return None

            # abre de forma segura
            try:
                with open(file_path, mode="r", encoding="utf-8") as f:
                    content = f.read()
                    if not content:
                        self.show_alert("Maturador de chips", "O arquivo selecionado não pode estar vazio!")
                        return None
            except Exception as e:
                self.show_alert("Maturador de chips", f"Erro ao abrir arquivo: {e}")
                return None

            self.messages_base["filename"] = os.path.basename(file_path)
            self.messages_base["path"] = file_path
            return file_path
        except Exception as e:
            print(f"[Controller] erro em select_file: {e}")
            return None

    @pyqtSlot(str)
    def change_current_webview(self, name: str):
        """Trocar o webview de conta atual no stacked widget e ativar o botão na sidebar."""
        try:
            # limpa class active de todos (proteção se sidebar não existir)
            if self.home and getattr(self.home, "sidebar", None) and self.home.sidebar.page():
                try:
                    self.home.sidebar.page().runJavaScript(
                        "document.querySelectorAll('.contact-item').forEach(el => el.classList.remove('active'));"
                    )
                except Exception:
                    pass

            # adiciona o botão remover no menu se ainda não estiver presente
            try:
                if self.home and self.home.remove_account_action not in self.home.options_menu.actions():
                    self.home.options_menu.addAction(self.home.remove_account_action)
            except Exception:
                pass

            # troca o webview no stacked
            if not self.home:
                return

            for key, value in self.home.webviews.items():
                if key == name:
                    # ativa o botão na sidebar via JS de forma segura
                    script = f"""
                    (function(){{
                        const selected = document.querySelector("[webview='{name}']");
                        if(selected) {{
                            document.querySelectorAll('.contact-item').forEach(el => el.classList.remove('active'));
                            selected.classList.add('active');
                        }}
                    }})();
                    """
                    try:
                        if self.home.sidebar and self.home.sidebar.page():
                            self.home.sidebar.page().runJavaScript(script)
                    except Exception:
                        pass

                    try:
                        self.home.stacked.setCurrentWidget(value["webview"])
                    except Exception:
                        pass
                    return
        except Exception as e:
            print(f"[Controller] erro em change_current_webview: {e}")

    def setSessionTobeDelete(self, session_path: str):
        """Adicionar sessão ao arquivo delete.json para remoção no próximo start."""
        try:
            path = "delete.json"
            if not os.path.exists(path):
                json_content = {"deleteLaster": [session_path]}
            else:
                with open(path, "r", encoding="utf-8") as file:
                    content = file.read().strip()
                    try:
                        json_content = json.loads(content) if content else {"deleteLaster": []}
                    except json.JSONDecodeError:
                        json_content = {"deleteLaster": []}
                json_content.setdefault("deleteLaster", [])
                json_content["deleteLaster"].append(session_path)

            with open(path, "w", encoding="utf-8") as file:
                json.dump(json_content, file, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[Controller] erro ao escrever delete.json: {e}")

    def accountAuthenticated(self, data: dict):
        """Marca a sessão como conectada e atualiza a UI (sidebar)."""
        try:
            session_name = data.get("sessionName")
            phone = data.get("phone")
            photo = data.get("photo") or "assets/medias/contact.jpg"
            if not session_name or not self.home or session_name not in self.home.webviews:
                return

            self.home.webviews[session_name]["connected"] = True
            self.home.webviews[session_name]["phone"] = phone

            # atualiza a sidebar com segurança
            script = f"""
            (function(){{
                const el = document.querySelector("[webview='{session_name}']");
                if (!el) return;
                const numberEl = el.querySelector(".contact-number");
                const iconEl = el.querySelector(".contact-icon");
                if(numberEl) numberEl.textContent = "{session_name} (Conectado)";
                if(iconEl) iconEl.src = "{photo}";
            }})();
            """
            try:
                if self.home.sidebar and self.home.sidebar.page():
                    self.home.sidebar.page().runJavaScript(script)
            except Exception:
                pass
        except Exception as e:
            print(f"[Controller] erro em accountAuthenticated: {e}")

    def accountDisconnected(self, data: dict):
        """Marca a sessão como desconectada e atualiza a UI (sidebar)."""
        try:
            session_name = data.get("sessionName")
            if not session_name or not self.home or session_name not in self.home.webviews:
                return

            self.home.webviews[session_name]["phone"] = None
            self.home.webviews[session_name]["connected"] = False

            script = f"""
            (function(){{
                const el = document.querySelector("[webview='{session_name}']");
                if (!el) return;
                const numberEl = el.querySelector(".contact-number");
                const iconEl = el.querySelector(".contact-icon");
                if(numberEl) numberEl.textContent = "{session_name} (Desconectado)";
                if(iconEl) iconEl.src = "assets/medias/contact.jpg";
            }})();
            """
            try:
                if self.home.sidebar and self.home.sidebar.page():
                    self.home.sidebar.page().runJavaScript(script)
            except Exception:
                pass
        except Exception as e:
            print(f"[Controller] erro em accountDisconnected: {e}")

    def notify(self, title: str, message: str):
        """Mostrar notificação via bandeja."""
        try:
            # showMessage aceita (title, message, icon_or_enum, timeout_ms) — aqui usamos apenas title/message
            self.tray.showMessage(title, message)
        except Exception as e:
            print(f"[Controller] erro em notify: {e}")

    def inject_message_row(self, data:dict):
        js_code = f"""
        if (typeof injectMessageRow !== 'function') {{
            function injectMessageRow(sender, receiver, message, time) {{
                const tbody = document.querySelector("tbody");
                if (!tbody) return;
                const tr = document.createElement("tr");
                const tdSender = document.createElement("td");
                tdSender.textContent = sender;
                const tdReceiver = document.createElement("td");
                tdReceiver.textContent = receiver;
                const tdMessage = document.createElement("td");
                tdMessage.textContent = message;
                const tdTime = document.createElement("td");
                tdTime.textContent = time;
                tr.appendChild(tdSender);
                tr.appendChild(tdReceiver);
                tr.appendChild(tdMessage);
                tr.appendChild(tdTime);
                tbody.appendChild(tr);
            }}
        }}
        injectMessageRow({json.dumps(data["sender"])}, {json.dumps(data["receiver"])}, {json.dumps(data["message"])}, {json.dumps(data["time"])});
        """
        self.home.status_view.page().runJavaScript(js_code)