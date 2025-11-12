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

    @pyqtSlot()
    def close_preferences_signal(self):
        self.signals.close_preferences.emit()
    
    def close_preferences(self):
        self.home.stacked.setCurrentIndex(0)
    
    def setHomePage(self, home):
        self.home = home