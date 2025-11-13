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
              json.dump(obj=json_data, fp=file, indent=2)
         
    @pyqtSlot(str, str)
    def show_alert(self, title:str, message:str):
            """Alternativa ao alert metodo do js"""
            QMessageBox.about(
            self.home,
            title,
            message
        )