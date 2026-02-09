import os
import ctypes
import subprocess

def lock_screen():
    try:
        ctypes.windll.user32.LockWorkStation()
        return "Screen locked."
    except Exception as e:
        return f"Error locking screen: {e}"

def shutdown_pc(abort=False):
    try:
        if abort:
            subprocess.Popen(["shutdown", "/a"], creationflags=subprocess.CREATE_NO_WINDOW)
            return "Shutdown aborted."
        else:
            # Shutdown in 60 seconds to give time to abort
            subprocess.Popen(["shutdown", "/s", "/t", "60"], creationflags=subprocess.CREATE_NO_WINDOW)
            return "PC will shutdown in 60 seconds. Say 'abort shutdown' to cancel."
    except Exception as e:
        return f"Error executing shutdown: {e}"

def restart_pc():
    try:
         subprocess.Popen(["shutdown", "/r", "/t", "60"], creationflags=subprocess.CREATE_NO_WINDOW)
         return "PC will restart in 60 seconds. Say 'abort' to cancel."
    except Exception as e:
        return f"Error executing restart: {e}"

def sleep_pc():
    try:
        # Hibernation off required for S3 sleep usually, but this triggers default suspend
        subprocess.Popen(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], creationflags=subprocess.CREATE_NO_WINDOW)
        return "Putting computer to sleep..."
    except Exception as e:
        return f"Error executing sleep: {e}"
