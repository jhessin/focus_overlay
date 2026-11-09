# src/focus_overlay/schedule_manager.py
import json
from dataclasses import dataclass, field
from datetime import datetime, time
from os import PathLike
from pathlib import Path


@dataclass
class TimeBlock:
    start: time = field(default_factory=time)
    end: time = field(default_factory=time)
    mode: str = field(default_factory=str)


@dataclass
class Schedule:
    name: str
    blocks: list[TimeBlock] = field(default_factory=list)


class ScheduleManager:
    def __init__(self, config_path: PathLike = Path("schedules.json")) -> None:
        self.config_path: Path = Path(config_path)
        self.schedules: dict[str, Schedule] = {}
        self.active_schedule_name: str | None = None
        self.load_schedules()

    def add_schedule(self, schedule: Schedule) -> None:
        self.schedules[schedule.name] = schedule
        if not self.active_schedule_name:
            self.active_schedule_name = schedule.name
        self.save_schedules()

    def set_active_schedule(self, name: str) -> bool:
        if name in self.schedules:
            self.active_schedule_name = name
            self.save_schedules()
            return True
        return False

    def get_active_schedule(self) -> Schedule | None:
        if self.active_schedule_name:
            return self.schedules.get(self.active_schedule_name)
        return None

    def remove_schedule(self, name: str) -> bool:
        if name in self.schedules:
            del self.schedules[name]
            if self.active_schedule_name == name:
                self.active_schedule_name = next(iter(self.schedules), None)
            self.save_schedules()
            return True
        return False

    def get_current_block(self, check_time: time | None = None) -> TimeBlock | None:
        """Returns the active TimeBlock for the current time (or a specified time)."""
        active_schedule = self.get_active_schedule()
        if not active_schedule:
            return None

        now = check_time or datetime.now().time()
        for block in active_schedule.blocks:
            # Simple check for blocks within the same day
            if block.start <= now <= block.end:
                return block
        return None

    def load_schedules(self) -> None:
        """Loads schedules and the active schedule setting from JSON."""
        if not self.config_path.exists():
            return

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.active_schedule_name = data.get("active_schedule")
            self.schedules.clear()

            for name, sched_data in data.get("schedules", {}).items():
                blocks = [
                    TimeBlock(
                        start=time.fromisoformat(b["start"]),
                        end=time.fromisoformat(b["end"]),
                        mode=b.get("mode", "Focus"),
                    )
                    for b in sched_data.get("blocks", [])
                ]
                self.schedules[name] = Schedule(name=name, blocks=blocks)

            # Ensure active_schedule_name points to a valid schedule if available
            if self.active_schedule_name not in self.schedules:
                self.active_schedule_name = next(iter(self.schedules), None)

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Warning: Could not load schedules from {self.config_path}: {e}")

    def save_schedules(self) -> None:
        """Persists schedules and active schedule state to JSON."""
        serialized = {
            "active_schedule": self.active_schedule_name,
            "schedules": {
                name: {
                    "name": sched.name,
                    "blocks": [
                        {
                            "start": block.start.strftime("%H:%M"),
                            "end": block.end.strftime("%H:%M"),
                            "mode": block.mode,
                        }
                        for block in sched.blocks
                    ],
                }
                for name, sched in self.schedules.items()
            },
        }

        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(serialized, f, indent=2)
