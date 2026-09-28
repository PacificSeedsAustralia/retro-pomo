"""Loads themes/<name>/theme.json and turns its text-grid sprites into images.

See themes/THEME_SPEC.md for the file format.
"""
import json

import pygame

from . import THEMES_DIR

TRANSPARENT = ". "


def available_themes():
    return sorted(p.parent.name for p in THEMES_DIR.glob("*/theme.json"))


class Theme:
    def __init__(self, name):
        self.name = name
        self.dir = THEMES_DIR / name
        with open(self.dir / "theme.json") as f:
            data = json.load(f)
        self.title = data.get("title", name)
        self.scale = int(data.get("pixel_scale", 2))
        self.palette = {k: pygame.Color(v) for k, v in data.get("palette", {}).items() if v}
        self.colors = {k: pygame.Color(v) for k, v in data.get("colors", {}).items()}
        self.labels = data.get("labels", {})
        self.options = data.get("options", {})
        self._specs = data.get("sprites", {})
        self._grids = {}
        self._frames = {}
        self._flipped = {}
        self._warned = set()
        for name in self._specs:
            self._build(name)

    # ---- lookups -------------------------------------------------------
    def color(self, key, default="#ffffff"):
        c = self.colors.get(key)
        return c if c is not None else pygame.Color(default)

    def label(self, key, default=""):
        return self.labels.get(key, default)

    def frames(self, name):
        return self._frames.get(name, [])

    def sprite(self, name, frame=0, flip=False):
        frames = self._frames.get(name)
        if not frames:
            return None
        i = int(frame) % len(frames)
        if not flip:
            return frames[i]
        key = (name, i)
        if key not in self._flipped:
            self._flipped[key] = pygame.transform.flip(frames[i], True, False)
        return self._flipped[key]

    # ---- building ------------------------------------------------------
    def _build(self, name, stack=()):
        if name in self._frames:
            return self._grids.get(name)
        if name in stack or name not in self._specs:
            print("theme %s: missing or circular sprite %r" % (self.name, name))
            self._frames[name] = []
            return None
        pngs = self._png_frames(name)
        if pngs:
            self._frames[name] = pngs
            return None
        spec = self._specs[name]
        scale = self.scale
        if isinstance(spec, dict):
            scale = int(spec.get("scale", scale))
            if "frames" in spec:
                grids = self._as_frames(spec["frames"])
            elif "from" in spec:
                src = self._build(spec["from"], stack + (name,)) or []
                table = spec.get("map", {})
                grids = [["".join(table.get(ch, ch) for ch in row) for row in g] for g in src]
                if spec.get("flip"):
                    grids = [[row[::-1] for row in g] for g in grids]
            elif spec.get("shape") == "mound":
                grids = [_mound(spec)]
            else:
                grids = []
        else:
            grids = self._as_frames(spec)
        self._grids[name] = grids
        self._frames[name] = [self._surface(g, scale) for g in grids]
        return grids

    @staticmethod
    def _as_frames(spec):
        if spec and isinstance(spec[0], str):
            return [spec]
        return list(spec)

    def _png_frames(self, name):
        files = [self.dir / (name + ".png")]
        if not files[0].exists():
            files = sorted(self.dir.glob(name + "_[0-9]*.png"))
        out = []
        for p in files:
            if p.exists():
                img = pygame.image.load(str(p))
                out.append(img.convert_alpha() if pygame.display.get_surface() else img)
        return out

    def _surface(self, grid, scale):
        w = max((len(r) for r in grid), default=1)
        surf = pygame.Surface((max(1, w), max(1, len(grid))), pygame.SRCALPHA)
        for y, row in enumerate(grid):
            for x, ch in enumerate(row):
                if ch in TRANSPARENT:
                    continue
                c = self.palette.get(ch)
                if c is None:
                    if ch not in self._warned:
                        self._warned.add(ch)
                        print("theme %s: no palette colour for %r" % (self.name, ch))
                    continue
                surf.set_at((x, y), c)
        if scale != 1:
            surf = pygame.transform.scale(surf, (surf.get_width() * scale, surf.get_height() * scale))
        return surf


def _mound(spec):
    """Procedural rounded hill: {"shape": "mound", "w": 40, "h": 18, "fill": "g", "outline": "K", "spots": "D"}"""
    w, h = int(spec.get("w", 40)), int(spec.get("h", 18))
    fill = spec.get("fill", "g")
    outline, spots = spec.get("outline", fill), spec.get("spots")
    cx = (w - 1) / 2.0

    def inside(x, y):
        if not (0 <= x < w and 0 <= y < h):
            return y >= h and 0 <= x < w
        dx = (x - cx) / (w / 2.0)
        dy = (h - y) / float(h)
        return dx * dx + dy * dy <= 1.0

    rows = []
    for y in range(h):
        row = []
        for x in range(w):
            if not inside(x, y):
                row.append(".")
            elif not all(inside(x + a, y + b) for a, b in ((1, 0), (-1, 0), (0, -1))):
                row.append(outline)
            else:
                row.append(fill)
        rows.append(row)
    if spots:
        for sx, sy in ((cx - w * 0.12, h * 0.35), (cx + w * 0.1, h * 0.45), (cx - w * 0.02, h * 0.62)):
            for dy in range(3):
                x, y = int(sx), int(sy) + dy
                if 0 <= y < h and rows[y][x] == fill:
                    rows[y][x] = spots
    return ["".join(r) for r in rows]
