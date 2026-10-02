import json
import os
import sys
import ctypes

from PySide6.QtWidgets import QApplication

from app.spotify.auth_runner import AuthRunner
from app.ui.connection_dialog import ConnectionDialog
from app.ui.icons import get_veyrodock_icon
from app.ui.window import SpotifyWidget

if getattr(sys, "frozen", False) and sys.platform == "win32":
    APP_DATA_DIR = os.path.join(
        os.environ.get(
            "LOCALAPPDATA",
            os.path.expanduser("~"),
        ),
        "VeyroDock",
        "data",
    )
else:
    APP_DATA_DIR = "data"

TOKEN_FILE = os.path.join(
    APP_DATA_DIR,
    "token.json",
)


def set_windows_app_id():
    """Set the Windows application identity used by the taskbar."""
    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "VeyroDock.VeyroDock"
        )


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
    set_windows_app_id()

    app = QApplication(sys.argv)
    app.setApplicationName("VeyroDock")
    app.setWindowIcon(get_veyrodock_icon())
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
        dialog.set_error(f"Connection failed: {message}")

    def authentication_finished():
        dialog.set_success()

        dialog.accept()

        state["window"] = start_widget(app)

    dialog.connect_requested.connect(start_authentication)

    auth_runner.failed.connect(authentication_failed)

    auth_runner.finished.connect(authentication_finished)

    dialog.exec()

    # If the user cancelled the connection dialog,
    # there is nothing else to run.
    if state["window"] is None:
        app.quit()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
