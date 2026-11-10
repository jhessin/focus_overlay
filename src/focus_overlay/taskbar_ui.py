# src/focus\_overlay/taskbar\_ui.py
import tkinter as tk
from collections.abc import Callable

from .schedule_manager import ScheduleManager, TimeBlock

SCHEDULE_FONT_SIZE = 15
MODE_FONT_SIZE = 20


class TaskbarOverlay(tk.Tk):
    """A compact, frameless desktop overlay widget built with Tkinter."""

    def __init__(
        self,
        schedule_manager: ScheduleManager,
        on_open_settings_callback: Callable[[], None],
    ) -> None:
        super().__init__()
        self.schedule_manager: ScheduleManager = schedule_manager
        self.on_open_settings: Callable[[], None] = on_open_settings_callback

        # Window drag offsets
        self._offset_x = 0
        self._offset_y = 0

        self.clickthrough: bool = False

        self._init_ui()
        self._setup_timer()

    def _init_ui(self) -> None:
        """Configures window properties, styling, and layout."""
        # Make frameless and keep always on top
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        # Set window opacity (0.0 to 1.0)
        self.attributes("-alpha", 0.92)

        # Main window background
        self.configure(bg="#1E1E1E")

        # Container frame
        container = tk.Frame(self, bg="#1E1E1E", padx=10, pady=6)
        container.pack(fill=tk.BOTH, expand=True)

        # Label container for schedule & mode text
        text_frame = tk.Frame(container, bg="#1E1E1E")
        text_frame.pack(side=tk.LEFT, padx=(0, 10))

        self.schedule_label = tk.Label(
            text_frame,
            text="Schedule: None",
            font=("Segoe UI", SCHEDULE_FONT_SIZE),
            fg="#A0A0A0",
            bg="#1E1E1E",
            anchor=tk.W,
        )
        self.schedule_label.pack(fill=tk.X)

        self.mode_label = tk.Label(
            text_frame,
            text="No Active Block",
            font=("Segoe UI", MODE_FONT_SIZE, "bold"),
            fg="#4CAF50",
            bg="#1E1E1E",
            anchor=tk.W,
        )
        self.mode_label.pack(fill=tk.X)

        # Button Container
        button_container: tk.Frame = tk.Frame(container)
        button_container.pack(side=tk.RIGHT)

        # Clickthrough button
        self.clickthrough_button: tk.Button = tk.Button(
            button_container,
            text="🔓",
            font=("Segoe UI", 11),
            fg="#CCCCCC",
            bg="#1E1E1E",
            activeforeground="#FFFFFF",
            activebackground="#2A2A2A",
            bd=0,
            cursor="hand2",
            command=self.toggle_clickthrough,
        )
        self.clickthrough_button.pack()

        # Settings gear button
        settings_button = tk.Button(
            button_container,
            text="⚙️",
            font=("Segoe UI", 11),
            fg="#CCCCCC",
            bg="#1E1E1E",
            activeforeground="#FFFFFF",
            activebackground="#2A2A2A",
            bd=0,
            cursor="hand2",
            command=self.on_open_settings,
        )
        settings_button.pack()

        # Enable window dragging on all static elements
        for widget in (
            self,
            container,
            text_frame,
            self.schedule_label,
            self.mode_label,
        ):
            widget.bind("<Button-1>", self._start_drag)
            widget.bind("<B1-Motion>", self._drag)

    def toggle_clickthrough(self):
        # try:
        import ctypes

        hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
        GWL_EXSTYLE = -20
        WS_EX_LAYERED = 0x80000
        WS_EX_TRANSPARENT = 0x20
        styles = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)

        if not self.clickthrough:
            ctypes.windll.user32.SetWindowLongW(
                hwnd, GWL_EXSTYLE, styles | WS_EX_LAYERED | WS_EX_TRANSPARENT
            )
        else:
            ctypes.windll.user32.SetWindowLongW(
                hwnd, GWL_EXSTYLE, styles & ~WS_EX_TRANSPARENT
            )

        self.clickthrough = not self.clickthrough

        if self.clickthrough:
            self.clickthrough_button["text"] = "🔒"
        else:
            self.clickthrough_button["text"] = "🔓"

        # except Exception as e:
        #     messagebox.showerror("Error", str(e))

    def _start_drag(self, event: tk.Event) -> None:
        """Captures initial mouse offset when dragging begins."""
        self._offset_x = event.x
        self._offset_y = event.y

    def _drag(self, event: tk.Event) -> None:
        """Moves the frameless window based on pointer movement."""
        x = self.winfo_pointerx() - self._offset_x
        y = self.winfo_pointery() - self._offset_y
        self.geometry(f"+{x}+{y}")

    def _setup_timer(self) -> None:
        """Periodically refreshes the display every 10 seconds."""
        self.update_display()
        self.after(10000, self._setup_timer)

    def update_display(self) -> None:
        """Queries ScheduleManager and updates overlay text."""
        active_schedule = self.schedule_manager.get_active_schedule()

        if not active_schedule:
            self.schedule_label.config(text="Schedule: None")
            self.mode_label.config(text="Idle", fg="#888888")
            return

        self.schedule_label.config(text=f"Schedule: {active_schedule.name}")

        current_block: TimeBlock | None = self.schedule_manager.get_current_block()
        if current_block:
            self.mode_label.config(text=f"💠 {current_block.mode}", fg="#4CAF50")
        else:
            self.mode_label.config(text="Off-Schedule", fg="#FFA726")
