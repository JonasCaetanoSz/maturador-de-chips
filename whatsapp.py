from controller import Controller
from datetime import datetime
from openai import OpenAI
from PyQt6 import QtCore
import subprocess
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
        self.client = None
        self.mode = "private" 

    def prepare(self, mode="private") -> bool:
        self.mode = mode
        connected_keys = self.get_connected_keys()

        if self.mode == "private" and len(connected_keys) < 2:
            return self.controller.signals.show_alert.emit("Maturador de chips", "É necessário pelo menos 2 contas conectadas para o modo privado.")

        if self.mode == "group" and len(connected_keys) < 1:
            return self.controller.signals.show_alert.emit("Maturador de chips", "É necessário pelo menos 1 conta conectada para iniciar o modo grupos.")
        
        try:
            with open("preferences.json", "r", encoding="utf8") as f:
                self.preferences = json.load(f)
        except Exception as e:
            return self.controller.signals.show_alert.emit("Maturador de chips", f"Erro ao carregar preferências: {str(e)}")

        if self.mode == "private":
            msg_type = self.preferences.get("MessageType", "file")
            file_path = self.preferences.get("selectedFilePath", "")
            api_token = self.preferences.get("ApiToken", "")
        else:
            msg_type = self.preferences.get("MessageTypeGrp", "file")
            file_path = self.preferences.get("SelectedFilePathGrp", "")
            api_token = self.preferences.get("ApiTokenGrp", "")

        if msg_type == "file":
            if not file_path:
                return self.controller.signals.show_alert.emit("Maturador de chips", "Nenhum arquivo de mensagens selecionado.")

            if not os.path.exists(file_path):
                return self.controller.signals.show_alert.emit("Maturador de chips", "Arquivo de mensagens não existe.")

            with open(file_path, mode="r", encoding="utf-8") as mf:
                self.messages = [line.strip() for line in mf if line.strip()]

            if not self.messages:
                return self.controller.signals.show_alert.emit("Maturador de chips", "O arquivo de mensagens está vazio.")

        if msg_type == "openai":
            if not api_token:
                return self.controller.signals.show_alert.emit("Maturador de chips", "Token da OpenAI não informado na aba correspondente.")
            try:
                self.client = OpenAI(api_key=api_token, timeout=15.0)
            except Exception as e:
                return self.controller.signals.show_alert.emit("Maturador de chips", f"Erro ao iniciar cliente OpenAI: {str(e)}")

        self.controller.setMaturationRunning(True)
        self.controller.signals.change_current_stacked_index.emit(2)
        self.controller.removeMenuOnStatusPage()
        super().start()
        return True

    def get_connected_keys(self):
        return [
            key for key, wv in self.controller.home.webviews.items()
            if wv.get("connected", False)
        ]

    def safe_sleep(self, seconds: int) -> bool:
        # Checa a cada 200ms em vez de 100ms para poupar ciclos de CPU
        steps = int(seconds * 5)
        for _ in range(steps):
            if self.isInterruptionRequested():
                return False
            self.msleep(200)
        return True

    def run(self) -> None:
        if self.mode == "group":
            self.run_group_maturation()
        else:
            self.run_private_maturation()
            
        if self.preferences.get("ShutdownAfterCompletion", False):
            subprocess.run(["shutdown", "/s", "/t", "30"])

        self.controller.notify("Maturador de chips", "Maturação concluída com sucesso!")
        self.controller.signals.stop_maturation.emit()

    def run_group_maturation(self):
        limit = int(self.preferences.get("LimitMessagesGrp", 20))
        min_delay = int(self.preferences.get("MinIntervalGrp", 10)) * 60
        max_delay = int(self.preferences.get("MaxIntervalGrp", 30)) * 60
        
        targets = self.preferences.get("GroupMaturationTargets", {})
        
        if not targets:
            self.controller.signals.stop_maturation.emit()
            return self.controller.signals.show_alert.emit("Maturador", "Nenhum chip possui grupo alvo configurado nas preferências.")

        sender_index = 0
        send_stickers = self.preferences.get("SendStickersGrp", True)
        is_file_mode = self.preferences.get("MessageTypeGrp", "file") == "file"

        for _ in range(limit):
            if self.isInterruptionRequested(): return
            
            connected_keys = self.get_connected_keys()
            eligible_senders = [k for k in connected_keys if k in targets and targets[k]]
            
            if not eligible_senders:
                if not self.safe_sleep(5): return
                continue
            
            sender_key = eligible_senders[sender_index % len(eligible_senders)]
            sender_index += 1

            target_group = targets[sender_key]
            is_sticker = send_stickers and (random.random() < 0.30)
            final_message = None

            if is_sticker:
                final_message = "[👍 Emoji Aleatório]"
            else:
                if is_file_mode:
                    final_message = random.choice(self.messages)
                else:
                    messages = [{"role": "system", "content": "Crie uma mensagem muito curta, informal e natural para enviar em um grupo brasileiro no WhatsApp. Use gírias locais. Não use aspas."}]
                    final_message = self.generate_openai_message(messages)
            
            if not final_message:
                if not self.safe_sleep(random.randint(min_delay, max_delay)): return
                continue
                
            if self.isInterruptionRequested(): return

            time_str = datetime.now().strftime("%H:%M:%S")
            self.controller.signals.inject_message_row.emit({
                "sender": sender_key,
                "receiver": f"Grupo Vinculado ({sender_key})",
                "message": final_message,
                "time": time_str,
            })
            
            self.controller.signals.send_whatsapp_group_message.emit({
                "target_group": target_group,
                "sender_key": sender_key,
                "message": final_message if not is_sticker else None,
                "is_sticker": is_sticker
            })
            
            if not self.safe_sleep(random.randint(min_delay, max_delay)): return

    def run_private_maturation(self):
        limit = int(self.preferences.get("LimitMessages", 1))
        min_delay = int(self.preferences.get("MinInterval", 1))
        max_delay = int(self.preferences.get("MaxInterval", 3))
        switch_after = self.preferences.get("switchAccountAfter", 1)
        is_file_mode = self.preferences.get("MessageType", "file") == "file"

        sender_count = 0
        sender_key = None

        for _ in range(limit):
            if self.isInterruptionRequested(): return

            connected_keys = self.get_connected_keys()
            if len(connected_keys) < 2:
                self.controller.signals.stop_maturation.emit()
                return
            
            if not sender_key or sender_count >= switch_after:
                possible_senders = [k for k in connected_keys if k != sender_key]
                sender_key = random.choice(possible_senders) if possible_senders else random.choice(connected_keys)
                sender_count = 0

            receiver_candidates = []
            for k in connected_keys:
                if k == sender_key: continue
                pair = tuple(sorted([sender_key, k]))
                history = self.conversation_histories.get(pair, [])
                if not history or history[-1]["author"] != sender_key:
                    receiver_candidates.append(k)

            if not receiver_candidates:
                possible_receivers = [k for k in connected_keys if k != sender_key]
                if possible_receivers:
                    sender_key = random.choice(possible_receivers)
                    sender_count = 0
                    receiver_candidates = [k for k in connected_keys if k != sender_key]

            if not receiver_candidates:
                if not self.safe_sleep(2): return
                continue

            receiver_key = random.choice(receiver_candidates)
            base_pair = tuple(sorted([sender_key, receiver_key]))

            if base_pair not in self.conversation_histories:
                self.conversation_histories[base_pair] = []
            
            history = self.conversation_histories[base_pair]

            # OTIMIZAÇÃO DE MEMÓRIA: Limita o histórico das últimas 20 mensagens por par
            if len(history) > 20:
                history = history[-20:]
                self.conversation_histories[base_pair] = history

            final_message = None

            if len(history) == 0:
                final_message = self.messages[0] if is_file_mode and self.messages else "Olá, tudo bem?"
            else:
                if is_file_mode:
                    final_message = random.choice(self.messages)
                else:
                    messages = self.build_messages_for_openai(history, responder_key=sender_key)
                    final_message = self.generate_openai_message(messages)

            if not final_message:
                if not self.safe_sleep(random.randint(min_delay, max_delay)): return
                continue

            if self.isInterruptionRequested(): return

            receiver_phone = self.controller.home.webviews[receiver_key]["phone"]
            history.append({"author": sender_key, "content": final_message})
            time_str = datetime.now().strftime("%H:%M:%S")
            
            self.controller.signals.inject_message_row.emit({
                "sender": sender_key,
                "receiver": receiver_key,
                "message": final_message,
                "time": time_str,
            })
            
            self.controller.signals.send_whatsapp_text_message.emit({
                "final_message": final_message, 
                "receiver_phone": receiver_phone, 
                "sender_key": sender_key
            })
            
            sender_count += 1
            if not self.safe_sleep(random.randint(min_delay, max_delay)): return

    def build_messages_for_openai(self, history, responder_key):
        messages = [
            {
                "role": "system",
                "content": "Você está simulando uma conversa extremamente natural, informal e dinâmica via WhatsApp entre duas pessoas conhecidas do Brasil. Use gírias leves, abreviações comuns (como vc, tbm, q) e responda de forma curta."
            }
        ]
        for entry in history:
            role = "assistant" if entry["author"] == responder_key else "user"
            messages.append({"role": role, "content": entry["content"]})
        return messages

    def generate_openai_message(self, messages):
        if not self.client: return None
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.8
            )
            return response.choices[0].message.content
        except Exception as e:
            self.controller.notify("Erro OpenAI", str(e))
            return None
    
    def stop(self):
        self.requestInterruption()
        self.wait()