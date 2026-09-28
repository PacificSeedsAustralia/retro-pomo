"""Shared constants, paths and small JSON helpers."""
import json
import os
from pathlib import Path

# Logical screen size. Everything is drawn at this size and scaled to the display.
W, H = 480, 320

ROOT = Path(__file__).resolve().parent.parent
THEMES_DIR = ROOT / "themes"

# RETRO_POMO_HOME redirects settings + stats (used for testing/screenshots).
_home = os.environ.get("RETRO_POMO_HOME")
DATA_DIR = Path(_home) if _home else Path.home() / ".local" / "share" / "retro-pomo"
CONFIG_DIR = Path(_home) if _home else Path.home() / ".config" / "retro-pomo"


def load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def save_json(path, data):
    """Write atomically so a power cut can't leave a half-written file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)
