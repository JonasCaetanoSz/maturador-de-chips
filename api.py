from PyQt5.QtCore import QThread
from tkinter import messagebox
from flask_cors import CORS
import webbrowser
import requests
import flask
import json
import os

class Api(QThread):

    def __init__(self, version, signals_receive):
        super().__init__()
        self.PORT = 5025
        self.messages_base = {"content":[], "filename":"Selecionar arquivo"}
        self.accounts_phone = {}
        self.accounts_page_instance = None
        self.accounts_page_is_open = False
        self.SIGNAL_RECEIVER = signals_receive
        self.VERSION = version
        self.TEMPLASTES_FOLDER = os.getcwd() + "/pages"
        self.ASSETS_FOLDER =  os.getcwd() + "/pages/assets"
        self.app = flask.Flask(
            import_name=__name__,
            template_folder=self.TEMPLASTES_FOLDER,
            static_folder=self.ASSETS_FOLDER,
            static_url_path="/assets"
        )
        CORS(self.app)
        super().start()

    # setar a variável "accounts_page_is_open" como verdadeiro ou falso
    
    def set_account_page_state(self, op:bool, instance = None):
        self.accounts_page_instance = instance
        self.accounts_page_is_open = op

    def run(self):
        
        # entregar a primeira pagina do programa
        
        @self.app.route(rule="/dashboard")

        def dashboard():
            with open(file="state.json", mode="r", encoding="utf-8") as configs_file:
                configs_dict = json.load(configs_file)
            if not flask.request.args["t"] == "0":
                raise Exception("validação erro, request não veio do programa")

            return flask.render_template(
                template_name_or_list="dashboard.html",
                continue_with_block= "" if configs_dict["continue_with_block"] != "True" else 'checked="true"',
                shutdown_computer= "" if configs_dict["shutdown_computer"] != "True" else 'checked="true"',
                min_message_interval=configs_dict["min_message_interval"],
                max_message_interval=configs_dict["max_message_interval"],
                selected_file=self.messages_base["filename"],
                change_account_after_messages=configs_dict["change_account_after_messages"],
                stop_after_messages=configs_dict["stop_after_messages"],
                phones=self.accounts_phone
            )
    
        # entregar a pagina de logs

        @self.app.route(rule="/maturation-updates",methods=["GET"])
        def logs_page():
            return flask.render_template("updates.html")
        
        # atualizar as configurações do usuario

        @self.app.route(rule="/api/update-configs", methods=["POST"])
        def receive_update_configs():
            with open(file="state.json", mode="w", encoding="utf-8") as config_file:
                json.dump(
                    obj=flask.request.json,
                    fp=config_file,
                    indent=4
                )
            return flask.jsonify(ok=True)
        
        # mostrar versão do projeto

        @self.app.route(rule="/api/version-view")
        def view_version_project():
            messagebox.showinfo(
                "Maturador de chips",
                f"você está usando a versão {self.VERSION}, verifique a qualquer momento no github se há atualizações disponiveis."
            )
            return flask.jsonify(ok=True)
        
        # mostrar pagina do disparador 

        @self.app.route(rule="/api/disparador")
        def disparador():
            messagebox.showinfo(
                "Maturador de chips",
                f"este recurso estará disponivel na proxima atualização!"
            )
            return flask.jsonify(ok=True)
        
        # abrir o link do repositório do projeto no github

        @self.app.route(rule="/api/github-open")
        def open_github_repository():
            webbrowser.open(url="https://github.com/JonasCaetanoSz/maturador-de-chips")
            return flask.jsonify(ok=True)
        
        # abrir o link da licença do código

        @self.app.route(rule="/api/license-open")
        def open_license_repository():
            webbrowser.open(url="https://github.com/JonasCaetanoSz/maturador-de-chips/blob/main/LICENSE")
            return flask.jsonify(ok=True)
        
        # abrir o link de numero virtual

        @self.app.route(rule="/api/virtual-number-open")
        def open_virtual_number():
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
            return flask.jsonify(ok=True)
        
                
        # mostrar contas conectadas

        @self.app.route(rule="/api/accounts-view")
        def accounts_viewer():
            if self.accounts_page_is_open:
                self.accounts_page_instance.activateWindow()
                return flask.jsonify(ok=False)  
            self.SIGNAL_RECEIVER.viewer_accounts.emit()
            return flask.jsonify(ok=True)
        
        # relatar problema 
        
        @self.app.route(rule="/api/issue-open")
        def open_insues_link():
            webbrowser.open(url="https://github.com/JonasCaetanoSz/maturador-de-chips/issues")
            return flask.jsonify(ok=True)
        
        # nova conta adicionada

        @self.app.route(rule="/api/account-added", methods=["POST"])
        def account_added():
            instance = flask.request.json["sessionName"]
            phone = flask.request.json["phone"]
            self.accounts_phone[instance] = phone
            self.SIGNAL_RECEIVER.new_phone_number.emit()
            return flask.jsonify(ok=True)
        
        # contas bloqueada ou desconectada
        
        @self.app.route(rule="/api/account-blocked", methods=["POST"])
        def account_blocked():
            account_number = flask.request.json["phone"]
            self.SIGNAL_RECEIVER.account_blocked.emit(account_number)
            for key, value in self.accounts_phone.items():
                if value == account_number:
                    self.accounts_phone.pop(key)
                    break
            return flask.jsonify(ok=True)
        
        # selecionar o arquivo de conversas

        @self.app.route(rule="/api/selected-messages-file", methods=["POST"])
        def selected_file():
            file = flask.request.files["file"]
            file.save("sessions/cache/messages.txt")
            with open(file="sessions/cache/messages.txt", mode="r", encoding="utf8") as f:
                content = f.readlines()
            
            os.remove("sessions/cache/messages.txt")
            if not content:
                return flask.jsonify(ok=False, message="o arquivo não pode estar vazio.")
            self.messages_base["filename"]= file.filename
            self.messages_base["content"]= content
            return flask.jsonify(ok=True)
        
        # iniciar maturação

        @self.app.route(rule="/api/start-maturation", methods=["GET"])
        def start_maturation():
            self.SIGNAL_RECEIVER.start_maturation.emit(self.messages_base, self.accounts_phone)
            return flask.jsonify(ok=True)

                
        # parar a maturação

        @self.app.route(rule="/api/stop-maturation", methods=["GET"])
        def stop_maturation():
            self.SIGNAL_RECEIVER.stop_maturation.emit()
            return flask.jsonify(ok=True)

        # iniciar a API

        self.app.run(port=self.PORT, debug=False)