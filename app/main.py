import json
import os
import sys

from PySide6.QtWidgets import QApplication

from app.spotify.auth_runner import AuthRunner
from app.ui.connection_dialog import ConnectionDialog
from app.ui.window import SpotifyWidget


TOKEN_FILE = "data/token.json"


def spotify_token_exists():
    """Return True when a usable local Spotify token exists."""
    if not os.path.exists(TOKEN_FILE):
        return False

    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as file:
            token_data = json.load(file)

        return bool(token_data.get("access_token"))

    except (OSError, json.JSONDecodeError):
        return False


def start_widget(app):
    """Start the existing widget using the current QApplication."""
    window = SpotifyWidget()
    window.show()

    return window


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    # ==================================================
    # EXISTING USER
    # ==================================================

    if spotify_token_exists():
        window = start_widget(app)

        try:
            exit_code = app.exec()
        except KeyboardInterrupt:
            window.force_exit = True
            window.close()
            exit_code = 0

        sys.exit(exit_code)

    # ==================================================
    # FIRST-TIME USER
    # ==================================================

    dialog = ConnectionDialog()
    auth_runner = AuthRunner(parent=dialog)

    state = {
        "window": None,
    }

    def start_authentication():
        dialog.set_connecting()
        auth_runner.start()

    def authentication_failed(message):
        dialog.set_error(
            f"Connection failed: {message}"
        )

    def authentication_finished():
        dialog.set_success()

        dialog.accept()

        state["window"] = start_widget(app)

    dialog.connect_requested.connect(
        start_authentication
    )

    auth_runner.failed.connect(
        authentication_failed
    )

    auth_runner.finished.connect(
        authentication_finished
    )

    dialog.exec()

    # If the user cancelled the connection dialog,
    # there is nothing else to run.
    if state["window"] is None:
        app.quit()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
