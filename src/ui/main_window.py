"""Main application window."""
import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QLabel, QPushButton, QSlider, QCheckBox, QComboBox, QFrame
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QRect, QPoint, QEasingCurve, QSettings, QUrl
from PyQt6.QtGui import QCursor
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

from .styles import MAIN_STYLESHEET
from .worker import AIWorker
from .tabs import ChatTab, CalendarTab, MusicTab, SettingsTab


class AssistantWindow(QMainWindow):
    """Main application window for DesktopAI."""
    
    def __init__(self, ai_agent, db_manager):
        """Initialize the main window.
        
        Args:
            ai_agent: AIAgent instance
            db_manager: DatabaseManager instance
        """
        super().__init__()
        self.ai = ai_agent
        self.db = db_manager
        
        # Window configuration
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Load persistent settings
        self.settings = QSettings("DesktopAI", "Preferences")
        self.load_settings()
        
        # Configuration
        self.panel_width = 380
        self.is_open = False
        self.animation_duration = 300
        
        self.screens = QApplication.screens()
        
        # Audio setup
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(0.5)
        self.media_player = QMediaPlayer()
        self.media_player.setAudioOutput(self.audio_output)
        
        # Set initial geometry
        screen_geo = self.get_screen_geometry()
        self.setGeometry(screen_geo.right() + 10, screen_geo.top() + 20, self.panel_width, screen_geo.height() - 40)
        
        # Initialize UI
        self.init_ui()
        
        # Edge detection timer
        self.edge_timer = QTimer(self)
        self.edge_timer.timeout.connect(self.check_edge_hover)
        self.edge_timer.start(50)
        
        # Animation setup
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(self.animation_duration)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.ai_worker = None
    
    def load_settings(self):
        """Load user preferences from QSettings."""
        self.dock_side = self.settings.value("dock_side", "right")
        try:
            self.target_screen_idx = int(self.settings.value("target_screen_idx", 0))
        except:
            self.target_screen_idx = 0
        try:
            self.left_edge_inset = int(self.settings.value("left_edge_inset", 8))
        except:
            self.left_edge_inset = 8
        self.left_edge_inset = max(0, min(100, self.left_edge_inset))
        
        try:
            self.right_edge_inset = int(self.settings.value("right_edge_inset", 100))
        except:
            self.right_edge_inset = 100
        self.right_edge_inset = max(0, min(100, self.right_edge_inset))

    def get_screen_geometry(self):
        """Get geometry of target screen."""
        self.screens = QApplication.screens()
        if self.target_screen_idx >= len(self.screens):
            self.target_screen_idx = 0
        return self.screens[self.target_screen_idx].geometry()

    def get_screen_available_geometry(self):
        """Get available geometry of target screen."""
        self.screens = QApplication.screens()
        if self.target_screen_idx >= len(self.screens):
            self.target_screen_idx = 0
        return self.screens[self.target_screen_idx].availableGeometry()

    def init_ui(self):
        """Initialize the user interface."""
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        
        self.central_widget.setObjectName("MainPanel")
        self.central_widget.setStyleSheet(MAIN_STYLESHEET)
        
        layout = QVBoxLayout(self.central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create tabs
        self.tabs = QTabWidget()
        
        # Chat tab
        self.chat_tab = ChatTab()
        self.chat_tab.send_message.connect(self.send_chat_message)
        self.tabs.addTab(self.chat_tab, "Chat")
        
        # Calendar tab
        self.calendar_tab = CalendarTab(self.db)
        self.calendar_tab.add_schedule_requested.connect(self.refresh_calendar_display)
        self.tabs.addTab(self.calendar_tab, "Calendar")
        
        # Music tab
        self.music_tab = MusicTab(self.db, self.media_player, self.audio_output)
        self.tabs.addTab(self.music_tab, "Music")
        
        # Settings tab
        self.settings_tab = self.create_settings_tab()
        self.tabs.addTab(self.settings_tab, "Settings")
        
        layout.addWidget(self.tabs)

    def send_chat_message(self, text):
        """Process a chat message."""
        if not text:
            return
        
        self.chat_tab.append_user_message(text)
        
        # Process in worker thread
        self.ai_worker = AIWorker(self.ai, text)
        self.ai_worker.finished.connect(self.receive_chat_message)
        self.ai_worker.play_song_signal.connect(self.on_ai_play_song)
        self.ai_worker.calendar_refresh_signal.connect(self.refresh_calendar_display)
        self.ai_worker.start()

    def receive_chat_message(self, response: str):
        """Receive and display AI response."""
        self.chat_tab.append_ai_message(response)

    def on_ai_play_song(self, file_path):
        """Handle AI request to play a song."""
        self.music_tab.play_song_by_path(file_path)
        self.tabs.setCurrentIndex(2)  # Switch to music tab

    def refresh_calendar_display(self):
        """Refresh calendar display after schedule changes."""
        self.calendar_tab.refresh_schedules()

    def create_settings_tab(self):
        """Create the settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("Preference Settings"))
        
        # Autostart setting
        auto_start_chk = QCheckBox("Start App Automatically on Boot")
        auto_start = self.settings.value("auto_start", False, type=bool)
        auto_start_chk.setChecked(auto_start)
        auto_start_chk.stateChanged.connect(lambda state: self.settings.setValue("auto_start", bool(state)))
        layout.addWidget(auto_start_chk)
        
        # Music settings
        layout.addWidget(QLabel("Music Settings"))
        
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("Music Volume:"))
        volume_slider = QSlider(Qt.Orientation.Horizontal)
        volume_slider.setRange(0, 100)
        volume_slider.setValue(int(self.audio_output.volume() * 100))
        volume_slider.valueChanged.connect(lambda v: self.audio_output.setVolume(v / 100.0))
        volume_layout.addWidget(volume_slider)
        layout.addLayout(volume_layout)
        
        # Dock side setting
        dock_layout = QHBoxLayout()
        dock_layout.addWidget(QLabel("Dock Side:"))
        dock_combo = QComboBox()
        dock_combo.addItems(["Right Edge", "Left Edge"])
        dock_combo.setCurrentText("Right Edge" if self.dock_side == "right" else "Left Edge")
        dock_combo.currentTextChanged.connect(self.change_dock_side)
        dock_layout.addWidget(dock_combo)
        layout.addLayout(dock_layout)
        
        # Monitor selection
        monitor_layout = QHBoxLayout()
        monitor_layout.addWidget(QLabel("Target Monitor:"))
        self.monitor_combo = QComboBox()
        self.refresh_monitor_list()
        self.monitor_combo.currentIndexChanged.connect(self.change_monitor)
        monitor_layout.addWidget(self.monitor_combo)
        layout.addLayout(monitor_layout)
        
        # Edge inset controls
        left_inset_layout = QHBoxLayout()
        left_inset_layout.addWidget(QLabel("Left Edge Inset:"))
        left_slider = QSlider(Qt.Orientation.Horizontal)
        left_slider.setRange(0, 100)
        left_slider.setValue(self.left_edge_inset)
        self.left_inset_label = QLabel(f"{self.left_edge_inset}px")
        left_slider.valueChanged.connect(lambda v: self.change_left_edge_inset(v, self.left_inset_label))
        left_inset_layout.addWidget(left_slider)
        left_inset_layout.addWidget(self.left_inset_label)
        layout.addLayout(left_inset_layout)
        
        right_inset_layout = QHBoxLayout()
        right_inset_layout.addWidget(QLabel("Right Edge Inset:"))
        right_slider = QSlider(Qt.Orientation.Horizontal)
        right_slider.setRange(0, 100)
        right_slider.setValue(self.right_edge_inset)
        self.right_inset_label = QLabel(f"{self.right_edge_inset}px")
        right_slider.valueChanged.connect(lambda v: self.change_right_edge_inset(v, self.right_inset_label))
        right_inset_layout.addWidget(right_slider)
        right_inset_layout.addWidget(self.right_inset_label)
        layout.addLayout(right_inset_layout)
        
        layout.addStretch()
        
        quit_btn = QPushButton("Quit Application")
        quit_btn.setStyleSheet("background-color: #f7768e; color: white;")
        quit_btn.clicked.connect(QApplication.quit)
        layout.addWidget(quit_btn)
        
        return widget

    def change_left_edge_inset(self, value, label):
        """Update left edge inset."""
        self.left_edge_inset = int(value)
        self.settings.setValue("left_edge_inset", self.left_edge_inset)
        label.setText(f"{self.left_edge_inset}px")
        self._update_geometry_for_inset()

    def change_right_edge_inset(self, value, label):
        """Update right edge inset."""
        self.right_edge_inset = int(value)
        self.settings.setValue("right_edge_inset", self.right_edge_inset)
        label.setText(f"{self.right_edge_inset}px")
        self._update_geometry_for_inset()

    def _update_geometry_for_inset(self):
        """Update window geometry based on inset settings."""
        hidden_rect, shown_rect = self._get_animation_rects()
        if self.is_open:
            self.setGeometry(shown_rect)
        else:
            self.setGeometry(hidden_rect)

    def refresh_monitor_list(self):
        """Refresh the monitor selection list."""
        self.monitor_combo.clear()
        self.screens = QApplication.screens()
        for i, screen in enumerate(self.screens):
            geo = screen.geometry()
            name = screen.name()
            if screen == QApplication.primaryScreen():
                name += " (Primary)"
            self.monitor_combo.addItem(f"Monitor {i+1}: {name} [{geo.width()}x{geo.height()}]")
        self.monitor_combo.setCurrentIndex(self.target_screen_idx)

    def change_monitor(self, index):
        """Change target monitor."""
        if index >= 0 and index < len(self.screens):
            self.target_screen_idx = index
            self.settings.setValue("target_screen_idx", self.target_screen_idx)
            self._reset_position()

    def change_dock_side(self, text):
        """Change dock side (left or right)."""
        self.dock_side = "left" if "Left" in text else "right"
        self.settings.setValue("dock_side", self.dock_side)
        self._reset_position()

    def _get_animation_rects(self):
        """Get hidden and shown animation rectangles."""
        screen_geo = self.get_screen_available_geometry()
        y = screen_geo.y() + 20
        h = screen_geo.height() - 40
        w = self.panel_width
        
        if self.dock_side == "right":
            hidden_x = screen_geo.x() + screen_geo.width() + 10
            shown_x = screen_geo.x() + screen_geo.width() - w - self.right_edge_inset
            
            hidden_rect = QRect(hidden_x, y, w, h)
            shown_rect = QRect(shown_x, y, w, h)
        else:
            hidden_x = screen_geo.x() - w - 10
            shown_x = screen_geo.x() + self.left_edge_inset
            
            hidden_rect = QRect(hidden_x, y, w, h)
            shown_rect = QRect(shown_x, y, w, h)
        
        return hidden_rect, shown_rect

    def _reset_position(self):
        """Reset window position."""
        self.is_open = False
        hidden_rect, _ = self._get_animation_rects()
        self.setGeometry(hidden_rect)
        self.hide()

    def check_edge_hover(self):
        """Check for edge hover to show/hide panel."""
        pos = QCursor.pos()
        screen_geo = self.get_screen_geometry()
        _, shown_rect = self._get_animation_rects()
        
        if not screen_geo.contains(pos):
            return

        trigger_area = 5
        
        if self.dock_side == "right":
            if pos.x() >= screen_geo.x() + screen_geo.width() - trigger_area and not self.is_open:
                self.show_panel()
            elif pos.x() < shown_rect.left() - 80 and self.is_open:
                self.hide_panel()
        elif self.dock_side == "left":
            if pos.x() <= screen_geo.x() + trigger_area and not self.is_open:
                self.show_panel()
            elif pos.x() > shown_rect.right() + 80 and self.is_open:
                self.hide_panel()

    def show_panel(self):
        """Show the panel with animation."""
        if self.is_open:
            return
        self.is_open = True
        
        self.animation.stop()
        try:
            self.animation.finished.disconnect()
        except TypeError:
            pass
        
        hidden_rect, shown_rect = self._get_animation_rects()
        self.setGeometry(hidden_rect)
        self.show()
        
        self.animation.setStartValue(hidden_rect)
        self.animation.setEndValue(shown_rect)
        self.animation.start()

    def hide_panel(self):
        """Hide the panel with animation."""
        if not self.is_open:
            return
        self.is_open = False
        
        self.animation.stop()
        try:
            self.animation.finished.disconnect()
        except TypeError:
            pass
        
        hidden_rect, shown_rect = self._get_animation_rects()
        
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(hidden_rect)
        self.animation.finished.connect(self._on_hide_finished)
        self.animation.start()

    def _on_hide_finished(self):
        """Called when hide animation finishes."""
        if not self.is_open:
            self.hide()
