import sys

import time

from PySide6.QtCore import (
    QEasingCurve,

    QPoint,

    QPropertyAnimation,

    QSequentialAnimationGroup,

    Qt,

    QTimer,
)

from PySide6.QtGui import (
    QColor,

    QGuiApplication,

    QPainter,

    QPainterPath,

    QPixmap,
)

from PySide6.QtWidgets import (
    QApplication,

    QBoxLayout,

    QGraphicsOpacityEffect,

    QGraphicsDropShadowEffect,

    QFrame,

    QGridLayout,

    QHBoxLayout,

    QLabel,

    QPushButton,

    QSlider,

    QSystemTrayIcon,

    QVBoxLayout,

    QWidget,
)

from app.config.settings import SettingsManager

from app.services.command_executor import (
    CommandExecutor,
)

from app.ui.icons import (
    create_icon,

    get_veyrodock_icon,

    get_veyrodock_icon_path,
)

from app.ui.seek_bar import SeekBar

from app.ui.settings_dialog import (
    QuotesDialog,

    SettingsDialog,
)

from app.ui.styles import (
    ACCENT_COLOR,

    ACCENT_HOVER,

    ALBUM_FONT_SIZE,

    ARTIST_FONT_SIZE,

    ARTWORK_RADIUS,

    ARTWORK_SIZE,

    CARD_BORDER,

    CARD_COLOR,

    CONTROL_SIZE,

    CORNER_RADIUS,

    HEADER_FONT_SIZE,

    MAIN_CONTROL_SIZE,

    MUTED_TEXT,

    PRIMARY_TEXT,

    SECONDARY_TEXT,

    SONG_FONT_SIZE,

    WINDOW_HEIGHT,

    WINDOW_OPACITY,

    WINDOW_WIDTH,
)

from app.ui.tray import SystemTray

from app.ui.worker import SpotifyWorker

