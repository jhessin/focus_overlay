# src/focus_overlay/main.py

from collections.abc import Callable

from .schedule_gui import ScheduleManagerWindow
from .schedule_manager import ScheduleManager
from .taskbar_ui import TaskbarOverlay
from .tray_icon import TrayIcon


class FocusOverlayApp:
    """Main application controller linking data management and Tkinter views."""

    def __init__(self) -> None:
        self.schedule_manager: ScheduleManager = ScheduleManager()
        self.gui_window: ScheduleManagerWindow | None = None

        # The taskbar overlay serves as the primary Tk root window instance
        self.overlay: TaskbarOverlay = TaskbarOverlay(
            schedule_manager=self.schedule_manager,
            on_open_settings_callback=self.open_schedule_gui,
            on_quit_callback=self.quit,
        )
        self.tray: TrayIcon = TrayIcon(
            schedule_on_ui=self._schedule_on_ui,
            on_open_settings=self.open_schedule_gui,
            on_toggle_clickthrough=self.overlay.toggle_clickthrough,
            on_quit=self.quit,
        )

    def _schedule_on_ui(self, action: Callable[[], None]) -> None:
        """Runs a tray action on the Tk thread."""
        self.overlay.after(0, action)

    def open_schedule_gui(self) -> None:
        """Opens or brings the schedule management GUI window to the front."""
        if self.gui_window is None or not self.gui_window.winfo_exists():
            self.gui_window = ScheduleManagerWindow(
                schedule_manager=self.schedule_manager,
                on_schedule_changed_callback=self.overlay.update_display,
                parent=self.overlay,
            )
        else:
            self.gui_window.deiconify()
            self.gui_window.lift()
            self.gui_window.focus_force()

    def quit(self) -> None:
        """Stops the tray icon and ends the Tk event loop."""
        self.tray.stop()
        self.overlay.quit()

    def run(self) -> None:
        """Starts the tray icon and the Tkinter event loop."""
        self.tray.start()
        self.overlay.mainloop()
