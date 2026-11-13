# src/focus_overlay/tray_icon.py
import threading
from collections.abc import Callable

import pystray
from PIL import Image, ImageDraw

ICON_SIZE = 64
ICON_BACKGROUND = (0, 120, 215)
ICON_MARK = "F"


class TrayIcon:
    """System tray icon for schedule, click-through, and exit actions.

    pystray runs menu callbacks on its own thread. Each action is passed to
    ``schedule_on_ui`` so Tk widgets are only touched on the Tk thread.
    """

    def __init__(
        self,
        schedule_on_ui: Callable[[Callable[[], None]], None],
        on_open_settings: Callable[[], None],
        on_toggle_clickthrough: Callable[[], None],
        on_quit: Callable[[], None],
    ) -> None:
        self._schedule_on_ui: Callable[[Callable[[], None]], None] = schedule_on_ui
        self._on_open_settings: Callable[[], None] = on_open_settings
        self._on_toggle_clickthrough: Callable[[], None] = on_toggle_clickthrough
        self._on_quit: Callable[[], None] = on_quit
        self._icon: pystray.Icon = pystray.Icon(
            "FocusOverlay",
            self._create_image(),
            "Focus Overlay",
            menu=self._build_menu(),
        )

    def start(self) -> None:
        """Shows the icon on a daemon thread so the Tk loop stays on the main thread."""
        threading.Thread(
            target=self._icon.run,
            name="focus-overlay-tray",
            daemon=True,
        ).start()

    def stop(self) -> None:
        """Removes the icon. Does nothing when the icon is already stopped."""
        self._icon.stop()

    def _build_menu(self) -> pystray.Menu:
        """Builds the tray menu for schedule, click-through, and exit."""
        return pystray.Menu(
            pystray.MenuItem("Open Schedule Manager", self._open_settings),
            pystray.MenuItem("Toggle Click Through", self._toggle_clickthrough),
            pystray.MenuItem("Exit", self._quit),
        )

    def _open_settings(self) -> None:
        self._schedule_on_ui(self._on_open_settings)

    def _toggle_clickthrough(self) -> None:
        self._schedule_on_ui(self._on_toggle_clickthrough)

    def _quit(self) -> None:
        self._schedule_on_ui(self._on_quit)

    @staticmethod
    def _create_image() -> Image.Image:
        """Draws the blue square icon with a white F mark."""
        image = Image.new("RGB", (ICON_SIZE, ICON_SIZE), ICON_BACKGROUND)
        draw = ImageDraw.Draw(image)
        draw.text((18, 18), ICON_MARK, fill="white")
        return image
