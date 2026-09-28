"""Completed-pomodoro history, stored in ~/.local/share/retro-pomo/stats.json."""
import datetime

from . import DATA_DIR, load_json, save_json


def _today():
    return datetime.date.today()


class Stats:
    def __init__(self):
        self.path = DATA_DIR / "stats.json"
        data = load_json(self.path, {})
        self.days = data.get("days", {}) if isinstance(data, dict) else {}
        self.focus_minutes = data.get("focus_minutes", 0) if isinstance(data, dict) else 0

    def add_focus(self, minutes):
        key = _today().isoformat()
        self.days[key] = self.days.get(key, 0) + 1
        self.focus_minutes += minutes
        try:
            save_json(self.path, {"days": self.days, "focus_minutes": self.focus_minutes})
        except OSError as e:
            print("stats: could not save:", e)

    @property
    def today(self):
        return self.days.get(_today().isoformat(), 0)

    @property
    def total(self):
        return sum(self.days.values())

    @property
    def streak(self):
        """Consecutive days with at least one pomodoro, ending today (or yesterday
        if today has none yet, so the streak doesn't vanish at midnight)."""
        day = _today()
        if not self.days.get(day.isoformat()):
            day -= datetime.timedelta(days=1)
        n = 0
        while self.days.get(day.isoformat()):
            n += 1
            day -= datetime.timedelta(days=1)
        return n
