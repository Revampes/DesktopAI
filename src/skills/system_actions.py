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
            os.system("shutdown /a")
            return "Shutdown aborted."
        else:
            # Shutdown in 60 seconds to give time to abort
            os.system("shutdown /s /t 60")
            return "PC will shutdown in 60 seconds. Say 'abort shutdown' to cancel."
    except Exception as e:
        return f"Error executing shutdown: {e}"

def restart_pc():
    try:
         os.system("shutdown /r /t 60")
         return "PC will restart in 60 seconds. Say 'abort' to cancel."
    except Exception as e:
        return f"Error executing restart: {e}"

def sleep_pc():
    try:
        # Hibernation off required for S3 sleep usually, but this triggers default suspend
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        return "Putting computer to sleep..."
    except Exception as e:
        return f"Error executing sleep: {e}"
