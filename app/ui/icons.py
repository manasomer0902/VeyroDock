import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QColor,
    QIcon,
    QPainter,
    QPainterPath,
    QPixmap,
)


def get_veyrodock_icon_path():
    """Return the bundled VeyroDock PNG icon path in source or PyInstaller builds."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        root = Path(sys._MEIPASS)
    else:
        root = Path(__file__).resolve().parents[2]

    return root / "assets" / "icons" / "veyrodock.png"


def get_veyrodock_icon():
    """Return the VeyroDock application icon."""
    icon_path = get_veyrodock_icon_path()
    return QIcon(str(icon_path)) if icon_path.exists() else QIcon()


def create_icon(
    name,
    color="#F5F2EA",
    size=24,
):
    pixmap = QPixmap(
        size,
        size,
    )

    pixmap.fill(
        Qt.GlobalColor.transparent
    )

    painter = QPainter(
        pixmap
    )

    painter.setRenderHint(
        QPainter.RenderHint.Antialiasing
    )

    pen = painter.pen()

    pen.setColor(
        QColor(color)
    )

    pen.setWidthF(
        max(1.7, size * 0.08)
    )

    pen.setCapStyle(
        Qt.PenCapStyle.RoundCap
    )

    pen.setJoinStyle(
        Qt.PenJoinStyle.RoundJoin
    )

    painter.setPen(
        pen
    )

    painter.setBrush(
        Qt.BrushStyle.NoBrush
    )

    center = size / 2

    if name == "previous":
        path = QPainterPath()

        path.moveTo(
            size * 0.72,
            size * 0.20,
        )

        path.lineTo(
            size * 0.36,
            center,
        )

        path.lineTo(
            size * 0.72,
            size * 0.80,
        )

        painter.drawPath(
            path
        )

        painter.drawLine(
            int(size * 0.22),
            int(size * 0.20),
            int(size * 0.22),
            int(size * 0.80),
        )

    elif name == "next":
        path = QPainterPath()

        path.moveTo(
            size * 0.28,
            size * 0.20,
        )

        path.lineTo(
            size * 0.64,
            center,
        )

        path.lineTo(
            size * 0.28,
            size * 0.80,
        )

        painter.drawPath(
            path
        )

        painter.drawLine(
            int(size * 0.78),
            int(size * 0.20),
            int(size * 0.78),
            int(size * 0.80),
        )

    elif name == "play":

        painter.setPen(
            Qt.PenStyle.NoPen
        )

        painter.setBrush(
            QColor(color)
        )

        path = QPainterPath()

        path.moveTo(
            size * 0.34,
            size * 0.20,
        )

        path.lineTo(
            size * 0.78,
            center,
        )

        path.lineTo(
            size * 0.34,
            size * 0.80,
        )

        path.closeSubpath()

        painter.drawPath(
            path
        )

    elif name == "pause":

        painter.setPen(
            Qt.PenStyle.NoPen
        )

        painter.setBrush(
            QColor(color)
        )

        painter.drawRoundedRect(
            int(size * 0.25),
            int(size * 0.20),
            int(size * 0.18),
            int(size * 0.60),
            3,
            3,
        )

        painter.drawRoundedRect(
            int(size * 0.57),
            int(size * 0.20),
            int(size * 0.18),
            int(size * 0.60),
            3,
            3,
        )

    elif name == "close":

        painter.drawLine(
            int(size * 0.28),
            int(size * 0.28),
            int(size * 0.72),
            int(size * 0.72),
        )

        painter.drawLine(
            int(size * 0.72),
            int(size * 0.28),
            int(size * 0.28),
            int(size * 0.72),
        )

    elif name == "settings":

        # Gear-like icon.
        import math

        painter.setPen(
            Qt.PenStyle.NoPen
        )

        painter.setBrush(
            QColor(color)
        )

        outer_radius = size * 0.34
        inner_radius = size * 0.15

        points = []

        teeth = 8

        for i in range(teeth * 2):

            angle = (
                i
                * math.pi
                / teeth
                - math.pi / 2
            )

            radius = (
                outer_radius
                if i % 2 == 0
                else outer_radius * 0.78
            )

            x = (
                center
                + math.cos(angle) * radius
            )

            y = (
                center
                + math.sin(angle) * radius
            )

            points.append(
                (x, y)
            )

        path = QPainterPath()

        path.moveTo(
            points[0][0],
            points[0][1],
        )

        for x, y in points[1:]:

            path.lineTo(
                x,
                y,
            )

        path.closeSubpath()

        painter.drawPath(
            path
        )

        painter.setBrush(
            QColor("#0E0E10")
        )

        painter.drawEllipse(
            int(center - inner_radius),
            int(center - inner_radius),
            int(inner_radius * 2),
            int(inner_radius * 2),
        )

    elif name == "music":

        painter.setPen(
            pen
        )

        painter.drawLine(
            int(size * 0.62),
            int(size * 0.20),
            int(size * 0.62),
            int(size * 0.68),
        )

        painter.drawLine(
            int(size * 0.62),
            int(size * 0.20),
            int(size * 0.82),
            int(size * 0.27),
        )

        painter.drawEllipse(
            int(size * 0.34),
            int(size * 0.58),
            int(size * 0.28),
            int(size * 0.22),
        )

    painter.end()

    return QIcon(
        pixmap
    )
