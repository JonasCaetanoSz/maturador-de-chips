from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, messagebox, END
from pathlib import Path
import os
import json
from utils.whatsapp import Whatssap
from threading import Thread
import subprocess
class Gui:

    def __init__(self) -> None:

        self.window = Tk()
        self.OUTPUT_PATH = Path(__file__).parent
        self.ASSETS_PATH = os.getcwd() + "/assets"
        with open("utils/configs.json", "r") as f: self.configurations = json.loads(f.read())
        self.dark_mode = self.configurations["dark_mode"]
        self.window.iconbitmap(self.relative_to_assets("icon.ico"))
        self.whatssap = Whatssap(self.window, self.configurations)
        self.version = "1.3.1"

    def relative_to_assets(self,path: str) -> Path:
        return self.ASSETS_PATH / Path(path)

    def start(self):

        self.window.geometry("691x433")
        self.window.configure(bg = "#FFFFFF")

        canvas = Canvas(
            self.window,
            bg = self.theme(),
            height = 433,
            width = 691,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )

        canvas.place(x = 0, y = 0)
        canvas.create_rectangle(
            0.0,
            1.0,
            146.0,
            434.0,
            fill="#201D1D",
            outline="")

        button_image_1 = PhotoImage(
            file=self.relative_to_assets("button_1.png"))
        button_1 = Button(
            image=button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.configs(),
            relief="flat",
            cursor="hand2"
        )
        button_1.place(
            x=0.0,
            y=207.0,
            width=146.0,
            height=38.0
        )

        button_image_2 = PhotoImage(
            file=self.relative_to_assets("button_2.png"))
        button_2 = Button(
            image=button_image_2,
            borderwidth=0,
            highlightthickness=0,
            relief="flat",
            cursor="hand2"
        )
        button_2.place(
            x=0.0,
            y=73.0,
            width=146.0,
            height=38.0
        )

        canvas.create_text(
            58.0,
            15.0,
            anchor="nw",
            text="MENU",
            fill="#FFFFFF",
            font=("Inter", 12 * -1)
        )

        canvas.create_rectangle(
            -1.0,
            41.0,
            146.0,
            42.0,
            fill="#74D589",
            outline="")

        button_image_3 = PhotoImage(
            file=self.relative_to_assets("button_3.png"))
        button_3 = Button(
            image=button_image_3,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.add_account(),
            relief="flat",
            cursor="hand2"
        )
        button_3.place(
            x=0.0,
            y=140.0,
            width=146.0,
            height=38.0
        )

        canvas.create_text(
            17.0,
            402.0,
            anchor="nw",
            text=f"build version: {self.version}",
            fill="#FFFFFF",
            font=("Inter", 12 * -1)
        )

        canvas.create_rectangle(
            192.0,
            77.0,
            652.0,
            100.72727394104004,
            fill="#24312A",
            outline="")

        canvas.create_text(
            205.10882568359375,
            80.51515197753906,
            anchor="nw",
            text="de:",
            fill="#FFFFFF",
            font=("Inter", 12 * -1)
        )

        canvas.create_text(
            326.0,
            80.0,
            anchor="nw",
            text="para:",
            fill="#FFFFFF",
            font=("Inter", 12 * -1)
        )

        canvas.create_rectangle(
            315.32122802734375,
            75.51515197753906,
            316.32122802734375,
            102.00000190734863,
            fill="#DFEEFF",
            outline="")

        canvas.create_rectangle(
            471.05181884765625,
            76.8787841796875,
            472.05181884765625,
            101.60605812072754,
            fill="#DFEEFF",
            outline="")

        canvas.create_text(
            479.20208740234375,
            82.2727279663086,
            anchor="nw",
            text="mensagem:",
            fill="#FFFFFF",
            font=("Inter", 12 * -1)
        )

        button_image_4 = PhotoImage(
            file=self.relative_to_assets("button_4.png"))
        button_4 = Button(
            image=button_image_4,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.whatssap.add_base_chat(),
            relief="flat",
            cursor="hand2"
        )
        button_4.place(
            x=224.0,
            y=373.0,
            width=132.0,
            height=32.0
        )

        button_image_5 = PhotoImage(
            file=self.relative_to_assets("button_5.png"))
        button_5 = Button(
            image=button_image_5,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.whatssap.SetRunding(),
            relief="flat",
            cursor="hand2"
        )
        button_5.place(
            x=548.0,
            y=373.0,
            width=60.0,
            height=32.0
        )

        button_image_6 = PhotoImage(
            file=self.relative_to_assets("button_6.png"))
        button_6 = Button(
            image=button_image_6,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: Thread(target=self.whatssap.maturation , args=(entry_1,)).start(),
            relief="flat",
            cursor="hand2"
        )
        button_6.place(
            x=472.0,
            y=373.0,
            width=55.0,
            height=32.0
        )

        button_image_7 = PhotoImage(
            file=self.relative_to_assets("button_7.png"))
        button_7 = Button(
            image=button_image_7,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.clear_log(entry_1),
            relief="flat",
            cursor="hand2"
        )
        button_7.place(
            x=383.0,
            y=373.0,
            width=58.1363525390625,
            height=32.0
        )

        entry_image_1 = PhotoImage(
            file=self.relative_to_assets("entry_1.png"))
        entry_bg_1 = canvas.create_image(
            422.0,
            233.5,
            image=entry_image_1
        )
        entry_1 = Text(
            bd=0,
            bg="#D1CAE0",
            fg="#000716",
            highlightthickness=0,
            state="disabled",
            font=("Inter", 14 * -1)
        )
        entry_1.place(
            x=192.0,
            y=118.0,
            width=460.0,
            height=229.0
        )

        self.whatssap.log_entry = entry_1
        self.window.resizable(False, False)
        self.window.title("maturator de chips - iniciar")
        self.window.mainloop()
    
    def configs(self, darked=False):

        self.window.geometry("529x433")
        self.window.configure(bg = "#FFFFFF")
        canvas = Canvas(
            self.window,
            bg = self.theme(),
            height = 433,
            width = 529,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )

        canvas.place(x = 0, y = 0)
        canvas.create_rectangle(
            0.0,
            1.0,
            146.0,
            434.0,
            fill="#201D1D",
            outline="")

        button_image_1 = PhotoImage(
            file=self.relative_to_assets("button_1.png"))
        button_1 = Button(
            image=button_image_1,
            borderwidth=0,
            highlightthickness=0,
            relief="flat",
            cursor="hand2"
        )
        button_1.place(
            x=0.0,
            y=207.0,
            width=146.0,
            height=38.0
        )

        button_image_2 = PhotoImage(
            file=self.relative_to_assets("button_2.png"))
        button_2 = Button(
            image=button_image_2,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.start(),
            relief="flat"
        )
        button_2.place(
            x=0.0,
            y=73.0,
            width=146.0,
            height=38.0
        )

        canvas.create_text(
            58.0,
            15.0,
            anchor="nw",
            text="MENU",
            fill="#FFFFFF",
            font=("Inter", 12 * -1)
        )

        canvas.create_rectangle(
            -1.0,
            41.0,
            146.0,
            42.0,
            fill="#74D589",
            outline="")

        button_image_3 = PhotoImage(
            file=self.relative_to_assets("button_3.png"))
        button_3 = Button(
            image=button_image_3,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.add_account(),
            relief="flat",
            cursor="hand2"
        )
        button_3.place(
            x=0.0,
            y=140.0,
            width=146.0,
            height=38.0
        )

        canvas.create_text(
            17.0,
            402.0,
            anchor="nw",
            text=f"build version: {self.version}",
            fill="#FFFFFF",
            font=("Inter", 12 * -1)
        )

        canvas.create_text(
            294.0,
            33.0,
            anchor="nw",
            text="configurações",
            fill=self.theme(is_label=True),
            font=("Inter", 15 * -1)
        )

        canvas.create_text(
            311.0,
            129.0,
            anchor="nw",
            text="interface:",
            fill= self.theme(is_label=True, is_green=True),
            font=("Inter", 13 * -1)
        )

        canvas.create_text(
            286.0,
            212.0,
            anchor="nw",
            text="intervalo e quantidade:",
            fill= self.theme(is_label=True, is_green=True),
            font=("Inter", 13 * -1)
        )

        canvas.create_rectangle(
            256.0,
            150.0,
            430.9998779296875,
            152.0042266845703,
            fill="#020000",
            outline="")

        canvas.create_rectangle(
            256.0,
            235.0,
            432.0,
            236.03114318847656,
            fill="#020000",
            outline="")

        if darked or self.dark_mode: button_image_4 = PhotoImage(file=self.relative_to_assets("button_12.png"))
        else: button_image_4 = PhotoImage(file=self.relative_to_assets("button_8.png"))
        button_4 = Button(
            image=button_image_4,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.SetTheme(),
            relief="flat",
            cursor="hand2"
        )
        button_4.place(
            x=305.0,
            y=169.0,
            width=99.0,
            height=26.0
        )

        #
        entry_image_1 = PhotoImage(
            file=self.relative_to_assets("entry_2.png"))
        entry_bg_1 = canvas.create_image(
            371.0,
            276.0,
            image=entry_image_1
        )
        entry_1 = Entry(
            bd=0,
            bg="#D9D9D9",
            fg="#000716",
            highlightthickness=0
        )
        entry_1.place(
            x=341.0,
            y=265.0,
            width=60.0,
            height=20.0
        )

        entry_image_2 = PhotoImage(
            file=self.relative_to_assets("entry_3.png"))
        entry_bg_2 = canvas.create_image(
            371.0,
            312.0,
            image=entry_image_2
        )
        entry_2 = Entry(
            bd=0,
            bg="#D9D9D9",
            fg="#000716",
            highlightthickness=0
        )
        entry_2.place(
            x=341.0,
            y=301.0,
            width=60.0,
            height=20.0
        )
        # set values default
        entry_1.insert(0, self.configurations["max_message"])
        entry_2.insert(0,self.configurations["interval_message"])
        canvas.create_text(
            276.0,
            265.0,
            anchor="nw",
            text="max:",
            fill=self.theme(is_label=True),
            font=("Inter", 13 * -1)
        )

        canvas.create_text(
            276.0,
            310.0,
            anchor="nw",
            text="intervalo:",
            fill=self.theme(is_label=True),
            font=("Inter", 13 * -1)
        )

        button_image_5 = PhotoImage(
            file=self.relative_to_assets("button_9.png"))
        button_5 = Button(
            image=button_image_5,
            borderwidth=0,
            highlightthickness=0,
            command=lambda:self.save_configuration(entry_1, entry_2),
            relief="flat",
            cursor="hand2"
        )
        button_5.place(
            x=275.0,
            y=382.0,
            width=123.0,
            height=31.0
        )
        self.window.resizable(False, False)
        self.window.title("maturator de chips - configurações")
        self.window.mainloop()

    def add_account(self):

        self.window.geometry("500x433")
        self.window.configure(bg = "#FFFFFF")


        canvas = Canvas(
            self.window,
            bg = self.theme(),
            height = 433,
            width = 500,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )

        canvas.place(x = 0, y = 0)
        canvas.create_rectangle(
            0.0,
            1.0,
            146.0,
            434.0,
            fill="#201D1D",
            outline="")

        button_image_1 = PhotoImage(
            file=self.relative_to_assets("button_1.png"))
        button_1 = Button(
            image=button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.configs(),
            relief="flat",
            cursor="hand2"
        )
        button_1.place(
            x=0.0,
            y=207.0,
            width=146.0,
            height=38.0
        )

        button_image_2 = PhotoImage(
            file=self.relative_to_assets("button_2.png"))
        button_2 = Button(
            image=button_image_2,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.start(),
            relief="flat",
            cursor="hand2"
        )
        button_2.place(
            x=0.0,
            y=73.0,
            width=146.0,
            height=38.0
        )

        canvas.create_text(
            58.0,
            15.0,
            anchor="nw",
            text="MENU",
            fill="#FFFFFF",
            font=("Inter", 12 * -1)
        )

        canvas.create_rectangle(
            -1.0,
            41.0,
            146.0,
            42.0,
            fill="#74D589",
            outline="")

        button_image_3 = PhotoImage(
            file=self.relative_to_assets("button_3.png"))
        button_3 = Button(
            image=button_image_3,
            borderwidth=0,
            highlightthickness=0,
            relief="flat",
            cursor="hand2"
        )
        button_3.place(
            x=0.0,
            y=140.0,
            width=146.0,
            height=38.0
        )

        canvas.create_text(
            17.0,
            402.0,
            anchor="nw",
            text=f"build version: {self.version}",
            fill="#FFFFFF",
            font=("Inter", 12 * -1)
        )

        canvas.create_text(
            264.0,
            32.0,
            anchor="nw",
            text="gerenciar contas",
            fill=self.theme(is_label=True),
            font=("Inter", 15 * -1)
        )

        canvas.create_text(
            295.0,
            111.0,
            anchor="nw",
            text="adicionar:",
            fill=self.theme(is_label=True, is_green=True),
            font=("Inter", 15 * -1)
        )

        canvas.create_rectangle(
            263.0,
            139.0,
            401.0,
            140.0,
            fill="#6B805E",
            outline="")

        entry_image_1 = PhotoImage(
            file=self.relative_to_assets("entry_4.png"))
        entry_bg_1 = canvas.create_image(
            404.0,
            185.0,
            image=entry_image_1
        )
        entry_1 = Entry(
            bd=0,
            bg="#D9D9D9",
            fg="#000716",
            highlightthickness=0
        )
        entry_1.place(
            x=363.0,
            y=175.0,
            width=82.0,
            height=18.0
        )

        canvas.create_text(
            264.0,
            178.0,
            anchor="nw",
            text="apelido da conta:",
            fill=self.theme(is_label=True),
            font=("Inter", 11 * -1)
        )

        button_image_4 = PhotoImage(
            file=self.relative_to_assets("button_10.png"))
        button_4 = Button(
            image=button_image_4,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: Thread(target=self.whatssap.add_acconut , args=(entry_1, accounts_text, canvas)).start(),
            relief="flat",
            cursor="hand2"
        )
        button_4.place(
            x=277.0,
            y=218.0,
            width=127.0,
            height=27.0
        )

        canvas.create_text(
            295.0,
            280.0,
            anchor="nw",
            text="remover:",
            fill=self.theme(is_label=True, is_green=True),
            font=("Inter", 15 * -1)
        )

        canvas.create_rectangle(
            263.0,
            305.0,
            401.0,
            306.0,
            fill="#6B805E",
            outline="")

        canvas.create_text(
            264.0,
            331.0,
            anchor="nw",
            text="apelido da conta:",
            fill=self.theme(is_label=True),
            font=("Inter", 11 * -1)
        )

        entry_image_2 = PhotoImage(
            file=self.relative_to_assets("entry_5.png"))
        entry_bg_2 = canvas.create_image(
            404.0,
            338.0,
            image=entry_image_2
        )
        entry_2 = Entry(
            bd=0,
            bg="#D9D9D9",
            fg="#000716",
            highlightthickness=0
        )
        entry_2.place(
            x=363.0,
            y=328.0,
            width=82.0,
            height=18.0
        )

        button_image_5 = PhotoImage(
            file=self.relative_to_assets("button_11.png"))
        button_5 = Button(
            image=button_image_5,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.whatssap.remove_account(entry_2, accounts_text, canvas),
            relief="flat",
            cursor="hand2"
        )
        button_5.place(
            x=277.0,
            y=375.0,
            width=127.0,
            height=27.0
        )

        accounts_text = canvas.create_text(
            154.0,
            6.0,
            anchor="nw",
            text=f"total de contas: {len(self.whatssap.accounts)}",
            fill=self.theme(is_label=True),
            font=("Inter", 11 * -1)
            
        )
        self.window.resizable(False, False)
        self.window.title("maturator de chips - gerenciar contas")
        self.window.mainloop()

    def theme(self, is_label=False, is_green=False):

        if is_label:

            if self.dark_mode:  return "#FFFFFF"

            else:

                if is_green: return "#6B805E"
                else: return "#000000"

        else:

            if self.dark_mode: return "#1E1D24" ##394649
            else: return "#FFFFFF"

        
        
    def SetTheme(self):

        if self.dark_mode:

            self.dark_mode = False
            self.configs(darked=False)
            self.configurations["dark_mode"] = False
        else:

            self.dark_mode = True
            self.configs(darked=True)
            self.configurations["dark_mode"] = True
        
        with open("utils/configs.json", "w") as f:
            json.dump(self.configurations, f)
    
    def save_configuration(self, max:object, interval:object):

        if  max.get().isnumeric()  and interval.get().isnumeric() :


            new_max = int(max.get())
            new_interval = int(interval.get())

            if new_interval != int(self.configurations["interval_message"]) or new_max != int(self.configurations["max_message"]):

                self.configurations["interval_message"] = new_interval
                self.configurations["max_message"] = new_max
                with open("utils/configs.json", "w") as f: json.dump(self.configurations, f)
                messagebox.showinfo("configurações atualizada", "suas alterações foram salvas com sucesso!")

        else: messagebox.showerror("alterações invalidas", "as alterações não podem ser salvas, verfique os dados informados.")

            
    def clear_log(self, entry:Text):

        entry.configure(state="normal")
        entry.delete(1.0, END)
        entry.configure(state="disabled")


# instalar o webdriver do chrome
# só é necessario se o --noconsole for ativado no pyinstaller
#subprocess.run("installWebDriver.exe") 
Gui().start()