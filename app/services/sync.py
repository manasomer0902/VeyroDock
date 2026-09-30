import time
from typing import Callable

from app.spotify.playback import get_current_track


class SpotifySync:
    def __init__(
        self,
        callback: Callable,
        interval: float = 3.0,
    ):
        self.callback = callback
        self.interval = interval
        self.running = False

        self.last_track_id = None
        self.last_is_playing = None

    def start(self):
        self.running = True

        print("Spotify sync started.")

        while self.running:
            try:
                track = get_current_track()

                if track is None:
                    if self.last_track_id is not None:
                        self.last_track_id = None
                        self.last_is_playing = None

                        self.callback(None)

                else:
                    track_changed = (
                        track.name,
                        track.artist,
                        track.album,
                    ) != self.last_track_id

                    playback_changed = track.is_playing != self.last_is_playing

                    if track_changed or playback_changed:
                        self.last_track_id = (
                            track.name,
                            track.artist,
                            track.album,
                        )

                        self.last_is_playing = track.is_playing

                        self.callback(track)

            except Exception as error:
                print(f"Sync error: {error}")

            time.sleep(self.interval)

    def stop(self):
        self.running = False
        print("Spotify sync stopped.")
