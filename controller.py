from PyQt5.QtWidgets import QMessageBox, QMainWindow
from PyQt5.QtCore import pyqtSlot, QObject
from tkinter import filedialog
import shutil
import webbrowser
import json
import os

class Controller(QObject):
    def __init__(self, version, signals):
        super().__init__()
        self.signals = signals
        self.home = None
        self.messages_base = {"content":[], "filename": "Selecionar arquivo", "path":""}
    
    # Deleta sessões anteriores marcadas para exclusão (motivo: por algum motivo a sessão ainda está sendo usada quando o programa encerra não podendo ser feito por lá. essa é a melhor opção)
    
    with open("delete.json", "r+", encoding="utf-8") as file:
        json_content = json.loads(file.read())
        delete_list = json_content.get("deleteLaster", [])

        for session_path in delete_list[:]:
            shutil.rmtree(session_path)
            delete_list.remove(session_path)

        json_content["deleteLaster"] = delete_list

        file.seek(0)
        json.dump(json_content, file, indent=4, ensure_ascii=False)
        file.truncate()


    def setHomePage(self, home):
        """Definir instancia da janela principal"""
        self.home = home

    @pyqtSlot()
    def close_preferences_signal(self):
        """Evento que vem do JavaScript pagina de preferencias"""
        self.signals.close_preferences.emit()
    
    def close_preferences(self):
        """Fechar aba de preferecias"""
        self.home.stacked.setCurrentIndex(0)
    
    @pyqtSlot(result=str)
    def get_user_configs(self):
        """Obter configurações de usuario"""
        with open(file="preferences.json", mode="r", encoding="utf-8") as configs:
            return configs.read()
    
    @pyqtSlot(str)
    def update_user_configs(self, new_configs:str):
         with open(file="preferences.json", mode="w", encoding="utf-8") as file:
              json_data = json.loads(new_configs)
              json_data.update({"seletedFilePath": self.messages_base["path"] })
              json.dump(obj=json_data, fp=file, indent=2)
         
    @pyqtSlot(str, str)
    def show_alert(self, title:str, message:str):
            """Alternativa ao alert metodo do js"""
            QMessageBox.about(
            self.home,
            title,
            message
        )
    
    @pyqtSlot(result=str)
    def select_file(self):
        """Selecionar arquivo de mensagens"""
        file_path = filedialog.askopenfilename(
        filetypes=[("Arquivos de Texto", "*.txt"),],
        title="Maturador de Chips - selecione o arquivo de mensagens")
        if not file_path:
            return None
        file = open(mode="r", encoding="utf8", file=file_path)

        if not file.read():
            self.show_alert("Maturador de chips", "O arquivo selecionado não pode estar vazio!")
            file.close()
            return None
        file.seek(0)
        self.messages_base["filename"]= file.name.split("/")[len(file.name.split("/")) - 1]
        self.messages_base["content"]= file.readlines()
        self.messages_base["path"] = file_path
        file.close()
        return  file_path
    
    @pyqtSlot(str)
    def change_current_webview(self, name):
        """Trocar o webview de conta atual """
        
        self.home.sidebar.page().runJavaScript(""" document.querySelectorAll(".contact-item").forEach(el => el.classList.remove("active")); """)
        script = f"""
        function change_current_activate_button(){{
        
        const seletedButton = document.querySelector("[webview='{name}']");
        seletedButton.classList.add("active");
        }};

        change_current_activate_button();
        """
        self.home.options_menu.addAction(self.home.remove_account_action)
        for key, value in self.home.webviews.items():
            if key == name:
                self.home.sidebar.page().runJavaScript(script)
                self.home.stacked.setCurrentWidget(value["webview"])
                return 
    
    def setSessionTobeDelete(self, session_path: str):
        """Definir sessão para exclusão futura (quando o programa for reiniciado)"""
        with open("delete.json", "r+", encoding="utf-8") as file:
            content = file.read().strip()

            if not content:
                json_content = {"deleteLaster": []}
            else:
                try:
                    json_content = json.loads(content)
                except json.JSONDecodeError:
                    json_content = {"deleteLaster": []}

            json_content.setdefault("deleteLaster", []).append(session_path)

            file.seek(0)
            json.dump(json_content, file, indent=4, ensure_ascii=False)
            file.truncate()
    
    def accountAuthenticated(self, data:dict):
        """Conta conectada leitor do evento"""
        session_name = data["sessionName"]
        photo = data["photo"] if data["photo"] and not data["photo"].isspace() else "assets/medias/contact.jpg"
        script = f"""

        function setContactConected(){{
        
        const contactElement = document.querySelector("[webview='{session_name}']");
        contactElement.querySelector(".contact-number").textContent = "{session_name} (Conectado)";
        contactElement.querySelector(".contact-icon").src = "{photo}";

        }};
        
        setContactConected();
        """

        self.home.sidebar.page().runJavaScript(script)
        print(data)

    def accountDisconnected(self, data:dict):
        """Conta desconectada leitor do evento"""
        session_name = data["sessionName"]
        script = f"""

        function setContactDisconnected(){{
        
        const contactElement = document.querySelector("[webview='{session_name}']");
        
        if (contactElement){{
            contactElement.querySelector(".contact-number").textContent = "{session_name} (Desconectado)";
            contactElement.querySelector(".contact-icon").src = "assets/medias/contact.jpg";
        }};

        }};
        
        setContactDisconnected();
        """

        self.home.sidebar.page().runJavaScript(script)
        print(data)