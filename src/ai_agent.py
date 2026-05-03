import json
from openai import OpenAI
from src.tools import TOOL_DEFINITIONS, ToolExecutor


class AIAgent:
    """AI Agent for processing user messages and executing tools."""
    
    def __init__(self, db_manager, model_name="llama3.1"):
        """Initialize the AI agent.
        
        Args:
            db_manager: Database manager instance
            model_name: Name of the model to use (default: llama3.1)
        """
        # Configure to use local Ollama instance via OpenAI compatibility layer
        self.client = OpenAI(
            base_url="http://127.0.0.1:11434/v1",
            api_key="ollama"  # api_key is required by the client but ignored by Ollama
        )
        self.model = model_name
        self.db = db_manager
        
        self.conversation_history = [
            {
                "role": "system",
                "content": "You are a helpful desktop assistant. You can control system settings like brightness and volume, manage the user's calendar, and play music from their library. Keep your answers brief and concise."
            }
        ]
        
        self.play_song_cb = None
        self.calendar_add_cb = None
        self.tool_executor = None
        
    def set_callbacks(self, play_song_callback, calendar_add_callback):
        """Set callbacks for UI events.
        
        Args:
            play_song_callback: Callback when AI requests to play a song
            calendar_add_callback: Callback when AI adds to calendar
        """
        self.play_song_cb = play_song_callback
        self.calendar_add_cb = calendar_add_callback
        
        # Initialize tool executor with callbacks
        self.tool_executor = ToolExecutor(
            self.db,
            play_song_callback=play_song_callback,
            calendar_callback=calendar_add_callback
        )

    @property
    def tools(self):
        """Get list of available tools."""
        return TOOL_DEFINITIONS

    def process_message(self, user_msg: str) -> str:
        """Process a user message and generate a response.
        
        Args:
            user_msg: The user's message
            
        Returns:
            The AI agent's response
        """
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
                    
                    # Execute tool using tool executor
                    if self.tool_executor is None:
                        # Initialize on first use if not set via callbacks
                        self.tool_executor = ToolExecutor(self.db)
                    
                    function_response = self.tool_executor.execute(function_name, function_args)
                    
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
