from tkinter import messagebox
import webbrowser
import shutil
import flask
import json
import os

class Api:

    def __init__(self, version, signals_receive):
        self.PORT = 5025
        self.messages_base = {"content":[], "filename":"Selecionar arquivo"}
        self.accounts_phone_list = ["Desconectado" for i in range(0,10)]
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
        
    # setar a varavel "pagina de contas aberta" como verdadeiro ou falso
    
    def set_account_page_state(self, op:bool, instance = None):
        self.accounts_page_instance = instance
        self.accounts_page_is_open = op

    def start(self):
        
        # entregar a primeira pagina do programa
        
        @self.app.route(rule="/dashboard")

        def dashboard():
            with open(file="state.json", mode="r", encoding="utf-8") as configs_file:
                configs_dict = json.load(configs_file)
            return flask.render_template(
                template_name_or_list="dashboard.html",
                continue_with_block= "" if configs_dict["continue_with_block"] != "True" else 'checked="true"',
                min_message_interval=configs_dict["min_message_interval"],
                max_message_interval=configs_dict["max_message_interval"],
                selected_file=self.messages_base["filename"],
                change_account_after_messages=configs_dict["change_account_after_messages"],
                stop_after_messages=configs_dict["stop_after_messages"],
                phones=self.accounts_phone_list
            )
        
        # entregar a a pagina de logs

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
                title="Maturador de chips",
                message=f"você está usando a versão {self.VERSION}, verifique a qualquer momento no github se há atualizações disponiveis."
            )
            return flask.jsonify(ok=True)
        
        # abrir o link do repositorio do projeto no github

        @self.app.route(rule="/api/github-open")
        def open_github_repository():
            webbrowser.open(url="https://github.com/JonasCaetanoSz/maturador-de-chips")
            return flask.jsonify(ok=True)
        
        # abrir o link da licensa do codigo

        @self.app.route(rule="/api/license-open")
        def open_license_repository():
            webbrowser.open(url="https://github.com/JonasCaetanoSz/maturador-de-chips/blob/main/LICENSE")
            return flask.jsonify(ok=True)
        
                
        # mostrar contas conectadas

        @self.app.route(rule="/api/accounts-view")
        def accounts_viewer():
            if self.accounts_page_is_open:
                self.accounts_page_instance.activateWindow()
                return flask.jsonify(ok=False)  
            self.SIGNAL_RECEIVER.viewer_accounts.emit()
            return flask.jsonify(ok=True)
        
        # apoiar projeto (nubank pix link)
        
        @self.app.route(rule="/api/apoia-pix-open")
        def open_apoia_linky():
            webbrowser.open(url="https://nubank.com.br/pagar/1ciknr/cao9amcj1Y")
            return flask.jsonify(ok=True)
        
        # nova conta adicionada

        @self.app.route(rule="/api/account-added", methods=["POST"])
        def account_added():
            instance = int(flask.request.json["instance"])
            phone = flask.request.json["phone"]
            self.accounts_phone_list[instance] = phone
            self.SIGNAL_RECEIVER.new_phone_number.emit()
            return flask.jsonify(ok=True)
        
        # contas bloqueada ou desconectada
        
        @self.app.route(rule="/api/account-blocked", methods=["POST"])
        def account_blocked():
            account_number = flask.request.json["phone"]
            self.SIGNAL_RECEIVER.account_blocked.emit(account_number)
            account_index = self.accounts_phone_list.index(account_number)
            self.accounts_phone_list[account_index] = "Desconectado"

            return flask.jsonify(ok=True)
        
        # selecionar o arquivo de conversas

        @self.app.route(rule="/api/selected-messages-file", methods=["POST"])
        def selected_file():
            file = flask.request.files["file"]
            file.save("sessions/cache/messages")
            with open(file="sessions/cache/messages", mode="r", encoding="utf8") as f:
                content = f.readlines()
            os.remove("sessions/cache/messages")
            if not content:
                return flask.jsonify(ok=False, message="o arquivo não pode estar vazio.")
            self.messages_base["filename"]= file.filename
            self.messages_base["content"]= content
            return flask.jsonify(ok=True)
        
        # iniciar maturação

        @self.app.route(rule="/api/start-maturation", methods=["GET"])
        def start_maturation():
            self.SIGNAL_RECEIVER.start_maturation.emit(self.messages_base, self.accounts_phone_list)
            return flask.jsonify(ok=True)

                
        # parar a maturação

        @self.app.route(rule="/api/stop-maturation", methods=["GET"])
        def stop_maturation():
            self.SIGNAL_RECEIVER.stop_maturation.emit()
            return flask.jsonify(ok=True)



        # iniciar a API

        self.app.run(port=self.PORT, debug=False)