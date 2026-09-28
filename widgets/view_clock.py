"""Big-clock view: a giant countdown, one ? block per session in the cycle
(each pops a coin when that focus session is done), hero strolling below."""
import math

from engine import W
from engine.font import draw_text
from widgets.pomodoro import FOCUS, PAUSED, READY, RUNNING
from widgets.scenery import blink, draw_big_time, draw_hud, draw_scenery


class ClockView:
    def __init__(self, widget):
        self.w = widget

    def draw(self, surf):
        theme, timer, t = self.w.app.theme, self.w.timer, self.w.t
        fg, sh = theme.color("text"), theme.color("text_shadow")
        gy = draw_scenery(surf, theme, timer.phase, t, clouds=False)
        draw_hud(surf, theme, timer, self.w.app.stats)

        key = {"focus": "focus", "short": "short_break", "long": "long_break"}[timer.phase]
        draw_text(surf, theme.label(key, key.upper()), (W // 2, 50), 3,
                  theme.color("accent"), sh, anchor="midtop")
        draw_big_time(surf, theme, timer.remaining, 80, 12)

        # one block per focus session in the cycle
        block = theme.sprite("block")
        bw, bh = block.get_size() if block else (32, 32)
        n, gap, by = timer.long_every, 20, 186
        x0 = (W - (n * bw + (n - 1) * gap)) // 2
        bump_i, bump_t = self.w.last_done
        since = t - bump_t
        for i in range(n):
            x = x0 + i * (bw + gap)
            if i == bump_i and 0 <= since < 0.8:
                coin = theme.sprite("coin", int(since * 16))
                if coin:
                    surf.blit(coin, (x + (bw - coin.get_width()) / 2, by - coin.get_height() - since * 70))
            bump = 8 * math.sin(math.pi * since / 0.2) if i == bump_i and 0 <= since < 0.2 else 0
            if i < timer.done_in_cycle:
                img = theme.sprite("block_used")
            elif i == timer.done_in_cycle and timer.phase == FOCUS and timer.state == RUNNING \
                    and theme.frames("block_dim") and int(t * 3) % 3 == 2:
                img = theme.sprite("block_dim")
            else:
                img = block
            if img:
                surf.blit(img, (x, by - bump))

        # hero strolls back and forth while focusing
        hero = theme.sprite("hero_idle")
        if hero:
            hw, hh = hero.get_size()
            span = W - 80 - hw
            if timer.phase == FOCUS and timer.state == RUNNING:
                s = (self.w.walk * 36) % (2 * span)
                x, flip = 40 + (s if s < span else 2 * span - s), s >= span
                img = theme.sprite("hero_run", t * 10, flip)
            else:
                x, img = 40, (theme.sprite("hero_rest") if timer.phase != FOCUS else None) or hero
            surf.blit(img, (x, gy - hh))

        if timer.state == READY and blink(t) and not self.w.celebrating:
            draw_text(surf, theme.label("start", "TAP TO START"), (W // 2, 232), 2, fg, sh, anchor="midtop")
        elif timer.state == PAUSED and blink(t):
            draw_text(surf, theme.label("paused", "PAUSED"), (W // 2, 232), 2, fg, sh, anchor="midtop")
