from PySide6.QtCore import QSettings


class SettingsManager:
    ORGANIZATION = "SpotifyDesktopWidget"
    APPLICATION = "SpotifyDesktopWidget"

    OPACITY_KEY = "opacity_v3"

    DEFAULT_SIZE_PERCENT = 33
    DEFAULT_OPACITY = 55

    def __init__(self):
        self.settings = QSettings(
            self.ORGANIZATION,
            self.APPLICATION,
        )

    # ==================================================
    # WINDOW POSITION
    # ==================================================

    def get_window_position(self):
        x = self.settings.value(
            "window_x",
            None,
        )
        y = self.settings.value(
            "window_y",
            None,
        )

        if x is None or y is None:
            return None

        try:
            return int(x), int(y)
        except (TypeError, ValueError):
            return None

    def save_window_position(
        self,
        x,
        y,
    ):
        self.settings.setValue(
            "window_x",
            int(x),
        )
        self.settings.setValue(
            "window_y",
            int(y),
        )
        self.settings.sync()

    # ==================================================
    # WINDOW SIZE
    # ==================================================

    def get_size_percent(self):
        value = self.settings.value(
            "size_percent",
            self.DEFAULT_SIZE_PERCENT,
        )

        try:
            value = int(value)
        except (TypeError, ValueError):
            value = self.DEFAULT_SIZE_PERCENT

        return max(
            0,
            min(
                100,
                value,
            ),
        )

    def save_size_percent(
        self,
        value,
    ):
        value = max(
            0,
            min(
                100,
                int(value),
            ),
        )

        self.settings.setValue(
            "size_percent",
            value,
        )

        self.settings.sync()

    # ==================================================
    # OPACITY
    # ==================================================

    def get_opacity(self):
        """Return the saved slider value, including 0%."""
        value = self.settings.value(
            self.OPACITY_KEY,
            self.DEFAULT_OPACITY,
        )

        try:
            value = int(value)
        except (TypeError, ValueError):
            return self.DEFAULT_OPACITY

        return max(
            0,
            min(
                100,
                value,
            ),
        )

    @staticmethod
    def effective_opacity_percent(value):
        """
        Convert the slider value to real widget visibility.

        Slider 0% remains 0% in Settings and is saved as 0%.
        The actual widget opacity is held at 20% so it cannot
        disappear completely.
        """
        value = max(
            0,
            min(
                100,
                int(value),
            ),
        )

        return (
            20
            if value == 0
            else value
        )

    def get_effective_opacity_percent(self):
        return self.effective_opacity_percent(
            self.get_opacity()
        )

    def save_opacity(
        self,
        value,
    ):
        value = max(
            0,
            min(
                100,
                int(value),
            ),
        )

        self.settings.setValue(
            self.OPACITY_KEY,
            value,
        )

        self.settings.sync()

    # ==================================================
    # ALWAYS ON TOP
    # ==================================================

    def get_always_on_top(self):
        value = self.settings.value(
            "always_on_top",
            True,
        )

        if isinstance(value, bool):
            return value

        return str(value).lower() in (
            "true",
            "1",
            "yes",
        )

    def save_always_on_top(
        self,
        enabled,
    ):
        self.settings.setValue(
            "always_on_top",
            bool(enabled),
        )

        self.settings.sync()


    # ==================================================
    # QUOTES
    # ==================================================

    DEFAULT_QUOTES = [
        "“Somewhere between who I was and who I’m becoming.”",
        "“Keep going. Your story is still being written.”",
        "“Build the life you keep imagining.”",
    ]

    def get_quotes(self):
        value = self.settings.value("quotes", None)

        if value is None:
            return list(self.DEFAULT_QUOTES)

        if isinstance(value, str):
            import json
            try:
                value = json.loads(value)
            except (TypeError, ValueError):
                return list(self.DEFAULT_QUOTES)

        if not isinstance(value, (list, tuple)):
            return list(self.DEFAULT_QUOTES)

        quotes = [
            str(item).strip()
            for item in value
            if str(item).strip()
        ]

        return quotes or list(self.DEFAULT_QUOTES)

    def save_quotes(self, quotes):
        import json

        cleaned = [
            str(item).strip()
            for item in quotes
            if str(item).strip()
        ]

        self.settings.setValue(
            "quotes",
            json.dumps(cleaned, ensure_ascii=False),
        )
        self.settings.sync()

    def get_active_quote_index(self, quote_count):
        if quote_count <= 0:
            return 0

        value = self.settings.value(
            "active_quote_index",
            0,
        )

        try:
            value = int(value)
        except (TypeError, ValueError):
            value = 0

        return max(0, min(quote_count - 1, value))

    def save_active_quote_index(self, value):
        self.settings.setValue(
            "active_quote_index",
            max(0, int(value)),
        )
        self.settings.sync()

    # ==================================================
    # RESET POSITION
    # ==================================================

    def clear_window_position(self):
        self.settings.remove(
            "window_x"
        )

        self.settings.remove(
            "window_y"
        )

        self.settings.sync()
