"""User settings, stored in ~/.config/retro-pomo/settings.json.

Edit that file on the Pi to change durations; the app fills in anything missing.
"""
from . import CONFIG_DIR, load_json, save_json

DEFAULTS = {
    "theme": "mario",
    "view": "level",          # "level" or "clock"
    "focus_min": 25,
    "short_min": 5,
    "long_min": 15,
    "long_every": 4,          # long break after this many focus sessions
    "auto_start_break": True,
    "auto_start_focus": False,
    "fps": 30,
}


class Settings(dict):
    def __init__(self):
        self.path = CONFIG_DIR / "settings.json"
        super().__init__(DEFAULTS)
        saved = load_json(self.path, {})
        if isinstance(saved, dict):
            self.update({k: v for k, v in saved.items() if k in DEFAULTS})
        if not self.path.exists():
            self.save()

    def save(self):
        try:
            save_json(self.path, dict(self))
        except OSError as e:
            print("settings: could not save:", e)

    def set(self, key, value):
        self[key] = value
        self.save()
