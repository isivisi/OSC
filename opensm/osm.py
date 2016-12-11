# Open Sound Mixer
# written by John Iannandrea

import time
import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.font as font
import threading
# pipimport("numpy", "numpy>=1.11.0")
# pipimport("sounddevice", "sounddevice>=0.3.3")
import numpy
import math
import sounddevice as sd
from opensm.devicecontroller import *


def lerp(begin, end, time):
    return begin + time * (end - begin)

def main():
    print("Starting osm")

    numpy.set_printoptions(suppress=True)
    # audio engine
    sd.default.samplerate = 44100
    # sd.default.device = "digital output"
    dc = DeviceController()
    # dc.setOutputDevice(10)
    device = dc

    # ui
    print("Starting UI thread...")
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
    # app.master.maxsize(1920, 720)
    app.master.geometry('{}x{}'.format(720, 375))
    app.master.minsize(width=500, height=375)
    app.mainloop()


class ui(tk.Frame):
    def __init__(self, master=None, device=None):
        tk.Frame.__init__(self, master)
        self.device = device
        self.audioDevices = []
        self.outputDevices = []

        # self.pack()
        self.createFrames()
        self.createWidgets()

        # threading.Thread(target=self.statusBarUpdate).start()

    def createFrames(self):
        # canvas hack for scrollbar
        # self.leftFrame = tk.Frame(self).pack(side="left")
        # self.rightFrame = tk.Frame(self).pack(side="right", anchor="e")
        self.devicesFrame = tk.Frame(self, relief='sunken').grid(row=0)
        # self.bottomFrame = tk.Frame(self).grid(row=1)

    def resetDevices(self):
        while len(self.audioDevices) > 0:
            for uiDev in self.audioDevices:
                uiDev.close()

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
        # self.statusBar = tk.Label(self.bottomFrame, text="Initial load", bd=1, relief=tk.SUNKEN, anchor=tk.E)
        # self.statusBar.grid(sticky="e")

        self.editMenu = tk.Menu(self.topBar)
        self.editMenu.add_command(label="Add Device", command=self.addDevice)
        self.topBar.add_cascade(label="Edit", menu=self.editMenu)

        # self.quit = tk.Button(self.middleFrame, text="+", fg="black", command=self.addDevice)
        # self.quit.pack(side="right")

    def statusBarUpdate(self):
        cpu = " cpu usage: %s " % self.device.getTotalCpuLoad()
        latency = " latency: %s " % self.device.getTotalLatency()
        self.statusBar.config(text=cpu + latency)
        time.sleep(1)

    def newSetup(self):
        self.resetDevices()

    def openSetup(self):
        self.resetDevices()
        filename = filedialog.askopenfilename(filetypes=(("OSM Files", "*.osm"),("All Files", "*.*")))
        with open(filename) as f:
            for line in f:
                # DEVICE[%s % s % s % s]
                id, outid, vol, active = line.replace("DEVICE [", "").replace("]\n", "").split(' ')
                foundDevice = [dev for dev in self.device.deviceList if dev.id == int(id)]
                if len(foundDevice) > 0:
                    foundDevice = foundDevice[0] # because it always returns list
                    print("Found device from save: " + repr(foundDevice))
                    foundOutput = [out for out in self.device.outputDevices if out.id == int(outid)]
                    if len(foundOutput) > 0:
                        foundDevice.out = foundOutput[0]
                    foundDevice.volume = float(vol)
                    foundDevice.active = bool(active)
                    uid = self.addDevice(audioDevice=foundDevice)
                    #uid.setupDevice(foundDevice)
                    if foundDevice.active:
                        foundDevice.startStream()
                    uid.refresh()

    def saveSetup(self):
        f = filedialog.asksaveasfile(mode='w', defaultextension='.osm')
        if f is None:
            return

        print("Saving osm file...")
        for uiDev in self.audioDevices:
            print(str(uiDev.audioDevice))
            f.write(str(uiDev.audioDevice))
        f.close()

    def exit(self):
        quit()

    def closeDevice(self, dev):
        self.audioDevices.remove(dev)
        dev.grid_forget()
        dev.destroy()

    # adds empty audio device to ui
    def addDevice(self, audioDevice=None):
        ad = uiAudioDevice(master=self.devicesFrame, device=self.device, audioDevice=audioDevice, type="input",
                           closeCall=self.closeDevice)
        self.audioDevices.append(ad)
        ad.grid(row=0, column=len(self.audioDevices), sticky="wn")
        self.positionOut()
        return ad

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
        self.updateOutputLists()

    def positionOut(self):
        pos = 1
        for outdev in self.outputDevices:
            outdev.grid(row=0, column=len(self.audioDevices) + pos, sticky="wn")
            pos += 1

    def updateOutputLists(self):
        for uiAudio in self.audioDevices:
            uiAudio.setupOutputList()


