import os
import sys

# Ensure the workspace root is in the python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


if __name__ == "__main__":
    try:
        # Try to launch the modern Webview UI
        from src.gui_webview import start_app
        start_app()
    except Exception as e:
        print(f"Failed to start Webview UI: {e}, falling back to legacy...")
        # Fallback to legacy
        from src.ui import DesktopSidebar
        app = DesktopSidebar()
        app.mainloop()
