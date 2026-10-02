import webbrowser

from PySide6.QtCore import Qt, Signal

from PySide6.QtGui import QFont

from app.ui.icons import get_veyrodock_icon

from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSlider,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

# ==========================================================

# VEYRODOCK SETTINGS VISUAL SYSTEM

# ==========================================================

BG = "#090B0D"

PANEL = "#0F1215"

PANEL_2 = "#12171A"

BORDER = "#20282A"

BORDER_SOFT = "#182023"

PRIMARY = "#F2F5F4"

SECONDARY = "#9AA5A2"

MUTED = "#66716E"

GREEN = "#21E6A4"

GREEN_HOVER = "#35F0B2"

GREEN_SOFT = "rgba(33, 230, 164, 28)"

GREEN_BORDER = "rgba(33, 230, 164, 95)"


class SettingsDialog(QDialog):
    """VeyroDock settings panel.

    The UI is redesigned only; existing settings behavior and signal

    compatibility are retained. The old widget-size control is removed from

    the visible UI, but the optional size_percent argument and five-value

    settings_saved signal are kept so the current window.py continues to work

    without modification.

    """

    # opacity, always_on_top, reset_position, size_percent

    settings_saved = Signal(int, bool, bool, int)

    size_preview = Signal(int)

    quotes_requested = Signal()

    def __init__(
        self,
        opacity,
        always_on_top,
        size_percent=47,
        parent=None,
    ):
        super().__init__(parent)

        self.setWindowTitle("VeyroDock Settings")

        self.setWindowIcon(get_veyrodock_icon())

        self.setFixedSize(640, 460)

        self.setFont(QFont("Segoe UI Variable", 10, QFont.Weight.DemiBold))

        self.opacity_value = max(0, min(100, int(opacity)))

        self.always_on_top_value = bool(always_on_top)

        self.size_percent_value = max(0, min(100, int(size_percent)))

        self.reset_position_requested = False

        self.setStyleSheet(f"""

            QDialog {{
                background: {BG};

                color: {PRIMARY};
            }}

            QLabel {{
                background: transparent;
            }}

            QFrame#root {{
                background: {BG};

                border: 1px solid {BORDER};

                border-radius: 12px;
            }}

            QLabel#headerTitle {{
                color: {PRIMARY};

                font-family: "Segoe UI Variable", "Segoe UI";

                font-size: 15px;

                font-weight: 700;
            }}

            QLabel#pageTitle {{
                color: {PRIMARY};

                font-family: "Segoe UI Variable", "Segoe UI";

                font-size: 19px;

                font-weight: 700;
            }}

            QLabel#pageSubtitle {{
                color: {SECONDARY};

                font-size: 10px;
            }}

            QLabel#sectionTitle {{
                color: {GREEN};

                font-size: 10px;

                font-weight: 700;

                letter-spacing: 1px;
            }}

            QLabel#bodyText {{
                color: {SECONDARY};

                font-size: 11px;
            }}

            QLabel#valueLabel {{
                color: {PRIMARY};

                background: {GREEN_SOFT};

                border: 1px solid {GREEN_BORDER};

                border-radius: 8px;

                min-width: 58px;

                padding: 5px 8px;

                font-size: 11px;

                font-weight: 700;
            }}

            QPushButton#navButton {{
                color: {SECONDARY};

                background: transparent;

                border: 1px solid transparent;

                border-radius: 8px;

                text-align: left;

                padding: 9px 12px;

                font-family: "Segoe UI Variable", "Segoe UI";

                font-size: 11px;

                font-weight: 600;
            }}

            QPushButton#navButton:hover {{
                color: {PRIMARY};

                background: rgba(255, 255, 255, 7);
            }}

            QPushButton#navButton:checked {{
                color: {PRIMARY};

                background: rgba(255, 255, 255, 10);

                border-left: 2px solid {GREEN};

                padding-left: 10px;
            }}

            QFrame#sidebar {{
                background: rgba(255, 255, 255, 3);

                border-right: 1px solid {BORDER};

                border-radius: 10px;
            }}

            QFrame#content {{
                background: rgba(255, 255, 255, 2);

                border: 1px solid {BORDER_SOFT};

                border-radius: 10px;
            }}

            QFrame#settingCard {{
                background: rgba(255, 255, 255, 5);

                border: 1px solid {BORDER};

                border-radius: 9px;
            }}

            QCheckBox {{
                color: {PRIMARY};

                font-size: 11px;

                spacing: 9px;

                background: transparent;
            }}

            QCheckBox::indicator {{
                width: 17px;

                height: 17px;

                border-radius: 4px;

                border: 1px solid #3A4544;

                background: #111518;
            }}

            QCheckBox::indicator:hover {{
                border: 1px solid {GREEN_BORDER};
            }}

            QCheckBox::indicator:checked {{
                background: {GREEN};

                border: 1px solid {GREEN};
            }}

            QSlider::groove:horizontal {{
                height: 5px;

                background: #27302F;

                border-radius: 2px;
            }}

            QSlider::sub-page:horizontal {{
                background: {GREEN};

                border-radius: 2px;
            }}

            QSlider::add-page:horizontal {{
                background: #27302F;

                border-radius: 2px;
            }}

            QSlider::handle:horizontal {{
                width: 14px;

                height: 14px;

                margin: -5px 0;

                background: {GREEN};

                border: 2px solid #D8FFF1;

                border-radius: 7px;
            }}

            QSlider::handle:horizontal:hover {{
                background: {GREEN_HOVER};
            }}

            QPushButton#actionButton {{
                color: {PRIMARY};

                background: rgba(255, 255, 255, 5);

                border: 1px solid {BORDER};

                border-radius: 8px;

                min-height: 32px;

                padding: 5px 12px;

                font-size: 10px;

                font-weight: 700;
            }}

            QPushButton#actionButton:hover {{
                color: {GREEN};

                background: {GREEN_SOFT};

                border: 1px solid {GREEN_BORDER};
            }}

            QPushButton#primaryButton {{
                color: #06110D;

                background: {GREEN};

                border: 1px solid {GREEN};

                border-radius: 8px;

                min-width: 82px;

                min-height: 32px;

                padding: 5px 14px;

                font-size: 10px;

                font-weight: 700;
            }}

            QPushButton#primaryButton:hover {{
                background: {GREEN_HOVER};

                border: 1px solid {GREEN_HOVER};
            }}

            QDialogButtonBox QPushButton {{
                min-width: 82px;

                min-height: 32px;

                padding: 5px 14px;

                border-radius: 8px;

                font-size: 10px;

                font-weight: 600;
            }}

            QDialogButtonBox QPushButton[text="OK"] {{
                color: #06110D;

                background: {GREEN};

                border: 1px solid {GREEN};
            }}

            QDialogButtonBox QPushButton[text="OK"]:hover {{
                background: {GREEN_HOVER};
            }}

            QDialogButtonBox QPushButton[text="Cancel"] {{
                color: {SECONDARY};

                background: transparent;

                border: 1px solid {BORDER};
            }}

            QDialogButtonBox QPushButton[text="Cancel"]:hover {{
                color: {PRIMARY};

                background: rgba(255, 255, 255, 7);
            }}

            QLineEdit {{
                color: {PRIMARY};

                background: rgba(255, 255, 255, 5);

                border: 1px solid {BORDER};

                border-radius: 8px;

                padding: 8px 10px;

                font-size: 11px;
            }}

            QLineEdit:focus {{
                border: 1px solid {GREEN_BORDER};
            }}

            QListWidget {{
                color: {PRIMARY};

                background: rgba(255, 255, 255, 4);

                border: 1px solid {BORDER};

                border-radius: 9px;

                padding: 5px;

                outline: none;
            }}

            QListWidget::item {{
                padding: 9px 10px;

                border-radius: 7px;
            }}

            QListWidget::item:selected {{
                background: {GREEN_SOFT};

                border: 1px solid {GREEN_BORDER};
            }}

            """)

        self.setup_ui()

    def setup_ui(self):
        root = QFrame()

        root.setObjectName("root")

        root_layout = QVBoxLayout(root)

        root_layout.setContentsMargins(14, 12, 14, 12)

        root_layout.setSpacing(10)

        # Header

        header = QHBoxLayout()

        header.setContentsMargins(5, 0, 3, 0)

        brand = QLabel("VeyroDock Settings")

        brand.setObjectName("headerTitle")

        header_status = QLabel("SETTINGS")

        header_status.setStyleSheet(
            f"color: {MUTED}; font-size: 8px; font-weight: 700; letter-spacing: 1px;"
        )

        header.addWidget(brand)

        header.addStretch()

        header.addWidget(header_status)

        root_layout.addLayout(header)

        # Main body

        body = QHBoxLayout()

        body.setContentsMargins(0, 0, 0, 0)

        body.setSpacing(10)

        sidebar = QFrame()

        sidebar.setObjectName("sidebar")

        sidebar.setFixedWidth(158)

        sidebar_layout = QVBoxLayout(sidebar)

        sidebar_layout.setContentsMargins(7, 9, 7, 9)

        sidebar_layout.setSpacing(4)

        self.nav_buttons = []

        nav_items = [
            ("⚙  General", 0),
            ("◈  Appearance", 1),
            ("♫  Player", 2),
            ("ⓘ  About", 3),
        ]

        for text, index in nav_items:
            button = QPushButton(text)

            button.setObjectName("navButton")

            button.setCheckable(True)

            button.setCursor(Qt.CursorShape.PointingHandCursor)

            button.clicked.connect(lambda checked=False, i=index: self.select_page(i))

            sidebar_layout.addWidget(button)

            self.nav_buttons.append(button)
        sidebar_layout.addStretch()

        version = QLabel("VeyroDock")

        version.setStyleSheet(f"color: {MUTED}; font-size: 8px; padding: 3px 6px;")

        sidebar_layout.addWidget(version)

        body.addWidget(sidebar)

        self.pages = QStackedWidget()

        self.pages.setStyleSheet("background: transparent; border: none;")

        self.pages.addWidget(self.build_general_page())

        self.pages.addWidget(self.build_appearance_page())

        self.pages.addWidget(self.build_player_page())

        self.pages.addWidget(self.build_about_page())

        body.addWidget(self.pages, 1)

        root_layout.addLayout(body, 1)

        # Bottom buttons

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )

        button_box.accepted.connect(self.save_settings)

        button_box.rejected.connect(self.reject)

        root_layout.addWidget(button_box)

        outer = QVBoxLayout(self)

        outer.setContentsMargins(0, 0, 0, 0)

        outer.addWidget(root)

        self.select_page(0)

    def build_general_page(self):
        page = QFrame()

        page.setObjectName("content")

        layout = QVBoxLayout(page)

        layout.setContentsMargins(18, 16, 18, 12)

        layout.setSpacing(10)

        title = QLabel("General")

        title.setObjectName("pageTitle")

        layout.addWidget(title)

        subtitle = QLabel("Window behavior and quick controls.")

        subtitle.setObjectName("pageSubtitle")

        layout.addWidget(subtitle)

        layout.addSpacing(8)

        section = QLabel("WINDOW")

        section.setObjectName("sectionTitle")

        layout.addWidget(section)

        card = QFrame()

        card.setObjectName("settingCard")

        card_layout = QVBoxLayout(card)

        card_layout.setContentsMargins(13, 10, 13, 10)

        card_layout.setSpacing(10)

        self.always_on_top_checkbox = QCheckBox("Keep widget above other windows")

        self.always_on_top_checkbox.setChecked(self.always_on_top_value)

        card_layout.addWidget(self.always_on_top_checkbox)

        position_hint = QLabel(
            "When enabled, VeyroDock stays above normal application windows."
        )

        position_hint.setObjectName("bodyText")

        position_hint.setWordWrap(True)

        card_layout.addWidget(position_hint)

        layout.addWidget(card)

        section2 = QLabel("QUICK ACTIONS")

        section2.setObjectName("sectionTitle")

        layout.addWidget(section2)

        self.manage_quotes_button = QPushButton("Manage Quotes")

        self.manage_quotes_button.setObjectName("actionButton")

        self.manage_quotes_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.manage_quotes_button.clicked.connect(self.quotes_requested.emit)

        layout.addWidget(self.manage_quotes_button)

        self.reset_position_button = QPushButton("Reset window position")

        self.reset_position_button.setObjectName("actionButton")

        self.reset_position_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.reset_position_button.clicked.connect(self.request_reset_position)

        layout.addWidget(self.reset_position_button)

        self.contact_us_button = QPushButton("Contact Us")

        self.contact_us_button.setObjectName("actionButton")

        self.contact_us_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.contact_us_button.clicked.connect(self.open_contact_dialog)

        layout.addWidget(self.contact_us_button)

        layout.addStretch()

        return page

    def build_appearance_page(self):
        page = QFrame()

        page.setObjectName("content")

        layout = QVBoxLayout(page)

        layout.setContentsMargins(18, 16, 18, 12)

        layout.setSpacing(10)

        title = QLabel("Appearance")

        title.setObjectName("pageTitle")

        layout.addWidget(title)

        subtitle = QLabel("Control the visual transparency of the widget.")

        subtitle.setObjectName("pageSubtitle")

        layout.addWidget(subtitle)

        layout.addSpacing(10)

        section = QLabel("OPACITY")

        section.setObjectName("sectionTitle")

        layout.addWidget(section)

        card = QFrame()

        card.setObjectName("settingCard")

        card_layout = QVBoxLayout(card)

        card_layout.setContentsMargins(13, 13, 13, 13)

        card_layout.setSpacing(10)

        top_row = QHBoxLayout()

        opacity_text = QLabel("Widget opacity")

        opacity_text.setStyleSheet(
            f"color: {PRIMARY}; font-size: 11px; font-weight: 600;"
        )

        self.opacity_label = QLabel()

        self.opacity_label.setObjectName("valueLabel")

        self.opacity_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        top_row.addWidget(opacity_text)

        top_row.addStretch()

        top_row.addWidget(self.opacity_label)

        card_layout.addLayout(top_row)

        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)

        self.opacity_slider.setRange(0, 100)

        self.opacity_slider.setValue(self.opacity_value)

        self.opacity_slider.setCursor(Qt.CursorShape.PointingHandCursor)

        self.opacity_slider.setPageStep(10)

        self.opacity_slider.valueChanged.connect(self.handle_opacity_changed)

        card_layout.addWidget(self.opacity_slider)

        endpoints = QHBoxLayout()

        low = QLabel("0%")

        low.setStyleSheet(f"color: {MUTED}; font-size: 8px;")

        high = QLabel("100%")

        high.setStyleSheet(f"color: {MUTED}; font-size: 8px;")

        endpoints.addWidget(low)

        endpoints.addStretch()

        endpoints.addWidget(high)

        card_layout.addLayout(endpoints)

        layout.addWidget(card)

        hint = QLabel("The widget keeps a small minimum visibility even at 0%.")

        hint.setObjectName("bodyText")

        hint.setWordWrap(True)

        layout.addWidget(hint)

        layout.addStretch()

        self.update_opacity_label(self.opacity_value)

        return page

    def build_player_page(self):
        page = QFrame()

        page.setObjectName("content")

        layout = QVBoxLayout(page)

        layout.setContentsMargins(18, 16, 18, 12)

        layout.setSpacing(10)

        title = QLabel("Player")

        title.setObjectName("pageTitle")

        layout.addWidget(title)

        subtitle = QLabel("Playback controls are handled directly by VeyroDock.")

        subtitle.setObjectName("pageSubtitle")

        subtitle.setWordWrap(True)

        layout.addWidget(subtitle)

        layout.addSpacing(10)

        section = QLabel("PLAYBACK")

        section.setObjectName("sectionTitle")

        layout.addWidget(section)

        card = QFrame()

        card.setObjectName("settingCard")

        card_layout = QVBoxLayout(card)

        card_layout.setContentsMargins(14, 14, 14, 14)

        card_layout.setSpacing(8)

        info = QLabel(
            "Use the main widget for Previous, Play / Pause, Next, "
            "Seek, and Volume controls."
        )

        info.setObjectName("bodyText")

        info.setWordWrap(True)

        card_layout.addWidget(info)

        layout.addWidget(card)

        layout.addStretch()

        return page

    def build_about_page(self):
        page = QFrame()

        page.setObjectName("content")

        layout = QVBoxLayout(page)

        layout.setContentsMargins(18, 16, 18, 12)

        layout.setSpacing(10)

        title = QLabel("About")

        title.setObjectName("pageTitle")

        layout.addWidget(title)

        subtitle = QLabel(
            "A lightweight Spotify desktop widget built around VeyroDock."
        )

        subtitle.setObjectName("pageSubtitle")

        subtitle.setWordWrap(True)

        layout.addWidget(subtitle)

        layout.addSpacing(10)

        section = QLabel("VEYRODOCK")

        section.setObjectName("sectionTitle")

        layout.addWidget(section)

        card = QFrame()

        card.setObjectName("settingCard")

        card_layout = QVBoxLayout(card)

        card_layout.setContentsMargins(14, 14, 14, 14)

        card_layout.setSpacing(7)

        name = QLabel("VeyroDock")

        name.setStyleSheet(f"color: {PRIMARY}; font-size: 16px; font-weight: 700;")

        description = QLabel("Spotify desktop playback widget.")

        description.setObjectName("bodyText")

        status = QLabel("Built for Windows • Desktop")

        status.setStyleSheet(f"color: {MUTED}; font-size: 9px;")

        card_layout.addWidget(name)

        card_layout.addWidget(description)

        card_layout.addWidget(status)

        layout.addWidget(card)

        layout.addStretch()

        return page

    def select_page(self, index):
        index = max(0, min(index, len(self.nav_buttons) - 1))

        self.pages.setCurrentIndex(index)

        for i, button in enumerate(self.nav_buttons):
            button.setChecked(i == index)

    def update_opacity_label(self, value):
        self.opacity_label.setText(f"{int(value)}%")

    def handle_opacity_changed(self, value):
        self.opacity_value = int(value)

        self.update_opacity_label(value)

    def request_reset_position(self):
        self.reset_position_requested = True

        self.reset_position_button.setText("Position will reset on Apply")

    def open_contact_dialog(self):
        dialog = ContactDialog(parent=self)

        dialog.exec()

    def save_settings(self):
        self.settings_saved.emit(
            int(self.opacity_value),
            bool(self.always_on_top_checkbox.isChecked()),
            bool(self.reset_position_requested),
            int(self.size_percent_value),
        )

        self.accept()


