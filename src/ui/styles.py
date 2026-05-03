"""UI styling constants and utilities."""

MAIN_STYLESHEET = """
    #MainPanel {
        background-color: #1a1b26;
        border-left: 2px solid #292e42;
        border-right: 2px solid #292e42;
        border-radius: 12px;
    }
    QWidget {
        background-color: #1a1b26;
        color: #a9b1d6;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 10pt;
        border-radius: 6px;
    }
    QTabWidget::pane {
        border: none;
        background-color: transparent;
    }
    QTabBar::tab {
        background: #1f2335;
        padding: 12px 18px;
        border: none;
        margin-right: 2px;
        color: #565f89;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
    }
    QTabBar::tab:selected {
        background: #24283b;
        color: #7aa2f7;
        font-weight: bold;
        border-bottom: 3px solid #7aa2f7;
    }
    QTabBar::tab:hover {
        background: #292e42;
    }
    QLineEdit, QTextEdit, QListWidget {
        background-color: #16161e;
        border: 1px solid #414868;
        border-radius: 8px;
        padding: 10px;
        color: #c0caf5;
        selection-background-color: #3d59a1;
    }
    QLineEdit:focus, QTextEdit:focus, QListWidget:focus {
        border: 1px solid #7aa2f7;
    }
    QPushButton {
        background-color: #7aa2f7;
        color: #1a1b26;
        border: none;
        border-radius: 8px;
        padding: 10px 15px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #89b4fa;
    }
    QPushButton:pressed {
        background-color: #3d59a1;
        color: #c0caf5;
    }
    QComboBox {
        background-color: #16161e;
        border: 1px solid #414868;
        border-radius: 8px;
        padding: 8px;
    }
    QComboBox::drop-down {
        border: none;
    }
    QLabel {
        font-size: 11pt;
        font-weight: bold;
        color: #bb9af7;
        margin-bottom: 5px;
        background-color: transparent;
    }
    QCheckBox {
        spacing: 8px;
        background-color: transparent;
    }
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border: 1px solid #414868;
        border-radius: 4px;
        background-color: #16161e;
    }
    QCheckBox::indicator:checked {
        background-color: #7aa2f7;
        border: 1px solid #7aa2f7;
    }
"""
