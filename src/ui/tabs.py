"""Tab creation and management utilities."""
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QListWidget, QFileDialog, QInputDialog, QCalendarWidget,
    QSlider, QCheckBox, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QUrl
from PyQt6.QtMultimedia import QMediaPlayer


class ChatTab(QWidget):
    """Chat interface tab."""
    
    send_message = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.append("⚡ **AI Status**: Local Llama Engine Ready.\n💡 Try typing: \"Turn my volume to 20%\" or \"Dim brightness to 10\"\n" + "-"*40)
        
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type a command (e.g., 'Turn brightness to 50%')...")
        self.chat_input.returnPressed.connect(self.send_message_action)
        
        layout.addWidget(self.chat_history)
        layout.addWidget(self.chat_input)
    
    def send_message_action(self):
        text = self.chat_input.text().strip()
        if text:
            self.send_message.emit(text)
            self.chat_input.clear()
    
    def append_user_message(self, text):
        self.chat_history.append(f"👨‍💻 **You**: {text}")
        self.set_input_busy(True)
    
    def append_ai_message(self, text):
        self.chat_history.append(f"🤖 **AI**: {text}\n")
        self.set_input_busy(False)
    
    def set_input_busy(self, busy):
        if busy:
            self.chat_input.setPlaceholderText("Generating response...")
            self.chat_input.setEnabled(False)
        else:
            self.chat_input.setPlaceholderText("Type a command...")
            self.chat_input.setEnabled(True)
            self.chat_input.setFocus()


class CalendarTab(QWidget):
    """Calendar and schedule management tab."""
    
    schedule_date_changed = pyqtSignal()
    add_schedule_requested = pyqtSignal()
    
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Monthly Calendar"))
        
        self.calendar_widget = QCalendarWidget()
        self.calendar_widget.selectionChanged.connect(self.refresh_schedules)
        layout.addWidget(self.calendar_widget)
        
        layout.addWidget(QLabel("Schedules for selected date:"))
        self.schedule_list = QListWidget()
        layout.addWidget(self.schedule_list)
        
        add_btn = QPushButton("Add Schedule Manually")
        add_btn.clicked.connect(self.on_add_schedule)
        layout.addWidget(add_btn)
        
        self.refresh_schedules()
    
    def refresh_schedules(self):
        self.schedule_list.clear()
        selected_date = self.calendar_widget.selectedDate().toString("yyyy-MM-dd")
        all_schedules = self.db.get_all_schedules()
        
        for sched in all_schedules:
            if sched[2] == selected_date:
                notify_str = "Yes" if sched[4] else "No"
                self.schedule_list.addItem(f"[{sched[3]}] {sched[1]} (Notify: {notify_str})")
        
        self.schedule_date_changed.emit()
    
    def on_add_schedule(self):
        title, ok = QInputDialog.getText(self, 'New Schedule', 'Enter schedule title:')
        if ok and title:
            time_str, time_ok = QInputDialog.getText(self, 'Time', 'Enter Time (HH:MM):', text="12:00")
            if time_ok:
                notify = 1
                date_str = self.calendar_widget.selectedDate().toString("yyyy-MM-dd")
                self.db.add_schedule(title, date_str, time_str, notify)
                self.refresh_schedules()
                self.add_schedule_requested.emit()


class MusicTab(QWidget):
    """Music player and library tab."""
    
    song_selected = pyqtSignal(str)
    
    def __init__(self, db, media_player, audio_output, parent=None):
        super().__init__(parent)
        self.db = db
        self.media_player = media_player
        self.audio_output = audio_output
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
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

    def set_music_position(self, position):
        self.media_player.setPosition(position)

    def update_music_position(self, position):
        self.progress_slider.setValue(position)

    def update_music_duration(self, duration):
        self.progress_slider.setRange(0, duration)

    def refresh_music_list(self):
        self.music_list.clear()
        songs = self.db.get_all_songs()
        for song in songs:
            display = f"{song[1]} - {song[2]}" if song[2] else song[1]
            self.music_list.addItem(display)
    
    def upload_song(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Audio File", "", "Audio Files (*.mp3 *.wav *.m4a *.mp4)")
        if file_path:
            title, ok = QInputDialog.getText(self, 'Song Info', 'Enter Song Title:')
            if ok and title:
                author, _ = QInputDialog.getText(self, 'Song Info', 'Enter Author/Artist (Optional):')
                self.db.add_song(title, author, file_path)
                self.refresh_music_list()

    def play_selected_music(self, item=None):
        if item is None:
            item = self.music_list.currentItem()
        if not item:
            return
            
        display_text = item.text()
        title = display_text.split(" - ")[0].strip()
        file_path = self.db.find_song_by_name(title)
        
        if file_path and os.path.exists(file_path):
            self.media_player.setSource(QUrl.fromLocalFile(file_path))
            self.media_player.play()
            self.btn_play_pause.setText("Pause")
            self.song_selected.emit(file_path)
        else:
            print(f"Error: Could not find or play file at '{file_path}'")

    def toggle_play_pause(self):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
            self.btn_play_pause.setText("Play")
        else:
            self.media_player.play()
            self.btn_play_pause.setText("Pause")
    
    def play_song_by_path(self, file_path):
        """Play a song from file path."""
        if file_path and os.path.exists(file_path):
            self.media_player.setSource(QUrl.fromLocalFile(file_path))
            self.media_player.play()
            self.btn_play_pause.setText("Pause")


class SettingsTab(QWidget):
    """Settings and preferences tab."""
    
    def __init__(self, settings, screens, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.screens = screens
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Preference Settings"))
        self.auto_start_chk = QCheckBox("Start App Automatically on Boot")
        auto_start = self.settings.value("auto_start", False, type=bool)
        self.auto_start_chk.setChecked(auto_start)
        self.auto_start_chk.stateChanged.connect(self.change_auto_start)
        layout.addWidget(self.auto_start_chk)
        
        music_title_layout = QVBoxLayout()
        music_title_layout.addWidget(QLabel("Music Settings"))
        layout.addLayout(music_title_layout)
        
        layout.addStretch()
        
        quit_btn = QPushButton("Quit Application")
        quit_btn.setStyleSheet("background-color: #f7768e; color: white;")
        layout.addWidget(quit_btn)
    
    def change_auto_start(self, state):
        self.settings.setValue("auto_start", bool(state))
    
    def add_volume_control(self, volume_changed_signal):
        """Add volume control slider."""
        pass
