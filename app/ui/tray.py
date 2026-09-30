from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (
    QMenu,
    QSystemTrayIcon,
)


class SystemTray(QObject):

    show_requested = Signal()
    settings_requested = Signal()
    exit_requested = Signal()

    def __init__(
        self,
        parent=None,
    ):
        super().__init__(
            parent
        )

        self.tray = QSystemTrayIcon(
            self.create_icon(),
            parent,
        )

        self.tray.setToolTip(
            "Spotify Desktop Widget"
        )

        self.menu = QMenu()

        # ==================================================
        # SHOW
        # ==================================================

        self.show_action = self.menu.addAction(
            "Show Widget"
        )

        self.show_action.triggered.connect(
            self.show_requested.emit
        )

        # ==================================================
        # SETTINGS
        # ==================================================

        self.settings_action = self.menu.addAction(
            "Settings"
        )

        self.settings_action.triggered.connect(
            self.settings_requested.emit
        )

        # ==================================================
        # SEPARATOR
        # ==================================================

        self.menu.addSeparator()

        # ==================================================
        # EXIT
        # ==================================================

        self.exit_action = self.menu.addAction(
            "Exit"
        )

        self.exit_action.triggered.connect(
            self.exit_requested.emit
        )

        # ==================================================
        # TRAY MENU
        # ==================================================

        self.tray.setContextMenu(
            self.menu
        )

        self.tray.activated.connect(
            self.handle_activation
        )

        self.tray.show()

    @staticmethod
    def create_icon():

        size = 64

        pixmap = QPixmap(
            size,
            size,
        )

        pixmap.fill(
            QColor(
                0,
                0,
                0,
                0,
            )
        )

        painter = QPainter(
            pixmap
        )

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        painter.setBrush(
            QColor(
                212,
                162,
                76,
            )
        )

        painter.setPen(
            QColor(
                212,
                162,
                76,
            )
        )

        painter.drawEllipse(
            4,
            4,
            56,
            56,
        )

        painter.setPen(
            QColor(
                20,
                20,
                20,
            )
        )

        painter.setFont(
            QFont(
                "Segoe UI Symbol",
                30,
            )
        )

        painter.drawText(
            pixmap.rect(),
            0,
            "♪",
        )

        painter.end()

        return QIcon(
            pixmap
        )

    def handle_activation(
        self,
        reason,
    ):

        if (
            reason
            == QSystemTrayIcon.ActivationReason.DoubleClick
        ):

            self.show_requested.emit()

    def hide(self):

        self.tray.hide()
