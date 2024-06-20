import os
import tkinter as tk
import tkinter.font as font
from tkinter import messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinterdnd2 import DND_FILES, TkinterDnD
from backend import *
import threading 


def load_new_content(path):
    new_label = tb.Label(main_frame, text=f"Path submitted: {path}", bootstyle="success")
    new_label.pack(pady=20)


class App(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ascot Aumoated Loss Runs Entry ")
        self.geometry('500x350')
        self.title_font = font.Font(family='Helvetica', size=18, weight="bold", slant="italic")
        self.iconbitmap('front_end/images/ascot.ico')
        
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        for F in (StartPage, ProcessPage, WarningPage, CompletePage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame("StartPage")

    def show_frame(self, page_name, *args):
        frame = self.frames[page_name]
        if hasattr(frame, 'on_show'):
            frame.on_show(*args)
        frame.tkraise()

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.pack(expand=True, fill='both', padx=20, pady=20)

        welcome_label = tb.Label(self, text="Welcome to the Ascot automated loss runs entry system!", bootstyle="primary")
        welcome_label.pack(pady=(20, 10))
        
        instruction_label = tb.Label(self, text="Drag and drop your submission file here:", bootstyle="info")
        instruction_label.pack(pady=(10, 10))
        
        drop_area = tb.Frame(self, bootstyle="secondary", width=300, height=300)
        drop_area.pack(pady=20, padx=50)
        drop_area.drop_target_register(DND_FILES)
        drop_area.dnd_bind('<<Drop>>', self.on_drop)

    def on_drop(self, event):
        # paths = event.data.split()
        # print(f'paths is {paths}')

        
        paths = event.data.splitlines()
        print("Dropped paths:", paths)  # Debugging print

        pdf_files = [path for path in paths if path.lower().endswith('.pdf')]

        for path in paths:
            path = path.strip("{}")  # Remove any surrounding braces
        if os.path.isfile(path):
            print(f"{path} is a valid file.")  # Debugging print
            if path.lower().endswith('.pdf'):
                print(f"{path} is a PDF file.")  # Debugging print
                pdf_files.append(path)
            else:
                print(f"{path} is not a PDF file.")  # Debugging print
        else:
            print(f"{path} is not a valid file.")  # Debugging print
        
        # TODO: if it's a valid file and the file extension is .pdf then it is valid
        if not pdf_files:
            messagebox.showerror("Error", "Please drop a valid pdf file.")
            self.controller.show_frame("WarningPage")
        else:
            self.controller.show_frame("ProcessPage", pdf_files[0])
            

# Process page will be shown when the file is valid
class ProcessPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        # self.controller = controller
        # label = tk.Label(self, text=f"Processing your input...", font=self.controller.title_font)
        # label.pack(side="top", fill="x", pady=10)
        # button = tk.Button(self, text="Back to Start", command=lambda: self.controller.show_frame("StartPage"))
        # button.pack()
        self.controller = controller
        label = tk.Label(self, text="Operation Complete", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="New File", command=lambda: controller.show_frame("StartPage"))
        button.pack()

    def on_show(self, file_path):
        self.controller.show_frame("CompletePage", file_path)

        
class WarningPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        label = tk.Label(self, text="Warning: Invalid File Type", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Try Again", command=lambda: controller.show_frame("StartPage"))
        button.pack()


class CompletePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        label = tk.Label(self, text="Operation Complete", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="New File", command=lambda: controller.show_frame("StartPage"))
        button.pack()

    def on_show(self, file_path):

        # Start processing 
        print(f"Starting backend processing for file at {file_path}")
        start_backend(file_path)

        # Simulate processing time and then show the Complete page
        # self.after_idle(lambda: self.controller.show_frame("CompletePage"))

def run():
    app = App()
    app.mainloop()


run()

