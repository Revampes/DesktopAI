"""DesktopAI - Local AI Desktop Assistant"""

__version__ = "1.0.0"
__author__ = "DesktopAI Team"

from src.ai_agent import AIAgent
from src.db_manager import db
from src.ui import AssistantWindow, AIWorker
from src.system_controls import SystemController
from src.tools import ToolExecutor, TOOL_DEFINITIONS

__all__ = [
    'AIAgent',
    'db',
    'AssistantWindow',
    'AIWorker',
    'SystemController',
    'ToolExecutor',
    'TOOL_DEFINITIONS',
]
