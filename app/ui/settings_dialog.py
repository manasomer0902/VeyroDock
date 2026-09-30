from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QAbstractItemView,
    QSlider,
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


class SettingsDialog(QDialog):
    """Clean settings panel with live widget-size preview."""

    # opacity, always_on_top, reset_position, size_percent
    settings_saved = Signal(int, bool, bool, int)
    quotes_requested = Signal()
    size_preview = Signal(int)

    def __init__(
        self,
        opacity,
        always_on_top,
        size_percent,
        parent=None,
    ):
        super().__init__(parent)

        self.setWindowTitle("Spotify Widget Settings")
        self.setFixedSize(420, 455)

        # Clear, familiar Windows UI font.
        self.setFont(QFont("Segoe UI", 10))

        self.opacity_value = max(0, min(100, int(opacity)))
        self.always_on_top_value = bool(always_on_top)
        self.size_percent_value = max(
            0,
            min(100, int(size_percent)),
        )
        self.reset_position_requested = False

        self.setStyleSheet(
            f"""
            QDialog {{
                background: #0C0C0F;
                color: {PRIMARY_TEXT};
            }}

            QLabel#title {{
                color: {PRIMARY_TEXT};
                font-family: "Segoe UI";
                font-size: 20px;
                font-weight: 700;
                background: transparent;
            }}

            QLabel#subtitle {{
                color: {SECONDARY_TEXT};
                font-family: "Segoe UI";
                font-size: 11px;
                background: transparent;
            }}

            QLabel#sectionTitle {{
                color: {ACCENT_COLOR};
                font-family: "Segoe UI";
                font-size: 11px;
                font-weight: 700;
                background: transparent;
                letter-spacing: 1px;
            }}

            QLabel#valueLabel {{
                color: {PRIMARY_TEXT};
                background: rgba(212, 162, 76, 18);
                border: 1px solid rgba(212, 162, 76, 85);
                border-radius: 8px;
                padding: 0 6px;
                font-family: "Segoe UI";
                font-size: 11px;
                font-weight: 700;
            }}

            QLabel#endpointLabel {{
                color: {MUTED_TEXT};
                font-family: "Segoe UI";
                font-size: 9px;
                font-weight: 600;
                background: transparent;
            }}

            QLabel#hintLabel {{
                color: {SECONDARY_TEXT};
                font-family: "Segoe UI";
                font-size: 10px;
                background: transparent;
            }}

            QLabel#formLabel {{
                color: {PRIMARY_TEXT};
                font-family: "Segoe UI";
                font-size: 12px;
                font-weight: 600;
                background: transparent;
            }}

            QSlider::groove:horizontal {{
                height: 5px;
                background: rgba(255, 255, 255, 30);
                border-radius: 2px;
            }}

            QSlider::sub-page:horizontal {{
                background: {ACCENT_COLOR};
                border-radius: 2px;
            }}

            QSlider::add-page:horizontal {{
                background: rgba(255, 255, 255, 30);
                border-radius: 2px;
            }}

            QSlider::handle:horizontal {{
                width: 14px;
                height: 14px;
                margin: -5px 0;
                background: {ACCENT_COLOR};
                border: 2px solid rgba(255, 255, 255, 125);
                border-radius: 7px;
            }}

            QSlider::handle:horizontal:hover {{
                width: 16px;
                height: 16px;
                margin: -6px 0;
                background: {ACCENT_HOVER};
                border: 2px solid rgba(255, 255, 255, 165);
                border-radius: 8px;
            }}

            QCheckBox {{
                color: {PRIMARY_TEXT};
                font-family: "Segoe UI";
                font-size: 12px;
                spacing: 8px;
                background: transparent;
            }}

            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 5px;
                border: 1px solid rgba(212, 162, 76, 90);
                background: rgba(255, 255, 255, 10);
            }}

            QCheckBox::indicator:checked {{
                border: 1px solid {ACCENT_COLOR};
                background: rgba(212, 162, 76, 95);
            }}

            QPushButton#resetPosition {{
                color: {PRIMARY_TEXT};
                background: rgba(255, 255, 255, 5);
                border: 1px solid {CARD_BORDER};
                border-radius: 9px;
                padding: 9px 14px;
                font-family: "Segoe UI";
                font-size: 12px;
                font-weight: 600;
            }}

            QPushButton#resetPosition:hover {{
                color: {ACCENT_HOVER};
                border: 1px solid rgba(212, 162, 76, 90);
                background: rgba(212, 162, 76, 20);
            }}

            QPushButton#manageQuotes {{
                color: {PRIMARY_TEXT};
                background: rgba(212, 162, 76, 14);
                border: 1px solid rgba(212, 162, 76, 65);
                border-radius: 9px;
                padding: 9px 14px;
                font-family: "Segoe UI";
                font-size: 12px;
                font-weight: 600;
            }}

            QPushButton#manageQuotes:hover {{
                color: {ACCENT_HOVER};
                background: rgba(212, 162, 76, 24);
                border: 1px solid rgba(212, 162, 76, 100);
            }}

            QDialogButtonBox QPushButton {{
                min-width: 86px;
                min-height: 34px;
                padding: 7px 14px;
                border-radius: 9px;
                font-family: "Segoe UI";
                font-size: 11px;
                font-weight: 600;
            }}

            QDialogButtonBox QPushButton[text="OK"] {{
                color: #0C0C0F;
                background: {ACCENT_COLOR};
                border: 1px solid {ACCENT_COLOR};
            }}

            QDialogButtonBox QPushButton[text="OK"]:hover {{
                background: {ACCENT_HOVER};
                border: 1px solid {ACCENT_HOVER};
            }}

            QDialogButtonBox QPushButton[text="Cancel"] {{
                color: {SECONDARY_TEXT};
                background: transparent;
                border: 1px solid {CARD_BORDER};
            }}

            QDialogButtonBox QPushButton[text="Cancel"]:hover {{
                color: {PRIMARY_TEXT};
                background: rgba(255, 255, 255, 18);
            }}
            """
        )

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(10)

        title = QLabel("Widget Settings")
        title.setObjectName("title")
        layout.addWidget(title)

        subtitle = QLabel("Control size, transparency, and window behavior.")
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle)

        layout.addSpacing(5)

        # ==================================================
        # WIDGET SIZE
        # ==================================================

        size_title = QLabel("WIDGET SIZE")
        size_title.setObjectName("sectionTitle")
        layout.addWidget(size_title)

        size_row = QHBoxLayout()
        size_row.setSpacing(10)

        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(0, 100)
        self.size_slider.setValue(self.size_percent_value)
        self.size_slider.setCursor(Qt.CursorShape.PointingHandCursor)
        self.size_slider.setPageStep(10)

        self.size_value_label = QLabel()
        self.size_value_label.setObjectName("valueLabel")
        self.size_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.size_value_label.setFixedSize(54, 30)

        size_row.addWidget(self.size_slider, 1)
        size_row.addWidget(self.size_value_label)
        layout.addLayout(size_row)

        size_hints = QHBoxLayout()
        size_hints.setContentsMargins(2, 0, 2, 0)

        smallest = QLabel("Smallest")
        smallest.setObjectName("hintLabel")
        largest = QLabel("Largest")
        largest.setObjectName("hintLabel")

        size_hints.addWidget(smallest)
        size_hints.addStretch()
        size_hints.addWidget(largest)
        layout.addLayout(size_hints)

        self.size_slider.valueChanged.connect(self.handle_size_changed)
        self.update_size_label(self.size_percent_value)

        layout.addSpacing(6)

        # ==================================================
        # APPEARANCE
        # ==================================================

        appearance_title = QLabel("APPEARANCE")
        appearance_title.setObjectName("sectionTitle")
        layout.addWidget(appearance_title)

        opacity_row = QHBoxLayout()
        opacity_row.setContentsMargins(0, 0, 0, 0)
        opacity_row.setSpacing(12)

        opacity_text = QLabel("Opacity")
        opacity_text.setObjectName("formLabel")
        opacity_text.setFixedWidth(62)

        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        # 0% is the minimum. The full range is 0% to 100%.
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(self.opacity_value)
        self.opacity_slider.setCursor(Qt.CursorShape.PointingHandCursor)
        self.opacity_slider.setPageStep(10)
        self.opacity_slider.valueChanged.connect(
            self.handle_opacity_changed
        )

        self.opacity_label = QLabel()
        self.opacity_label.setObjectName("valueLabel")
        self.opacity_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.opacity_label.setFixedSize(62, 30)

        opacity_row.addWidget(opacity_text)
        opacity_row.addWidget(self.opacity_slider, 1)
        opacity_row.addWidget(self.opacity_label)
        layout.addLayout(opacity_row)

        # Explicit endpoints so 0% is always visible.
        opacity_endpoints = QHBoxLayout()
        opacity_endpoints.setContentsMargins(64, 0, 74, 0)

        opacity_min = QLabel("0%")
        opacity_min.setObjectName("endpointLabel")

        opacity_max = QLabel("100%")
        opacity_max.setObjectName("endpointLabel")

        opacity_endpoints.addWidget(opacity_min)
        opacity_endpoints.addStretch()
        opacity_endpoints.addWidget(opacity_max)
        layout.addLayout(opacity_endpoints)

        window_row = QHBoxLayout()
        window_row.setContentsMargins(0, 0, 0, 0)
        window_row.setSpacing(12)

        window_text = QLabel("Window")
        window_text.setObjectName("formLabel")
        window_text.setFixedWidth(62)

        self.always_on_top_checkbox = QCheckBox(
            "Keep widget above other windows"
        )
        self.always_on_top_checkbox.setChecked(
            self.always_on_top_value
        )

        window_row.addWidget(window_text)
        window_row.addWidget(self.always_on_top_checkbox)
        window_row.addStretch()
        layout.addLayout(window_row)

        self.update_opacity_label(self.opacity_value)

        layout.addSpacing(6)

        self.manage_quotes_button = QPushButton(
            "Manage Quotes"
        )
        self.manage_quotes_button.setObjectName("manageQuotes")
        self.manage_quotes_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.manage_quotes_button.clicked.connect(
            self.quotes_requested.emit
        )
        layout.addWidget(self.manage_quotes_button)

        self.reset_position_button = QPushButton(
            "Reset window position"
        )
        self.reset_position_button.setObjectName("resetPosition")
        self.reset_position_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.reset_position_button.clicked.connect(
            self.request_reset_position
        )
        layout.addWidget(self.reset_position_button)

        layout.addStretch()

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def update_size_label(self, value):
        self.size_value_label.setText(f"{int(value)}%")

    def handle_size_changed(self, value):
        self.size_percent_value = int(value)
        self.update_size_label(value)
        self.size_preview.emit(int(value))

    def update_opacity_label(self, value):
        self.opacity_label.setText(f"{int(value)}%")

    def handle_opacity_changed(self, value):
        self.opacity_value = int(value)
        self.update_opacity_label(value)

    def request_reset_position(self):
        self.reset_position_requested = True
        self.reset_position_button.setText(
            "Position will reset on Apply"
        )

    def save_settings(self):
        self.settings_saved.emit(
            int(self.opacity_value),
            bool(self.always_on_top_checkbox.isChecked()),
            bool(self.reset_position_requested),
            int(self.size_percent_value),
        )
        self.accept()



