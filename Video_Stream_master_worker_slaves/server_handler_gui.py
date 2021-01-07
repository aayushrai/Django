import os
import sys


# if __name__ == "__main__":
#     os.system("sh runner.sh")


from tkinter import *

window = Tk()

window.title("Server")

window.geometry('350x200')
lbl = Label(window, text="Click to start all flask servers!!!!!")

lbl.grid(column=0, row=0)

def clicked():
    # if not click:
    lbl.configure(text="Starting Server*******")
    os.system("sh runner.sh")
    lbl.configure(text="Server Started********")
    click = True

btn = Button(window, text="Click Me", command=clicked)

btn.grid(column=1, row=0)

window.mainloop()
