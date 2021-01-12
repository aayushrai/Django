import os
import sys
import tkinter as tk
import numpy as np
LARGE_FONT = ("Verdana", 12)


class mainApp(tk.Tk):


    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.attributes('-zoomed', True) 
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        # self.state("zoomed")
        self.frames = {}

        frame = StartPage(container, self)

        for F in (StartPage,Details):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Server status", font=LARGE_FONT)
        label.pack(pady=50, padx=10)

        cam_frame = tk.Frame(self)
        lbl = tk.Label(cam_frame, text="Click to start all flask servers!!!!!")
        lbl.pack(pady=50, padx=10)
        btn = tk.Button(cam_frame, text="Click Me",command=lambda: controller.show_frame(Details))
        btn.pack(side="left",padx=10)
        cam_frame.pack(side="left")
        
    # def clicked(self):
    #     # if not click:
    #     lbl.configure(text="Starting Server*******")
    #     os.system("sh runner.sh")
    #     lbl.configure(text="Server Started********")

class Details(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Server Details", font=LARGE_FONT)
        label.pack(pady=90,padx=10)
        
        serverStatus = tk.Frame(self, width=20, height=20)
        master = tk.Button(serverStatus, text="Master",height=4,width=4,bg="red")
        master.pack(side="left", padx=10)
        master = tk.Button(serverStatus, text="Workers",height=4,width=4,bg="red")
        master.pack(side="left", padx=10)
        master = tk.Button(serverStatus, text="Slaves",height=4,width=4,bg="red")
        master.pack(side="left", padx=10)
        master = tk.Button(serverStatus, text="Online",height=4,width=4,bg="red")
        master.pack(side="left", padx=10)
        serverStatus.pack(side="left",padx=10,pady=10,anchor="nw")

        

    
app = mainApp()
app.mainloop()