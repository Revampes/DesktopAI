import json
from openai import OpenAI
from src.system_controls import SystemController
from src.db_manager import db

class AIAgent:
    def __init__(self, model_name="llama3.1"):
        # Configure to use local Ollama instance via OpenAI compatibility layer
        self.client = OpenAI(
            base_url="http://127.0.0.1:11434/v1",
            api_key="ollama" # api_key is required by the client but ignored by Ollama
        )
        self.model = model_name
        self.conversation_history = [
            {"role": "system", "content": "You are a helpful desktop assistant. You can control system settings like brightness and volume, manage the user's calendar, and play music from their library. Keep your answers brief and concise."}
        ]
        
        self.play_song_cb = None
        self.calendar_add_cb = None
        
    def set_callbacks(self, play_song_callback, calendar_add_callback):
        self.play_song_cb = play_song_callback
        self.calendar_add_cb = calendar_add_callback

    @property
    def tools(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "adjust_brightness",
                    "description": "Sets the screen brightness to a specific level.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "level": {
                                "type": "integer",
                                "description": "The brightness level from 0 to 100."
                            }
                        },
                        "required": ["level"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "adjust_volume",
                    "description": "Sets the system volume to a specific level.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "level": {
                                "type": "integer",
                                "description": "The volume level from 0 to 100."
                            }
                        },
                        "required": ["level"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "system_power_action",
                    "description": "Perform system power actions like shutdown, sleep, or lock computer.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["shutdown", "sleep", "lock"],
                                "description": "The power action to perform."
                            }
                        },
                        "required": ["action"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "open_application",
                    "description": "Open an application or bring it to the front.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "app_name": {
                                "type": "string",
                                "description": "The name of the application to open (e.g. 'notepad', 'calculator')."
                            }
                        },
                        "required": ["app_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "find_file",
                    "description": "Finds a file location by name on the computer.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "The name of the file to search for."
                            }
                        },
                        "required": ["filename"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "open_windows_settings",
                    "description": "Open specific Windows settings pages.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "setting_type": {
                                "type": "string",
                                "enum": ["bluetooth", "nightlight", "energysaver"],
                                "description": "The type of settings page to open."
                            }
                        },
                        "required": ["setting_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "add_schedule",
                    "description": "Adds a schedule to the user's local calendar.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "The name or title of the schedule"},
                            "date_str": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                            "time_str": {"type": "string", "description": "Time in HH:MM format"},
                            "notify": {"type": "integer", "description": "1 to enable notification, 0 otherwise"}
                        },
                        "required": ["title", "date_str", "time_str"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "play_music",
                    "description": "Plays a song from the user's local library by title.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "song_name": {"type": "string", "description": "The title of the song to search and play"}
                        },
                        "required": ["song_name"]
                    }
                }
            }
        ]

    def process_message(self, user_msg: str) -> str:
        self.conversation_history.append({"role": "user", "content": user_msg})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
                tools=self.tools,
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls
            
            # If the model decided to call a function
            if tool_calls:
                self.conversation_history.append(response_message)
                
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    # Execute locally
                    function_response = ""
                    if function_name == "adjust_brightness":
                        function_response = SystemController.adjust_brightness(function_args.get("level", 50))
                    elif function_name == "adjust_volume":
                        function_response = SystemController.adjust_volume(function_args.get("level", 50))
                    elif function_name == "system_power_action":
                        function_response = SystemController.system_power_action(function_args.get("action"))
                    elif function_name == "open_application":
                        function_response = SystemController.open_application(function_args.get("app_name"))
                    elif function_name == "find_file":
                        function_response = SystemController.find_file(function_args.get("filename"))
                    elif function_name == "open_windows_settings":
                        function_response = SystemController.open_windows_settings(function_args.get("setting_type"))
                    elif function_name == "add_schedule":
                        title = function_args.get("title")
                        date_str = function_args.get("date_str")
                        time_str = function_args.get("time_str")
                        notify = function_args.get("notify", 0)
                        
                        success = db.add_schedule(title, date_str, time_str, notify)
                        if success:
                            function_response = f"Schedule '{title}' successfully added for {date_str} at {time_str}."
                            if self.calendar_add_cb: self.calendar_add_cb()
                        else:
                            function_response = f"Failed to add schedule."
                            
                    elif function_name == "play_music":
                        song_name = function_args.get("song_name")
                        file_path = db.find_song_by_name(song_name)
                        
                        if file_path:
                            function_response = f"Playing {song_name} from the library."
                            if self.play_song_cb: self.play_song_cb(file_path)
                        else:
                            function_response = f"Song '{song_name}' could not be found in the local library."
                    else:
                        function_response = f"Unknown function: {function_name}"
                        
                    # Send function result back to the model
                    self.conversation_history.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response
                    })
                    
                # Second API call to get the final response from the model
                second_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.conversation_history
                )
                final_text = second_response.choices[0].message.content
                self.conversation_history.append({"role": "assistant", "content": final_text})
                return final_text
            
            # If standard text response
            else:
                final_text = response_message.content
                self.conversation_history.append({"role": "assistant", "content": final_text})
                return final_text
                
        except Exception as e:
            error_msg = f"❌ **Error communicating with local LLM.**\nPlease make sure:\n1. You have downloaded and installed [Ollama](https://ollama.com)\n2. Ollama is currently running in your system tray.\n3. **CRITICAL**: You must open your command prompt/terminal and run exactly:\n`ollama run llama3.1`\n(This downloads the brain. Wait for it to finish!)\n\n*(Raw Details: {str(e)})*"
            return error_msg
