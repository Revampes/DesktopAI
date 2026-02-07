from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

try:
    print("Getting speakers...")
    devices = AudioUtilities.GetSpeakers()
    print(f"Devices type: {type(devices)}")
    print(f"Devices dir: {dir(devices)}")
    
    print("Activating...")
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    print("Activated.")
except Exception as e:
    print(f"Error: {e}")
