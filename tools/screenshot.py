#!/usr/bin/env python3
"""Render each view/phase to PNG without a display, to check layouts.

    python3 tools/screenshot.py [theme] [out_dir]
"""
import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("RETRO_POMO_HOME", tempfile.mkdtemp())
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pygame  # noqa: E402

from main import App  # noqa: E402
from widgets.pomodoro import LONG, PAUSED, READY, RUNNING, SHORT  # noqa: E402


def shoot(theme=None, out="shots"):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    app = App(windowed=True, theme=theme)
    w = app.widget
    w.hint_until = -1
    for day in ("2026-09-26", "2026-09-27"):
        app.stats.days[day] = 3
    app.stats.days["2026-09-28"] = 2
    tm = w.timer

    def snap(name, view):
        app.settings["view"] = view
        app.draw()
        pygame.image.save(app.screen, str(out / ("%s-%s.png" % (view, name))))

    for view in ("level", "clock"):
        tm.__init__(app.settings)
        w.t, w.celebrate_from, w.banner_until, w.flash_until, w.last_done = 10.1, -99, -1, -1, (-1, -99)
        tm.done_in_cycle = 2
        snap("1-ready", view)
        tm.state = RUNNING
        tm.remaining = tm.duration() * 0.6
        w.walk = 5
        snap("2-running", view)
        tm.state = PAUSED
        w.t = 10.1
        snap("3-paused", view)
        tm.state = RUNNING
        tm.remaining = 0.01
        app.update(0.05)
        w.t += 0.3
        w.flash_until = -1
        snap("4-course-clear", view)
        w.t += 5
        snap("5-short-break", view)
        tm.phase, tm.remaining, tm.done_in_cycle = LONG, 600, 4
        snap("6-long-break", view)
        tm.state = READY
        snap("7-break-ready", view)
    print("saved to", out.resolve())


if __name__ == "__main__":
    shoot(sys.argv[1] if len(sys.argv) > 1 else None, sys.argv[2] if len(sys.argv) > 2 else "shots")
