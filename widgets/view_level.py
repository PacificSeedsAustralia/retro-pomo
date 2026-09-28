"""Level-run view: the hero runs through a level as the focus timer counts down,
jumping pipes and bumping blocks, and reaches the flagpole at 00:00."""
import datetime
import math
import random

from engine import W
from engine.font import draw_text
from widgets.pomodoro import FOCUS, LONG, PAUSED, READY, RUNNING
from widgets.scenery import (blink, draw_big_time, draw_hud, draw_scenery,
                             ground_top, hash2)

RUN_SPEED = 24      # world pixels per second of focus time
HERO_X = 110        # where the hero sits on screen while the level scrolls
BLOCK_LIFT = 112    # block top is this far above the ground


def build_level(seed, length):
    rnd = random.Random(seed)
    out, x = [], 420
    while x < length - 300:
        out.append({"kind": rnd.choice(("pipe", "block", "block", "bricks")), "x": x, "hit": None})
        x += rnd.randint(260, 520)
    return out


class LevelView:
    def __init__(self, widget):
        self.w = widget
        self.level_session = None
        self.obstacles = []
        self.length = 1.0

    def _ensure_level(self):
        timer = self.w.timer
        if timer.phase == FOCUS and timer.session != self.level_session:
            self.level_session = timer.session
            self.length = timer.duration(FOCUS) * RUN_SPEED
            seed = hash2(datetime.date.today().toordinal(), timer.session)
            self.obstacles = build_level(seed, self.length)

    def draw(self, surf):
        self._ensure_level()
        timer = self.w.timer
        if timer.phase == FOCUS:
            self._draw_run(surf, timer.progress)
        elif self.w.celebrating:
            self._draw_run(surf, 1.0, finished=True)
        else:
            self._draw_break(surf)
        draw_hud(surf, self.w.app.theme, timer, self.w.app.stats)

    # ---- focus: the run --------------------------------------------------
    def _draw_run(self, surf, p, finished=False):
        theme, timer, t = self.w.app.theme, self.w.timer, self.w.t
        hx = p * self.length
        cam = max(0.0, min(hx - HERO_X, self.length - 340))
        gy = draw_scenery(surf, theme, FOCUS, t, cam)

        hero = theme.sprite("hero_idle")
        hw, hh = hero.get_size() if hero else (32, 32)
        hc = hx + hw / 2
        arc = 0.0
        moving = timer.state == RUNNING and timer.phase == FOCUS

        block = theme.sprite("block")
        bw, bh = block.get_size() if block else (32, 32)
        pipe = theme.sprite("pipe")
        pw, ph = pipe.get_size() if pipe else (32, 40)
        by = gy - BLOCK_LIFT

        for o in self.obstacles:
            sx = o["x"] - cam
            if o["kind"] == "pipe":
                a, b, height = o["x"] - 56, o["x"] + pw + 56, ph + 24
            else:
                cx = o["x"] + bw / 2
                a, b, height = cx - 44, cx + 44, BLOCK_LIFT - bh - hh
                if o["hit"] is None and hc >= cx:
                    o["hit"] = t if moving else -99.0
            if a <= hc <= b:
                arc = max(arc, height * math.sin(math.pi * (hc - a) / (b - a)))
            if sx > W + 40 or sx < -bw - 40:
                continue
            if o["kind"] == "pipe":
                if pipe:
                    surf.blit(pipe, (sx, gy - ph))
                continue
            since = t - o["hit"] if o["hit"] is not None else -1
            if 0 <= since < 0.6:
                coin = theme.sprite("coin", int(since * 16))
                if coin:
                    surf.blit(coin, (sx + (bw - coin.get_width()) / 2, by - coin.get_height() - since * 90))
            if o["kind"] == "bricks":
                brick = theme.sprite("brick")
                if brick:
                    surf.blit(brick, (sx - bw, by))
                    surf.blit(brick, (sx + bw, by))
            bump = 8 * math.sin(math.pi * since / 0.2) if 0 <= since < 0.2 else 0
            if o["hit"] is not None:
                img = theme.sprite("block_used")
            else:
                img = theme.sprite("block_dim" if theme.frames("block_dim") and int(t * 3) % 3 == 2 else "block")
            if img:
                surf.blit(img, (sx, by - bump))

        # flagpole
        fx = int(self.length + 40 - cam)
        top = gy - 170
        surf.fill(theme.color("pole"), (fx, top, 4, gy - top))
        surf.fill(theme.color("pole_top"), (fx - 3, top - 8, 10, 10))
        flag = theme.sprite("flag")
        if flag:
            drop = min(1.0, (t - self.w.celebrate_from) / 1.2) * 130 if finished else 0
            surf.blit(flag, (fx - flag.get_width(), top + 4 + drop))

        # hero
        if finished:
            arc = abs(math.sin((t - self.w.celebrate_from) * 5)) * 24
        elif timer.state == READY:
            arc = abs(math.sin(t * 4)) * 14 if int(t) % 3 == 0 else 0
        if arc > 2:
            img = theme.sprite("hero_jump") or hero
        elif moving:
            img = theme.sprite("hero_run", t * 10)
        else:
            img = hero
        if img:
            surf.blit(img, (hx - cam, gy - hh - arc))

        draw_big_time(surf, theme, timer.remaining if not finished else 0, 50, 5)
        self._prompts(surf)

    # ---- breaks ---------------------------------------------------------
    def _draw_break(self, surf):
        theme, timer, t = self.w.app.theme, self.w.timer, self.w.t
        gy = draw_scenery(surf, theme, timer.phase, t, 0, cloud_cam=t * 10)
        label = theme.label("long_break" if timer.phase == LONG else "short_break", "BREAK")
        draw_text(surf, label, (W // 2, 100), 3, theme.color("accent"), theme.color("text_shadow"), anchor="midtop")
        coins = theme.frames("coin")
        if coins:
            n = 7
            for i in range(n):
                img = theme.sprite("coin", t * 8 + i)
                x = W // 2 + (i - (n - 1) / 2) * 40 - img.get_width() / 2
                surf.blit(img, (x, 185 + math.sin(t * 2 + i * 0.7) * 10))
        hero = theme.sprite("hero_rest") or theme.sprite("hero_idle")
        if hero:
            surf.blit(hero, (60, gy - hero.get_height()))
        draw_big_time(surf, theme, timer.remaining, 50, 5)
        self._prompts(surf)

    def _prompts(self, surf):
        theme, timer, t = self.w.app.theme, self.w.timer, self.w.t
        fg, sh = theme.color("text"), theme.color("text_shadow")
        if self.w.celebrating and timer.phase != FOCUS:
            return
        if timer.state == READY:
            if timer.phase == FOCUS:
                world = "%s %d-%d" % (theme.label("world", "WORLD"), max(1, self.w.app.stats.streak), timer.round)
                draw_text(surf, world, (W // 2, 108), 3, fg, sh, anchor="midtop")
            if blink(t):
                draw_text(surf, theme.label("start", "TAP TO START"), (W // 2, 146), 2, fg, sh, anchor="midtop")
        elif timer.state == PAUSED and blink(t):
            draw_text(surf, theme.label("paused", "PAUSED"), (W // 2, 116), 3, fg, sh, anchor="midtop")