class ContactDialog(QDialog):
    """Contact and feedback dialog."""

    CONTACT_EMAIL = "manasomer09@gmail.com"

    WHATSAPP_NUMBER = "917007527711"

    WHATSAPP_DISPLAY = "+91 7007527711"

    INSTAGRAM_USERNAME = "manasomer09"

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Contact Us")

        self.setFixedSize(430, 400)

        self.setFont(QFont("Segoe UI", 10))

        self.setStyleSheet(f"""

            QDialog {{
                background: {BG};

                color: {PRIMARY};
            }}

            QLabel#title {{
                color: {PRIMARY};

                font-family: "Segoe UI Variable", "Segoe UI";

                font-size: 19px;

                font-weight: 700;
            }}

            QLabel#subtitle {{
                color: {SECONDARY};

                font-size: 10px;
            }}

            QLabel#contactValue {{
                color: {GREEN};

                background: {GREEN_SOFT};

                border: 1px solid {GREEN_BORDER};

                border-radius: 8px;

                padding: 9px 10px;

                font-family: "Segoe UI Variable", "Segoe UI";

                font-size: 11px;

                font-weight: 600;
            }}

            QPushButton {{
                color: {PRIMARY};

                background: rgba(255, 255, 255, 5);

                border: 1px solid {BORDER};

                border-radius: 8px;

                min-height: 31px;

                padding: 5px 12px;

                font-size: 10px;

                font-weight: 600;
            }}

            QPushButton:hover {{
                color: {GREEN};

                background: {GREEN_SOFT};

                border: 1px solid {GREEN_BORDER};
            }}

            QPushButton#closeButton {{
                color: #06110D;

                background: {GREEN};

                border: 1px solid {GREEN};

                min-width: 78px;
            }}

            QPushButton#closeButton:hover {{
                background: {GREEN_HOVER};

                border: 1px solid {GREEN_HOVER};
            }}

            """)

        layout = QVBoxLayout(self)

        layout.setContentsMargins(24, 22, 24, 20)

        layout.setSpacing(9)

        title = QLabel("Contact Us")

        title.setObjectName("title")

        layout.addWidget(title)

        subtitle = QLabel("Have a bug, idea, or feedback? We'd love to hear from you.")

        subtitle.setObjectName("subtitle")

        subtitle.setWordWrap(True)

        layout.addWidget(subtitle)

        layout.addSpacing(7)

        email_label = QLabel(self.CONTACT_EMAIL)

        email_label.setObjectName("contactValue")

        email_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(email_label)

        email_button = QPushButton("Open Gmail")

        email_button.setCursor(Qt.CursorShape.PointingHandCursor)

        email_button.clicked.connect(self.open_email)

        layout.addWidget(email_button)

        whatsapp_label = QLabel(self.WHATSAPP_DISPLAY)

        whatsapp_label.setObjectName("contactValue")

        whatsapp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(whatsapp_label)

        whatsapp_button = QPushButton("Chat on WhatsApp")

        whatsapp_button.setCursor(Qt.CursorShape.PointingHandCursor)

        whatsapp_button.clicked.connect(self.open_whatsapp)

        layout.addWidget(whatsapp_button)

        instagram_label = QLabel(f"@{self.INSTAGRAM_USERNAME}")

        instagram_label.setObjectName("contactValue")

        instagram_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(instagram_label)

        instagram_button = QPushButton("Message on Instagram")

        instagram_button.setCursor(Qt.CursorShape.PointingHandCursor)

        instagram_button.clicked.connect(self.open_instagram)

        layout.addWidget(instagram_button)

        layout.addStretch()

        close_button = QPushButton("Close")

        close_button.setObjectName("closeButton")

        close_button.setCursor(Qt.CursorShape.PointingHandCursor)

        close_button.clicked.connect(self.accept)

        layout.addWidget(
            close_button,
            0,
            Qt.AlignmentFlag.AlignRight,
        )

    def open_email(self):
        gmail_url = (
            "https://mail.google.com/mail/?view=cm&fs=1"
            f"&to={self.CONTACT_EMAIL}"
            "&su=VeyroDock - Feedback"
        )

        webbrowser.open_new_tab(gmail_url)

    def open_whatsapp(self):
        whatsapp_url = (
            f"https://wa.me/{self.WHATSAPP_NUMBER}"
            "?text=Hi, I need help with VeyroDock."
        )

        webbrowser.open_new_tab(whatsapp_url)

    def open_instagram(self):
        instagram_url = f"https://ig.me/m/{self.INSTAGRAM_USERNAME}"

        webbrowser.open_new_tab(instagram_url)


