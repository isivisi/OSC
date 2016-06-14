# Open Sound Mixer
# written by John Iannandrea

from install import *
pipimport("numpy", "numpy>=1.11.0")
pipimport("sounddevice", "sounddevice>=0.3.3")
import sounddevice as sd
from devicecontroller import *

def main():
    print("Starting osm")

    #sd.default.samplerate = 44100
    #sd.default.device = "digital output"

    dc = DeviceController(sd)

    dc.setOutputDevice(9)

    while 1:
        device = input()
        if (device):
            dc.enableDevice(int(device))


if __name__ == "__main__":
    main()