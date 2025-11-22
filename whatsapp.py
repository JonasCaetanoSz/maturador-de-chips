from controller import Controller

from openai import OpenAI

from PyQt5 import QtCore

import random
import json
import os



class WhatsApp(QtCore.QThread):
    def __init__(self, signals: QtCore.QObject, controller: Controller):
        super().__init__()
        self.controller = controller
        self.signals = signals
        self.messages = []
        self.preferences = {}
        self.conversation_histories = {}


    def prepare(self) -> bool:
        connected_keys = [
            key for key, webview in self.controller.home.webviews.items()
            if webview.get("connected", False)
        ]

        if len(connected_keys) < 2:
            return self.controller.show_alert("Maturador de chips", "É necessário pelo menos 2 contas conectadas para iniciar.")

        with open("preferences.json", "r", encoding="utf8") as f:
            self.preferences = json.load(f)

        if self.preferences["MessageType"] == "file":
            if not self.preferences["seletedFilePath"]:
                return self.controller.show_alert("Maturador de chips", "Nenhum arquivo de mensagens selecionado.")

            if not os.path.exists(self.preferences["seletedFilePath"]):
                return self.controller.show_alert("Maturador de chips", "Arquivo de mensagens não existe.")

            with open(self.preferences["seletedFilePath"], "r", encoding="utf-8") as mf:
                self.messages = mf.readlines()

            if not self.messages:
                return self.controller.show_alert("Maturador de chips", "O arquivo de mensagens está vazio.")

        if self.preferences["MessageType"] == "openai" and not self.preferences["ApiToken"]:
            return self.controller.show_alert("Maturador de chips", "Token da OpenAI não informado.")

        self.controller.home.stacked.setCurrentIndex(2)
        super().start()


    def run(self) -> None:
        limit = int(self.preferences.get("LimitMessages", 1)) + 1

        for _ in range(limit):

            connected_keys = [
                key for key, wv in self.controller.home.webviews.items()
                if wv.get("connected", False)
            ]

            if len(connected_keys) < 2:
                print("Par insuficiente.")
                return

            # escolhe quem envia

            sender_key = random.choice(connected_keys)

            # escolhe quem recebe

            receiver_candidates = [k for k in connected_keys if k != sender_key]
            receiver_key = random.choice(receiver_candidates)

            # chave única independente da direção

            base_pair = tuple(sorted([sender_key, receiver_key]))

            if base_pair not in self.conversation_histories:
                self.conversation_histories[base_pair] = []

            history = self.conversation_histories[base_pair]

            # Primeira mensagem daquele par → envia apenas uma vez

            if len(history) == 0:
                first_message = "Olá, tudo bem?"
                history.append({
                    "author": sender_key,
                    "content": first_message
                })
                print(f"{sender_key} → {first_message}")
                continue

            # openAI responde automaticamente se a ÚLTIMA mensagem foi do receiver

            last_author = history[-1]["author"]

            # se o inverso caiu → responder automaticamente

            if last_author == receiver_key and self.preferences["MessageType"] == "openai":
                messages = self.build_messages_for_openai(history, responder_key=sender_key)

                final_message = self.generate_openai_message(
                    self.preferences["ApiToken"],
                    messages
                )

                history.append({
                    "author": sender_key,
                    "content": final_message
                })

                print(f"{sender_key} (IA) → {final_message}")
                continue

            #  Caso normal: mensagem do sender, sem IA responder agora

            if self.preferences["MessageType"] == "file":
                final_message = random.choice(self.messages).strip()
            else:
                # openAI gerando mensagem normal (não resposta)

                messages = self.build_messages_for_openai(history, responder_key=sender_key)
                final_message = self.generate_openai_message(
                    self.preferences["ApiToken"],
                    messages
                )

            # Falha ao gerar mensagem — ignorando envio.

            if not final_message:
                continue
            
            history.append({
                "author": sender_key,
                "content": final_message
            })

            print(f"{sender_key} → {final_message}")

    
    def verify_have_account_blocked():
        pass
    
    def build_messages_for_openai(self, history, responder_key):
        """Formatando mensagens para formato aceito pela API"""
        messages = [
            {
                "role": "system",
                "content": "Você está simulando uma conversa natural entre duas pessoas."
            }
        ]

        # cria lista de mensagens anteriores

        for entry in history:
            role = "assistant" if entry["author"] == responder_key else "user"
            messages.append({"role": role, "content": entry["content"]})

        return messages

    def generate_openai_message(self, api_key, messages):
        try:
            client = OpenAI(api_key=api_key)

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7
            )

            return response.choices[0].message["content"]

        except Exception as e:
            self.controller.notify("Erro OpenAI", str(e))
            return None
