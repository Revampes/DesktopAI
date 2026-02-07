from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

def _get_volume_interface():
    """
    Helper to get the volume interface safely across pycaw versions.
    """
    devices = AudioUtilities.GetSpeakers()
    
    # Check if we have the simplified wrapper (newer pycaw)
    if hasattr(devices, 'EndpointVolume'):
        return devices.EndpointVolume
        
    # Standard raw COM object approach
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return cast(interface, POINTER(IAudioEndpointVolume))

def set_volume(level):
    """
    Sets the system master volume (0-100).
    """
    try:
        level = max(0, min(100, int(level)))
        
        volume = _get_volume_interface()
        
        # Scalar volume is 0.0 to 1.0
        scalar = level / 100.0
        volume.SetMasterVolumeLevelScalar(scalar, None)
        
        return f"Volume set to {level}%"
    except Exception as e:
        return f"Error setting volume: {e}"

def get_volume():
    try:
        volume = _get_volume_interface()
        
        current = volume.GetMasterVolumeLevelScalar()
        return f"Current volume is {int(current * 100)}%"
    except Exception as e:
        return f"Error getting volume: {e}"

def mute_volume(mute=True):
    """
    Mutes or Unmutes the system volume.
    """
    try:
        volume = _get_volume_interface()
        
        volume.SetMute(1 if mute else 0, None)
        return "Audio muted." if mute else "Audio unmuted."
    except Exception as e:
        return f"Error changing mute state: {e}"
