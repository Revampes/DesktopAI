import os
import subprocess
import re

def set_power_mode(mode):
    """
    Switches power plan. 
    Mode can be 'saver', 'balanced', 'high'.
    """
    mode = mode.lower()
    
    # Common GUIDs for Windows Power Plans
    # These are standard but can vary per machine, so parsing is better usually.
    # However, aliases often work: scheme_max, scheme_min, scheme_balanced
    
    if 'saver' in mode or 'battery' in mode:
        cmd = "powercfg /setactive scheme_min"
        target = "Power Saver"
    elif 'high' in mode or 'performance' in mode:
        cmd = "powercfg /setactive scheme_max"
        target = "High Performance"
    else:
        cmd = "powercfg /setactive scheme_balanced"
        target = "Balanced"
        
    try:
        # Running the command
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return f"Switched power mode to {target}."
        else:
            return f"Failed to switch power mode. (Error code: {result.returncode})"
    except Exception as e:
        return f"Error executing power command: {e}"

def open_settings(setting_name):
    """
    Opens Windows Settings pages using URI schemes.
    """
    uris = {
        "bluetooth": "ms-settings:bluetooth",
        "wifi": "ms-settings:network-wifi",
        "network": "ms-settings:network-status",
        "display": "ms-settings:display",
        "sound": "ms-settings:sound",
        "notifications": "ms-settings:notifications",
        "battery": "ms-settings:batterysaver",
        "power": "ms-settings:powersleep",
        "nightlight": "ms-settings:nightlight"
    }
    
    uri = uris.get(setting_name.lower())
    if uri:
        try:
            os.system(f"start {uri}")
            return f"Opened {setting_name} settings."
        except Exception as e:
            return f"Failed to open settings: {e}"
    return f"I don't know the settings page for '{setting_name}'."


def toggle_night_light(action=None):
    """
    Attempts to toggle Night light. Direct programmatic toggling requires
    manipulating a Windows registry blob and is not reliable across versions.
    This helper opens the Night light settings page where the user can toggle it,
    and returns an explanatory message. If `action` is provided ('on'/'off'),
    the function will still open the settings page because a safe automated
    toggle is not implemented.
    """
    try:
        os.system("start ms-settings:nightlight")
        if action:
            return "Opened Night light settings. Automatic toggle not supported; please use the switch in Settings."
        return "Opened Night light settings. You can toggle Night light there."
    except Exception as e:
        return f"Failed to open Night light settings: {e}"
