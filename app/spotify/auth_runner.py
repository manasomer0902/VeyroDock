from PySide6.QtCore import QObject, Signal

from app.spotify import auth


class AuthRunner(QObject):
    """Runs Spotify authentication without blocking the Qt UI."""

    finished = Signal()
    failed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.thread = None

    def start(self):
        if self.thread and self.thread.is_alive():
            return

        import threading

        self.thread = threading.Thread(
            target=self._run,
            daemon=True,
        )
        self.thread.start()

    def _run(self):
        try:
            auth.main()
            self.finished.emit()

        except Exception as error:
            self.failed.emit(str(error))
