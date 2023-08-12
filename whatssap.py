from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, QThread
from dashboard import MainWindow
from tkinter import messagebox

import websockets
import subprocess
import datetime
import asyncio
import random
import time
import json

class Whatssap(QThread):

    def __init__(self, window:MainWindow, messages_file:dict, phones:list, signals, webviews:list) -> None:
        super().__init__()
        self.messages = [i.rstrip("\r").rstrip("\n") for i in messages_file["content"]]
        self.phones = [phone for phone in phones if phone !=  "Desconectado"]
        self.webviews = webviews
        self.window = window
        self.signals = signals
        self.rundding = False
        self.configs = self.load_configs()

        # variáveis que ajuda a gerenciar a maturação

        self.messages_send_count = 0
        self.last_number_sender = None
        self.last_message = None
        self.account_sender:QWebEngineView = None
        self.block = False

    def start(self) -> None:
    
        if len(self.phones) < 2:
            messagebox.showerror(title="Maturador de chips", message="número de contas insuficiente para iniciar a maturação. duas contas ou mais são necessárias.")
            return
        
        if not self.messages:
            messagebox.showerror(title="Maturador de chips", message="você não escolheu nenhum arquivo de mensagens ou o escolhido está vazio, por favor corrija isso.")
            return
        
        # fechar a pagina de contas
        self.signals.close_accounts_page.emit()
        # transfere o webview principal para a tela de logs e configura a tela
        
        self.start_websocket_server()
        self.window.webview.load(QUrl("http://127.0.0.1:5025/maturation-updates"))
        self.window.setWindowTitle("Maturador de chips - maturação em andamento ")
        self.window.setFixedSize(749, 560)
        super().start()

    # maturar os chips em uma theard separada para não travar a interface

    def run(self):
        for i in range(0 , int(self.configs["stop_after_messages"])):
            
            # mudar a conta que envia mensagem

            if self.messages_send_count == int(self.configs["change_account_after_messages"]) or  not self.account_sender :
                new_sender = random.randint(0, (len(self.phones) - 1))
                while new_sender == self.last_number_sender:
                    new_sender = random.randint(0, (len(self.phones) -1) )
                
                self.last_number_sender = new_sender
                self.account_sender = self.webviews[new_sender]
                self.messages_send_count = 0 # reset na variável
            
            # escolher a conta que vai receber mensagem

            receive_phone_index = random.randint(0, (len(self.phones) -1))
            while receive_phone_index == self.last_number_sender:
                receive_phone_index = random.randint(0, (len(self.phones) -1))
            
            # escolher a mensagem que vai ser enviada

            message = self.messages[random.randint(0,  (len(self.messages) -1) )]
            receive_phone_number = self.phones[receive_phone_index]
            sender_phone_number = self.phones[self.last_number_sender]

            account_is_blocked = self.check_block(sender_phone_number)
            if account_is_blocked == -1:
                continue
            elif account_is_blocked:
                return
            
            # tudo certo enviar a mensagem e aguardar o intervalo escolhido pelo usuário
            self.open_chat(phone=receive_phone_number)
            self.send_message(message=message)
            self.close_chat()
            try: asyncio.run(self.send_websocket_message(sender=sender_phone_number, receiver=receive_phone_number, message=message))
            except: pass
            self.messages_send_count += 1
            interval = random.randint(int(self.configs["min_message_interval"]), int(self.configs["max_message_interval"]))
            time.sleep(interval)
                    
        # maturação concluída

        messagebox.showinfo(title="Maturador de chips", message="maturação concluída com sucesso!")
        self.signals.stop_maturation.emit()

    # parar maturação e voltar pro dashboard
    
    def stop(self):
        self.rundding = False
        super().terminate()
        #self.stop_websocket_server()
        #self.websocket_server.terminate()
        try:
            subprocess.check_call(['taskkill', '/F', '/IM', "websocket_server.exe" ])
        except:
            pass
        self.window.webview.load(QUrl("http://127.0.0.1:5025/dashboard"))
        self.window.setWindowTitle("Maturador de chips - Dashboard")
        self.window.setFixedSize(769, 660)

    # enviar mensagem de log para o websocket

    async def send_websocket_message(self, sender:str, receiver:str, message:str):
        async with websockets.connect('ws://localhost:5026') as websocket:
            data = {
            "enviadoDe": sender,
            "recebidoPor": receiver,
            "mensagem":message,
            "horario": datetime.datetime.now().strftime("%H:%M:%S") 
            }
            mensagem_json = json.dumps(data)
            await websocket.send(mensagem_json)
    
    # iniciar servidor websocket

    def start_websocket_server(self):
        subprocess.Popen(executable="websocket_server.exe", args=[])

    # carrega as configurações do usuário

    def load_configs(self) -> dict:
        with open(file="state.json", mode="r", encoding="utf-8") as f:
            return json.load(fp=f)
    
    # setar que uma conta foi bloqueada

    def set_account_block(self, phone:str):
        self.block = True
    
    # checar se a conta que esta enviando mensagem foi bloqueada os desconectada

    def check_block(self, phone:str) -> bool|int:
        with open(file="scripts/check_block.js", mode="r", encoding="utf8") as f:
            script = f.read()
        self.account_sender.page().runJavaScript(script.replace("@PHONE", phone)) 
        time.sleep(3) # acredito que seja tempo suficiente para o script rodar e enviar o sinal para a API
        
        if self.block and self.configs["continue_with_block"] == "False":
            messagebox.showerror(title="Maturador de chips" ,message=f"o número {phone} foi desconectado ou banido. parando maturação!")
            self.signals.stop_maturation.emit()
            return True
        
        elif self.block and len(self.phones) == 2:
            messagebox.showerror(title="Maturador de chips", message=f"o número {phone} foi desconectado ou banido e agora o número de contas conectadas é insuficiente para continuar. parando maturação!")
            self.signals.stop_maturation.emit()
            return True

        elif self.block:
            self.account_sender.page().runJavaScript(f""" $.notify("o numero {phone} foi desconectado", "error"); """)
            self.phones.pop(self.last_number_sender)
            self.block = False
            self.account_sender = None
            self.last_number_sender = None
            return -1
        
        return False
    
    # executar o script que abre o chat da conversa

    def open_chat(self, phone:str):
        with open(file="scripts/open_chat.js", mode="r", encoding="utf8") as script:
            self.account_sender.page().runJavaScript(script.read().replace("@PHONE", phone ))
        time.sleep(2)
    
    # enviar mensagem para o numero escolhido

    def send_message(self, message:str):
        with open(file="scripts/send_message.js", mode="r", encoding="utf8") as script:
            self.account_sender.page().runJavaScript(script.read().replace("@MESSAGE", message ))
        time.sleep(1)
    
    # fechar o chat com o contato atual

    def close_chat(self):
        with open(file="scripts/close_chat.js", mode="r", encoding="utf8") as script:
            self.account_sender.page().runJavaScript(script.read())
        time.sleep(1)
        
