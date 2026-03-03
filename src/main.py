import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QLabel, QLineEdit, QPushButton, QSlider, QCheckBox, 
    QComboBox, QTextEdit, QListWidget, QFileDialog, QInputDialog, QCalendarWidget, QTimeEdit
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QRect, QPoint, QEasingCurve, QThread, pyqtSignal, QUrl, QSettings
from PyQt6.QtGui import QCursor
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ai_agent import AIAgent
from src.db_manager import db

class AIWorker(QThread):
    finished = pyqtSignal(str)
    # Signals for triggering actions in the main UI thread
    play_song_signal = pyqtSignal(str)
    calendar_refresh_signal = pyqtSignal()

    def __init__(self, agent: AIAgent, message: str):
        super().__init__()
        self.agent = agent
        self.message = message
        # Connect agent callbacks back to UI
        self.agent.set_callbacks(
            play_song_callback=self._trigger_play_song,
            calendar_add_callback=self._trigger_calendar_refresh
        )

    def _trigger_play_song(self, path):
        self.play_song_signal.emit(path)
        
    def _trigger_calendar_refresh(self):
        self.calendar_refresh_signal.emit()

    def run(self):
        response = self.agent.process_message(self.message)
        self.finished.emit(response)

class AssistantWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Load Persistent Settings
        self.settings = QSettings("DesktopAI", "Preferences")
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
            
        # Configuration
        self.panel_width = 380 # Slightly wider to prevent text clipping
        self.is_open = False
        self.animation_duration = 300
        
        self.screens = QApplication.screens()
        
        # Base dimensions based on Target Screen
        screen_geo = self.get_screen_geometry()
        self.setGeometry(screen_geo.right() + 10, screen_geo.top() + 20, self.panel_width, screen_geo.height() - 40)
        
        # Audio setup must be created before settings tab tries to read it.
        # Initialize Audio Player directly here 
        if not hasattr(self, 'audio_output'):
            self.audio_output = QAudioOutput()
            self.audio_output.setVolume(0.5) # Match 50% slider initial value
            self.media_player = QMediaPlayer()
            self.media_player.setAudioOutput(self.audio_output)
            
        self.ai = AIAgent()
        self.ai_worker = None
            
        self.init_ui()
        
        # Edge Detection Timer
        self.edge_timer = QTimer(self)
        self.edge_timer.timeout.connect(self.check_edge_hover)
        self.edge_timer.start(50) # 50ms check
        
        # Animation
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(self.animation_duration)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def get_screen_geometry(self):
        # Refresh screens in case monitor count changes
        self.screens = QApplication.screens()
        # Fallback to primary if saved monitor index was unplugged
        if self.target_screen_idx >= len(self.screens):
            self.target_screen_idx = 0
        return self.screens[self.target_screen_idx].geometry()

    def get_screen_available_geometry(self):
        self.screens = QApplication.screens()
        if self.target_screen_idx >= len(self.screens):
            self.target_screen_idx = 0
        return self.screens[self.target_screen_idx].availableGeometry()

    def init_ui(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        
        # Basic Styling
        self.central_widget.setObjectName("MainPanel")
        self.central_widget.setStyleSheet("""
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
        """)
        
        layout = QVBoxLayout(self.central_widget)
        # Add 10px margins so borders/rounded corners don't get clipped
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Add Tabs
        self.tabs.addTab(self.create_chat_tab(), "Chat")
        self.tabs.addTab(self.create_calendar_tab(), "Calendar")
        self.tabs.addTab(self.create_music_tab(), "Music")
        self.tabs.addTab(self.create_settings_tab(), "Settings")

    def create_chat_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.append("⚡ **AI Status**: Local Llama Engine Ready.\n💡 Try typing: \"Turn my volume to 20%\" or \"Dim brightness to 10\"\n" + "-"*40)
        
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type a command (e.g., 'Turn brightness to 50%')...")
        self.chat_input.returnPressed.connect(self.send_chat_message)
        
        layout.addWidget(self.chat_history)
        layout.addWidget(self.chat_input)
        return widget
        
    def send_chat_message(self):
        text = self.chat_input.text().strip()
        if not text: return
        
        # Display User Input
        self.chat_history.append(f"👨‍💻 **You**: {text}")
        self.chat_input.clear()
        self.chat_input.setPlaceholderText("Generating response...")
        self.chat_input.setEnabled(False)
        
        # Dispatch to Worker Thread
        self.ai_worker = AIWorker(self.ai, text)
        self.ai_worker.finished.connect(self.receive_chat_message)
        self.ai_worker.play_song_signal.connect(self._ai_play_song)
        self.ai_worker.calendar_refresh_signal.connect(self.refresh_schedules)
        self.ai_worker.start()

    def _ai_play_song(self, file_path):
        if file_path and os.path.exists(file_path):
            self.media_player.setSource(QUrl.fromLocalFile(file_path))
            self.media_player.play()
            self.btn_play_pause.setText("Pause")
            self.tabs.setCurrentIndex(2) # Switch to music tab

    def receive_chat_message(self, response: str):
        self.chat_history.append(f"🤖 **AI**: {response}\n")
        self.chat_input.setEnabled(True)
        self.chat_input.setPlaceholderText("Type a command...")
        self.chat_input.setFocus()

    def create_calendar_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("Monthly Calendar"))
        
        self.calendar_widget = QCalendarWidget()
        self.calendar_widget.selectionChanged.connect(self.refresh_schedules)
        layout.addWidget(self.calendar_widget)
        
        layout.addWidget(QLabel("Schedules for selected date:"))
        self.schedule_list = QListWidget()
        layout.addWidget(self.schedule_list)
        
        add_btn = QPushButton("Add Schedule Manually")
        add_btn.clicked.connect(self.add_manual_schedule)
        layout.addWidget(add_btn)
        
        self.refresh_schedules()
        return widget
        
    def refresh_schedules(self):
        self.schedule_list.clear()
        selected_date = self.calendar_widget.selectedDate().toString("yyyy-MM-dd")
        all_schedules = db.get_all_schedules()
        
        for sched in all_schedules:
            if sched[2] == selected_date:
                # Format: [HH:mm] Title (Notify: Yes/No)
                notify_str = "Yes" if sched[4] else "No"
                self.schedule_list.addItem(f"[{sched[3]}] {sched[1]} (Notify: {notify_str})")

    def add_manual_schedule(self):
        title, ok = QInputDialog.getText(self, 'New Schedule', 'Enter schedule title:')
        if ok and title:
            # Simple Time Dialog replacement
            time_str, time_ok = QInputDialog.getText(self, 'Time', 'Enter Time (HH:MM):', text="12:00")
            if time_ok:
                notify = 1 # By default yes for manual testing
                date_str = self.calendar_widget.selectedDate().toString("yyyy-MM-dd")
                db.add_schedule(title, date_str, time_str, notify)
                self.refresh_schedules()

    def create_music_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("Music Library Player"))
        
        self.music_list = QListWidget()
        self.refresh_music_list()
        self.music_list.itemDoubleClicked.connect(self.play_selected_music)
        layout.addWidget(self.music_list)
        
        controls_layout = QHBoxLayout()
        self.btn_play_pause = QPushButton("Play")
        self.btn_play_pause.clicked.connect(self.toggle_play_pause)
        
        self.btn_upload = QPushButton("Upload Song")
        self.btn_upload.clicked.connect(self.upload_song)
        
        controls_layout.addWidget(self.btn_play_pause)
        controls_layout.addWidget(self.btn_upload)
        layout.addLayout(controls_layout)
        
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, 0)
        self.progress_slider.sliderMoved.connect(self.set_music_position)
        layout.addWidget(self.progress_slider)

        self.media_player.positionChanged.connect(self.update_music_position)
        self.media_player.durationChanged.connect(self.update_music_duration)

        return widget

    def set_music_position(self, position):
        self.media_player.setPosition(position)

    def update_music_position(self, position):
        self.progress_slider.setValue(position)

    def update_music_duration(self, duration):
        self.progress_slider.setRange(0, duration)

    def change_internal_volume(self, value):
        # QAudioOutput volume is scalar from 0.0 to 1.0
        self.audio_output.setVolume(value / 100.0)

    def refresh_music_list(self):
        self.music_list.clear()
        songs = db.get_all_songs()
        for song in songs:
            # Format: 'Title - Author'
            display = f"{song[1]} - {song[2]}" if song[2] else song[1]
            self.music_list.addItem(display)
            
    def upload_song(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Audio File", "", "Audio Files (*.mp3 *.wav *.m4a *.mp4)")
        if file_path:
            title, ok = QInputDialog.getText(self, 'Song Info', 'Enter Song Title:')
            if ok and title:
                author, _ = QInputDialog.getText(self, 'Song Info', 'Enter Author/Artist (Optional):')
                db.add_song(title, author, file_path)
                self.refresh_music_list()

    def play_selected_music(self, item=None):
        if item is None:
            item = self.music_list.currentItem()
        if not item:
            return
            
        display_text = item.text()
        title = display_text.split(" - ")[0].strip()
        file_path = db.find_song_by_name(title)
        
        if file_path and os.path.exists(file_path):
            self.media_player.setSource(QUrl.fromLocalFile(file_path))
            self.media_player.play()
            self.btn_play_pause.setText("Pause")
        else:
            print(f"Error: Could not find or play file at '{file_path}'")

    def toggle_play_pause(self):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
            self.btn_play_pause.setText("Play")
        else:
            self.media_player.play()
            self.btn_play_pause.setText("Pause")

    def create_settings_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Settings
        layout.addWidget(QLabel("Preference Settings"))
        self.auto_start_chk = QCheckBox("Start App Automatically on Boot")
        
        # Load Autostart setting
        auto_start = self.settings.value("auto_start", False, type=bool)
        self.auto_start_chk.setChecked(auto_start)
        self.auto_start_chk.stateChanged.connect(self.change_auto_start)
        layout.addWidget(self.auto_start_chk)
        
        # Internal Volume Control for Music Player moved to Settings Tab
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("Music Volume:"))
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(int(self.audio_output.volume() * 100))
        self.volume_slider.valueChanged.connect(self.change_internal_volume)
        volume_layout.addWidget(self.volume_slider)
        layout.addLayout(volume_layout)
        
        dock_layout = QHBoxLayout()
        dock_layout.addWidget(QLabel("Dock Side:"))
        self.dock_combo = QComboBox()
        self.dock_combo.addItems(["Right Edge", "Left Edge"])
        
        # Apply persistent dock side text
        if self.dock_side == "left":
            self.dock_combo.setCurrentText("Left Edge")
        else:
            self.dock_combo.setCurrentText("Right Edge")
            
        self.dock_combo.currentTextChanged.connect(self.change_dock_side)
        dock_layout.addWidget(self.dock_combo)
        layout.addLayout(dock_layout)
        
        # Monitor Selection
        monitor_layout = QHBoxLayout()
        monitor_layout.addWidget(QLabel("Target Monitor:"))
        self.monitor_combo = QComboBox()
        self.refresh_monitor_list()
        self.monitor_combo.currentIndexChanged.connect(self.change_monitor)
        monitor_layout.addWidget(self.monitor_combo)
        layout.addLayout(monitor_layout)

        left_inset_layout = QHBoxLayout()
        left_inset_layout.addWidget(QLabel("Left Edge Inset:"))
        self.left_edge_inset_slider = QSlider(Qt.Orientation.Horizontal)
        self.left_edge_inset_slider.setRange(0, 100)
        self.left_edge_inset_slider.setValue(self.left_edge_inset)
        self.left_edge_inset_slider.valueChanged.connect(self.change_left_edge_inset)
        left_inset_layout.addWidget(self.left_edge_inset_slider)
        self.left_edge_inset_value = QLabel(f"{self.left_edge_inset}px")
        left_inset_layout.addWidget(self.left_edge_inset_value)
        layout.addLayout(left_inset_layout)

        right_inset_layout = QHBoxLayout()
        right_inset_layout.addWidget(QLabel("Right Edge Inset:"))
        self.right_edge_inset_slider = QSlider(Qt.Orientation.Horizontal)
        self.right_edge_inset_slider.setRange(0, 100)
        self.right_edge_inset_slider.setValue(self.right_edge_inset)
        self.right_edge_inset_slider.valueChanged.connect(self.change_right_edge_inset)
        right_inset_layout.addWidget(self.right_edge_inset_slider)
        self.right_edge_inset_value = QLabel(f"{self.right_edge_inset}px")
        right_inset_layout.addWidget(self.right_edge_inset_value)
        layout.addLayout(right_inset_layout)
        
        layout.addStretch()
        
        quit_btn = QPushButton("Quit Application")
        quit_btn.setStyleSheet("background-color: #f7768e; color: white;")
        quit_btn.clicked.connect(QApplication.quit)
        layout.addWidget(quit_btn)
        
        return widget

    def change_auto_start(self, state):
        self.settings.setValue("auto_start", bool(state))

    def change_left_edge_inset(self, value):
        self.left_edge_inset = int(value)
        self.settings.setValue("left_edge_inset", self.left_edge_inset)
        if hasattr(self, "left_edge_inset_value"):
            self.left_edge_inset_value.setText(f"{self.left_edge_inset}px")
        self._update_geometry_for_inset()

    def change_right_edge_inset(self, value):
        self.right_edge_inset = int(value)
        self.settings.setValue("right_edge_inset", self.right_edge_inset)
        if hasattr(self, "right_edge_inset_value"):
            self.right_edge_inset_value.setText(f"{self.right_edge_inset}px")
        self._update_geometry_for_inset()
        
    def _update_geometry_for_inset(self):
        hidden_rect, shown_rect = self._get_animation_rects()
        if self.is_open:
            self.setGeometry(shown_rect)
        else:
            self.setGeometry(hidden_rect)
        
    def refresh_monitor_list(self):
        self.monitor_combo.clear()
        self.screens = QApplication.screens()
        for i, screen in enumerate(self.screens):
            geo = screen.geometry()
            name = screen.name()
            # Mark primary
            if screen == QApplication.primaryScreen():
                name += " (Primary)"
            self.monitor_combo.addItem(f"Monitor {i+1}: {name} [{geo.width()}x{geo.height()}]")
        self.monitor_combo.setCurrentIndex(self.target_screen_idx)
        
    def change_monitor(self, index):
        if index >= 0 and index < len(self.screens):
            self.target_screen_idx = index
            self.settings.setValue("target_screen_idx", self.target_screen_idx)
            self._reset_position()

    def change_dock_side(self, text):
        if "Right" in text:
            self.dock_side = "right"
        else:
            self.dock_side = "left"
        self.settings.setValue("dock_side", self.dock_side)
        self._reset_position()
        
    def _get_animation_rects(self):
        screen_geo = self.get_screen_available_geometry()
        y = screen_geo.y() + 20
        h = screen_geo.height() - 40
        w = self.panel_width
        
        # When moving the window off-screen to hide it, we physically move the X coordinate 
        # outside the monitor's bounds, while keeping the width constant, ensuring it never squishes content
        
        if self.dock_side == "right":
            hidden_x = screen_geo.x() + screen_geo.width() + 10
            shown_x = screen_geo.x() + screen_geo.width() - w - self.right_edge_inset
            
            hidden_rect = QRect(hidden_x, y, w, h)
            shown_rect = QRect(shown_x, y, w, h)
        else:
            hidden_x = screen_geo.x() - w - 10 # completely off left edge
            shown_x = screen_geo.x() + self.left_edge_inset
            
            hidden_rect = QRect(hidden_x, y, w, h)
            shown_rect = QRect(shown_x, y, w, h)
            
        return hidden_rect, shown_rect
            
    def _reset_position(self):
        # Instantly hide and reset position to new monitor or dock side
        self.is_open = False
        hidden_rect, _ = self._get_animation_rects()
        self.setGeometry(hidden_rect)
        self.hide()

    def check_edge_hover(self):
        pos = QCursor.pos()
        screen_geo = self.get_screen_geometry()
        _, shown_rect = self._get_animation_rects()
        
        # Guard clause: ignore if cursor isn't active on our TARGET screen
        if not screen_geo.contains(pos):
            return

        # Trigger hover based on configured edge
        trigger_area = 5
        
        if self.dock_side == "right":
            if pos.x() >= screen_geo.x() + screen_geo.width() - trigger_area and not self.is_open:
                self.show_panel()
            elif pos.x() < shown_rect.left() - 80 and self.is_open:
                # Extra 80px visual buffer so the mouse doesn't accidentally dismiss it instantly
                self.hide_panel()
        elif self.dock_side == "left":
            if pos.x() <= screen_geo.x() + trigger_area and not self.is_open:
                self.show_panel()
            elif pos.x() > shown_rect.right() + 80 and self.is_open:
                self.hide_panel()

    def show_panel(self):
        if self.is_open: return
        self.is_open = True
        
        # Stop current animation before starting a new one
        self.animation.stop()
        try: self.animation.finished.disconnect()
        except TypeError: pass
        
        hidden_rect, shown_rect = self._get_animation_rects()
        
        # Force start at 0 width boundary anchor
        self.setGeometry(hidden_rect)
        self.show()
        
        self.animation.setStartValue(hidden_rect)
        self.animation.setEndValue(shown_rect)
        self.animation.start()

    def hide_panel(self):
        if not self.is_open: return
        self.is_open = False
        
        self.animation.stop()
        try: self.animation.finished.disconnect()
        except TypeError: pass
        
        hidden_rect, shown_rect = self._get_animation_rects()
        
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(hidden_rect)
        self.animation.finished.connect(self._on_hide_finished)
        self.animation.start()
        
    def _on_hide_finished(self):
        if not self.is_open:
            self.hide()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False) # Keep running when panel is hidden
    
    # Run the window
    window = AssistantWindow()
    window.show()
    
    sys.exit(app.exec())
