import subprocess
import sys
import time

from PySide6.QtCore import QThread, Signal

from app.services.artwork_service import download_artwork
from app.spotify.playback import get_current_track


class SpotifyWorker(QThread):
    track_updated = Signal(object)
    artwork_updated = Signal(object)
    error_occurred = Signal(str)
    status_updated = Signal(str)

    def __init__(self, interval=3):
        super().__init__()
        self.interval = interval
        self.running = True
        self.last_artwork_url = None

    @staticmethod
    def spotify_process_state():
        """
        Return True when the Windows Spotify desktop process is running,
        False when it is definitely not running, or None if the check
        cannot be performed.
        """
        if not sys.platform.startswith("win"):
            return None

        try:
            result = subprocess.run(
                [
                    "tasklist",
                    "/FI",
                    "IMAGENAME eq Spotify.exe",
                    "/NH",
                ],
                capture_output=True,
                text=True,
                timeout=2,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            return "spotify.exe" in result.stdout.lower()
        except (OSError, subprocess.SubprocessError):
            return None

    def emit_track_state(self, track):
        if track is None:
            self.status_updated.emit("not_playing")
        elif track.is_playing:
            self.status_updated.emit("playing")
        else:
            self.status_updated.emit("paused")

        self.track_updated.emit(track)

    def run(self):
        while self.running:
            try:
                # Ask Spotify's Web API first. This is the authoritative
                # source for the currently playing track. We only use the
                # Windows process check as a fallback when the API reports
                # no playback. This avoids falsely hiding a real track when
                # Windows reports Spotify's process differently.
                track = get_current_track()

                if track is not None:
                    self.emit_track_state(track)

                    if track.album_art_url != self.last_artwork_url:
                        self.last_artwork_url = track.album_art_url
                        artwork = download_artwork(track.album_art_url)
                        if artwork:
                            self.artwork_updated.emit(artwork)
                else:
                    process_state = self.spotify_process_state()

                    if process_state is False:
                        self.status_updated.emit("not_running")
                    else:
                        self.status_updated.emit("not_playing")

                    self.track_updated.emit(None)

            except Exception as error:
                # If the API request fails, distinguish a closed Spotify
                # desktop app from a genuine API/connection failure when
                # possible.
                process_state = self.spotify_process_state()

                if process_state is False:
                    self.status_updated.emit("not_running")
                    self.track_updated.emit(None)
                else:
                    self.status_updated.emit("error")
                    self.error_occurred.emit(str(error))

            time.sleep(self.interval)

    def stop(self):
        self.running = False
        self.wait()
