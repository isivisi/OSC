import sounddevice
import threading
import audioop

duration = 5  # seconds


class device:
    def __init__(self, deviceInfo, id):
        self.active = True
        self.volume = 1;

        self.streaming = False

        self.id = id
        self.name = deviceInfo['name'];
        self.hostapi = deviceInfo['hostapi']
        self.maxInputChannels = deviceInfo['max_input_channels']
        self.maxOutputChannels = deviceInfo['max_output_channels']
        self.defaultLowOutputLatency = deviceInfo['default_low_output_latency']
        self.defaultHighOutputLatency = deviceInfo['default_high_output_latency']
        self.defaultLowInputLatency = deviceInfo['default_low_input_latency']
        self.defaultHighInputLatency = deviceInfo['default_high_input_latency']
        self.defaultSamplerate = deviceInfo['default_samplerate']

        self.rawStream = sounddevice.RawStream()
        self.currRawData = []

        self.out = None  # will be output stream

        self.streamCallback = None  # function to be called during stream

    # audio callback
    def callback(self, indata, outdata, frames, time, status):
        if self.active:
            outdata[:] = indata * self.volume;
        else:
            outdata.fill(0)

        self.currRawData = outdata

        # if status:
        #    print("[%s] frames: %s, status: %s, time: %s, status: %s" %(self.name, frames, time, status))

        if (self.streamCallback != 0):
            self.streamCallback()

    # get average of waveform at current time
    def getDeviceAvg(self):
        try:
            return audioop.avg(self.currRawData, 1)
        except:
            return -100

    def stream(self):
        try:
            if (self.out != None):
                sounddevice.default.channels = self.out.maxOutputChannels
                self.rawStream = sounddevice.Stream(device=(self.id, self.out.id), samplerate=self.defaultSamplerate,
                                                    channels=(self.maxInputChannels, self.out.maxOutputChannels),
                                                    callback=self.callback, latency="low")
                self.rawStream.start()
                self.streaming = True
                print("starting %s stream for output: %s" % (self.name, self.out.name,))
            else:
                print("Cannot start device stream, no output set")
        except sounddevice.PortAudioError as e:
            print("Port audio error for (" + self.name + ") " + str(e))

    # start a sounddevice stream in a new thread (this might not be needed anymore)
    def startStream(self):
        threading.Thread(target=self.stream).start()

    def stopStream(self):
        self.rawStream.stop()
        self.streaming = False

    def setOutput(self, out):
        if self.streaming:
            self.stopStream()
        self.out = out
        self.startStream()

    def getType(self):
        if (self.maxOutputChannels > 0):
            return "output"
        else:
            return "input"


# A controller for all devices
class DeviceController:
    def __init__(self):

        self.deviceList = []

        self.outputDevices = []

        self.initDevices()

    def initDevices(self):
        id = 0
        for dev in sounddevice.query_devices():
            print(str(id) + " " + str(dev))
            d = device(dev, id)
            if d.getType() == "input":
                self.deviceList.append(d)
            else:
                self.outputDevices.append(d)
            id += 1

    '''
    def enableDevice(self, id):
        devList = [d for d in self.deviceList if d.id == id and d.getType() == "input"]
        for dev in devList:
            print(dev.name + "device enabled")
            if (dev not in self.activeDevices):
                self.activeDevices.append(dev)
            dev.startStream()

    def disableDevice(self, id):
        devList = [d for d in self.activeDevices if d.id == id]
        for dev in devList:
            dev.stopStream()
            self.activeDevices.remove(dev)
            print(dev.name + "disabled")
    '''

    def getDevice(self, id):
        dlist = [d for d in self.deviceList if d.id == id]
        for dev in dlist:
            return dev

    def getOutputDevice(self, id):
        dlist = [d for d in self.outputDevices if d.id == id]
        for dev in dlist:
            return dev

    '''
    def addOutputDevice(self, id):
        devList = [d for d in self.deviceList if d.id == id and d.getType() == "output"]
        if (devList):
            print(devList[0].name + " output added")
            self.outputDevices.append(devList[0])
        else:
            print("[error] id " + str(id) + " not found, output device not added")
    '''

    def getTotalCpuLoad(self):
        totalCpu = 0
        for dev in self.activeDevices:
            if dev.active:
                totalCpu += dev.rawStream.cpu_load
        return totalCpu

    # TODO average instead of additive
    def getTotalLatency(self):
        totalLat = 0
        for dev in self.activeDevices:
            if dev.active:
                totalLat += dev.rawStream.latency()
        return totalLat
