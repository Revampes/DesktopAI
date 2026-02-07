import sys
import os

# Ensure the project root is in the python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

if __name__ == "__main__":
    try:
        from src.gui_webview import start_app
        start_app()
    except ImportError as e:
        print(f"Startup Error: {e}")
        print("Please ensure you are running this script from the project root directory.")
