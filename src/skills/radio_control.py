import os
import subprocess
import sys
from .system_settings import open_settings

def toggle_wifi(turn_on):
    """
    Toggles WiFi using netsh. Requires Administrator privileges usually.
    """
    state = "enabled" if turn_on else "disabled"
    # Note: Interface name "Wi-Fi" is standard but might vary ("Wireless Network Connection")
    cmd = f'netsh interface set interface "Wi-Fi" admin={state}'
    
    try:
        # Run command
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        # Check for admin error
        if "admin" in result.stderr.lower() or "elevated" in result.stderr.lower():
             return "I need Administrator privileges to toggle Wi-Fi directly. Please run 'python main.py' as Administrator."
             
        if result.returncode == 0:
            return f"Wi-Fi has been {state}."
        else:
            # Fallback for error (e.g., interface name mismatch)
            return f"Could not toggle Wi-Fi via command line. (Error: {result.stderr.strip() or 'Unknown'})"
    except Exception as e:
        return f"Error executing Wi-Fi command: {e}"

def set_state(radio_name, state_str):
    """
    Control radio states.
    """
    turn_on = 'on' in state_str.lower() or 'enable' in state_str.lower()
    
    if 'wifi' in radio_name.lower():
        # Try direct toggle for WiFi
        response = toggle_wifi(turn_on)
        # If it failed or required admin, we might want to open settings as fallback?
        # For now, let's return the response. 
        if "Could not" in response or "Error" in response:
             open_settings("wifi") # Fallback
             return f"{response} -> Opened Settings instead."
        return response

    elif 'bluetooth' in radio_name.lower():
        # Direct Bluetooth toggle is extremely hard without 'winsdk' (which failed to install).
        # We fallback to opening settings for now.
        open_settings("bluetooth")
        return f"Direct Bluetooth toggle is unavailable without the 'winsdk' library (incompatible with this Python version). Opened Bluetooth settings for you."
    
    return f"I don't know how to control {radio_name}."
