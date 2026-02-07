from AppOpener import open as open_app
import os
import ctypes
from ctypes import windll, create_unicode_buffer, c_bool, c_int, POINTER
import time

def focus_window_by_name(name):
    """
    Finds a window containing `name` in its title and brings it to foreground.
    """
    found_hwnds = []
    
    def enum_windows_callback(hwnd, lParam):
        length = windll.user32.GetWindowTextLengthW(hwnd)
        if length > 0:
            buff = create_unicode_buffer(length + 1)
            windll.user32.GetWindowTextW(hwnd, buff, length + 1)
            title = buff.value
            
            # Use 'in' match, simple fuzzy
            if windll.user32.IsWindowVisible(hwnd) and name.lower() in title.lower():
                found_hwnds.append(hwnd)
                return False # Stop if found (finds first/topmost z-order match)
        return True

    EnumWindowsProc = ctypes.WINFUNCTYPE(c_bool, c_int, POINTER(c_int))
    windll.user32.EnumWindows(EnumWindowsProc(enum_windows_callback), 0)
    
    if found_hwnds:
        hwnd = found_hwnds[0]
        # Restore if minimized
        if windll.user32.IsIconic(hwnd):
             windll.user32.ShowWindow(hwnd, 9) # SW_RESTORE
        
        # Bring to foreground
        try:
            windll.user32.SetForegroundWindow(hwnd)
        except:
            pass
        return True
    return False

def launch_application(app_name):
    """
    Attempts to open an application by name and bring it to front.
    """
    try:
        # AppOpener is quite fuzzy, which is good for "open chrome"
        print(f"Attempting to open: {app_name}")
        open_app(app_name, match_closest=True, output=False) 
        
        # Try to focus it (give it a moment to spawn/register window)
        # Note: If app was already open, AppOpener might just focus it, but let's Ensure it.
        # We search for the window title matching the command roughly
        time.sleep(1.0) 
        focus_window_by_name(app_name)
        
        return f"Opening {app_name}..."
    except Exception as e:
        return f"Failed to open {app_name}: {e}"

def close_application(app_name):
    """
    Attempts to close an application by name (SIGTERM).
    """
    try:
        # AppOpener supports close based on match_closest=True
        print(f"Attempting to close: {app_name}")
        from AppOpener import close as close_app
        close_app(app_name, match_closest=True, output=False)
        return f"Closed {app_name}."
    except Exception as e:
        return f"Failed to close {app_name}: {e}"

def get_running_apps():
    """
    Returns a list of visible window titles/apps that are likely user applications.
    Excludes system processes and itself.
    This is a heuristic approach using EnumWindows.
    """
    apps = []
    
    def enum_windows_callback(hwnd, lParam):
        if not windll.user32.IsWindowVisible(hwnd):
            return True
        
        length = windll.user32.GetWindowTextLengthW(hwnd)
        if length > 0:
            buff = create_unicode_buffer(length + 1)
            windll.user32.GetWindowTextW(hwnd, buff, length + 1)
            title = buff.value
            
            # Simple filters to remove garbage
            # You might want to filter out 'Program Manager', 'Settings', etc.
            skip_list = ["Program Manager", "Windows Input Experience", "DesktopAI", "Settings", "Microsoft Text Input Application"]
            
            if title and title not in skip_list:
                apps.append(title)
        return True

    EnumWindowsProc = ctypes.WINFUNCTYPE(c_bool, c_int, POINTER(c_int))
    windll.user32.EnumWindows(EnumWindowsProc(enum_windows_callback), 0)
    
    return apps
