# src/focus_overlay/schedule_gui.py
import tkinter as tk
from collections.abc import Callable
from datetime import time
from tkinter import messagebox, ttk

from .schedule_manager import Schedule, ScheduleManager, TimeBlock


class ScheduleManagerWindow(tk.Toplevel):
    """A Tkinter management window to create, switch, and edit focus schedules."""

    def __init__(
        self,
        schedule_manager: ScheduleManager,
        on_schedule_changed_callback: Callable[[], None],
        parent: tk.Tk | None = None,
    ) -> None:
        self.schedule_manager: ScheduleManager = schedule_manager
        self.on_schedule_changed: Callable[[], None] = on_schedule_changed_callback

        self.title("Focus Overlay - Schedule Manager")
        self.geometry("520x450")
        self.minsize(480, 400)
        self.configure(bg="#252526")

        # Keep on top when opened from taskbar
        self.attributes("-topmost", True)

        self._init_ui()
        self._refresh_schedule_list()

    def _init_ui(self) -> None:
        """Sets up the layout and widgets."""
        # Style configuration for TTK Widgets
        style: ttk.Style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "TCombobox",
            fieldbackground="#333333",
            background="#333333",
            foreground="#FFFFFF",
        )
        style.configure(
            "Treeview",
            background="#333333",
            foreground="#FFFFFF",
            fieldbackground="#333333",
        )
        style.configure(
            "Treeview.Heading",
            background="#2D2D2D",
            foreground="#CCCCCC",
            font=("Segoe UI", 9, "bold"),
        )

        main_frame: tk.Frame = tk.Frame(self, bg="#252526", padx=15, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Section 1: Active Schedule Selector ---
        selector_frame: tk.LabelFrame = tk.LabelFrame(
            main_frame,
            text=" Active Schedule ",
            bg="#252526",
            fg="#A0A0A0",
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=8,
        )
        selector_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            selector_frame,
            text="Select Schedule:",
            bg="#252526",
            fg="#FFFFFF",
            font=("Segoe UI", 9),
        ).pack(side=tk.LEFT, padx=(0, 8))

        self.schedule_combo: ttk.Combobox = ttk.Combobox(
            selector_frame, state="readonly", width=25
        )
        self.schedule_combo.pack(side=tk.LEFT, padx=(0, 8))
        self.schedule_combo.bind("<<ComboboxSelected>>", self._on_select_schedule)

        delete_btn: tk.Button = tk.Button(
            selector_frame,
            text="Delete",
            bg="#D32F2F",
            fg="#FFFFFF",
            activebackground="#B71C1C",
            activeforeground="#FFFFFF",
            bd=0,
            padx=8,
            cursor="hand2",
            command=self._delete_current_schedule,
        )
        delete_btn.pack(side=tk.RIGHT)

        # --- Section 2: Time Blocks Overview ---
        blocks_frame: tk.LabelFrame = tk.LabelFrame(
            main_frame,
            text=" Time Blocks ",
            bg="#252526",
            fg="#A0A0A0",
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=8,
        )
        blocks_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Table showing start, end, and focus mode
        columns = ("start", "end", "mode")
        self.blocks_tree: ttk.Treeview = ttk.Treeview(
            blocks_frame, columns=columns, show="headings", height=6
        )
        self.blocks_tree.heading("start", text="Start Time")
        self.blocks_tree.heading("end", text="End Time")
        self.blocks_tree.heading("mode", text="Focus Mode")

        self.blocks_tree.column("start", width=100, anchor=tk.CENTER)
        self.blocks_tree.column("end", width=100, anchor=tk.CENTER)
        self.blocks_tree.column("mode", width=240, anchor=tk.W)
        self.blocks_tree.pack(fill=tk.BOTH, expand=True)

        # --- Section 3: Add Block & Create Schedule Controls ---
        control_frame: tk.Frame = tk.Frame(main_frame, bg="#252526")
        control_frame.pack(fill=tk.X)

        # Add Time Block inputs
        block_input_frame: tk.Frame = tk.Frame(control_frame, bg="#252526")
        block_input_frame.pack(fill=tk.X, pady=(0, 8))

        tk.Label(
            block_input_frame,
            text="Start (HH:MM):",
            bg="#252526",
            fg="#CCCCCC",
            font=("Segoe UI", 8),
        ).grid(row=0, column=0, padx=(2, 8), sticky=tk.W)
        self.start_entry: tk.Entry = tk.Entry(
            block_input_frame,
            width=8,
            bg="#333333",
            fg="#FFFFFF",
            bd=1,
            insertbackground="white",
        )
        self.start_entry.grid(row=0, column=1, padx=(2, 8))

        tk.Label(
            block_input_frame,
            text="End (HH:MM):",
            bg="#252526",
            fg="#CCCCCC",
            font=("Segoe UI", 8),
        ).grid(row=0, column=2, padx=(2, 8), sticky=tk.W)
        self.end_entry: tk.Entry = tk.Entry(
            block_input_frame,
            width=8,
            bg="#333333",
            fg="#FFFFFF",
            bd=1,
            insertbackground="white",
        )
        self.end_entry.grid(row=0, column=3, padx=(2, 8))

        tk.Label(
            block_input_frame,
            text="Mode:",
            bg="#252526",
            fg="#CCCCCC",
            font=("Segoe UI", 8),
        ).grid(row=0, column=4, padx=(2, 8), sticky=tk.W)
        self.mode_entry: tk.Entry = tk.Entry(
            block_input_frame,
            width=14,
            bg="#333333",
            fg="#FFFFFF",
            bd=1,
            insertbackground="white",
        )
        self.mode_entry.grid(row=0, column=5, padx=(2, 8))

        add_block_btn: tk.Button = tk.Button(
            block_input_frame,
            text="+ Add Block",
            bg="#388E3C",
            fg="#FFFFFF",
            activebackground="#2E7D32",
            bd=0,
            padx=8,
            cursor="hand2",
            command=self._add_time_block,
        )
        add_block_btn.grid(row=0, column=6)

        # Create New Schedule input
        new_sched_frame: tk.Frame = tk.Frame(control_frame, bg="#252526")
        new_sched_frame.pack(fill=tk.X)

        tk.Label(
            new_sched_frame,
            text="New Schedule Name:",
            bg="#252526",
            fg="#CCCCCC",
            font=("Segoe UI", 9),
        ).pack(side=tk.LEFT, padx=(0, 6))
        self.new_sched_entry: tk.Entry = tk.Entry(
            new_sched_frame, bg="#333333", fg="#FFFFFF", bd=1, insertbackground="white"
        )
        self.new_sched_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        create_sched_btn = tk.Button(
            new_sched_frame,
            text="Create Schedule",
            bg="#1976D2",
            fg="#FFFFFF",
            activebackground="#1565C0",
            bd=0,
            padx=10,
            cursor="hand2",
            command=self._create_new_schedule,
        )
        create_sched_btn.pack(side=tk.RIGHT)

    def _refresh_schedule_list(self) -> None:
        """Populates the schedule dropdown and refreshes time blocks for active schedule."""
        schedules: list[str] = list(self.schedule_manager.schedules.keys())
        self.schedule_combo["values"] = schedules

        active: Schedule | None = self.schedule_manager.get_active_schedule()
        if active:
            self.schedule_combo.set(active.name)
            self._populate_blocks(active)
        else:
            self.schedule_combo.set("")
            self._clear_blocks()

    def _populate_blocks(self, schedule: Schedule) -> None:
        """Populates the treeview table with blocks of the given schedule."""
        self._clear_blocks()
        for block in schedule.blocks:
            self.blocks_tree.insert(
                "",
                tk.END,
                values=(
                    block.start.strftime("%H:%M"),
                    block.end.strftime("%H:%M"),
                    block.mode,
                ),
            )

    def _clear_blocks(self) -> None:
        for item in self.blocks_tree.get_children():
            self.blocks_tree.delete(item)

    def _on_select_schedule(self, event: tk.Event) -> None:
        select_name: str = self.schedule_combo.get()
        if self.schedule_manager.set_active_schedule(select_name):
            self.on_schedule_changed()
            active: Schedule | None = self.schedule_manager.get_active_schedule()
            if active:
                self._populate_blocks(active)

    def _create_new_schedule(self) -> None:
        name = self.new_sched_entry.get().strip()
        if not name:
            messagebox.showwarning(
                "Input Error", "Please enter a schedule name.", parent=self
            )
            return

        new_schedule: Schedule = Schedule(name=name)
        self.schedule_manager.add_schedule(new_schedule)
        self.new_sched_entry.delete(0, tk.END)

        self._refresh_schedule_list()
        self.on_schedule_changed()

    def _add_time_block(self) -> None:
        active = self.schedule_manager.get_active_schedule()
        if not active:
            messagebox.showwarning(
                "No Schedule", "Please select or create a schedule first.", parent=self
            )
            return

        try:
            start_t: time = time.fromisoformat(self.start_entry.get().strip())
            end_t: time = time.fromisoformat(self.end_entry.get().strip())
        except ValueError:
            messagebox.showerror(
                "Time Format Error",
                "Use HH:MM format for times (e.g., 09:00).",
                parent=self,
            )
            return

        mode_name: str = self.mode_entry.get().strip() or "Focus"

        block: TimeBlock = TimeBlock(start=start_t, end=end_t, mode=mode_name)
        active.blocks.append(block)

        # Sort blocks by start time
        active.blocks.sort(key=lambda b: b.start)

        self.schedule_manager.save_schedules()
        self._populate_blocks(active)
        self.on_schedule_changed()

        # Clear input fields
        self.start_entry.delete(0, tk.END)
        self.end_entry.delete(0, tk.END)
        self.mode_entry.delete(0, tk.END)

    def _delete_current_schedule(self):
        active: Schedule | None = self.schedule_manager.get_active_schedule()
        if not active:
            return

        if messagebox.askyesno(
            "Confirm Delete", f"Delete schedule '{active.name}'?", parent=self
        ):
            self.schedule_manager.remove_schedule(active.name)
            self._refresh_schedule_list()
            self.on_schedule_changed()