class QuotesDialog(QDialog):
    """Manage the quotes shown at the bottom of the widget."""

    quotes_saved = Signal(list, int)

    def __init__(self, quotes, active_index=0, parent=None):
        super().__init__(parent)

        self.setWindowTitle("VeyroDock Quotes")

        self.setFixedSize(520, 500)

        self.setFont(QFont("Segoe UI", 10))

        self.quotes = list(quotes)

        self.active_index = (
            max(
                0,
                min(
                    len(self.quotes) - 1,
                    int(active_index),
                ),
            )
            if self.quotes
            else 0
        )

        self.setStyleSheet(f"""

            QDialog {{
                background: {BG};

                color: {PRIMARY};
            }}

            QLabel#title {{
                color: {PRIMARY};

                font-size: 20px;

                font-weight: 700;
            }}

            QLabel#subtitle {{
                color: {SECONDARY};

                font-size: 11px;
            }}

            QLabel#sectionTitle {{
                color: {GREEN};

                font-size: 10px;

                font-weight: 700;

                letter-spacing: 1px;
            }}

            QListWidget {{
                color: {PRIMARY};

                background: rgba(255, 255, 255, 4);

                border: 1px solid {BORDER};

                border-radius: 9px;

                padding: 6px;

                outline: none;
            }}

            QListWidget::item {{
                padding: 10px 12px;

                border-radius: 7px;

                margin: 2px 0;
            }}

            QListWidget::item:selected {{
                background: {GREEN_SOFT};

                border: 1px solid {GREEN_BORDER};
            }}

            QLineEdit {{
                color: {PRIMARY};

                background: rgba(255, 255, 255, 5);

                border: 1px solid {BORDER};

                border-radius: 8px;

                padding: 9px 11px;

                font-size: 11px;
            }}

            QLineEdit:focus {{
                border: 1px solid {GREEN_BORDER};
            }}

            QPushButton {{
                color: {PRIMARY};

                background: rgba(255, 255, 255, 5);

                border: 1px solid {BORDER};

                border-radius: 8px;

                padding: 8px 13px;

                font-size: 10px;

                font-weight: 600;
            }}

            QPushButton:hover {{
                color: {GREEN};

                background: {GREEN_SOFT};

                border: 1px solid {GREEN_BORDER};
            }}

            QPushButton#useQuote {{
                color: #06110D;

                background: {GREEN};

                border: 1px solid {GREEN};
            }}

            QPushButton#useQuote:hover {{
                background: {GREEN_HOVER};
            }}

            QDialogButtonBox QPushButton {{
                min-width: 82px;

                min-height: 32px;
            }}

            """)

        self.setup_ui()

        self.refresh_list()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        layout.setContentsMargins(24, 22, 24, 20)

        layout.setSpacing(10)

        title = QLabel("Quotes")

        title.setObjectName("title")

        layout.addWidget(title)

        subtitle = QLabel("Add your own lines and choose the one shown on the widget.")

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
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )

        button_box.accepted.connect(self.save_and_close)

        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)

    def refresh_list(self):
        self.list_widget.clear()

        for quote in self.quotes:
            item = QListWidgetItem(quote)

            item.setToolTip(quote)

            self.list_widget.addItem(item)
        if self.quotes:
            self.active_index = max(
                0,
                min(
                    self.active_index,
                    len(self.quotes) - 1,
                ),
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
                min(
                    self.active_index,
                    len(self.quotes) - 1,
                ),
            )
        else:
            self.active_index = 0
        self.quotes_saved.emit(
            list(self.quotes),
            int(self.active_index),
        )

        self.accept()
