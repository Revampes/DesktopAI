# DesktopAI - Modular Architecture Guide

## 📁 Directory Structure

```
DesktopAI/
│
├── src/
│   ├── __init__.py                    # Package init (clean imports)
│   ├── main.py                        # ⭐ Entry point (30 lines)
│   ├── ai_agent.py                    # AI message processor
│   ├── system_controls.py             # System utilities
│   ├── db_manager.py                  # Database management
│   │
│   ├── ui/                            # 🎨 UI Package (Refactored)
│   │   ├── __init__.py
│   │   ├── main_window.py             # AssistantWindow class (300 lines)
│   │   ├── worker.py                  # AIWorker thread (45 lines)
│   │   ├── tabs.py                    # Tab components (250 lines)
│   │   └── styles.py                  # UI styling (60 lines)
│   │
│   ├── tools/                         # 🔧 Tools Package (New)
│   │   ├── __init__.py
│   │   ├── tool_definitions.py        # Tool definitions (150 lines)
│   │   └── tool_executor.py           # Tool execution (80 lines)
│   │
│   ├── music_library/                 # 🎵 Music storage
│   └── assistant.db                   # Database file
│
├── REFACTORING_NOTES.md               # Complete refactoring guide
├── REFACTORING_CHECKLIST.md           # Before/after comparison
├── build.py                           # Build script
└── requirements.txt                   # Dependencies
```

## 🔄 Data Flow Architecture

```
User Input (main.py)
    ↓
AssistantWindow (ui/main_window.py)
    ↓
ChatTab (ui/tabs.py) - sends message signal
    ↓
AIWorker (ui/worker.py) - runs in thread
    ↓
AIAgent (ai_agent.py) - processes message
    ↓
ToolExecutor (tools/tool_executor.py)
    ├── SystemController (system_controls.py) - system operations
    └── DatabaseManager (db_manager.py) - data operations
    ↓
Response → UI Update (CalendarTab, MusicTab, etc.)
```

## 📦 Module Responsibilities

### Main Entry Point
```
main.py
├── Initialize QApplication
├── Create AIAgent with database
├── Create AssistantWindow
└── Start event loop
```

### UI Package (ui/)
```
ui/main_window.py
├── Window configuration
├── Geometry management
├── Animation control
├── Tab initialization
└── Edge detection

ui/worker.py
├── Background thread
├── Message processing
└── Signal emission

ui/tabs.py
├── ChatTab: Message input/output
├── CalendarTab: Schedule management
├── MusicTab: Music player
└── SettingsTab: Preferences

ui/styles.py
└── Centralized styling
```

### Tools Package (tools/)
```
tools/tool_definitions.py
├── adjust_brightness
├── adjust_volume
├── system_power_action
├── open_application
├── find_file
├── open_windows_settings
├── add_schedule
└── play_music

tools/tool_executor.py
└── ToolExecutor class
    └── execute(function_name, args)
```

### AI & Database
```
ai_agent.py
├── Message history
├── Model client (Ollama)
├── Tool calling
└── Response generation

db_manager.py
├── Calendar management
├── Music library
└── SQLite operations

system_controls.py
├── Brightness control
├── Volume control
├── Power actions
├── Application launch
└── File search
```

## 🎯 Component Communication

```
┌─────────────────────────────────────────────────────────┐
│                    Main Window                          │
│  ┌──────────┬──────────┬──────────┬─────────────────┐   │
│  │  Chat   │ Calendar │  Music  │    Settings     │   │
│  │   Tab   │   Tab    │   Tab   │      Tab        │   │
│  └────┬─────┴─────┬────┴────┬────┴─────────┬──────┘   │
│       │           │         │              │          │
│  ┌────▼─────┐ ┌───▼───┐ ┌──▼────┐    ┌────▼────┐     │
│  │ AI Worker│ │ Music │ │Calendar│    │ Settings│     │
│  │  Thread  │ │Player │ │Refresh │    │ Updates │     │
│  └────┬─────┘ └───┬───┘ └──┬─────┘    └────┬────┘     │
│       │           │        │               │          │
└───────┼───────────┼────────┼───────────────┼──────────┘
        │           │        │               │
    ┌───▼───────────▼────────▼───────────────▼──────┐
    │          AIAgent (ai_agent.py)                │
    │  ┌──────────────────────────────────────────┐ │
    │  │  ToolExecutor (tools/tool_executor.py)   │ │
    │  │  ┌──────────────┬──────────┬────────┐   │ │
    │  │  │ SystemControl│ Database │ Others │   │ │
    │  │  └──────────────┴──────────┴────────┘   │ │
    │  └──────────────────────────────────────────┘ │
    └──────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Run Application
```bash
python src/main.py
```

### Key Files to Edit

**Add UI Element:**
- Edit: `src/ui/main_window.py` or `src/ui/tabs.py`
- Add new tab or modify existing tab

**Add AI Tool:**
1. `src/tools/tool_definitions.py` - Add tool definition
2. `src/tools/tool_executor.py` - Add execution logic

**Change Styling:**
- Edit: `src/ui/styles.py`

**Modify AI Behavior:**
- Edit: `src/ai_agent.py` (system prompt, etc.)

## ✨ Benefits of This Structure

| Aspect | Benefit |
|--------|---------|
| **Maintainability** | Each module has single responsibility |
| **Reusability** | Components can be used independently |
| **Testability** | Easy to unit test individual modules |
| **Scalability** | New features don't require major refactoring |
| **Readability** | Clear organization makes code easier to understand |
| **Extensibility** | New tools and tabs can be added cleanly |

## 📊 Code Metrics

| Metric | Value |
|--------|-------|
| Total lines (src/) | ~1500 |
| Average file size | ~150 lines |
| Max file size | 300 lines |
| Modules | 9 |
| Packages | 3 |
| Classes | 8 |

## 🔗 Import Reference

```python
# From src/__init__.py (recommended)
from src import AIAgent, AssistantWindow, AIWorker, SystemController

# Specific imports (when needed)
from src.ui import AssistantWindow, AIWorker
from src.ui.tabs import ChatTab, MusicTab
from src.ai_agent import AIAgent
from src.tools import ToolExecutor, TOOL_DEFINITIONS
from src.system_controls import SystemController
from src.db_manager import db
```

## 🎓 Architecture Principles Used

1. **Single Responsibility Principle**: Each module does one thing well
2. **DRY (Don't Repeat Yourself)**: No duplicate code
3. **Separation of Concerns**: UI, AI, and tools are separate
4. **Open/Closed Principle**: Easy to extend, hard to break
5. **Dependency Injection**: Dependencies passed to constructors

---

**Last Updated**: Refactoring Complete ✅
