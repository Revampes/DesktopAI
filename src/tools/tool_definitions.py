"""Tool definitions for the AI agent."""

TOOL_DEFINITIONS = [
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
