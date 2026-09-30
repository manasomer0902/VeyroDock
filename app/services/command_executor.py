import time
from concurrent.futures import ThreadPoolExecutor

from PySide6.QtCore import QObject, Signal

from app.services.artwork_service import download_artwork
from app.spotify.controller import (
    pause_playback,
    resume_playback,
    seek_to,
    skip_next,
    skip_previous,
)
from app.spotify.playback import get_current_track


class CommandExecutor(QObject):
    """
    Runs Spotify playback commands outside the GUI thread.

    This keeps the interface responsive while Spotify handles
    the requested command.
    """

    command_finished = Signal(str, object)
    command_failed = Signal(str, str)

    def __init__(
        self,
        parent=None,
    ):
        super().__init__(
            parent
        )

        # One worker keeps playback commands in order.
        self.executor = ThreadPoolExecutor(
            max_workers=1
        )

    # ==================================================
    # INTERNAL HELPERS
    # ==================================================

    @staticmethod
    def track_signature(track):
        if track is None:
            return None

        return (
            track.name,
            track.artist,
            track.album,
            track.duration_ms,
        )

    @staticmethod
    def build_result(track):
        if track is None:
            return None

        artwork = download_artwork(
            track.album_art_url
        )

        return {
            "track": track,
            "artwork": artwork,
        }

    def submit(
        self,
        command_name,
        function,
    ):
        future = self.executor.submit(
            function
        )

        def completed(future_object):
            try:
                result = future_object.result()

                self.command_finished.emit(
                    command_name,
                    result,
                )

            except Exception as error:

                self.command_failed.emit(
                    command_name,
                    str(error),
                )

        future.add_done_callback(
            completed
        )

    # ==================================================
    # WAIT FOR TRACK CHANGE
    # ==================================================

    def wait_for_track_change(
        self,
        previous_signature,
        timeout=1.5,
    ):
        deadline = (
            time.monotonic()
            + timeout
        )

        latest_track = None

        while time.monotonic() < deadline:

            latest_track = (
                get_current_track()
            )

            if latest_track is None:
                return None

            current_signature = (
                self.track_signature(
                    latest_track
                )
            )

            if (
                previous_signature is None
                or current_signature
                != previous_signature
            ):
                return latest_track

            time.sleep(
                0.12
            )

        return latest_track

    # ==================================================
    # WAIT FOR SEEK
    # ==================================================

    def wait_for_seek_position(
        self,
        target_position_ms,
        timeout=1.2,
    ):
        """
        Spotify can briefly return the pre-seek position after a
        successful seek command. Poll until the reported position
        is close enough to the requested position.
        """

        deadline = (
            time.monotonic()
            + timeout
        )

        latest_track = None
        tolerance_ms = 1800

        while time.monotonic() < deadline:

            latest_track = (
                get_current_track()
            )

            if latest_track is None:
                return None

            difference = abs(
                latest_track.progress_ms
                - target_position_ms
            )

            if difference <= tolerance_ms:
                return latest_track

            time.sleep(
                0.10
            )

        return latest_track

    # ==================================================
    # PAUSE
    # ==================================================

    def pause(
        self,
    ):

        def task():
            pause_playback()

            track = get_current_track()

            return self.build_result(
                track
            )

        self.submit(
            "pause",
            task,
        )

    # ==================================================
    # RESUME
    # ==================================================

    def resume(
        self,
    ):

        def task():
            resume_playback()

            track = get_current_track()

            return self.build_result(
                track
            )

        self.submit(
            "resume",
            task,
        )

    # ==================================================
    # NEXT
    # ==================================================

    def next(
        self,
        previous_signature=None,
    ):

        def task():
            skip_next()

            track = (
                self.wait_for_track_change(
                    previous_signature
                )
            )

            return self.build_result(
                track
            )

        self.submit(
            "next",
            task,
        )

    # ==================================================
    # PREVIOUS
    # ==================================================

    def previous(
        self,
        previous_signature=None,
    ):

        def task():
            skip_previous()

            track = (
                self.wait_for_track_change(
                    previous_signature
                )
            )

            return self.build_result(
                track
            )

        self.submit(
            "previous",
            task,
        )

    # ==================================================
    # SEEK
    # ==================================================

    def seek(
        self,
        position_ms,
    ):

        def task():
            seek_to(
                position_ms
            )

            track = (
                self.wait_for_seek_position(
                    position_ms
                )
            )

            return self.build_result(
                track
            )

        self.submit(
            "seek",
            task,
        )

    # ==================================================
    # REFRESH
    # ==================================================

    def refresh(
        self,
    ):

        def task():

            track = get_current_track()

            return self.build_result(
                track
            )

        self.submit(
            "refresh",
            task,
        )

    # ==================================================
    # SHUTDOWN
    # ==================================================

    def shutdown(
        self,
    ):

        self.executor.shutdown(
            wait=False,
            cancel_futures=True,
        )
