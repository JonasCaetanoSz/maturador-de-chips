from PyQt5.QtCore import pyqtSlot, QObject
from tkinter import filedialog, messagebox
import webbrowser
import json
import os

class Controller(QObject):
    def __init__(self, accounts_page, version, signals):
        super().__init__()
        self.siginals = signals
        self.accounts_page_instance = accounts_page
        self.messages_base = {"content":[], "filename":"Selecionar arquivo"}
        self.VERSION = version
        self.configs:dict = json.loads((open(file="state.json", mode="r", encoding="utf8").read()))
        self.connected_numbers = {}

    # bot de numeros virtuais no telegram
         
    @pyqtSlot()
    def telegram_bot_virtual_number_open(self):
        try:
            if os.path.exists(
                    os.path.join(
                    os.environ["APPDATA"],
                    "Telegram Desktop"
                )):
                telegram_url = "tg://resolve?domain=NotzSMSBot&start=6455672508"
            
            else:
                raise FileNotFoundError("telegram não encontrado")
        except:
            telegram_url = "https://t.me/NotzSMSBot?start=6455672508"

        webbrowser.open(url=telegram_url)

    # exibir contas conectadas
        
    @pyqtSlot()
    def accounts_viewer(self):
        if self.accounts_page_instance._opened:
            self.accounts_page_instance.activateWindow()
        self.accounts_page_instance._opened = True
        self.accounts_page_instance.show()

    # relatar problema 
    
    @pyqtSlot()
    def open_insues_link(self):
        webbrowser.open(url="https://github.com/JonasCaetanoSz/maturador-de-chips/issues")

    # abrir o link do repositório do projeto no github

    @pyqtSlot()
    def open_github_repository(self):
        webbrowser.open(url="https://github.com/JonasCaetanoSz/maturador-de-chips")    

    # abrir o link da licença do código

    @pyqtSlot()
    def open_license_repository(self):
        webbrowser.open(url="https://github.com/JonasCaetanoSz/maturador-de-chips/blob/main/LICENSE")

    # selecionar o arquivo de conversas

    @pyqtSlot(result=str)
    def selected_file(self):
        file_path = filedialog.askopenfilename(
        filetypes=[("Arquivos de Texto", "*.txt"),],
        title="Maturador de Chips - selecione o arquivo de mensagens base")
        if not file_path:
            return json.dumps({"ok":False, "message": "nenhum arquivo selecionado", "filename": self.messages_base["filename"]})
        file = open(mode="r", encoding="utf8", file=file_path)
        if not file.read():
            file.close()
            return json.dumps({"ok":False, "message": "o arquivo selecionado está vazio.",  "filename": self.messages_base["filename"]})
        
        self.messages_base["filename"]= file.name.split("/")[len(file.name.split("/")) - 1]
        self.messages_base["content"]= file.read()
        file.close()
        return  json.dumps({"ok":True, "message": "alterações foram salvas com êxito",  "filename": self.messages_base["filename"]})
    
    # mostrar versão do projeto

    @pyqtSlot()
    def view_version_project(self):
        messagebox.showinfo(
            "Maturador de chips",
            f"você está usando a versão {self.VERSION}, verifique a qualquer momento no github se há atualizações disponiveis."
        )

    # mostrar pagina do disparador 

    @pyqtSlot()
    def disparador(self):
        messagebox.showinfo(
            "Maturador de chips",
            f"este recurso estará disponivel na proxima atualização!"
        )

    # obter as configurações do usuario
        
    @pyqtSlot(result=str)

    def user_configs(self) -> str:
        configs = self.configs.copy()
        configs.update({
            "filename": self.messages_base["filename"],
            "accounts": self.connected_numbers.copy()
        })
        return json.dumps(configs)
    
    # atualizar as configurações do usuario

    @pyqtSlot(str, result=str)
    def update_user_configs(self, new_configs:str):
        new_configs = json.loads(new_configs)
        self.configs = new_configs
        configs_file = open(file="state.json", mode="w", encoding="utf8")
        json.dump(new_configs,configs_file, indent=2)
        configs_file.close()
        return json.dumps({"ok":True, "message":"alterações foram salvas com êxito"})

    # nova conta adicionada

    def account_added(self, account_data:dict):
        instance = account_data["sessionName"]
        phone = account_data["phone"]
        self.connected_numbers[instance] = phone

    # contas bloqueada ou desconectada
    
    def account_blocked(self, account_data):
        account_number = account_data["phone"]
        for key, value in self.connected_numbers.items():
            if value == account_number:
                self.connected_numbers.pop(key)
                break

    # iniciar maturação
    
    @pyqtSlot(result=str)
    def start_maturation(self):
        self.siginals.start_maturation.emit(self.messages_base, self.connected_numbers)
            
    # parar a maturação
        
    @pyqtSlot(result=str)
    def stop_maturation(self):
        self.siginals.stop_maturation.emit()
