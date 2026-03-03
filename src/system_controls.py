import platform
import os
import subprocess
from screen_brightness_control import set_brightness

class SystemController:
    @staticmethod
    def adjust_brightness(level: int):
        """Sets the screen brightness to a specific level (0-100)."""
        level = max(0, min(100, int(level)))
        try:
            set_brightness(level)
            return f"Brightness set to {level}%."
        except Exception as e:
            return f"Failed to set brightness: {str(e)}"
            
    @staticmethod
    def adjust_volume(level: int):
        """Sets the system volume to a specific level (0-100). Windows only."""
        if platform.system() != 'Windows':
            return "Volume control is currently only supported on Windows."
            
        level = max(0, min(100, int(level)))
        try:
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            
            devices = AudioUtilities.GetSpeakers()
            volume = devices.EndpointVolume
            
            # Unmute if it was muted
            volume.SetMute(0, None)
            
            scalar_level = level / 100.0
            volume.SetMasterVolumeLevelScalar(scalar_level, None)
            return f"Volume set to {level}%."
        except Exception as e:
            return f"Failed to set volume: {str(e)}"

    @staticmethod
    def system_power_action(action: str):
        if platform.system() != 'Windows':
            return "Power actions only supported on Windows."
        try:
            if action == 'shutdown':
                os.system("shutdown /s /t 0")
                return "Shutting down..."
            elif action == 'sleep':
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
                return "Going to sleep..."
            elif action == 'lock':
                os.system("rundll32.exe user32.dll,LockWorkStation")
                return "Locking computer..."
            else:
                return "Unknown action."
        except Exception as e:
            return f"Failed to perform {action}: {e}"

    @staticmethod
    def open_application(app_name: str):
        if platform.system() != 'Windows':
            return "Application management supported on Windows."
        try:
            # First, try to activate existing window
            ps_script = f"""
            $app = Get-Process | Where-Object {{$_.MainWindowTitle -match "{app_name}" -or $_.Name -match "{app_name}"}} | Select-Object -First 1
            if ($app) {{
                Add-Type -AssemblyName Microsoft.VisualBasic
                [Microsoft.VisualBasic.Interaction]::AppActivate($app.Id)
                Write-Output "Activated"
            }} else {{
                Start-Process "{app_name}" -ErrorAction SilentlyContinue
                Write-Output "Started"
            }}
            """
            result = subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True)
            if "Activated" in result.stdout:
                return f"Brought {app_name} to the front."
            elif "Started" in result.stdout:
                return f"Started new instance of {app_name}."
            else:
                # Fallback to start
                os.system(f"start {app_name}")
                return f"Attempted to open {app_name}."
        except Exception as e:
            return f"Failed to open {app_name}: {e}"

    @staticmethod
    def find_file(filename: str):
        if platform.system() != 'Windows':
            return "File search only supported on Windows."
        try:
            # Check user directories first for speed
            ps_script = f"Get-ChildItem -Path $env:USERPROFILE -Filter '*{filename}*' -Recurse -ErrorAction SilentlyContinue | Select-Object -First 5 FullName"
            result = subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True)
            output = result.stdout.strip()
            if output:
                return f"Found files:\n{output}"
            return f"Could not find '{filename}' in user directories."
        except Exception as e:
            return f"Failed to search for file: {e}"

    @staticmethod
    def open_windows_settings(setting_type: str):
        if platform.system() != 'Windows':
            return "Supported on Windows only."
        uris = {
            "bluetooth": "ms-settings:bluetooth",
            "nightlight": "ms-settings:nightlight",
            "energysaver": "ms-settings:batterysaver"
        }
        uri = uris.get(setting_type.lower())
        if uri:
            os.system(f"start {uri}")
            return f"Opened {setting_type} settings."
        return f"Unknown setting type: {setting_type}"
