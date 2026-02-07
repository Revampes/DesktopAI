import os
import sys

# Ensure the workspace root is in the python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ui import DesktopSidebar

if __name__ == "__main__":
    app = DesktopSidebar()
    app.mainloop()
