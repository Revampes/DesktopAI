"""Main application entry point for DesktopAI."""
import sys
import os
from PyQt6.QtWidgets import QApplication

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui import AssistantWindow
from src.ai_agent import AIAgent
from src.db_manager import db


def main():
    """Initialize and run the DesktopAI application."""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # Initialize AI agent with database manager
    ai_agent = AIAgent(db)
    
    # Create and show main window
    window = AssistantWindow(ai_agent, db)
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
