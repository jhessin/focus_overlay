# src/focus_overlay/main.py

from .schedule_gui import ScheduleManagerWindow
from .schedule_manager import ScheduleManager
from .taskbar_ui import TaskbarOverlay


class FocusOverlayApp:
    """Main application controller linking data management and Tkinter views."""

    def __init__(self) -> None:
        self.schedule_manager: ScheduleManager = ScheduleManager()
        self.gui_window: ScheduleManagerWindow | None = None

        # The taskbar overlay serves as the primary Tk root window instance
        self.overlay: TaskbarOverlay = TaskbarOverlay(
            schedule_manager=self.schedule_manager,
            on_open_settings_callback=self.open_schedule_gui,
        )

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

    def run(self) -> None:
        """Starts the Tkinter event loop."""
        self.overlay.mainloop()
