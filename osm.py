# Open Sound Mixer
# written by John Iannandrea

import tkinter as tk
import threading
from install import *
pipimport("numpy", "numpy>=1.11.0")
pipimport("sounddevice", "sounddevice>=0.3.3")
import sounddevice as sd
from devicecontroller import *

def main():
    print("Starting osm")

    # ui
    threading.Thread(target=initUI).start()

    # audio engine
    sd.default.samplerate = 44100
    #sd.default.device = "digital output"

    dc = DeviceController(sd)

    dc.setOutputDevice(9)

    while 1:
        device = input()
        if (device):
            dc.enableDevice(int(device))

def initUI():
    # ui
    root = tk.Tk()
    app = ui(master=root)
    app.master.title("Open Sound Mixer")
    app.master.maxsize(1920, 720)
    app.mainloop()

class ui(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

    def createWidgets(self):
        self.quit = tk.Button(self, text="quit", fg="black")
        self.quit.pack(side="bottom")

if __name__ == "__main__":
    main()