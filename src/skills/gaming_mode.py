from . import system_settings
from . import app_launcher
from . import volume_control

class GamingModeSkill:
    def __init__(self, engine_ref=None):
        self.engine = engine_ref
        
    def enable_gaming_mode(self):
        actions_taken = []
        
        # 1. High Performance Power Plan
        system_settings.set_power_mode("high")
        actions_taken.append("Power Plan set to High Performance")
        
        # 2. Check Running Apps
        running_apps = app_launcher.get_running_apps()
        
        # Filter for typical distractions
        distractions = [app for app in running_apps if any(x in app.lower() for x in ["chrome", "discord", "playlist", "spotify", "browser"])]
        
        # 3. Increase Brightness (example: 100)
        # In a real app, this value should be from settings
        # We can implement a simple settings getter in system_settings later
        from . import system_control
        system_control.set_brightness(100)
        actions_taken.append("Brightness set to 100%")
        
        response = "Gaming Mode Enabled:\n" + "\n".join(f"- {a}" for a in actions_taken)
        
        if distractions:
            response += "\n\nPerformance Warning: The following apps might impact performance:\n"
            response += "\n".join(f"- {d}" for d in distractions)
            response += "\n\nType 'close [app name]' to terminate them."
            
        return response
