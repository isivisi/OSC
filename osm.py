# Open Sound Mixer
# written by John Iannandrea

import time
import tkinter as tk
import threading
from install import *
pipimport("numpy", "numpy>=1.11.0")
pipimport("sounddevice", "sounddevice>=0.3.3")
import sounddevice as sd
from devicecontroller import *

def main():
    print("Starting osm")

    # audio engine
    sd.default.samplerate = 44100
    #sd.default.device = "digital output"
    dc = DeviceController()
    dc.setOutputDevice(10)
    device = dc

    # ui
    threading.Thread(target=initUI, args=(dc,)).start()

    while 1:
        device = input()
        if (device):
            dc.enableDevice(int(device))

def initUI(dc):
    # ui
    root = tk.Tk()
    app = ui(master=root, device=dc)
    app.master.title("Open Sound Mixer")
    #app.master.maxsize(1920, 720)
    app.master.geometry('{}x{}'.format(1080, 375))
    app.master.minsize(width=1080, height=375)
    app.mainloop()

class ui(tk.Frame):
    def __init__(self, master=None, device=None):
        tk.Frame.__init__(self, master)
        self.device = device
        self.audioDevices = []
        self.outputDevices = []

        #self.pack()
        self.createFrames()
        self.createWidgets()

        #threading.Thread(target=self.statusBarUpdate).start()

    def createFrames(self):
        # canvas hack for scrollbar
        #self.leftFrame = tk.Frame(self).pack(side="left")
        #self.rightFrame = tk.Frame(self).pack(side="right", anchor="e")
        self.devicesFrame = tk.Frame(self, relief='sunken').grid(row=0)
        #self.bottomFrame = tk.Frame(self).grid(row=1)

    def createWidgets(self):

        # top bar
        self.topBar = tk.Menu(self)
        self.master.config(menu=self.topBar)
        self.fileMenu = tk.Menu(self.topBar)
        self.fileMenu.add_command(label="New Setup...", command=self.newSetup)
        self.fileMenu.add_command(label="Open", command=self.openSetup)
        self.fileMenu.add_command(label="Save", command=self.saveSetup)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Exit", command=self.quit)
        self.topBar.add_cascade(label="File", menu=self.fileMenu)

        # output
        self.addOutput(self.device.outputDevice)

        # status bar
        #self.statusBar = tk.Label(self.bottomFrame, text="Initial load", bd=1, relief=tk.SUNKEN, anchor=tk.E)
        #self.statusBar.grid(sticky="e")

        self.editMenu = tk.Menu(self.topBar)
        self.editMenu.add_command(label="Add Device", command=self.addDevice)
        self.topBar.add_cascade(label="Edit", menu=self.editMenu)

        #self.quit = tk.Button(self.middleFrame, text="+", fg="black", command=self.addDevice)
        #self.quit.pack(side="right")

    def statusBarUpdate(self):
        cpu = " cpu usage: %s " % self.device.getTotalCpuLoad()
        latency = " latency: %s " % self.device.getTotalLatency()
        self.statusBar.config(text=cpu + latency)
        time.sleep(1)

    def newSetup(self):
        print("new project")

    def openSetup(self):
        print("open project")

    def saveSetup(self):
        print("save project")

    def exit(self):
        quit()

    # adds empty audio device to ui
    def addDevice(self):
        ad = uiAudioDevice(master=self.devicesFrame, device=self.device)
        self.audioDevices.append(ad)
        ad.grid(row=0, column=len(self.audioDevices), sticky="w")
        self.positionOut()

    def addOutput(self, device):
        ad = uiAudioDevice(master=self.devicesFrame, device=self.device, audioDevice=device)
        self.outputDevices.append(ad)
        self.positionOut()

    def positionOut(self):
        pos = 1
        for outdev in self.outputDevices:
            outdev.grid(row=0, column=len(self.audioDevices) + pos)
            pos+=1

class uiAudioDevice(tk.Frame):
    def __init__(self, master=None, audioDevice=None, device=None):
        tk.Frame.__init__(self, master, width=100, height=300)

        self.volumeSize = 250

        #self.pack(side="left")
        self.audioDevice = audioDevice
        self.device = device

        self.setup()

    def setup(self):

        self.title = tk.Label(self, text="Empty device")
        self.title.grid(row=0)
        #self.title.pack(side="left")

        # visual volume stuff
        self.volume = tk.Canvas(self, width=50, height=self.volumeSize)
        self.volume.grid(row=1, column=0)
        self.volume.create_rectangle(2, 0, 26, self.volumeSize, fill="#d3d3d3")
        self.volume.create_rectangle(26, 0, 50, self.volumeSize, fill="#d3d3d3")
        self.leftChannel = self.volume.create_rectangle(2, 200, 26, self.volumeSize, fill="#66ff00")
        self.rightChannel = self.volume.create_rectangle(26, 200, 50, self.volumeSize, fill="#66ff00")

        self.volumeScale = tk.Scale(self, from_=100, to=0, orient="vertical")
        self.volumeScale.grid(row=1, column=1, sticky="w")
        threading.Thread(target=self.getVolume).start()

        self.selectDevice = tk.OptionMenu(self, "Empty", tuple(self.device.deviceList))
        self.selectDevice.grid(row=2, columnspan=2, sticky="ew")

        self.toggle = tk.Button(self, text="Enable/Disable", fg="black", command=self.toggleDevice)
        self.toggle.grid(row=3, columnspan=2)
        #self.toggle.pack(fill=tk.X)

        if (self.audioDevice != None):
            self.title.config(text=self.audioDevice.name)

    def toggleDevice(self):
        self.audioDevice.active = not self.audioDevice.active

    def getVolume(self):
        if (self.audioDevice != None and self.audioDevice.getType() != "output"):
            self.audioDevice.volume = self.volumeScale.get() * 0.01
            avg = self.audioDevice.getDeviceAvg()
            self.leftChannel = self.volume.create_rectangle(avg + 2, avg, 26, self.volumeSize, fill="#66ff00")
            self.rightChannel = self.volume.create_rectangle(avg + 26, avg, 50, self.volumeSize, fill="#66ff00")

    def setDevice(self, id):
        devs = self.device.getDevice(id)
        for dev in devs:
            self.audioDevice = dev

if __name__ == "__main__":
    main()