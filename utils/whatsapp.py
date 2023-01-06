
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tkinter import messagebox, filedialog
import os
from pathlib import Path
from random import randint
import time
import shutil
from subprocess import CREATE_NO_WINDOW


class Whatssap:

    def __init__(self, window, configs) -> None:

        self.window = window
        self.runding = False
        self.accounts = []
        self.chat_base = ""
        self.accounts_driver = []
        self.configs = configs
        self.log_entry = None
        # buscar contas adicionadas

        for cookie in os.listdir("utils/sessions"): self.accounts.append(cookie)

    def add_acconut(self, apelido:object,account_text:int, canvas:object):

        apelido = apelido.get()

        if apelido.isspace() or apelido == "":

            messagebox.showerror("erro ao adiconar conta" , "o apelido da conta não pode estar vazio.")
        
        elif apelido in self.accounts:

             messagebox.showerror("erro ao adiconar conta" , "já existe uma conta com esse apelido, por favor escolha outro.")

        else:

            options = webdriver.ChromeOptions()
            options.add_argument(f"--user-data-dir={Path(__file__).parent}/sessions/{apelido}")
            options.add_argument("--lang=pt-BR")
            service = ChromeService(ChromeDriverManager().install())
            service.creation_flags = CREATE_NO_WINDOW
            driver = webdriver.Chrome(service=service  , options=options)
            driver.get("https://web.whatsapp.com/")
            try:

                wait = WebDriverWait(driver, 600)
                wait.until(EC.visibility_of_element_located((By.ID, "pane-side")))
                driver.quit()
                self.accounts.append(apelido)
                canvas.itemconfig(account_text, text=f"total de contas: {len(self.accounts)}")
                messagebox.showinfo("nova conta adicionada", f"a conta {apelido} foi adicionada com sucesso!")
            
            except Exception as e:

                messagebox.showerror("login não realizado" , "você deve adiconar a nova conta em até 10 minutos.")
                driver.quit()
                print(e)
                shutil.move(f"{os.getcwd()}/utils/sessions/{apelido}", f"{Path(__file__).parent}/session-delete/{apelido}")
    
    def remove_account(self, apelido:object, account_text:int, canvas:object):

        apelido = apelido.get()

        if apelido in self.accounts:

            self.accounts.remove(apelido)
        
            shutil.move(f"{os.getcwd()}/utils/sessions/{apelido}", f"{Path(__file__).parent}/session-delete/{apelido}")
            messagebox.showinfo("conta removida com sucesso", f"a conta {apelido} foi removida com sucesso!")
            canvas.itemconfig(account_text, text=f"total de contas: {len(self.accounts)}")
        else:

            messagebox.showerror("erro ao remover conta", f"o perfil {apelido} não foi adicionado ou já foi removido.")
    
    def maturation(self, log_entry):

        if len(self.chat_base) == 0:

            messagebox.showerror("arquivo invalido" , "o arquivo base para conversas é invalido ou não foi adicionado.")
        
        elif len(self.accounts) < 2:

            messagebox.showerror("numero de contas insuficiente", "você precisa adicionar ao menos 2 contas para iniciar a maturação.")
        
        elif self.runding:

            messagebox.showerror("impossivel iniciar maturação", "uma instancia para maturação já foi iniciada, você precisa para ela para iniciar uma nova.")
        
        else:
            
            self.runding = True
            self.log_entry = log_entry
            for apelido in self.accounts:

                options = webdriver.ChromeOptions()
                options.add_argument(f"--user-data-dir={Path(__file__).parent}/sessions/{apelido}")
                options.add_argument("--lang=pt-BR")
                #options.add_argument("--headless")
                service = ChromeService(ChromeDriverManager().install())
                service.creation_flags = CREATE_NO_WINDOW
                driver = webdriver.Chrome(service=service, options=options)
                driver.get("https://web.whatsapp.com/")
                self.accounts_driver.append({"driver":driver, "apelido":apelido})
                
            count = 0
            while self.runding:

                if int(self.configs["max_message"]) == count: self.runding = False

                while True:

                    index_receive = randint(0, len(self.accounts_driver) - 1)
                    index_send =  randint(0, len(self.accounts_driver) - 1)
                    if index_send != index_receive: break

                try:
                    message = self.chat_base[randint(0,len(self.chat_base) - 1)]
                    account_send = self.accounts_driver[index_send]
                    account_receive = self.accounts_driver[index_receive]
                    url = f"https://web.whatsapp.com/send/?phone={account_receive['apelido']}&text={message}"
                    account_send["driver"].get(url)
                    # Espera até que o botão de envio de mensagens apareça na página
                    send_button = WebDriverWait(account_send['driver'], 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-icon='send']")))
                    # espera de 3 a 6 segundos para enviar a mensagem
                    time.sleep(randint(3,6))
                    # Clica no botão de envio de mensagens
                    send_button.click()
                    self.writelog(f"{account_send['apelido']}\t{account_receive['apelido']} {message}")
                    count += 1
                
                except Exception as e: print(e)
                time.sleep(int(self.configs["interval_message"]))
            
            messagebox.showinfo("maturação concluida!" , "a maturação acabou, você pode fechar o programa e as abas do navegador agora.")


    def add_base_chat(self):

        file_base_path = filedialog.askopenfilename(title="arquivo base para conversa")
        if file_base_path == "" or file_base_path == None:

            pass

        elif not ".txt" in str(file_base_path):

            messagebox.showerror("arquivo invalido", "o arquivo escolhido não é um arquivo de texto.")
        
        else:
            
            with open(file_base_path , "r" , encoding="utf-8") as f: self.chat_base = f.readlines()
    
    def SetRunding(self):

        if self.runding: 

            self.runding = False
            for i in self.accounts_driver:

                i["driver"].quit()
                self.accounts_driver.remove(i)
                messagebox.showinfo("instancia encerrada" , "o programa foi parado com sucesso!")

        else:

            messagebox.showerror("não é possivel parar", "o programa não foi iniciado.")


    def writelog(self,message:str):

        try:
            self.log_entry.configure(state="normal")
            self.log_entry.insert("end", f"{message}\n")
            self.log_entry.see("end")
            self.log_entry.configure(state="disabled")
        except: pass