import json
import os
import threading
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, simpledialog

import pystray
from PIL import Image, ImageDraw
from pystray import MenuItem as item

DATA_FILE = "schedule.json"


class FocusOverlay:
    def __init__(self):
        self.schedule = self.load_schedule()

        self.root = tk.Tk()
        self.root.title("Focus Overlay")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.75)
        self.root.configure(bg="black")

        try:
            self.root.wm_attributes("-transparentcolor", "black")
        except:
            pass

        self.label = tk.Label(
            self.root,
            text="",
            font=("Segoe UI", 18, "bold"),
            fg="lime",
            bg="black",
            padx=10,
            pady=5,
        )
        self.label.pack()

        self.root.geometry("450x60+100+100")

        self.drag_x = 0
        self.drag_y = 0
        self.label.bind("<Button-1>", self.start_drag)
        self.label.bind("<B1-Motion>", self.drag)

        self.clickthrough = False

        self.update_focus()

    def load_schedule(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        return []

    def save_schedule(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.schedule, f, indent=2)

    def current_task(self):
        now = datetime.now().strftime("%H:%M")
        for entry in self.schedule:
            if entry["start"] <= now <= entry["end"]:
                return entry["task"]
        return "No scheduled focus right now"

    def update_focus(self):
        self.label.config(text=f"Focus: {self.current_task()}")
        self.root.after(30000, self.update_focus)

    def start_drag(self, event):
        self.drag_x = event.x
        self.drag_y = event.y

    def drag(self, event):
        x = self.root.winfo_x() + event.x - self.drag_x
        y = self.root.winfo_y() + event.y - self.drag_y
        self.root.geometry(f"+{x}+{y}")

    def add_schedule_item(self):
        start = simpledialog.askstring("Start", "Start time (HH:MM)")
        end = simpledialog.askstring("End", "End time (HH:MM)")
        task = simpledialog.askstring("Task", "Focus task")

        if start and end and task:
            self.schedule.append({"start": start, "end": end, "task": task})
            self.schedule.sort(key=lambda x: x["start"])
            self.save_schedule()

    def toggle_clickthrough(self):
        try:
            import ctypes

            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
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
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def create_image(self):
        img = Image.new("RGB", (64, 64), (0, 120, 215))
        d = ImageDraw.Draw(img)
        d.text((18, 18), "F", fill="white")
        return img

    def run_tray(self):
        menu = pystray.Menu(
            item("Add Schedule Item", lambda: self.add_schedule_item()),
            item("Toggle Click Through", lambda: self.toggle_clickthrough()),
            item("Exit", lambda icon, item: self.quit(icon)),
        )
        icon = pystray.Icon("FocusOverlay", self.create_image(), "Focus Overlay", menu)
        icon.run()

    def quit(self, icon):
        icon.stop()
        self.root.quit()

    def run(self):
        threading.Thread(target=self.run_tray, daemon=True).start()
        self.root.mainloop()


if __name__ == "__main__":
    FocusOverlay().run()
