from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from app.ui.styles import (
    ACCENT_COLOR,
    ACCENT_HOVER,
    CARD_BORDER,
    MUTED_TEXT,
    PRIMARY_TEXT,
    SECONDARY_TEXT,
)


class ConnectionDialog(QDialog):
    """First-run Spotify connection dialog."""

    connect_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Connect Spotify")
        self.setFixedSize(420, 300)
        self.setFont(QFont("Segoe UI", 10))

        self.setStyleSheet(
            f"""
            QDialog {{
                background: #0C0C0F;
                color: {PRIMARY_TEXT};
            }}

            QLabel#title {{
                color: {PRIMARY_TEXT};
                font-family: "Segoe UI";
                font-size: 21px;
                font-weight: 700;
                background: transparent;
            }}

            QLabel#subtitle {{
                color: {SECONDARY_TEXT};
                font-family: "Segoe UI";
                font-size: 11px;
                background: transparent;
            }}

            QLabel#status {{
                color: {MUTED_TEXT};
                font-family: "Segoe UI";
                font-size: 10px;
                background: transparent;
            }}

            QPushButton#connectButton {{
                color: #0C0C0F;
                background: {ACCENT_COLOR};
                border: 1px solid {ACCENT_COLOR};
                border-radius: 9px;
                padding: 10px 16px;
                font-family: "Segoe UI";
                font-size: 12px;
                font-weight: 700;
            }}

            QPushButton#connectButton:hover {{
                background: {ACCENT_HOVER};
                border: 1px solid {ACCENT_HOVER};
            }}

            QPushButton#connectButton:disabled {{
                color: rgba(12, 12, 15, 130);
                background: rgba(212, 162, 76, 80);
                border: 1px solid rgba(212, 162, 76, 80);
            }}

            QPushButton#cancelButton {{
                color: {SECONDARY_TEXT};
                background: transparent;
                border: 1px solid {CARD_BORDER};
                border-radius: 9px;
                padding: 9px 14px;
                font-family: "Segoe UI";
                font-size: 11px;
                font-weight: 600;
            }}

            QPushButton#cancelButton:hover {{
                color: {PRIMARY_TEXT};
                background: rgba(255, 255, 255, 18);
            }}
            """
        )

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 28, 30, 24)
        layout.setSpacing(12)

        title = QLabel("Connect Spotify")
        title.setObjectName("title")
        layout.addWidget(title)

        subtitle = QLabel(
            "Connect your Spotify account to start using the desktop widget."
        )
        subtitle.setObjectName("subtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        layout.addSpacing(12)

        info = QLabel(
            "A Spotify authorization page will open in your browser. "
            "Approve access, then return to the widget."
        )
        info.setObjectName("subtitle")
        info.setWordWrap(True)
        layout.addWidget(info)

        layout.addSpacing(6)

        self.status_label = QLabel("Ready to connect.")
        self.status_label.setObjectName("status")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        layout.addStretch()

        self.connect_button = QPushButton("Connect Spotify")
        self.connect_button.setObjectName("connectButton")
        self.connect_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.connect_button.clicked.connect(
            self.connect_requested.emit
        )
        layout.addWidget(self.connect_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.cancel_button.clicked.connect(self.reject)
        layout.addWidget(self.cancel_button)

    def set_connecting(self):
        self.status_label.setText(
            "Waiting for Spotify authorization in your browser..."
        )
        self.connect_button.setEnabled(False)
        self.cancel_button.setEnabled(False)

    def set_error(self, message):
        self.status_label.setText(message)
        self.connect_button.setEnabled(True)
        self.cancel_button.setEnabled(True)

    def set_success(self):
        self.status_label.setText(
            "Spotify connected successfully."
        )
        self.connect_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
