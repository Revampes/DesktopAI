import winreg

def set_theme(mode):
    """
    Sets Windows theme to 'dark' or 'light'.
    mode: 'dark' or 'light'
    """
    try:
        if mode not in ['dark', 'light']:
            return "Invalid theme mode. Use 'dark' or 'light'."

        value = 0 if mode == 'dark' else 1
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        
        # Open the registry key
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        
        # Set both Apps and System theme
        winreg.SetValueEx(key, "AppsUseLightTheme", 0, winreg.REG_DWORD, value)
        winreg.SetValueEx(key, "SystemUsesLightTheme", 0, winreg.REG_DWORD, value)
        
        winreg.CloseKey(key)
        
        return f"Theme set to {mode} mode. (You might need to restart some apps to see the effect)"
    except Exception as e:
        return f"Error setting theme: {e}"