class QuotesDialog(QDialog):
    """Manage the quotes shown at the bottom of the widget."""

    quotes_saved = Signal(list, int)

    def __init__(self, quotes, active_index=0, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Widget Quotes")
        self.setFixedSize(520, 500)
        self.setFont(QFont("Segoe UI", 10))

        self.quotes = list(quotes)
        self.active_index = (
            max(0, min(len(self.quotes) - 1, int(active_index)))
            if self.quotes
            else 0
        )

        self.setStyleSheet(
            f"""
            QDialog {{
                background: #0C0C0F;
                color: {PRIMARY_TEXT};
            }}

            QLabel#title {{
                color: {PRIMARY_TEXT};
                font-size: 20px;
                font-weight: 700;
                background: transparent;
            }}

            QLabel#subtitle {{
                color: {SECONDARY_TEXT};
                font-size: 11px;
                background: transparent;
            }}

            QLabel#sectionTitle {{
                color: {ACCENT_COLOR};
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 1px;
                background: transparent;
            }}

            QListWidget {{
                color: {PRIMARY_TEXT};
                background: rgba(255,255,255,7);
                border: 1px solid {CARD_BORDER};
                border-radius: 10px;
                padding: 6px;
                outline: none;
            }}

            QListWidget::item {{
                padding: 10px 12px;
                border-radius: 7px;
                margin: 2px 0;
            }}

            QListWidget::item:selected {{
                color: {PRIMARY_TEXT};
                background: rgba(212,162,76,38);
                border: 1px solid rgba(212,162,76,75);
            }}

            QLineEdit {{
                color: {PRIMARY_TEXT};
                background: rgba(255,255,255,8);
                border: 1px solid {CARD_BORDER};
                border-radius: 9px;
                padding: 10px 12px;
                font-size: 12px;
                selection-background-color: rgba(212,162,76,90);
            }}

            QLineEdit:focus {{
                border: 1px solid rgba(212,162,76,110);
            }}

            QPushButton {{
                color: {PRIMARY_TEXT};
                background: rgba(255,255,255,6);
                border: 1px solid {CARD_BORDER};
                border-radius: 9px;
                padding: 8px 13px;
                font-size: 11px;
                font-weight: 600;
            }}

            QPushButton:hover {{
                color: {ACCENT_HOVER};
                background: rgba(212,162,76,18);
                border: 1px solid rgba(212,162,76,85);
            }}

            QPushButton#useQuote {{
                color: #0C0C0F;
                background: {ACCENT_COLOR};
                border: 1px solid {ACCENT_COLOR};
            }}

            QPushButton#useQuote:hover {{
                background: {ACCENT_HOVER};
                border: 1px solid {ACCENT_HOVER};
            }}

            QDialogButtonBox QPushButton {{
                min-width: 86px;
                min-height: 34px;
            }}
            """
        )

        self.setup_ui()
        self.refresh_list()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(10)

        title = QLabel("Quotes")
        title.setObjectName("title")
        layout.addWidget(title)

        subtitle = QLabel(
            "Add your own lines and choose the one shown on the widget."
        )
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle)

        section = QLabel("YOUR QUOTES")
        section.setObjectName("sectionTitle")
        layout.addWidget(section)

        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.list_widget.itemDoubleClicked.connect(
            lambda _item: self.use_selected_quote()
        )
        layout.addWidget(self.list_widget, 1)

        add_row = QHBoxLayout()
        add_row.setSpacing(8)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Write your quote…")
        self.input.returnPressed.connect(self.add_quote)
        add_row.addWidget(self.input, 1)

        add_button = QPushButton("+ Add")
        add_button.clicked.connect(self.add_quote)
        add_row.addWidget(add_button)
        layout.addLayout(add_row)

        actions = QHBoxLayout()
        actions.setSpacing(8)

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_selected_quote)
        actions.addWidget(delete_button)

        self.use_button = QPushButton("Use Selected")
        self.use_button.setObjectName("useQuote")
        self.use_button.clicked.connect(self.use_selected_quote)
        actions.addWidget(self.use_button)
        layout.addLayout(actions)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.save_and_close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def refresh_list(self):
        self.list_widget.clear()

        for index, quote in enumerate(self.quotes):
            item = QListWidgetItem(quote)
            item.setToolTip(quote)
            self.list_widget.addItem(item)

        if self.quotes:
            self.active_index = max(
                0, min(self.active_index, len(self.quotes) - 1)
            )
            self.list_widget.setCurrentRow(self.active_index)

    def add_quote(self):
        quote = self.input.text().strip()
        if not quote:
            return

        self.quotes.append(quote)
        self.active_index = len(self.quotes) - 1
        self.input.clear()
        self.refresh_list()

    def delete_selected_quote(self):
        row = self.list_widget.currentRow()
        if row < 0 or row >= len(self.quotes):
            return

        self.quotes.pop(row)

        if not self.quotes:
            self.active_index = 0
        elif row < self.active_index:
            self.active_index -= 1
        elif row == self.active_index:
            self.active_index = min(
                row,
                len(self.quotes) - 1,
            )

        self.refresh_list()

    def use_selected_quote(self):
        row = self.list_widget.currentRow()
        if 0 <= row < len(self.quotes):
            self.active_index = row
            self.refresh_list()

    def save_and_close(self):
        if self.quotes:
            self.active_index = max(
                0,
                min(self.active_index, len(self.quotes) - 1),
            )
        else:
            self.active_index = 0

        self.quotes_saved.emit(
            list(self.quotes),
            int(self.active_index),
        )
        self.accept()
