from PyQt5.QtWidgets import QMessageBox, QMainWindow
from PyQt5.QtCore import pyqtSlot, QObject
from tkinter import filedialog
import webbrowser
import json
import os

class Controller(QObject):
    def __init__(self, version, signals):
        super().__init__()
        self.signals = signals
        self.home = None
        self.messages_base = {"content":[], "filename": "Selecionar arquivo", "path":""}

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
        for key, value in self.home.webviews.items():
            if key == name:
                self.home.sidebar.page().runJavaScript(script)
                self.home.stacked.setCurrentWidget(value["webview"])
                return 