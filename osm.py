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

def lerp(begin, end, time):
    return begin + time*(end-begin)

def main():
    print("Starting osm")

    # audio engine
    sd.default.samplerate = 44100
    #sd.default.device = "digital output"
    dc = DeviceController()
    #dc.setOutputDevice(10)
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

        # status bar
        #self.statusBar = tk.Label(self.bottomFrame, text="Initial load", bd=1, relief=tk.SUNKEN, anchor=tk.E)
        #self.statusBar.grid(sticky="e")

        self.editMenu = tk.Menu(self.topBar)
        self.editMenu.add_command(label="Add Input Device", command=self.addDevice)
        self.editMenu.add_command(label="Add Output Device", command=self.addOutput)
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
    def addDevice(self, audioDevice=None):
        ad = uiAudioDevice(master=self.devicesFrame, device=self.device, audioDevice=audioDevice, type="input")
        self.audioDevices.append(ad)
        ad.grid(row=0, column=len(self.audioDevices), sticky="w")
        self.positionOut()

    def addOutput(self, audioDevice=None, id=None):
        if device != None:
            ad = uiAudioDevice(master=self.devicesFrame, device=self.device, audioDevice=audioDevice, type="output")
        elif id != None:
            dev = self.device.getDevice(id)
            ad = uiAudioDevice(master=self.devicesFrame, device=self.device, audioDevice=dev, type="output")
        else:
            ad = uiAudioDevice(master=self.devicesFrame, device=self.device, type="output")
        self.outputDevices.append(ad)
        self.positionOut()

    def positionOut(self):
        pos = 1
        for outdev in self.outputDevices:
            outdev.grid(row=0, column=len(self.audioDevices) + pos)
            pos+=1

class uiAudioDevice(tk.Frame):
    def __init__(self, master=None, audioDevice=None, device=None, type="input"):
        tk.Frame.__init__(self, master, width=100, height=300)

        self.type = type

        self.volumeSize = 250
        self.prevAvg = [0, 0]
        self.currAvg = [0, 0]
        self.updateCount = 0

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
        self.leftChannel = self.volume.create_rectangle(2, 1000, 26, self.volumeSize, fill="#66ff00")
        self.rightChannel = self.volume.create_rectangle(26, 1000, 50, self.volumeSize, fill="#66ff00")

        self.volumeScale = tk.Scale(self, from_=100, to=0, orient="vertical")
        self.volumeScale.grid(row=1, column=1, sticky="w")

        # create dropdown based on type
        self.selectDeviceValue = tk.StringVar()
        self.selectDeviceValue.set("Empty")
        self.selectDevice = tk.OptionMenu(self, self.selectDeviceValue, *[str(d.id) + " " + d.name for d in self.device.deviceList if d.getType() == self.type], command=self.changeDevice)
        self.selectDevice.grid(row=2, columnspan=2, sticky="ew")

        self.toggle = tk.Button(self, text="Enable/Disable", fg="black", command=self.toggleDevice)
        self.toggle.grid(row=3, columnspan=2)
        #self.toggle.pack(fill=tk.X)

        if (self.audioDevice != None):
            self.setupDevice(self.audioDevice)

    # device needs to change
    def changeDevice(self, event):
        if self.audioDevice != None:
            self.device.disableDevice(self.audioDevice.id)
        string = self.selectDeviceValue.get()
        self.setupDevice(self.device.getDevice(int(string.split(" ")[0])))

    def setupDevice(self, dev):
        self.title.config(text=dev.name, width=20)
        if self.type == "input":
            self.device.enableDevice(dev.id)
            dev.streamCallback = self.onUpdate
        else:
            self.device.setOutputDevice(dev.id)
        self.audioDevice = dev


    def toggleDevice(self):
        self.audioDevice.active = not self.audioDevice.active

    def onUpdate(self):
        if (self.audioDevice != None):
            self.audioDevice.volume = self.volumeScale.get() * 0.01
            #avg = -self.audioDevice.getDeviceAvg() * 10
            self.updateCount += 0.3
            if (self.updateCount >= 1):
                left = []
                right = []
                for value in self.audioDevice.currRawData:
                    left.append(abs(value[0]))
                    right.append(abs(value[0]))
                self.prevAvg = self.currAvg
                self.currAvg = [(sum(left) / len(left)) * 10000, (sum(right) / len(right)) * 10000]
                self.updateCount = 0
            else:
                left = lerp(self.prevAvg[0], self.currAvg[0], self.updateCount)
                right = lerp(self.prevAvg[1], self.currAvg[1], self.updateCount)
                self.moveTowards(left, right)

    def moveTowards(self, left, right):
        #self.volume.delete(self.leftChannel)
        #self.volume.delete(self.rightChannel)
        self.volume.coords(self.leftChannel, 2, self.volumeSize - left, 26, self.volumeSize)
        self.volume.coords(self.rightChannel, 26, self.volumeSize - right, 50, self.volumeSize)

    def setDevice(self, id):
        devs = self.device.getDevice(id)
        for dev in devs:
            self.audioDevice = dev

if __name__ == "__main__":
    main()