"""AI Worker thread for background processing."""
from PyQt6.QtCore import QThread, pyqtSignal


class AIWorker(QThread):
    """Worker thread for processing AI messages asynchronously."""
    
    finished = pyqtSignal(str)
    play_song_signal = pyqtSignal(str)
    calendar_refresh_signal = pyqtSignal()

    def __init__(self, agent, message: str):
        """Initialize the worker thread.
        
        Args:
            agent: AIAgent instance
            message: User message to process
        """
        super().__init__()
        self.agent = agent
        self.message = message
        
        # Connect agent callbacks back to UI
        self.agent.set_callbacks(
            play_song_callback=self._trigger_play_song,
            calendar_add_callback=self._trigger_calendar_refresh
        )

    def _trigger_play_song(self, path):
        """Emit signal to play a song."""
        self.play_song_signal.emit(path)
        
    def _trigger_calendar_refresh(self):
        """Emit signal to refresh calendar."""
        self.calendar_refresh_signal.emit()

    def run(self):
        """Execute the message processing in the worker thread."""
        response = self.agent.process_message(self.message)
        self.finished.emit(response)
