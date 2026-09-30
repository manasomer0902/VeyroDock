from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QSlider


class SeekBar(QSlider):

    seek_requested = Signal(float)

    def __init__(self, parent=None):
        super().__init__(
            Qt.Orientation.Horizontal,
            parent,
        )

        self.setRange(
            0,
            1000,
        )

        self.setTracking(
            True
        )

        self.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

    def position_to_value(self, x):

        width = self.width()

        if width <= 0:
            return 0

        percentage = x / width

        percentage = max(
            0.0,
            min(1.0, percentage),
        )

        return int(
            percentage * self.maximum()
        )

    def mousePressEvent(self, event):

        if (
            event.button()
            == Qt.MouseButton.LeftButton
        ):

            value = self.position_to_value(
                event.position().x()
            )

            self.setValue(
                value
            )

            self.setSliderDown(
                True
            )

            event.accept()

            return

        super().mousePressEvent(
            event
        )

    def mouseMoveEvent(self, event):

        if self.isSliderDown():

            value = self.position_to_value(
                event.position().x()
            )

            self.setValue(
                value
            )

            event.accept()

            return

        super().mouseMoveEvent(
            event
        )

    def mouseReleaseEvent(self, event):

        if (
            event.button()
            == Qt.MouseButton.LeftButton
            and self.isSliderDown()
        ):

            value = self.position_to_value(
                event.position().x()
            )

            self.setValue(
                value
            )

            percentage = (
                value / self.maximum()
            )

            self.setSliderDown(
                False
            )

            self.seek_requested.emit(
                percentage
            )

            event.accept()

            return

        super().mouseReleaseEvent(
            event
        )
