#!/usr/bin/env python3
"""Retro Pomo: a retro-game themed Pomodoro timer for a Raspberry Pi + small screen.

    python3 main.py              fullscreen (what the Pi runs)
    python3 main.py --windowed   in a window (for testing on a computer)
    python3 main.py --fast       time runs 60x faster (1 min passes in 1 s)

Keys: Space start/pause · S skip · R reset · V switch view · T next theme
      Left/Right switch page · Esc or Q quit
Touch/mouse: tap = start/pause · top-right = theme · bottom-left = view
      right edge = skip (tap twice) · hold top-left 2 s = quit · swipe = page
"""
import argparse
import sys
import time

import pygame

from engine import DATA_DIR, H, W
from engine.font import draw_text
from engine.settings import Settings
from engine.stats import Stats
from engine.theme import Theme, available_themes
from widgets.pomodoro import PomodoroWidget

HOLD_EXIT_SECS = 2.0
SWIPE_PX = 100
EXIT_ZONE = pygame.Rect(0, 0, 110, 48)


class App:
    def __init__(self, windowed=False, speed=1.0, theme=None):
        pygame.display.init()
        self.settings = Settings()
        flags = pygame.SCALED | (0 if windowed else pygame.FULLSCREEN)
        self.screen = pygame.display.set_mode((W, H), flags)
        pygame.display.set_caption("Retro Pomo")
        if hasattr(pygame.display, "set_allow_screensaver"):
            pygame.display.set_allow_screensaver(False)
        self.windowed = windowed
        self.cursor_until = 0.0
        pygame.mouse.set_visible(windowed)
        self.stats = Stats()
        self.theme = self._load_theme(theme or self.settings["theme"])
        self.pages = [PomodoroWidget(self, speed)]
        self.page = 0
        self.t = 0.0
        self.press = None           # (pos, time) of the current mouse/touch press
        self.running = True

    # ---- themes & pages --------------------------------------------------
    def _load_theme(self, name):
        names = available_themes()
        for candidate in [name] + [n for n in names if n != name]:
            try:
                return Theme(candidate)
            except Exception as e:
                print("theme %r failed to load: %s" % (candidate, e))
        sys.exit("No usable theme in themes/")

    def next_theme(self):
        names = available_themes()
        i = names.index(self.theme.name) if self.theme.name in names else -1
        for step in range(1, len(names) + 1):
            name = names[(i + step) % len(names)]
            try:
                self.theme = Theme(name)
                self.settings.set("theme", name)
                return
            except Exception as e:
                print("theme %r failed to load: %s" % (name, e))

    @property
    def widget(self):
        return self.pages[self.page]

    def request_focus(self, widget):
        self.page = self.pages.index(widget)

    def turn_page(self, step):
        if len(self.pages) > 1:
            self.page = (self.page + step) % len(self.pages)
        else:
            self.widget.on_key(pygame.K_v)

    # ---- loop --------------------------------------------------------------
    def handle(self, ev):
        if ev.type == pygame.QUIT:
            self.running = False
        elif ev.type == pygame.KEYDOWN:
            if ev.key in (pygame.K_ESCAPE, pygame.K_q):
                self.running = False
            elif ev.key in (pygame.K_LEFT, pygame.K_RIGHT):
                self.turn_page(1 if ev.key == pygame.K_RIGHT else -1)
            elif ev.key == pygame.K_t:
                self.next_theme()
            else:
                self.widget.on_key(ev.key)
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            self.press = (ev.pos, self.t)
        elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1 and self.press:
            (x0, y0), t0 = self.press
            self.press = None
            dx, dy = ev.pos[0] - x0, ev.pos[1] - y0
            if EXIT_ZONE.collidepoint(x0, y0) and self.t - t0 > 0.6:
                return      # an abandoned hold-to-exit, not a tap
            if abs(dx) > SWIPE_PX and abs(dy) < 80:
                self.turn_page(-1 if dx > 0 else 1)
            else:
                self.widget.on_tap((x0, y0))
        elif ev.type == pygame.MOUSEMOTION and not self.windowed:
            self.cursor_until = self.t + 3.0
            pygame.mouse.set_visible(True)

    def update(self, dt):
        self.t += dt
        for page in self.pages:
            page.update(dt)
        if self.press and EXIT_ZONE.collidepoint(self.press[0]) and self.t - self.press[1] >= HOLD_EXIT_SECS:
            self.running = False
        if not self.windowed and self.cursor_until and self.t > self.cursor_until:
            self.cursor_until = 0.0
            pygame.mouse.set_visible(False)

    def draw(self):
        self.widget.draw(self.screen)
        if self.press and EXIT_ZONE.collidepoint(self.press[0]):
            held = self.t - self.press[1]
            if held > 0.4:
                left = max(0.0, HOLD_EXIT_SECS - held)
                draw_text(self.screen, "EXIT IN %.1f" % left, (W // 2, H // 2), 3,
                          (255, 255, 255), (0, 0, 0), anchor="center")

    def run(self):
        clock = pygame.time.Clock()
        fps = int(self.settings.get("fps", 30))
        last = time.monotonic()
        while self.running:
            for ev in pygame.event.get():
                self.handle(ev)
            now = time.monotonic()
            self.update(now - last)
            last = now
            self.draw()
            pygame.display.flip()
            clock.tick(fps)
        pygame.quit()


def single_instance():
    """Stop a second copy starting (e.g. if two autostart entries fire)."""
    try:
        import fcntl
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        lock = open(DATA_DIR / "app.lock", "w")
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return lock
    except (BlockingIOError, PermissionError):
        print("Retro Pomo is already running.")
        sys.exit(0)
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser(description="Retro Pomodoro timer")
    ap.add_argument("--windowed", action="store_true", help="run in a window instead of fullscreen")
    ap.add_argument("--fast", action="store_true", help="time runs 60x faster, for testing")
    ap.add_argument("--theme", help="theme folder name to start with")
    args = ap.parse_args()
    lock = single_instance()  # noqa: F841 (held open for the life of the app)
    App(windowed=args.windowed, speed=60.0 if args.fast else 1.0, theme=args.theme).run()


if __name__ == "__main__":
    main()
