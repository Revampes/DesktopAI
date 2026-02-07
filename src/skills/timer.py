import threading
import time
import re
from plyer import notification
from datetime import timedelta

class TimerSkill:
    def __init__(self):
        self.active_timers = []

    def set_timer(self, user_input):
        # Parse inputs like:
        # "set timer for 10 minutes"
        # "timer 5 min"
        # "set alarm for 30 seconds"
        
        seconds = 0
        
        # Regex for components
        hours_match = re.search(r'(\d+)\s*(?:hour|hr)', user_input)
        minutes_match = re.search(r'(\d+)\s*(?:minute|min)', user_input)
        seconds_match = re.search(r'(\d+)\s*(?:second|sec)', user_input)
        
        if hours_match: seconds += int(hours_match.group(1)) * 3600
        if minutes_match: seconds += int(minutes_match.group(1)) * 60
        if seconds_match: seconds += int(seconds_match.group(1))
        
        if seconds == 0:
            return "I couldn't understand the duration. Try 'set timer for 5 minutes'."
        
        # Start thread
        thread = threading.Thread(target=self._run_timer, args=(seconds,))
        thread.daemon = True
        thread.start()
        
        duration_str = str(timedelta(seconds=seconds))
        return f"Timer set for {duration_str}."

    def _run_timer(self, duration):
        time.sleep(duration)
        self._notify_user()

    def _notify_user(self):
        # Sound?
        try:
            # Simple beep 3 times
            import winsound
            winsound.Beep(1000, 500)
            winsound.Beep(1000, 500)
            winsound.Beep(1000, 500)
        except:
            pass
            
        try:
            notification.notify(
                title='DesktopAI Timer',
                message='Your timer has finished!',
                app_name='DesktopAI',
                timeout=10
            )
        except Exception as e:
            print(f"Notification failed: {e}")
