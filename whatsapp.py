from controller import Controller
from openai import OpenAI
from PyQt5 import QtCore
import random
import json
import os
import time

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
            return self.controller.show_alert(
                "Maturador de chips",
                "É necessário pelo menos 2 contas conectadas para iniciar."
            )

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

    def verify_have_account_blocked(self):
        stop_if_disconnected = not self.preferences.get("ContinueIfDisconnected", False)

        for key, webview in self.controller.home.webviews.items():
            if not webview.get("connected", False):
                if stop_if_disconnected:
                    self.signals.account_blocked.emit({"key": key})
                    return True
        return False

    def get_connected_keys(self):
        return [
            key for key, wv in self.controller.home.webviews.items()
            if wv.get("connected", False)
        ]

    def run(self) -> None:
        limit = int(self.preferences.get("LimitMessages", 1)) + 1

        min_delay = int(self.preferences.get("MinInterval", 1))
        max_delay = int(self.preferences.get("MaxInterval", 3))

        for _ in range(limit):

            if self.verify_have_account_blocked():
                return

            connected_keys = self.get_connected_keys()

            if len(connected_keys) < 2:
                print("Par insuficiente.")
                return

            sender_key = random.choice(connected_keys)

            receiver_candidates = [k for k in connected_keys if k != sender_key]
            receiver_key = random.choice(receiver_candidates)

            base_pair = tuple(sorted([sender_key, receiver_key]))

            if base_pair not in self.conversation_histories:
                self.conversation_histories[base_pair] = []

            history = self.conversation_histories[base_pair]

            if len(history) == 0:
                first_message = "Olá, tudo bem?"
                history.append({
                    "author": sender_key,
                    "content": first_message
                })
                print(f"{sender_key} → {first_message}")
                time.sleep(random.randint(min_delay, max_delay))
                continue

            last_author = history[-1]["author"]

            if last_author == receiver_key and self.preferences["MessageType"] == "openai":
                messages = self.build_messages_for_openai(history, responder_key=sender_key)
                final_message = self.generate_openai_message(self.preferences["ApiToken"], messages)
                history.append({"author": sender_key, "content": final_message})
                print(f"{sender_key} (IA) → {final_message}")
                time.sleep(random.randint(min_delay, max_delay))
                continue

            if self.preferences["MessageType"] == "file":
                final_message = random.choice(self.messages).strip()
            else:
                messages = self.build_messages_for_openai(history, responder_key=sender_key)
                final_message = self.generate_openai_message(self.preferences["ApiToken"], messages)

            if not final_message:
                continue

            history.append({"author": sender_key, "content": final_message})
            print(f"{sender_key} → {final_message}")

            time.sleep(random.randint(min_delay, max_delay))

    def build_messages_for_openai(self, history, responder_key):
        messages = [
            {
                "role": "system",
                "content": "Você está simulando uma conversa natural entre duas pessoas."
            }
        ]

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