class uiAudioDevice(tk.Frame):
    def __init__(self, master=None, audioDevice=None, device=None, type="input", closeCall=None):
        tk.Frame.__init__(self, master, width=100, height=300)
        self.closeCall = closeCall
        self.type = type

        self.volumeSize = 250
        #self.logspace = numpy.logspace(start=numpy.log10(1.0), stop=numpy.log10(self.volumeSize), num=self.volumeSize)
        self.peakCurrAvg = [0, 0]
        self.rmsCurrAvg = [0, 0]
        self.updateCount = 0
        # self.pack(side="left")
        self.audioDevice = audioDevice
        self.device = device

        self.setup()

    def setup(self):
        self.colors = {"output": "#5d8aa8", "input": "#5d8aa8"}
        self.color = self.colors[self.type]
        self.title = tk.Label(self, text=self.type, bg=self.color, height=1)
        self.title.grid(row=0, column=0, sticky="ew")
        self.closeButton = tk.Button(self, text="x", fg="black", bg=self.color, command=self.close, height=1,
                                     relief="flat", pady=0, border=1)
        self.closeButton.grid(row=0, column=1, sticky="ew")

        # visual volume stuff
        self.volume = tk.Canvas(self, width=50, height=self.volumeSize)
        self.volume.grid(row=1, column=0)
        self.volume.create_rectangle(2, 0, 26, self.volumeSize, fill="#d3d3d3")
        self.volume.create_rectangle(26, 0, 50, self.volumeSize, fill="#d3d3d3")
        self.peakLeftChannel = self.volume.create_rectangle(2, 1000, 26, self.volumeSize, fill="#66ff00")
        self.peakRightChannel = self.volume.create_rectangle(26, 1000, 50, self.volumeSize, fill="#66ff00")

        self.rmsLeftChannel = self.volume.create_rectangle(2, 1000, 26, self.volumeSize, fill="#3D9900")
        self.rmsRightChannel = self.volume.create_rectangle(26, 1000, 50, self.volumeSize, fill="#3D9900")

        self.volumeScale = tk.Scale(self, from_=100, to=0, orient="vertical", length=200, relief="sunken",
                                    sliderlength=10, showvalue=False)
        self.volumeScale.grid(row=1, column=1, sticky="w")

        # create dropdown based on type
        self.selectDeviceValue = tk.StringVar()
        self.selectDeviceValue.set("Empty")
        self.selectDevice = tk.OptionMenu(self, self.selectDeviceValue,
                                          *[str(d.id) + " " + d.name for d in self.device.deviceList if
                                            d.getType() == self.type], command=self.changeDevice)
        self.selectDevice.grid(row=2, columnspan=2, sticky="ew")
        self.selectDevice.config(width=8)

        self.toggle = tk.Button(self, text="Enable/Disable", fg="black", command=self.toggleDevice)
        self.toggle.grid(row=4, columnspan=2)
        # self.toggle.pack(fill=tk.X)

        if (self.audioDevice != None):
            self.volumeScale.set(self.audioDevice.volume * 100)
            self.setupDevice(self.audioDevice)

        self.selectOutput = None
        self.setupOutputList()

        print("Starting uiAudioDevice thread...")
        threading.Thread(target=self.updateLoop).start()

    def refresh(self):
        if self.audioDevice != None:
            self.selectDeviceValue.set([str(d.id) + " " + d.name for d in self.device.deviceList if d == self.audioDevice])
            if (self.audioDevice.out != None):
                self.setupOutputList()
                self.selectOutputValue.set("%s %s" %(self.audioDevice.out.id, self.audioDevice.out.name))

    def setupOutputList(self):
        if (self.audioDevice != None and self.type == "input"):
            if (self.selectOutput != None):
                self.selectOutput['menu'].delete(0, 'end')
                for outputDev in [str(d.id) + " " + d.name for d in self.device.outputDevices if
                                  d.hostapi == self.audioDevice.hostapi]:
                    self.selectOutput['menu'].add_command(label=outputDev,
                                                          command=tk._setit(self.selectOutputValue, outputDev))
            else:
                self.selectOutputValue = tk.StringVar()
                self.selectOutputValue.set("No Output")
                self.selectOutput = tk.OptionMenu(self, self.selectOutputValue,
                                                  *[str(d.id) + " " + d.name for d in self.device.outputDevices if
                                                    d.hostapi == self.audioDevice.hostapi], command=self.changeOutput)
                self.selectOutput.grid(row=3, columnspan=2, sticky="ew")
                self.selectOutput.config(width=8)

    # device needs to change
    def changeDevice(self, event):
        if self.audioDevice != None:
            self.audioDevice.stopStream()
        string = self.selectDeviceValue.get()
        self.setupDevice(self.device.getDevice(int(string.split(" ")[0])))
        self.setupOutputList()

    def changeOutput(self, event):
        if self.audioDevice != None:
            string = self.selectOutputValue.get()
            self.audioDevice.setOutput(self.device.getOutputDevice(int(string.split(" ")[0])))

    def setupDevice(self, dev):
        # self.title.config(text=dev.name, width=20)
        dev.streamCallback = self.onUpdate
        self.audioDevice = dev

    def toggleDevice(self):
        self.audioDevice.active = not self.audioDevice.active

    def close(self):
        if (self.audioDevice != None):
            try:
                self.audioDevice.stopStream()
            except sounddevice.PortAudioError as e:
                print("Port audio error" + str(e))
        self.closeCall(self)

    def updateLoop(self):
        snapshots = []
        currentPosition = [0, 0, 0, 0]
        while 1:
            time.sleep(0.000015)
            if self.audioDevice != None:
                #if self.peakCurrAvg > self.peakPrevAvg and self.rmsCurrAvg > self.rmsPrevAvg:
                self.updateCount += 0.5

                # take a snapshot of the audio peak and rms
                if self.updateCount >= 1:
                    snapshot = [self.peakCurrAvg[0], self.peakCurrAvg[1], self.rmsCurrAvg[0], self.rmsCurrAvg[1]]
                    snapshots.append(snapshot)
                    self.updateCount = 0

                # only 2 snapshots required to interpolate between
                if len(snapshots) > 2:
                    snapshots.pop(0)

                if len(snapshots) == 2:
                    # interpolate from snapshot1 to snapshot 2
                    peak = [lerp(snapshots[0][0], snapshots[1][0], self.updateCount),
                            lerp(snapshots[0][1], snapshots[1][1], self.updateCount)]
                    rms = [lerp(snapshots[0][2], snapshots[1][2], self.updateCount),
                            lerp(snapshots[0][3], snapshots[1][3], self.updateCount)]

                    # if any new values are larger than the current then lerp to it, else slowly drop visuals
                    if peak[0] > currentPosition[0] or peak[1] > currentPosition[1] or rms[0] > currentPosition[2] or rms[1] > currentPosition[3]:
                        currentPosition = [peak[0], peak[1], rms[0], rms[1]]
                        # actually set the position for the visuals
                        self.moveTowards(self.peakLeftChannel, self.peakRightChannel, peak[0], peak[1])
                        self.moveTowards(self.rmsLeftChannel, self.rmsRightChannel, rms[0], rms[1])
                    else:
                        # slowly lower values
                        currentPosition = [max(0, x - 0.3) for x in currentPosition]
                        currentPosition[0] -= 0.1
                        currentPosition[1] -= 0.1
                        # actually set the position for the visuals
                        self.moveTowards(self.peakLeftChannel, self.peakRightChannel, currentPosition[0], currentPosition[1])
                        self.moveTowards(self.rmsLeftChannel, self.rmsRightChannel, currentPosition[2], currentPosition[2])

    #todo move this to device
    def onUpdate(self):
        if (self.audioDevice != None):
            self.audioDevice.volume = self.volumeScale.get() * 0.01
            # avg = -self.audioDevice.getDeviceAvg() * 10
            left = []
            right = []
            rmsl = []
            rmsr = []
            #for value in self.audioDevice.currRawData:
            left.append(abs(self.audioDevice.getPeak(0)))
            right.append(abs(self.audioDevice.getPeak(1)))

            rmsl.append(abs(self.audioDevice.getRMS(0)))
            rmsr.append(abs(self.audioDevice.getRMS(1)))

            # calculate the average to interpolate to
            self.peakCurrAvg = [(sum(left) / len(left)), (sum(right) / len(right))]
            self.rmsCurrAvg = [(sum(rmsl) / len(rmsl)), (sum(rmsr) / len(rmsr))]

            # apply a range to the values so they fit
            # (maxAllowed - minAllowed) * (unscaledN - min) / (max - min) + minAllowed
            self.peakCurrAvg = [(self.volumeSize - 0) * (self.peakCurrAvg[0] - 0) / (1 - 0) + 0, (self.volumeSize - 0) * (self.peakCurrAvg[1] - 0) / (1 - 0) + 0]
            self.rmsCurrAvg = [(self.volumeSize - 0) * (self.rmsCurrAvg[0] - 0) / (1 - 0) + 0, (self.volumeSize - 0) * (self.rmsCurrAvg[1] - 0) / (1 - 0) + 0]

    def moveTowards(self, leftRect, rightRect, leftVal, rightVal):
        leftVal = int(math.ceil(leftVal))
        rightVal = int(math.ceil(rightVal))
        #print(self.logspace[max(0, leftVal-1)])
        self.volume.coords(leftRect, 2, self.volumeSize - leftVal, 26, self.volumeSize)
        self.volume.coords(rightRect, 26, self.volumeSize - rightVal, 50, self.volumeSize)

    def setDevice(self, id):
        devs = self.device.getDevice(id)
        for dev in devs:
            self.audioDevice = dev


if __name__ == "__main__":
    main()
