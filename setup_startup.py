import os
import sys
import winshell
from win32com.client import Dispatch

def create_startup_shortcut():
    # Get the startup directory
    startup_dir = winshell.startup()
    
    # Path to the main startup file (main.py)
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "main.py"))
    
    # Path to the Python executable (use pythonw.exe for no console window)
    python_exe = sys.executable.replace("python.exe", "pythonw.exe")
    if not os.path.exists(python_exe):
        python_exe = sys.executable # Fallback to python.exe if pythonw.exe is not found
    
    # Name of the shortcut
    shortcut_path = os.path.join(startup_dir, "DesktopAI.lnk")
    
    # Create the shortcut
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortcut(shortcut_path)
    shortcut.TargetPath = python_exe
    shortcut.Arguments = f'"{script_path}"'
    shortcut.WorkingDirectory = os.path.dirname(script_path)
    shortcut.Description = "Starts desktop AI automatically"
    shortcut.IconLocation = python_exe
    shortcut.save()
    
    print(f"Shortcut created at: {shortcut_path}")
    print("The AI will now start automatically when you log in.")

if __name__ == "__main__":
    create_startup_shortcut()
