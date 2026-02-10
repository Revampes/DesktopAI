import re
from .skills import system_control
from .skills import app_launcher
from .skills import volume_control
from .skills import system_settings
from .skills import radio_control
from .skills import theme_control
from .skills import system_actions
from .skills import web_skills
from .skills import weather_skill
from .skills import music_player
from .skills import translator
from .skills import gaming_mode
from .skills import timer
from .simple_nlp import SimpleIntentClassifier

class AIEngine:
    def __init__(self, productivity_manager=None):
        self.name = "DesktopAI"
        self.music = music_player.MusicSkill()
        self.productivity = productivity_manager
        self.translator = translator.TranslatorSkill()
        self.gaming_mode = gaming_mode.GamingModeSkill(self)
        self.timer = timer.TimerSkill()
        self.nlp = SimpleIntentClassifier()

    def set_music_mode(self, mode):
        return self.music.set_mode(mode)
    
    def set_productivity_manager(self, manager):
        self.productivity = manager

    def process_input(self, user_input):
        user_input = user_input.strip() # Keep case for some parts, but lower for logic usually
        lower_input = user_input.lower()
        
        # Rule -1: Productivity (Tasks/Notes/Calendar Events)
        if self.productivity:
            # Match: "Add event...", "Schedule...", "Deadline..." or "Project X due..."
            # Use user_input (original case) instead of lower_input for the regex text capture
            
            # Common prefixes
            prefix_pattern = r'(?:add event|schedule|remind me to|deadline for|add deadline|set deadline)(?:\s+of)?\s+(.+)'
            suffix_pattern = r'(.+) due (.+)'
            
            prefix_match = re.search(prefix_pattern, user_input, re.IGNORECASE)
            suffix_match = re.search(suffix_pattern, user_input, re.IGNORECASE)

            if prefix_match or suffix_match:
                raw_text = ""
                is_deadline = False
                
                if prefix_match:
                    raw_text = prefix_match.group(1)
                    if "deadline" in prefix_match.group(0).lower(): is_deadline = True
                elif suffix_match:
                    # reconstructing so date parser finds the date part
                    raw_text = suffix_match.group(1) + " " + suffix_match.group(2) 
                    is_deadline = True
                
                # --- Parsing Logic ---
                from datetime import datetime, timedelta
                title = raw_text
                date_val = datetime.now().strftime("%Y-%m-%d")
                start_time = None
                end_time = None
                
                # 1. Extract Date
                if re.search(r'\btomorrow\b', raw_text, re.IGNORECASE):
                    date_val = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
                    title = re.sub(r'\btomorrow\b', '', title, flags=re.IGNORECASE)
                elif re.search(r'\btoday\b', raw_text, re.IGNORECASE):
                    date_val = datetime.now().strftime("%Y-%m-%d")
                    title = re.sub(r'\btoday\b', '', title, flags=re.IGNORECASE)
                # Next [Day] logic could be added here
                
                # 2. Extract Timerange "at 2pm to 3pm" or "from 14:00 to 15:00"
                # Pattern: at XX(:XX)?(am/pm)? (to|until|-) XX(:XX)?(am/pm)?
                time_range = re.search(r'(?:at|from)\s+(\d{1,2}(?::\d{2})?(?:am|pm)?)\s+(?:to|until|-)\s+(\d{1,2}(?::\d{2})?(?:am|pm)?)', raw_text, re.IGNORECASE)
                
                if time_range:
                    start_time = time_range.group(1)
                    end_time = time_range.group(2)
                    # Clean title
                    title = title.replace(time_range.group(0), "")
                else:
                    # Single time "at 5pm"
                    single_time = re.search(r'(?:at|by)\s+(\d{1,2}(?::\d{2})?(?:am|pm)?)', raw_text, re.IGNORECASE)
                    if single_time:
                        start_time = single_time.group(1)
                        title = title.replace(single_time.group(0), "")

                # Clean Title Logic
                # 1. Remove common prepositions at the start ONLY if they make sense to remove
                title = title.strip()
                # If command was "Schedule OF [Course]", the 'of' is already consumed by prefix_pattern if present
                # But just in case:
                title = re.sub(r'^(?:for|on|at|about)\s+', '', title, flags=re.IGNORECASE)
                
                # 2. Remove "on" at the end if it was cut off weirdly, but use word boundary or just strip whitespace
                title = title.strip()
                
                category = "Deadline" if is_deadline else "Event"
                
                if start_time:
                    # It's an event with time
                    self.productivity.add_task(title, date_val, start_time, end_time, reminder=True, category=category)
                    return f"Scheduled {category.lower()}: '{title}' on {date_val} at {start_time}" + (f"-{end_time}" if end_time else "")
                else:
                    # Just a task
                    self.productivity.add_task(title, date_val, category=category)
                    return f"Added {category.lower()}: {title} for {date_val}"
            
            # "Take note: meeting at 5" or "Note this: ..."
            note_match = re.search(r'(?:take note|note this|save note)(?::| that)? (.+)', lower_input, re.IGNORECASE)
            if note_match:
                content = note_match.group(1).strip()
                current = self.productivity.get_scratchpad()
                new_content = current + "\n" + content if current else content
                self.productivity.save_scratchpad(new_content)
                return "Note saved to scratchpad."

        # Rule 0: Music Commands (m!add, m!play, m!loop, m!end)
        if lower_input.startswith("m!"):
            cmd_parts = user_input.split(" ", 1)
            command = cmd_parts[0].lower()
            arg = cmd_parts[1] if len(cmd_parts) > 1 else ""

            if command == "m!add":
                if not arg: return "Please provide a track name or link."
                if arg.startswith("#") and arg[1:].isdigit():
                    idx = int(arg[1:])
                    hist = self.music.get_history()
                    if 1 <= idx <= len(hist):
                        item = hist[idx-1]
                        return self.music.add_to_queue(item['title']) # Or use ID if logic permits
                return self.music.add_to_queue(arg)
            
            if command == "m!play":
                if not arg: return "Please provide a track name or link."
                # Check for history index e.g., "m!play #1"
                if arg.startswith("#") and arg[1:].isdigit():
                    return self.music.play_from_history(int(arg[1:]))
                return self.music.play_now(arg)
            
            if command == "m!history":
                return self.music.format_history()
            
            if command == "m!loop":
                return self.music.start_loop()
                
            if command == "m!end":
                return self.music.clear_queue()
                
            return "Unknown music command. Try m!add, m!play, m!loop, or m!end."

        # Rule 0.5: NLP Intent Classification
        nlp_intent, nlp_score = self.nlp.predict(lower_input)
        
        # Check for negation and safe-guards
        # Words that indicate the user does NOT want the action immediately
        negation_words = [
            "don't", "dont", "do not", "never", "no", "not", "abort", "cancel",
            "how", "what", "why", "where", "who", "when", "which", # Question words
            "ask", "about", "want" # Context/Discussion words
        ]
        is_negated = any(word in lower_input.split() for word in negation_words)

        # High confidence overrides
        if nlp_score > 0.7 and not is_negated:
            if nlp_intent == "system.shutdown":
                 return system_actions.shutdown_pc()
            elif nlp_intent == "system.restart":
                 return system_actions.restart_pc()
            elif nlp_intent == "system.lock":
                 return system_actions.lock_screen()
            elif nlp_intent == "volume.up":
                 return volume_control.set_volume("+10") # Increment logic handled by int conversion usually or we need to check set_volume impl
            elif nlp_intent == "volume.down":
                 return volume_control.set_volume("-10")
            elif nlp_intent == "app.open":
                 # Extract app name from remaining text? 
                 # Often complex w/o Named Entity Recognition (NER), fallback to regex for extraction below
                 pass 

        # Rule 1: Brightness Control
        brightness_match = re.search(r'brightness\D*(\d+)', lower_input)
        if brightness_match:
            level = brightness_match.group(1)
            return system_control.set_brightness(level)

        # Rule 2: Volume Control
        # Matches: "set volume to 50", "volume 100", "turn down volume to 20"
        volume_match = re.search(r'volume\D*(\d+)', user_input)
        if volume_match:
            level = volume_match.group(1)
            return volume_control.set_volume(level)

        if "mute" in user_input:
            if "unmute" in user_input or "stop" in user_input or "off" in user_input:
                return volume_control.mute_volume(False)
            return volume_control.mute_volume(True)

        # Rule 3: Power/Energy Modes
        if "energy saver" in user_input or "battery saver" in user_input:
             if "on" in user_input or "enable" in user_input or "activate" in user_input:
                 return system_settings.set_power_mode("saver")
             elif "off" in user_input or "disable" in user_input:
                 return system_settings.set_power_mode("balanced")
        
        if "high performance" in user_input or "game mode" in user_input:
             return system_settings.set_power_mode("high")
        
        if "balanced mode" in user_input:
             return system_settings.set_power_mode("balanced")

        # Night light handling: open settings since automated toggle is unreliable
        if "night light" in lower_input or "nightlight" in lower_input:
            # detect explicit on/off request
            if "on" in lower_input or "enable" in lower_input or "activate" in lower_input:
                return system_settings.toggle_night_light('on')
            if "off" in lower_input or "disable" in lower_input:
                return system_settings.toggle_night_light('off')
            # otherwise just open the Night light settings page
            return system_settings.toggle_night_light()

        # Rule 4: System Actions (Shutdown, Lock, Sleep, Theme)
        # Handle abort specifically
        if ("shutdown" in user_input or "restart" in user_input) and ("abort" in user_input or "cancel" in user_input):
            return system_actions.shutdown_pc(abort=True)

        # Note: Direct 'shutdown' or 'restart' string matching was removed to prevent accidental triggers.
        # These are now handled by the NLP Intent Classifier (Rule 0.5) with safer confidence thresholds.
            
        if "lock" in user_input and ("screen" in user_input or "pc" in user_input or "computer" in user_input):
             return system_actions.lock_screen()
             
        if "sleep" in user_input and ("pc" in user_input or "computer" in user_input or "mode" in user_input):
             return system_actions.sleep_pc()

        if "dark mode" in user_input or "dark theme" in user_input:
             return theme_control.set_theme("dark")
             
        if "light mode" in user_input or "light theme" in user_input:
             return theme_control.set_theme("light")

        # Rule 5: System Settings (Bluetooth, Wifi) - DIRECT TOGGLE
        # Matches: "turn on bluetooth", "turn off wifi"
        if "energy saver" in user_input or "battery saver" in user_input:
             if "on" in user_input or "enable" in user_input or "activate" in user_input:
                 return system_settings.set_power_mode("saver")
             elif "off" in user_input or "disable" in user_input:
                 return system_settings.set_power_mode("balanced")
        
        if "high performance" in user_input or "game mode" in user_input:
             return system_settings.set_power_mode("high")
        
        if "balanced mode" in user_input:
             return system_settings.set_power_mode("balanced")

        # Rule 5: System Settings (Bluetooth, Wifi) - DIRECT TOGGLE
        # Matches: "turn on bluetooth", "turn off wifi"
        if ("bluetooth" in user_input or "wifi" in user_input) and ("turn" in user_input or "switch" in user_input):
            target = "bluetooth" if "bluetooth" in user_input else "wifi"
            action = "on" if ("on" in user_input or "enable" in user_input) else "off"
            return radio_control.set_state(target, action)

        # Rule 6: Web Skills (Search, News, Weather) - NEW
        if "weather" in user_input:
            # simple extraction: "weather in London"
            city_match = re.search(r'weather\s+(?:in|for|at)?\s*([a-zA-Z\s]+)', user_input)
            if city_match:
                city = city_match.group(1).strip()
                return weather_skill.get_weather(city)
            return "Please specify a city. (e.g., 'weather in Tokyo')"

        if "news" in user_input:
            # "news about tech", "latest news"
            topic_match = re.search(r'news\s+(?:about|on|for)?\s*(.+)', user_input)
            query = topic_match.group(1) if topic_match else "latest updates"
            return web_skills.search_news(query)

        if "search" in user_input or "lookup" in user_input or "who is" in user_input or "what is" in user_input:
            # "search for python tutorials"
            # remove "search", "search for"
            query = re.sub(r'^(search|lookup|find)\s+(for\s+)?', '', user_input).strip()
            return web_skills.search_web(query)

        # Rule 7: System Settings (Fallback to opening window)
        # Matches: "open network settings", "check battery"
        settings_keywords = ["network", "display", "sound", "battery", "bluetooth", "wifi"]
        for keyword in settings_keywords:
            if keyword in user_input and ("open" in user_input or "check" in user_input or "show" in user_input):
                 return system_settings.open_settings(keyword)

        # Rule 6: Open Applications
        # Matches: "open google chrome", "launch notepad"
        open_match = re.search(r'(open|launch|start)\s+(.+)', lower_input)
        if open_match:
            app_name = open_match.group(2)
            return app_launcher.launch_application(app_name)

        # Rule 9: Close Application
        close_match = re.search(r'(close|quit|exit|terminate)\s+(.+)', lower_input)
        if close_match:
            target = close_match.group(2)
            # Avoid closing self or important things if possible (AppOpener handles match)
            if "desktopai" in target or "sidebar" in target:
                return "I cannot close myself this way. Use the quit button in settings."
            return app_launcher.close_application(target)
            
        # Rule 10: Translation
        # logic: "translate [text] to [language]"
        trans_match = re.search(r'translate (.+) to (english|chinese|mandarin|chinese simplified|chinese traditional)', lower_input, re.IGNORECASE)
        if trans_match:
            content = trans_match.group(1)
            target_lang = trans_match.group(2)
            return self.translator.translate(content, target_lang)

        # Rule 11: Gaming Mode
        if "gaming mode" in lower_input or "game mode" in lower_input:
            if "enable" in lower_input or "start" in lower_input or "on" in lower_input:
                return self.gaming_mode.enable_gaming_mode()
            elif "disable" in lower_input or "stop" in lower_input or "off" in lower_input:
                return "Gaming mode disabled. Settings restored." # Logic usually simpler for off
            elif "confirm" in lower_input and "close" in lower_input:
                 # Handling user confirmation "confirm close discord"
                 # This might need a state flow, but for now let's parse basic "close X" commands via Rule 9
                 pass

        # Rule 12: Timer
        if "timer" in lower_input or "alarm" in lower_input:
            if "set" in lower_input or "add" in lower_input or "remind" in lower_input:
                return self.timer.set_timer(lower_input)

        # Rule 13: General "Chat" (Fallback)
        return self.chat_response(lower_input)

    def chat_response(self, text):
        # Placeholder for LLM integration
        # In the future, you can connect this to OpenAI/Ollama/Gemini APIs
        responses = {
            "hello": "Hi there! How can I help you controlling your PC today?",
            "hi": "Hello! I am ready to help.",
            "who are you": "I am your Desktop Assistant.",
            "bye": "Goodbye! Have a nice day."
        }
        
        return responses.get(text, "I'm not sure how to answer that yet, but I can open apps or change settings!")
