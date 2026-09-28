"""Pomodoro timer: the state machine plus the widget that owns the two views."""
import pygame

from engine import W, H
from widgets.base import Widget
from widgets.scenery import draw_box_text

FOCUS, SHORT, LONG = "focus", "short", "long"
READY, RUNNING, PAUSED = "ready", "running", "paused"


class Timer:
    """FOCUS -> SHORT -> FOCUS ... and LONG after every `long_every` completed focus sessions."""

    def __init__(self, settings, speed=1.0):
        self.s = settings
        self.speed = speed          # >1 makes time pass faster (testing)
        self.phase = FOCUS
        self.state = READY
        self.done_in_cycle = 0      # completed focus sessions since the last long break
        self.session = 0            # bumps every phase change
        self.remaining = self.duration()
        self.events = []

    def duration(self, phase=None):
        key = {FOCUS: "focus_min", SHORT: "short_min", LONG: "long_min"}[phase or self.phase]
        return max(0.1, float(self.s[key])) * 60

    @property
    def long_every(self):
        return max(1, int(self.s["long_every"]))

    @property
    def progress(self):
        return min(1.0, max(0.0, 1.0 - self.remaining / self.duration()))

    @property
    def round(self):
        """Which focus session of the cycle we're on (1..long_every)."""
        if self.phase == FOCUS:
            return min(self.done_in_cycle + 1, self.long_every)
        return max(1, self.done_in_cycle)

    def toggle(self):
        self.state = PAUSED if self.state == RUNNING else RUNNING

    def reset(self):
        self.remaining = self.duration()
        self.state = READY

    def skip(self):
        self._advance(completed=False)

    def update(self, dt):
        if self.state == RUNNING:
            self.remaining -= dt * self.speed
            if self.remaining <= 0:
                self._advance(completed=True)

    def _advance(self, completed):
        if self.phase == FOCUS:
            if completed:
                self.done_in_cycle += 1
                self.events.append(("focus_done", self.done_in_cycle - 1))
            nxt = LONG if self.done_in_cycle >= self.long_every else SHORT
            auto = self.s["auto_start_break"]
        else:
            if completed:
                self.events.append(("break_done", None))
            if self.phase == LONG:
                self.done_in_cycle = 0
            nxt = FOCUS
            auto = self.s["auto_start_focus"]
        self.phase = nxt
        self.session += 1
        self.remaining = self.duration()
        self.state = RUNNING if auto else READY


# Tap zones on the 480x320 screen.
ZONE_THEME = pygame.Rect(W - 72, 0, 72, 48)
ZONE_VIEW = pygame.Rect(0, H - 48, 110, 48)
ZONE_SKIP = pygame.Rect(W - 72, 48, 72, H - 48)


class PomodoroWidget(Widget):
    name = "pomodoro"

    def __init__(self, app, speed=1.0):
        super().__init__(app)
        from widgets.view_clock import ClockView
        from widgets.view_level import LevelView
        self.timer = Timer(app.settings, speed)
        self.views = {"level": LevelView(self), "clock": ClockView(self)}
        self.t = 0.0
        self.flash_until = -1.0
        self.banner, self.banner_until = "", -1.0
        self.celebrate_from = -99.0     # when the last focus session finished
        self.last_done = (-1, -99.0)    # (cycle block index, time) for the coin pop
        self.skip_armed_until = -1.0
        self.hint_until = 5.0
        self.walk = 0.0                 # seconds of hero walking (clock view)
        self._flash = pygame.Surface((W, H))

    @property
    def view(self):
        v = self.app.settings.get("view")
        return v if v in self.views else "level"

    @property
    def celebrating(self):
        return self.t - self.celebrate_from < 4.0

    def update(self, dt):
        self.t += dt
        self.timer.update(dt)
        theme = self.app.theme
        for ev, arg in self.timer.events:
            if ev == "focus_done":
                self.app.stats.add_focus(self.app.settings["focus_min"])
                self.celebrate_from = self.t
                self.last_done = (arg, self.t)
                self._announce(theme.label("focus_done", "WELL DONE!"), 4.0)
            else:
                self._announce(theme.label("break_done", "BACK TO WORK!"), 3.0)
            self.app.request_focus(self)
        self.timer.events.clear()
        if self.timer.phase == FOCUS and self.timer.state == RUNNING:
            self.walk += dt

    def _announce(self, text, secs):
        self.banner, self.banner_until = text, self.t + secs
        self.flash_until = self.t + 1.5

    # ---- input ---------------------------------------------------------
    def on_tap(self, pos):
        self.hint_until = self.t + 4.0
        if ZONE_THEME.collidepoint(pos):
            self.app.next_theme()
        elif ZONE_VIEW.collidepoint(pos):
            self.switch_view()
        elif ZONE_SKIP.collidepoint(pos):
            if self.t < self.skip_armed_until:
                self.skip_armed_until = -1.0
                self.timer.skip()
            else:
                self.skip_armed_until = self.t + 2.5
        else:
            self.timer.toggle()

    def on_key(self, key):
        if key in (pygame.K_SPACE, pygame.K_RETURN):
            self.timer.toggle()
        elif key == pygame.K_s:
            self.timer.skip()
        elif key == pygame.K_r:
            self.timer.reset()
        elif key == pygame.K_v:
            self.switch_view()

    def switch_view(self):
        names = list(self.views)
        self.app.settings.set("view", names[(names.index(self.view) + 1) % len(names)])

    # ---- drawing -------------------------------------------------------
    def draw(self, surf):
        self.views[self.view].draw(surf)
        theme, t = self.app.theme, self.t
        if t < self.flash_until and int(t * 8) % 2 == 0:
            self._flash.fill(theme.color("flash"))
            self._flash.set_alpha(150)
            surf.blit(self._flash, (0, 0))
        if t < self.banner_until:
            draw_box_text(surf, theme, self.banner, (W // 2, 140 if self.view == "level" else 240), 3)
        if t < self.skip_armed_until:
            draw_box_text(surf, theme, "TAP AGAIN TO SKIP", (W // 2, 250), 2, 6)
        if t < self.hint_until:
            draw_box_text(surf, theme, "THEME", (ZONE_THEME.centerx, 18), 2, 4)
            draw_box_text(surf, theme, "VIEW", (ZONE_VIEW.centerx, H - 18), 2, 4)
            draw_box_text(surf, theme, "SKIP", (ZONE_SKIP.centerx, H // 2), 2, 4)
            draw_box_text(surf, theme, "HOLD=EXIT", (60, 18), 2, 4)
