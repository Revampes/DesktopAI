"""Tool executor for handling AI function calls."""
from src.system_controls import SystemController


class ToolExecutor:
    """Executes tool functions called by the AI agent."""
    
    def __init__(self, db_manager, play_song_callback=None, calendar_callback=None):
        """Initialize the tool executor.
        
        Args:
            db_manager: Database manager instance
            play_song_callback: Callback function for playing songs
            calendar_callback: Callback function for calendar updates
        """
        self.db = db_manager
        self.play_song_cb = play_song_callback
        self.calendar_cb = calendar_callback
    
    def execute(self, function_name: str, function_args: dict) -> str:
        """Execute a tool function.
        
        Args:
            function_name: Name of the function to execute
            function_args: Arguments for the function
            
        Returns:
            Result message from the function execution
        """
        if function_name == "adjust_brightness":
            return SystemController.adjust_brightness(function_args.get("level", 50))
        
        elif function_name == "adjust_volume":
            return SystemController.adjust_volume(function_args.get("level", 50))
        
        elif function_name == "system_power_action":
            return SystemController.system_power_action(function_args.get("action"))
        
        elif function_name == "open_application":
            return SystemController.open_application(function_args.get("app_name"))
        
        elif function_name == "find_file":
            return SystemController.find_file(function_args.get("filename"))
        
        elif function_name == "open_windows_settings":
            return SystemController.open_windows_settings(function_args.get("setting_type"))
        
        elif function_name == "add_schedule":
            title = function_args.get("title")
            date_str = function_args.get("date_str")
            time_str = function_args.get("time_str")
            notify = function_args.get("notify", 0)
            
            success = self.db.add_schedule(title, date_str, time_str, notify)
            if success:
                if self.calendar_cb:
                    self.calendar_cb()
                return f"Schedule '{title}' successfully added for {date_str} at {time_str}."
            else:
                return f"Failed to add schedule."
        
        elif function_name == "play_music":
            song_name = function_args.get("song_name")
            file_path = self.db.find_song_by_name(song_name)
            
            if file_path:
                if self.play_song_cb:
                    self.play_song_cb(file_path)
                return f"Playing {song_name} from the library."
            else:
                return f"Song '{song_name}' could not be found in the local library."
        
        else:
            return f"Unknown function: {function_name}"