class SpotifyWidget(QWidget):
    # Size-slider range. 0% is the smallest usable widget.

    MIN_WINDOW_WIDTH = 360

    # The current UI layout needs a few more than 323 px vertically.

    # 340 px gives Windows/Qt enough room and removes geometry correction loops.

    MIN_WINDOW_HEIGHT = 350

    MAX_WINDOW_WIDTH = 500

    MAX_WINDOW_HEIGHT = 350

    DEFAULT_SIZE_PERCENT = 50

    DESIGN_WINDOW_WIDTH = 430

    DESIGN_WINDOW_HEIGHT = 350

    def __init__(self):
        super().__init__()

        # ==================================================

        # STATE

        # ==================================================

        self.current_track = None

        self.spotify_status = "not_running"

        self.compact_header = False

        self.artwork_pixmap = None

        self.last_update_time = None

        self.last_playing_state = None

        self.drag_position = QPoint()

        self.is_seeking = False

        self.force_exit = False

        # Cross-monitor/DPI geometry guard.  Windows can temporarily resize
        # a top-level Qt window when it moves between displays with different
        # scaling.  Keep one requested geometry and re-apply it after the
        # display transition settles.
        self._geometry_sync_pending = False
        self._screen_change_connected = False

        self.playback_pending = False

        self.pending_playing_state = None

        self.navigation_pending = False

        self.seek_pending = False

        self.pending_seek_position_ms = None

        # ==================================================

        # ANIMATIONS

        # ==================================================

        self.play_pause_animation = None

        self.close_animation = None

        self.show_animation = None

        # ==================================================

        # SETTINGS

        # ==================================================

        self.settings_manager = SettingsManager()

        # Persistent quote state. The SettingsManager owns the saved list

        # and active selection; the widget only displays the active quote.

        self.quotes = self.settings_manager.get_quotes()

        self.active_quote_index = self.settings_manager.get_active_quote_index(
            len(self.quotes)
        )

        self.always_on_top = self.settings_manager.get_always_on_top()

        self.opacity_percent = self.settings_manager.get_opacity()

        self.widget_opacity = (
            self.settings_manager.get_effective_opacity_percent() / 100
        )

        self.size_percent = self.DEFAULT_SIZE_PERCENT

        # ==================================================

        # WINDOW

        # ==================================================

        self.setWindowTitle("VeyroDock")

        self.setWindowIcon(get_veyrodock_icon())

        # The widget is resized only through the Settings size slider.

        # Never lock the top-level window with setFixedSize().

        self.setMouseTracking(True)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setWindowOpacity(self.widget_opacity)

        self.apply_window_flags()

        self.restore_saved_position()

        # ==================================================

        # UI

        # ==================================================

        self.setup_ui()

        # Build the layout before applying the saved slider size.

        # This lets Qt calculate child minimums first instead of Windows

        # correcting a too-small geometry during startup.

        self.setMinimumSize(
            self.MIN_WINDOW_WIDTH,

            self.MIN_WINDOW_HEIGHT,
        )

        self.update_responsive_layout(
            width=self.DESIGN_WINDOW_WIDTH,

            height=self.DESIGN_WINDOW_HEIGHT,
        )

        self.apply_size_percent(
            self.size_percent,

            persist=False,
        )

        # ==================================================

        # COMMAND EXECUTOR

        # ==================================================

        self.command_executor = CommandExecutor(self)

        self.command_executor.command_finished.connect(self.handle_command_finished)

        self.command_executor.command_failed.connect(self.handle_command_failed)

        # ==================================================

        # SYSTEM TRAY

        # ==================================================

        self.setup_tray()

        # ==================================================

        # SPOTIFY SYNC WORKER

        # ==================================================

        self.worker = SpotifyWorker(interval=3)

        self.worker.track_updated.connect(self.update_track)

        self.worker.artwork_updated.connect(self.update_artwork)

        self.worker.status_updated.connect(self.update_spotify_status)

        self.worker.error_occurred.connect(self.show_error)

        self.worker.start()

        # ==================================================

        # PROGRESS TIMER

        # ==================================================

        self.progress_timer = QTimer(self)

        self.progress_timer.timeout.connect(self.update_progress)

        self.progress_timer.start(200)
    # ======================================================

    # WINDOW FLAGS

    # ======================================================

    def apply_window_flags(
        self,
    ):
        flags = Qt.WindowType.FramelessWindowHint

        if self.always_on_top:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
    # ======================================================

    # CUSTOM WINDOW PAINTING

    # ======================================================

    def paintEvent(
        self,

        event,
    ):
        painter = QPainter(self)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()

        path.addRoundedRect(
            1,

            1,

            self.width() - 2,

            self.height() - 2,

            CORNER_RADIUS,

            CORNER_RADIUS,
        )

        # Main glass background.

        background = QColor(
            12,

            12,

            15,

            215,
        )

        painter.fillPath(
            path,

            background,
        )

        # Subtle inner highlight.

        inner_path = QPainterPath()

        inner_path.addRoundedRect(
            2,

            2,

            self.width() - 4,

            self.height() - 4,

            CORNER_RADIUS - 1,

            CORNER_RADIUS - 1,
        )

        painter.fillPath(
            inner_path,

            QColor(
                255,

                255,

                255,

                5,
            ),
        )

        # Amber border.

        painter.setPen(
            QColor(
                38,

                226,

                160,

                62,
            )
        )

        painter.drawPath(path)

        # Soft top highlight.

        highlight = QPainterPath()

        highlight.moveTo(
            CORNER_RADIUS,

            1,
        )

        highlight.lineTo(
            self.width() - CORNER_RADIUS,

            1,
        )

        painter.setPen(
            QColor(
                255,

                255,

                255,

                18,
            )
        )

        painter.drawPath(highlight)

        painter.end()
    # ======================================================

    # POSITION

    # ======================================================

    def _connect_screen_change_handler(
        self,
    ):
        handle = self.windowHandle()

        if handle is None or self._screen_change_connected:
            return

        handle.screenChanged.connect(self._handle_screen_changed)

        self._screen_change_connected = True

    def _handle_screen_changed(
        self,
        screen,
    ):
        # A per-monitor DPI transition can generate several geometry changes.
        # Wait until Qt/Windows has finished the transition, then restore the
        # size selected by the user instead of keeping the transient expanded
        # geometry.
        if self._geometry_sync_pending:
            return

        self._geometry_sync_pending = True

        QTimer.singleShot(0, self._sync_geometry_after_screen_change)

        QTimer.singleShot(150, self._sync_geometry_after_screen_change)

    def _sync_geometry_after_screen_change(
        self,
    ):
        self._geometry_sync_pending = False

        if not self.isVisible():
            return

        value = self.size_percent

        width = self.MIN_WINDOW_WIDTH + int(
            (self.MAX_WINDOW_WIDTH - self.MIN_WINDOW_WIDTH) * (value / 100)
        )

        height = self.MIN_WINDOW_HEIGHT + int(
            (self.MAX_WINDOW_HEIGHT - self.MIN_WINDOW_HEIGHT) * (value / 100)
        )

        # Recalculate the child geometry for the requested size first, then
        # restore that exact top-level size.  This prevents stale layout
        # minimums from leaving large empty areas after a DPI/display change.
        self.update_responsive_layout(
            width=width,
            height=height,
        )

        self.resize(width, height)

        self.update_responsive_layout(
            width=width,
            height=height,
        )

    def apply_size_percent(
        self,

        value,

        persist=True,
    ):
        value = max(0, min(100, int(value)))

        self.size_percent = value

        width = self.MIN_WINDOW_WIDTH + int(
            (self.MAX_WINDOW_WIDTH - self.MIN_WINDOW_WIDTH) * (value / 100)
        )

        height = self.MIN_WINDOW_HEIGHT + int(
            (self.MAX_WINDOW_HEIGHT - self.MIN_WINDOW_HEIGHT) * (value / 100)
        )

        # IMPORTANT: prepare the child widgets for the target size BEFORE

        # resizing the top-level window. This prevents Qt/Windows from using

        # the previous (larger) child minimums while the slider is moving.

        self.update_responsive_layout(
            width=width,

            height=height,
        )

        # Qt can calculate a child-layout minimum that is one or more

        # pixels taller than the slider's requested geometry.  Use that

        # already-calculated minimum before resizing so Windows does not

        # emit a QWindowsWindow::setGeometry warning or silently add a

        # pixel to the requested height.

        layout_min_height = self.main_layout.minimumSize().height()

        if layout_min_height > height:
            height = layout_min_height
        self.resize(
            width,

            height,
        )

        if persist:
            self.settings_manager.save_size_percent(value)
        self.update_responsive_layout()
    def restore_saved_position(
        self,
    ):
        position = self.settings_manager.get_window_position()

        if position is None:
            return
        x, y = position

        self.move(
            x,

            y,
        )
    def save_window_state(
        self,
    ):
        self.settings_manager.save_window_position(
            self.x(),

            self.y(),
        )
    def reset_window_position(
        self,
    ):
        self.settings_manager.clear_window_position()

        self.move(
            100,

            100,
        )
    # ======================================================

    # SYSTEM TRAY

    # ======================================================

    def setup_tray(
        self,
    ):
        self.tray = None

        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        self.tray = SystemTray(self)

        self.tray.show_requested.connect(self.show_from_tray)

        self.tray.settings_requested.connect(self.open_settings)

        self.tray.exit_requested.connect(self.exit_application)
    # ======================================================

    # UI SETUP

    # ======================================================

    def setup_ui(
        self,
    ):
        # Main glass layout.  All existing widget references are preserved so

        # playback, seek, artwork, volume, quotes, and command handlers keep

        # using the same objects and signals.

        self.main_layout = QVBoxLayout()

        self.main_layout.setContentsMargins(18, 4, 18, 5)

        self.main_layout.setSpacing(3)

        # ==================================================

        # HEADER

        # ==================================================

        # A three-column grid keeps CONNECTED mathematically centered instead

        # of letting the left/right control widths shift it around.

        self.header_layout = QGridLayout()

        self.header_layout.setContentsMargins(1, 0, 1, 0)

        self.header_layout.setHorizontalSpacing(4)

        self.header_layout.setVerticalSpacing(0)

        self.header_layout.setColumnStretch(0, 1)

        self.header_layout.setColumnStretch(1, 1)

        self.header_layout.setColumnStretch(2, 1)

        brand_layout = QHBoxLayout()

        brand_layout.setContentsMargins(0, 0, 0, 0)

        brand_layout.setSpacing(7)

        self.brand_mark = QLabel()

        self.brand_mark.setFixedSize(27, 27)

        self.brand_mark.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.brand_mark.setPixmap(
            QPixmap(str(get_veyrodock_icon_path())).scaled(
                27,

                27,

                Qt.AspectRatioMode.KeepAspectRatio,

                Qt.TransformationMode.SmoothTransformation,
            )
        )

        self.brand_mark.setStyleSheet(
            "QLabel { background: transparent; border: none; }"
        )

        self.brand_label = QLabel("VEYRODOCK")

        self.brand_label.setStyleSheet("""
            QLabel {
                color: #F2F5F4;

                font-family: "Segoe UI";

                font-size: 11px;

                font-weight: 800;

                letter-spacing: 1.15px;

                background: transparent;
            }
        """)

        brand_layout.addWidget(self.brand_mark)

        brand_layout.addWidget(self.brand_label)

        brand_layout.addStretch()

        self.header_layout.addLayout(
            brand_layout,

            0,

            0,

            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
        )

        self.connection_label = QLabel("CONNECTED")

        self.connection_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.connection_label.setStyleSheet("""
            QLabel {
                color: #26E2A0;

                font-family: "Segoe UI";

                font-size: 8px;

                font-weight: 800;

                letter-spacing: 0.9px;

                background: transparent;
            }
        """)

        self.header_layout.addWidget(
            self.connection_label,

            0,

            1,

            Qt.AlignmentFlag.AlignCenter,
        )

        header_actions = QHBoxLayout()

        header_actions.setContentsMargins(0, 0, 0, 0)

        header_actions.setSpacing(2)

        self.settings_button = QPushButton()

        self.settings_button.setFixedSize(28, 28)

        self.settings_button.setIcon(create_icon("settings", "#B9C2BF", 17))

        self.settings_button.setIconSize(self.settings_button.size())

        self.settings_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.settings_button.setToolTip("Settings")

        self.settings_button.setStyleSheet("""
            QPushButton {
                background: transparent;

                border: 1px solid transparent;

                border-radius: 9px;
            }

            QPushButton:hover {
                background: rgba(38, 226, 160, 28);

                border: 1px solid rgba(38, 226, 160, 65);
            }

            QPushButton:pressed {
                background: rgba(38, 226, 160, 48);
            }
        """)

        self.settings_button.clicked.connect(self.open_settings)

        header_actions.addWidget(self.settings_button)

        self.minimize_button = QPushButton("—")

        self.minimize_button.setFixedSize(28, 28)

        self.minimize_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.minimize_button.setToolTip("Minimize")

        self.minimize_button.setStyleSheet("""
            QPushButton {
                background: transparent;

                border: 1px solid transparent;

                border-radius: 9px;

                color: #B9C2BF;

                font-family: "Segoe UI";

                font-size: 16px;

                font-weight: 600;

                padding-bottom: 4px;
            }

            QPushButton:hover {
                background: rgba(255, 255, 255, 24);

                border: 1px solid rgba(255, 255, 255, 35);

                color: #F2F5F4;
            }
        """)

        self.minimize_button.clicked.connect(self.showMinimized)

        header_actions.addWidget(self.minimize_button)

        self.close_button = QPushButton()

        self.close_button.setFixedSize(28, 28)

        self.close_button.setIcon(create_icon("close", "#B9C2BF", 16))

        self.close_button.setIconSize(self.close_button.size())

        self.close_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.close_button.setToolTip("Close")

        self.close_button.setStyleSheet("""
            QPushButton {
                background: transparent;

                border: 1px solid transparent;

                border-radius: 9px;
            }

            QPushButton:hover {
                background: rgba(255, 255, 255, 28);

                border: 1px solid rgba(255, 255, 255, 38);
            }
        """)

        self.close_button.clicked.connect(self.smooth_close)

        header_actions.addWidget(self.close_button)

        header_actions.addStretch()

        self.header_layout.addLayout(
            header_actions,

            0,

            2,

            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        )

        self.main_layout.addLayout(self.header_layout)

        # ==================================================

        # PLAYER CARD

        # ==================================================

        self.player_card = QFrame()

        self.player_card.setObjectName("playerCard")

        self.player_card.setStyleSheet("""
            QFrame#playerCard {
                background: rgba(16, 18, 20, 132);

                border: 1px solid rgba(255, 255, 255, 12);

                border-radius: 17px;
            }
        """)

        player_card_layout = QVBoxLayout(self.player_card)

        player_card_layout.setContentsMargins(10, 5, 10, 5)

        player_card_layout.setSpacing(3)

        self.player_layout = QBoxLayout(QBoxLayout.Direction.LeftToRight)

        self.player_layout.setSpacing(12)

        self.player_layout.setContentsMargins(0, 0, 0, 0)

        self.artwork_label = QLabel()

        self.artwork_label.setFixedSize(104, 104)

        self.artwork_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.artwork_label.setText("♪")

        self.artwork_label.setStyleSheet(f"""
            QLabel {{
                background: {CARD_COLOR};

                color: {ACCENT_COLOR};

                border: 1px solid {CARD_BORDER};

                border-radius: {ARTWORK_RADIUS}px;

                font-size: 34px;
            }}

            """)
        self.player_layout.addWidget(
            self.artwork_label,

            0,

            Qt.AlignmentFlag.AlignCenter,
        )

        self.info_layout = QVBoxLayout()

        self.info_layout.setSpacing(2)

        self.info_layout.setContentsMargins(0, 0, 0, 0)

        self.now_playing_label = QLabel("NOW PLAYING")

        self.now_playing_label.setStyleSheet("""
            QLabel {
                color: #26E2A0;

                font-family: "Segoe UI";

                font-size: 9px;

                font-weight: 800;

                letter-spacing: 1.5px;

                background: transparent;
            }
        """)

        self.song_label = QLabel("Waiting for Spotify...")

        self.song_label.setWordWrap(True)

        self.song_label.setStyleSheet(f"""
            QLabel {{
                color: {PRIMARY_TEXT};

                font-family: "Segoe UI Variable", "Segoe UI";

                font-size: {SONG_FONT_SIZE}px;

                font-weight: 700;

                background: transparent;
            }}

            """)
        self.artist_label = QLabel("Connecting...")

        self.artist_label.setWordWrap(True)

        self.artist_label.setStyleSheet(f"""
            QLabel {{
                color: {SECONDARY_TEXT};

                font-family: "Segoe UI Variable", "Segoe UI";

                font-size: {ARTIST_FONT_SIZE}px;

                background: transparent;
            }}

            """)
        self.album_label = QLabel("")

        self.album_label.setWordWrap(True)

        self.album_label.setStyleSheet(f"""
            QLabel {{
                color: {MUTED_TEXT};

                font-family: "Segoe UI Variable", "Segoe UI";

                font-size: {ALBUM_FONT_SIZE}px;

                background: transparent;
            }}

            """)
        self.info_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.info_layout.addWidget(self.now_playing_label)

        self.info_layout.addWidget(self.song_label)

        self.info_layout.addWidget(self.artist_label)

        self.info_layout.addWidget(self.album_label)

        self.player_layout.addLayout(self.info_layout, 1)

        player_card_layout.addLayout(self.player_layout)

        # ==================================================

        # SEEK + TIME

        # ==================================================

        self.progress_bar = SeekBar()

        self.progress_bar.setRange(0, 1000)

        self.progress_bar.setValue(0)

        self.progress_bar.setFixedHeight(15)

        self.progress_bar.setCursor(Qt.CursorShape.PointingHandCursor)

        self.progress_bar.setStyleSheet(f"""
            QSlider {{ background: transparent; }}

            QSlider::groove:horizontal {{
                height: 4px;

                background: rgba(255, 255, 255, 28);

                border-radius: 2px;
            }}

            QSlider::add-page:horizontal {{
                background: rgba(255, 255, 255, 28);

                border-radius: 2px;
            }}

            QSlider::sub-page:horizontal {{
                background: {ACCENT_COLOR};

                border-radius: 2px;
            }}

            QSlider::handle:horizontal {{
                width: 11px;

                height: 11px;

                margin: -4px 0;

                background: {ACCENT_COLOR};

                border: 2px solid rgba(255, 255, 255, 100);

                border-radius: 6px;
            }}

            QSlider::handle:horizontal:hover {{
                width: 15px;

                height: 15px;

                margin: -5px 0;

                background: {ACCENT_HOVER};

                border: 2px solid rgba(255, 255, 255, 155);

                border-radius: 8px;
            }}

            """)
        seek_glow = QGraphicsDropShadowEffect(self.progress_bar)

        seek_glow.setBlurRadius(12)

        seek_glow.setOffset(0, 0)

        seek_glow.setColor(QColor(38, 226, 160, 95))

        self.progress_bar.setGraphicsEffect(seek_glow)

        self.progress_bar.seek_requested.connect(self.handle_seek)

        self.progress_bar.sliderPressed.connect(self.handle_slider_pressed)

        self.progress_bar.sliderReleased.connect(self.handle_slider_released)

        player_card_layout.addWidget(self.progress_bar)

        self.time_label = QLabel("0:00 / 0:00")

        self.time_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.time_label.setStyleSheet(f"""
            QLabel {{
                color: {MUTED_TEXT};

                font-size: 10px;

                background: transparent;
            }}

            """)
        player_card_layout.addWidget(self.time_label)

        # ==================================================

        # PLAYBACK CONTROLS

        # ==================================================

        self.controls_layout = QHBoxLayout()

        self.controls_layout.setContentsMargins(0, 0, 0, 0)

        self.controls_layout.setSpacing(7)

        self.previous_button = QPushButton()

        self.play_pause_button = QPushButton()

        self.next_button = QPushButton()

        self.configure_secondary_button(self.previous_button, "previous")

        self.configure_main_button()

        self.configure_secondary_button(self.next_button, "next")

        self.controls_layout.addStretch()

        self.controls_layout.addWidget(self.previous_button)

        self.controls_layout.addWidget(self.play_pause_button)

        self.controls_layout.addWidget(self.next_button)

        self.controls_layout.addStretch()

        player_card_layout.addLayout(self.controls_layout)

        # ==================================================

        # VOLUME

        # ==================================================

        self.volume_layout = QHBoxLayout()

        self.volume_layout.setContentsMargins(2, 0, 2, 0)

        self.volume_layout.setSpacing(6)

        self.volume_icon = QPushButton("🔊")

        self.volume_icon.setFixedSize(24, 24)

        self.volume_icon.setCursor(Qt.CursorShape.PointingHandCursor)

        self.volume_icon.setToolTip("Mute")

        self.volume_icon.setStyleSheet("""
            QPushButton {
                color: #B9C2BF;

                background: transparent;

                border: none;

                font-size: 13px;
            }

            QPushButton:hover {
                color: #26E2A0;
            }
        """)

        self.volume_bar = QSlider(Qt.Orientation.Horizontal)

        self.volume_bar.setRange(0, 100)

        self.volume_bar.setValue(70)

        self.volume_bar.setCursor(Qt.CursorShape.PointingHandCursor)

        self.volume_bar.setFixedHeight(15)

        self.volume_bar.setStyleSheet("""
            QSlider { background: transparent; }

            QSlider::groove:horizontal {
                height: 5px;

                background: rgba(255, 255, 255, 28);

                border-radius: 3px;
            }

            QSlider::add-page:horizontal {
                background: rgba(255, 255, 255, 28);

                border-radius: 2px;
            }

            QSlider::sub-page:horizontal {
                background: #26E2A0;

                border-radius: 2px;
            }

            QSlider::handle:horizontal {
                width: 10px;

                height: 10px;

                margin: -3px 0;

                background: #26E2A0;

                border: 2px solid rgba(255, 255, 255, 120);

                border-radius: 6px;
            }
        """)

        self.previous_volume = 70

        self.volume_update_timer = QTimer(self)

        self.volume_update_timer.setSingleShot(True)

        self.volume_update_timer.timeout.connect(self.send_pending_volume)

        self.pending_volume = None

        self.volume_bar.valueChanged.connect(self.handle_volume_changed)

        self.volume_icon.clicked.connect(self.toggle_mute)

        self.volume_layout.addWidget(self.volume_icon)

        self.volume_layout.addWidget(self.volume_bar, 1)

        player_card_layout.addLayout(self.volume_layout)

        self.main_layout.addWidget(self.player_card)

        # ==================================================

        # QUOTE

        # ==================================================

        self.quote_label = QLabel(self.get_active_quote())

        self.quote_label.setWordWrap(True)

        self.quote_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.quote_label.setStyleSheet(f"""
            QLabel {{
                color: {SECONDARY_TEXT};

                font-family: "Segoe UI";

                font-size: 13px;

                font-style: italic;

                font-weight: 600;

                letter-spacing: 0.25px;

                background: transparent;

                padding: 0 12px;
            }}

            """)
        self.main_layout.addWidget(self.quote_label)

        self.setLayout(self.main_layout)

        # Existing playback handlers — intentionally unchanged.

        self.previous_button.clicked.connect(self.handle_previous)

        self.play_pause_button.clicked.connect(self.handle_play_pause)

        self.next_button.clicked.connect(self.handle_next)
    # ======================================================

    # RESPONSIVE ARTWORK

    # ======================================================

    def apply_responsive_artwork(self):
        if self.artwork_pixmap is None:
            return
        size = self.artwork_label.width()

        scaled_pixmap = self.artwork_pixmap.scaled(
            size,

            size,

            Qt.AspectRatioMode.KeepAspectRatio,

            Qt.TransformationMode.SmoothTransformation,
        )

        self.artwork_label.setPixmap(scaled_pixmap)
    @staticmethod

    def _clamp(value, minimum, maximum):
        return max(
            minimum,

            min(value, maximum),
        )
    def update_responsive_layout(
        self,

        width=None,

        height=None,
    ):
        if not hasattr(self, "main_layout"):
            return
        width = self.width() if width is None else int(width)

        height = self.height() if height is None else int(height)

        scale = self._clamp(
            min(
                width / self.DESIGN_WINDOW_WIDTH,

                height / self.DESIGN_WINDOW_HEIGHT,
            ),

            0.70,

            1.18,
        )

        # Keep the compact stacked layout for genuinely narrow/short

        # shapes.  The normal 380x360 widget should remain horizontal.

        compact = width < 350 or height < 325

        very_compact = width < 330 or height < 315

        # Margins tighten as the widget gets smaller.

        horizontal_margin = int(
            self._clamp(
                width * 0.052,

                14,

                22,
            )
        )

        vertical_margin = int(
            self._clamp(
                height * 0.030,
                7,
                11,
            )
        )

        self.main_layout.setContentsMargins(
            horizontal_margin,

            vertical_margin,

            horizontal_margin,

            vertical_margin,
        )

        # The entire player reflows when the widget becomes narrow or short.

        if compact:
            self.player_layout.setDirection(QBoxLayout.Direction.TopToBottom)

            self.player_layout.setSpacing(7)

            self.artwork_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            label_alignment = Qt.AlignmentFlag.AlignHCenter
        else:
            self.player_layout.setDirection(QBoxLayout.Direction.LeftToRight)

            self.player_layout.setSpacing(
                int(
                    self._clamp(
                        14 * scale,

                        10,

                        17,
                    )
                )
            )

            label_alignment = Qt.AlignmentFlag.AlignLeft
        self.song_label.setAlignment(label_alignment)

        self.artist_label.setAlignment(label_alignment)

        self.album_label.setAlignment(label_alignment)

        # Artwork scales down before the layout switches to compact mode.

        if compact:
            artwork_size = int(
                self._clamp(
                    88 * scale,

                    70,

                    104,
                )
            )
        else:
            artwork_size = int(
                self._clamp(
                    104 * scale,

                    88,

                    126,
                )
            )
        if very_compact:
            artwork_size = min(
                artwork_size,

                72,
            )
        self.artwork_label.setFixedSize(
            artwork_size,

            artwork_size,
        )

        self.apply_responsive_artwork()

        # Typography gently scales without becoming tiny.

        song_size = int(
            self._clamp(
                SONG_FONT_SIZE * scale,

                16,

                21,
            )
        )

        artist_size = int(
            self._clamp(
                ARTIST_FONT_SIZE * scale,

                12,

                14,
            )
        )

        album_size = int(
            self._clamp(
                ALBUM_FONT_SIZE * scale,

                10,

                12,
            )
        )

        footer_size = int(
            self._clamp(
                9 * scale,

                8,

                9,
            )
        )

        time_size = int(
            self._clamp(
                11 * scale,

                9,

                11,
            )
        )

        self.song_label.setStyleSheet(f"""
            QLabel {{
                color: {PRIMARY_TEXT};

                font-family: "Segoe UI Variable", "Segoe UI";

                font-size: {song_size}px;

                font-weight: 700;

                background: transparent;
            }}

            """)
        self.artist_label.setStyleSheet(f"""
            QLabel {{
                color: {SECONDARY_TEXT};

                font-family: "Segoe UI Variable", "Segoe UI";

                font-size: {artist_size}px;

                background: transparent;
            }}

            """)
        self.album_label.setStyleSheet(f"""
            QLabel {{
                color: {MUTED_TEXT};

                font-family: "Segoe UI Variable", "Segoe UI";

                font-size: {album_size}px;

                background: transparent;
            }}

            """)
        self.time_label.setStyleSheet(f"""
            QLabel {{
                color: {MUTED_TEXT};

                font-family: "Segoe UI Variable", "Segoe UI";

                font-size: {time_size}px;

                background: transparent;
            }}

            """)
        self.info_layout.setSpacing(3 if very_compact else 4)

        # Controls scale gently. They stay large enough to remain comfortable.

        secondary_size = int(
            self._clamp(
                46 * scale,

                40,

                50,
            )
        )

        main_size = int(
            self._clamp(
                56 * scale,

                48,

                60,
            )
        )

        if very_compact:
            secondary_size = 40

            main_size = 48
        for button in (
            self.previous_button,

            self.next_button,
        ):
            button.setFixedSize(
                secondary_size,

                secondary_size,
            )

            button.setIconSize(button.size())
        self.play_pause_button.setFixedSize(
            main_size,

            main_size,
        )

        self.play_pause_button.setIconSize(self.play_pause_button.size())

        self.controls_layout.setSpacing(6 if compact else 7)

        self.quote_label.setMaximumHeight(30 if compact else 34)

        header_button_size = 26 if compact else 28

        self.settings_button.setFixedSize(
            header_button_size,

            header_button_size,
        )

        self.settings_button.setIconSize(self.settings_button.size())

        self.minimize_button.setFixedSize(
            header_button_size,

            header_button_size,
        )

        self.close_button.setFixedSize(
            header_button_size,

            header_button_size,
        )

        self.close_button.setIconSize(self.close_button.size())

        quote_size = int(
            self._clamp(
                13 * scale,

                11,

                14,
            )
        )

        self.quote_label.setStyleSheet(f"""
            QLabel {{
                color: {PRIMARY_TEXT};

                font-family: "Segoe UI";

                font-size: {quote_size}px;

                font-style: italic;

                font-weight: 600;

                letter-spacing: 0.25px;

                background: transparent;

                padding: 0 12px;
            }}

            """)
        connection_size = int(
            self._clamp(
                8 * scale,

                6,

                8,
            )
        )

        self.connection_label.setStyleSheet(f"""
            QLabel {{
                color: #26E2A0;

                font-size: {connection_size}px;

                font-weight: 800;

                background: transparent;

                letter-spacing: 0.9px;
            }}

            """)
        # Keep the connection state visible even at the smallest widget

        # size. In compact mode the wording is shortened so the header

        # still fits beside the three window controls.

        self.compact_header = compact

        self.connection_label.setMinimumWidth(0)

        self.connection_label.show()

        self.refresh_connection_label()

        # Keep the header clean after every resize.
    def showEvent(
        self,

        event,
    ):
        super().showEvent(event)

        self._connect_screen_change_handler()

    def resizeEvent(
        self,

        event,
    ):
        super().resizeEvent(event)

        self.update_responsive_layout()
    # ======================================================

    # CONTROL BUTTONS

    # ======================================================

    def configure_secondary_button(
        self,

        button,

        icon_name,
    ):
        button.setFixedSize(
            CONTROL_SIZE,

            CONTROL_SIZE,
        )

        button.setIcon(
            create_icon(
                icon_name,

                SECONDARY_TEXT,

                21,
            )
        )

        button.setIconSize(button.size())

        button.setCursor(Qt.CursorShape.PointingHandCursor)

        button.setStyleSheet(f"""
            QPushButton {{
                background: transparent;

                border: 1px solid transparent;

                border-radius: 14px;
            }}

            QPushButton:hover {{
                background: rgba(255, 255, 255, 30);

                border: 1px solid rgba(38, 226, 160, 65);
            }}

            QPushButton:pressed {{
                background: rgba(38, 226, 160, 48);

                border: 1px solid rgba(38, 226, 160, 105);
            }}

            QPushButton:disabled {{
                background: transparent;

                border: 1px solid transparent;
            }}

            """)
    def configure_main_button(
        self,
    ):
        self.play_pause_button.setFixedSize(
            MAIN_CONTROL_SIZE,

            MAIN_CONTROL_SIZE,
        )

        self.set_play_pause_icon("play")

        self.play_pause_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.play_pause_button.setStyleSheet(f"""
            QPushButton {{
                background: rgba(38, 226, 160, 28);

                border: 1px solid rgba(38, 226, 160, 90);

                border-radius: 19px;
            }}

            QPushButton:hover {{
                background: rgba(38, 226, 160, 62);

                border: 1px solid rgba(74, 240, 184, 165);
            }}

            QPushButton:pressed {{
                background: rgba(38, 226, 160, 82);

                border: 1px solid rgba(74, 240, 184, 190);
            }}

            QPushButton:disabled {{
                background: rgba(38, 226, 160, 20);

                border: 1px solid rgba(38, 226, 160, 55);
            }}

            """)
    # ======================================================

    # PLAY / PAUSE ICON

    # ======================================================

    def set_play_pause_icon(
        self,

        state,
    ):
        icon_name = "pause" if state == "pause" else "play"

        self.play_pause_button.setIcon(
            create_icon(
                icon_name,

                ACCENT_HOVER,

                25,
            )
        )

        self.play_pause_button.setIconSize(self.play_pause_button.size())
    # ======================================================

    # SPOTIFY CONNECTION STATUS

    # ======================================================

    def refresh_connection_label(self):
        if self.spotify_status == "not_running":
            full_text = "NOT CONNECTED"

            compact_text = "OFFLINE"
        elif self.spotify_status == "error":
            full_text = "CONNECTION ERROR"

            compact_text = "ERROR"
        elif self.spotify_status == "paused":
            full_text = "CONNECTED • PAUSED"

            compact_text = "PAUSED"
        else:
            full_text = "CONNECTED"

            compact_text = "CONNECTED"
        self.connection_label.setText(
            compact_text if self.compact_header else full_text
        )
    def update_spotify_status(self, status):
        self.spotify_status = status

        self.refresh_connection_label()
    # ======================================================

    # TRACK UPDATE

    # ======================================================

    def update_track(
        self,

        track,
    ):
        incoming_signature = (
            self.command_executor.track_signature(track) if track is not None else None
        )

        current_signature = (
            self.command_executor.track_signature(self.current_track)

            if self.current_track is not None

            else None
        )

        # --------------------------------------------------

        # Protect optimistic playback state from stale polls.

        # --------------------------------------------------

        if (
            track is not None

            and self.playback_pending

            and self.pending_playing_state is not None

            and incoming_signature == current_signature
        ):
            track.is_playing = self.pending_playing_state
        # --------------------------------------------------

        # Protect the slider from stale progress while a

        # seek command is still being confirmed.

        # --------------------------------------------------

        if (
            track is not None

            and self.seek_pending

            and self.pending_seek_position_ms is not None

            and incoming_signature == current_signature
        ):
            track.progress_ms = self.pending_seek_position_ms
        self.current_track = track

        if track is None:
            self.song_label.setText("Nothing is playing")

            self.artist_label.setText("Spotify")

            self.album_label.setText("")

            self.progress_bar.setValue(0)

            self.time_label.setText("0:00 / 0:00")

            if self.last_playing_state is not None:
                self.last_playing_state = None

                self.animate_play_pause_icon("play")
            return
        # --------------------------------------------------

        # Track metadata.

        # --------------------------------------------------

        self.song_label.setText(track.name)

        self.artist_label.setText(track.artist)

        self.album_label.setText(track.album)

        # --------------------------------------------------

        # Keep progress timing smooth.

        # --------------------------------------------------

        if not self.is_seeking and not self.seek_pending:
            self.last_update_time = time.monotonic()
        # --------------------------------------------------

        # Update play/pause icon only when the state changes.

        # Ignore background state changes while a playback

        # command is still being confirmed.

        # --------------------------------------------------

        if not self.playback_pending:
            if self.last_playing_state != track.is_playing:
                self.last_playing_state = track.is_playing

                self.animate_play_pause_icon("pause" if track.is_playing else "play")
    # ======================================================

    # COMMAND FINISHED

    # ======================================================

    def handle_command_finished(
        self,

        command_name,

        result,
    ):
        if command_name in (
            "pause",

            "resume",
        ):
            if self.pending_playing_state is not None and result:
                track = result.get("track")

                if track is not None:
                    track.is_playing = self.pending_playing_state
            self.playback_pending = False

            self.pending_playing_state = None
        if command_name in (
            "next",

            "previous",
        ):
            self.navigation_pending = False
        if command_name == "seek":
            self.seek_pending = False

            self.pending_seek_position_ms = None
        # Volume commands return an integer (0-100),

        # not the normal track-result dictionary.

        if command_name == "volume":
            if result is not None:
                value = max(
                    0,

                    min(100, int(result)),
                )

                self.volume_bar.blockSignals(True)

                self.volume_bar.setValue(value)

                self.volume_bar.blockSignals(False)

                if value > 0:
                    self.previous_volume = value
                self.update_volume_icon(value)
            return
        if not result:
            return
        track = result.get("track")

        artwork = result.get("artwork")

        if track:
            self.update_track(track)
        if artwork:
            self.update_artwork(artwork)
    # ======================================================

    # COMMAND FAILED

    # ======================================================

    def handle_command_failed(
        self,

        command_name,

        error,
    ):
        if command_name in (
            "pause",

            "resume",
        ):
            self.playback_pending = False

            self.pending_playing_state = None
        if command_name in (
            "next",

            "previous",
        ):
            self.navigation_pending = False
        if command_name == "seek":
            self.seek_pending = False

            self.pending_seek_position_ms = None
        print(f"{command_name.title()} error: {error}")

        # Re-sync the UI with Spotify.

        self.command_executor.refresh()
    # ======================================================

    # PLAY / PAUSE ANIMATION

    # ======================================================

    def animate_play_pause_icon(
        self,

        state,
    ):
        if self.play_pause_animation:
            self.play_pause_animation.stop()
        effect = self.play_pause_button.graphicsEffect()

        if not isinstance(
            effect,

            (QGraphicsOpacityEffect, QGraphicsDropShadowEffect),
        ):
            effect = QGraphicsOpacityEffect(self.play_pause_button)

            self.play_pause_button.setGraphicsEffect(effect)
        effect.setOpacity(1.0)

        fade_out = QPropertyAnimation(
            effect,

            b"opacity",

            self,
        )

        fade_out.setDuration(70)

        fade_out.setStartValue(1.0)

        fade_out.setEndValue(0.0)

        fade_out.setEasingCurve(QEasingCurve.Type.InOutQuad)

        fade_in = QPropertyAnimation(
            effect,

            b"opacity",

            self,
        )

        fade_in.setDuration(100)

        fade_in.setStartValue(0.0)

        fade_in.setEndValue(1.0)

        fade_in.setEasingCurve(QEasingCurve.Type.InOutQuad)

        def change_icon():
            self.set_play_pause_icon(state)
        fade_out.finished.connect(change_icon)

        animation_group = QSequentialAnimationGroup(self)

        animation_group.addAnimation(fade_out)

        animation_group.addAnimation(fade_in)

        def animation_finished():
            self.play_pause_button.setGraphicsEffect(None)

            self.play_pause_animation = None
        animation_group.finished.connect(animation_finished)

        self.play_pause_animation = animation_group

        animation_group.start()
    # ======================================================

    # ARTWORK

    # ======================================================

    def update_artwork(
        self,

        image_data,
    ):
        pixmap = QPixmap()

        if not pixmap.loadFromData(image_data):
            return
        # Keep the original pixmap so the artwork can be resized

        # cleanly whenever the widget size changes.

        self.artwork_pixmap = pixmap

        self.apply_responsive_artwork()
    # ======================================================

    # PROGRESS

    # ======================================================

    def update_progress(
        self,
    ):
        if self.current_track is None:
            return
        if self.is_seeking:
            return
        duration = self.current_track.duration_ms

        if duration <= 0:
            return
        progress = self.current_track.progress_ms

        if self.current_track.is_playing:
            if self.last_update_time is not None:
                elapsed = (time.monotonic() - self.last_update_time) * 1000

                progress += int(elapsed)
        progress = min(
            progress,

            duration,
        )

        value = int((progress / duration) * 1000)

        self.progress_bar.setValue(value)

        self.time_label.setText(
            f"{self.format_time(progress)} / " f"{self.format_time(duration)}"
        )
    # ======================================================

    # TIME FORMAT

    # ======================================================

    @staticmethod

    def format_time(
        milliseconds,
    ):
        seconds = max(
            0,

            int(milliseconds / 1000),
        )

        minutes = seconds // 60

        seconds %= 60

        return f"{minutes}:{seconds:02d}"
    # ======================================================

    # SEEK

    # ======================================================

    def handle_slider_pressed(
        self,
    ):
        self.is_seeking = True
    def handle_slider_released(
        self,
    ):
        self.is_seeking = False
    def handle_seek(
        self,

        percentage,
    ):
        if self.current_track is None:
            return
        duration = self.current_track.duration_ms

        if duration <= 0:
            return
        position_ms = int(duration * percentage)

        # --------------------------------------------------

        # Hold the requested position locally until Spotify

        # confirms it. This prevents the progress timer and

        # background polling from snapping the slider backward.

        # --------------------------------------------------

        self.seek_pending = True

        self.pending_seek_position_ms = position_ms

        self.current_track.progress_ms = position_ms

        self.last_update_time = time.monotonic()

        self.progress_bar.setValue(int(percentage * 1000))

        self.time_label.setText(
            f"{self.format_time(position_ms)} / " f"{self.format_time(duration)}"
        )

        self.command_executor.seek(position_ms)
    # ======================================================

    # VOLUME

    # ======================================================

    def handle_volume_changed(
        self,

        value,
    ):
        value = max(0, min(100, int(value)))

        if value > 0:
            self.previous_volume = value
        # Move the UI immediately.

        self.update_volume_icon(value)

        # Keep only the latest requested volume.

        self.pending_volume = value

        # Send the latest value after the user pauses briefly.

        self.volume_update_timer.start(150)
    def send_pending_volume(
        self,
    ):
        if self.pending_volume is None:
            return
        value = self.pending_volume

        self.pending_volume = None

        self.command_executor.set_volume(value)
    def toggle_mute(
        self,
    ):
        current_volume = int(self.volume_bar.value())

        if current_volume > 0:
            self.previous_volume = current_volume

            target_volume = 0
        else:
            target_volume = max(
                1,

                int(self.previous_volume),
            )
        # Mute/unmute should happen immediately.

        self.volume_update_timer.stop()

        self.pending_volume = None

        self.volume_bar.blockSignals(True)

        self.volume_bar.setValue(target_volume)

        self.volume_bar.blockSignals(False)

        self.update_volume_icon(target_volume)

        self.command_executor.set_volume(target_volume)
    def update_volume_icon(
        self,

        value,
    ):
        if int(value) <= 0:
            self.volume_icon.setText("🔇")

            self.volume_icon.setToolTip("Unmute")
        else:
            self.volume_icon.setText("🔊")

            self.volume_icon.setToolTip("Mute")
    # ======================================================

    # PLAYBACK CONTROLS

    # ======================================================

    def handle_previous(
        self,
    ):
        if self.navigation_pending:
            return
        self.navigation_pending = True

        previous_signature = None

        if self.current_track:
            previous_signature = self.command_executor.track_signature(
                self.current_track
            )
        self.command_executor.previous(previous_signature)
    def handle_play_pause(
        self,
    ):
        if self.current_track is None:
            return
        if self.playback_pending:
            return
        # --------------------------------------------------

        # Optimistic UI update.

        # --------------------------------------------------

        target_playing = not self.current_track.is_playing

        self.playback_pending = True

        self.pending_playing_state = target_playing

        self.current_track.is_playing = target_playing

        self.last_playing_state = target_playing

        self.last_update_time = time.monotonic()

        self.animate_play_pause_icon("pause" if target_playing else "play")

        # --------------------------------------------------

        # Execute actual command in background.

        # --------------------------------------------------

        if target_playing:
            self.command_executor.resume()
        else:
            self.command_executor.pause()
    def handle_next(
        self,
    ):
        if self.navigation_pending:
            return
        self.navigation_pending = True

        previous_signature = None

        if self.current_track:
            previous_signature = self.command_executor.track_signature(
                self.current_track
            )
        self.command_executor.next(previous_signature)
    # ======================================================

    # SETTINGS

    # ======================================================

    def open_settings(
        self,
    ):
        dialog = SettingsDialog(
            opacity=self.opacity_percent,

            always_on_top=self.always_on_top,

            parent=self,
        )

        dialog.settings_saved.connect(self.apply_settings)

        dialog.quotes_requested.connect(self.open_quotes)

        dialog.exec()
    # ======================================================

    # QUOTES

    # ======================================================

    def get_active_quote(self):
        if not self.quotes:
            return ""
        self.active_quote_index = max(
            0,

            min(
                self.active_quote_index,

                len(self.quotes) - 1,
            ),
        )

        return self.quotes[self.active_quote_index]
    def update_quote_display(self):
        self.quote_label.setText(self.get_active_quote())
    def open_quotes(self):
        dialog = QuotesDialog(
            quotes=self.quotes,

            active_index=self.active_quote_index,

            parent=self,
        )

        dialog.quotes_saved.connect(self.apply_quotes)

        dialog.exec()
    def apply_quotes(self, quotes, active_index):
        self.quotes = list(quotes)

        if self.quotes:
            self.active_quote_index = max(
                0,

                min(
                    int(active_index),

                    len(self.quotes) - 1,
                ),
            )
        else:
            self.active_quote_index = 0
        self.settings_manager.save_quotes(self.quotes)

        self.settings_manager.save_active_quote_index(self.active_quote_index)

        self.update_quote_display()
    def apply_settings(
        self,

        opacity,

        always_on_top,

        reset_position,
    ):
        self.opacity_percent = max(
            0,

            min(100, int(opacity)),
        )

        self.widget_opacity = (
            self.settings_manager.effective_opacity_percent(self.opacity_percent) / 100
        )

        self.always_on_top = always_on_top

        self.settings_manager.save_opacity(self.opacity_percent)

        self.settings_manager.save_always_on_top(always_on_top)

        if reset_position:
            self.reset_window_position()
        current_position = self.pos()

        self.apply_window_flags()

        self.move(current_position)

        self.setWindowOpacity(self.widget_opacity)

        self.show()

        self.raise_()

        self.activateWindow()
    # ======================================================

    # ERROR HANDLING

    # ======================================================

    def show_error(
        self,

        error,
    ):
        self.update_spotify_status("error")

        print(f"Spotify worker error: {error}")
    # ======================================================

    # SMOOTH CLOSE

    # ======================================================

    def smooth_close(
        self,
    ):
        if self.close_animation:
            return
        self.force_exit = True

        self.save_window_state()

        if self.tray:
            self.tray.hide()
        self.close_animation = QPropertyAnimation(
            self,

            b"windowOpacity",

            self,
        )

        self.close_animation.setDuration(220)

        self.close_animation.setStartValue(self.windowOpacity())

        self.close_animation.setEndValue(0.0)

        self.close_animation.setEasingCurve(QEasingCurve.Type.InCubic)

        self.close_animation.finished.connect(self.close)

        self.close_animation.start()
    # ======================================================

    # SHOW FROM TRAY

    # ======================================================

    def show_from_tray(
        self,
    ):
        # A minimized Qt window is still considered "visible".

        # Restore it first so the tray's "Show Widget" command

        # actually brings the player back to the desktop.

        if self.isMinimized():
            self.showNormal()
        elif not self.isVisible():
            self.show()
        self.raise_()

        self.activateWindow()

        if self.show_animation:
            self.show_animation.stop()
        self.setWindowOpacity(0.0)

        self.show_animation = QPropertyAnimation(
            self,

            b"windowOpacity",

            self,
        )

        self.show_animation.setDuration(220)

        self.show_animation.setStartValue(0.0)

        self.show_animation.setEndValue(self.widget_opacity)

        self.show_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.show_animation.start()
    # ======================================================

    # EXIT

    # ======================================================

    def exit_application(
        self,
    ):
        self.force_exit = True

        self.save_window_state()

        if self.tray:
            self.tray.hide()
        self.close()
    # ======================================================

    # WINDOW DRAGGING

    # ======================================================

    def mousePressEvent(
        self,

        event,
    ):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )

            event.accept()

            return
        super().mousePressEvent(event)
    def mouseMoveEvent(
        self,

        event,
    ):
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)

            event.accept()

            return
        super().mouseMoveEvent(event)
    # ======================================================

    # CLOSE EVENT

    # ======================================================

    def closeEvent(
        self,

        event,
    ):
        if not self.force_exit:
            event.ignore()

            self.smooth_close()

            return
        self.save_window_state()

        self.progress_timer.stop()

        self.command_executor.shutdown()

        self.worker.stop()

        if self.tray:
            self.tray.hide()
        event.accept()
# ==========================================================

# APPLICATION ENTRY POINT

# ==========================================================

def run_widget():
    app = QApplication(sys.argv)

    app.setQuitOnLastWindowClosed(True)

    window = SpotifyWidget()

    window.show()

    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        window.force_exit = True

        window.progress_timer.stop()

        window.command_executor.shutdown()

        window.worker.stop()

        if window.tray:
            window.tray.hide()
if __name__ == "__main__":
    run_widget()
