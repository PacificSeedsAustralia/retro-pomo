"""Drawing helpers shared by the views: sky, parallax layers, ground, HUD, big clock."""
import math

import pygame

from engine import W, H
from engine.font import draw_text, text_surface


def hash2(a, b):
    x = (a * 73856093 ^ b * 19349663) & 0xFFFFFFFF
    x ^= x >> 13
    x = (x * 0x5BD1E995) & 0xFFFFFFFF
    x ^= x >> 15
    return x


def fmt_time(seconds):
    s = int(math.ceil(max(0.0, seconds)))
    return "%02d:%02d" % (s // 60, s % 60)


def ground_top(theme):
    tile = theme.sprite("ground")
    return H - (tile.get_height() if tile else 32)


def draw_sky(surf, theme, phase, t):
    surf.fill(theme.color("sky_" + phase, "#6890f8"))
    if phase in theme.options.get("star_phases", []):
        c = theme.color("star")
        for i in range(45):
            h = hash2(7, i)
            x, y = h % W, 48 + (h >> 9) % 190
            if math.sin(t * 1.7 + i * 1.3) > 0.7:
                surf.fill(c, (x - 2, y, 5, 1))
                surf.fill(c, (x, y - 2, 1, 5))
            else:
                surf.fill(c, (x, y, 1 + (h >> 20) % 2, 1 + (h >> 20) % 2))


def draw_layer(surf, theme, name, cam, factor, spacing, seed, y, jitter=0, skip=0, bottom=False):
    """Repeat a sprite across the screen at pseudo-random spacing, scrolled by cam*factor."""
    img = theme.sprite(name)
    if img is None:
        return
    off = cam * factor
    first = int(off // spacing) - 1
    for i in range(first, first + W // spacing + 3):
        h = hash2(seed, i)
        if skip and h % skip == 0:
            continue
        x = i * spacing + (h >> 4) % (spacing // 2) - off
        yy = y - img.get_height() if bottom else y + (h >> 8) % (jitter + 1)
        surf.blit(img, (int(x), int(yy)))


def draw_ground(surf, theme, cam, gy):
    tile = theme.sprite("ground")
    if tile is None:
        surf.fill(theme.color("ground", "#c85418"), (0, gy, W, H - gy))
        return
    tw, th = tile.get_size()
    for y in range(gy, H, th):
        for x in range(-(int(cam) % tw), W, tw):
            surf.blit(tile, (x, y))


def draw_scenery(surf, theme, phase, t, cam=0.0, cloud_cam=None, clouds=True):
    gy = ground_top(theme)
    draw_sky(surf, theme, phase, t)
    if clouds:
        draw_layer(surf, theme, "cloud", cam * 0.25 if cloud_cam is None else cloud_cam, 1.0, 190, 11, 96, jitter=60)
    draw_layer(surf, theme, "hill", cam, 0.5, 300, 23, gy, skip=3, bottom=True)
    draw_layer(surf, theme, "bush", cam, 1.0, 250, 37, gy, skip=2, bottom=True)
    draw_ground(surf, theme, cam, gy)
    return gy


def draw_hud(surf, theme, timer, stats):
    fg, sh = theme.color("hud_text"), theme.color("hud_shadow")
    cols, y1, y2 = (16, 140, 268, 388), 6, 24
    draw_text(surf, theme.label("player", "PLAYER"), (cols[0], y1), 2, fg, sh)
    draw_text(surf, "%06d" % (stats.total * 100), (cols[0], y2), 2, fg, sh)
    draw_text(surf, theme.label("coins", "COINS"), (cols[1], y1), 2, fg, sh)
    x = cols[1]
    coin = theme.sprite("hud_coin")
    if coin is not None:
        surf.blit(coin, (x, y2 + 1))
        x += coin.get_width() + 3
    draw_text(surf, "×%02d" % stats.today, (x, y2), 2, fg, sh)
    draw_text(surf, theme.label("world", "WORLD"), (cols[2], y1), 2, fg, sh)
    draw_text(surf, "%d-%d" % (max(1, stats.streak), timer.round), (cols[2], y2), 2, fg, sh)
    draw_text(surf, theme.label("time", "TIME"), (cols[3], y1), 2, fg, sh)
    draw_text(surf, fmt_time(timer.remaining), (cols[3], y2), 2, fg, sh)


def draw_big_time(surf, theme, seconds, y, scale):
    draw_text(surf, fmt_time(seconds), (W // 2, y), scale,
              theme.color("text"), theme.color("text_shadow"), anchor="midtop")


def blink(t, rate=2.0):
    return int(t * rate) % 2 == 0


def draw_box_text(surf, theme, text, center, scale=3, pad=8):
    s = text_surface(text, scale, theme.color("text"), theme.color("text_shadow"))
    r = s.get_rect(center=center)
    box = r.inflate(pad * 2, pad * 2)
    bg = pygame.Surface(box.size, pygame.SRCALPHA)
    c = theme.color("banner_bg", "#000000")
    bg.fill((c.r, c.g, c.b, 190))
    surf.blit(bg, box)
    surf.blit(s, r)
