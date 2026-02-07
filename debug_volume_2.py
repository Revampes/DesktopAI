from pycaw.pycaw import AudioUtilities

try:
    print("Getting speakers...")
    devices = AudioUtilities.GetSpeakers()
    
    # Try using the EndpointVolume property directly if it exists
    if hasattr(devices, 'EndpointVolume'):
        print("Found EndpointVolume property.")
        print(f"Type: {type(devices.EndpointVolume)}")
        # Let's see if we can use it directly
        vol = devices.EndpointVolume
        print(f"Current volume scalar: {vol.GetMasterVolumeLevelScalar()}")
        
except Exception as e:
    print(f"Error: {e}")
