# Theme spec

A theme is one folder, `themes/<name>/`, holding a `theme.json` file. You can add
PNG images to the same folder. The app finds new theme folders on its own, and
tapping the top-right corner (or pressing **T**) cycles through them.

`themes/mario/theme.json` is the working example to copy from.

## theme.json

```jsonc
{
  "title": "Super Plumber",       // display name
  "pixel_scale": 2,               // each sprite pixel is drawn 2x2 on screen
  "palette":  { "R": "#e02010", ... },   // one character -> colour. "." and " " are transparent
  "colors":   { ... },            // named screen colours (see below)
  "labels":   { ... },            // on-screen words (see below)
  "options":  { "star_phases": ["long"] },   // phases whose sky gets twinkling stars
  "sprites":  { ... }             // pixel art (see below)
}
```

### colors
| key | used for |
|---|---|
| `sky_focus`, `sky_short`, `sky_long` | background per phase |
| `hud_text`, `hud_shadow` | top status bar |
| `text`, `text_shadow` | big clock and messages |
| `accent` | phase name ("FOCUS", "BREAK TIME") |
| `pole`, `pole_top` | goal pole at the end of the level |
| `star` | night-sky stars |
| `flash` | screen flash when a phase ends |
| `banner_bg` | box behind messages |

### labels
`player`, `coins`, `world`, `time`, `focus`, `short_break`, `long_break`,
`start`, `paused`, `focus_done`, `break_done`. Use only A-Z, 0-9 and `: . , ! ' - + / ? & *`.
Keep `player` at 6 characters or fewer, and the others under about 18.

### sprites
Each sprite is a list of equal-length strings, one per pixel row, where each
character is a palette key. For animation, use a list of frames (a list of lists).

| name | size (sprite pixels) | frames | notes |
|---|---|---|---|
| `hero_idle` | 16x16 | 1 | faces right |
| `hero_run` | 16x16 | 3+ | run cycle, faces right |
| `hero_jump` | 16x16 | 1 | optional |
| `hero_rest` | 16x16 | 1 | optional, shown on breaks |
| `coin` | 8x12 | 4 | spin: full, narrow, edge, narrow |
| `hud_coin` | - | - | usually `{"from": "coin", "scale": 1}` |
| `block` | 16x16 | 1 | the "?"-style block |
| `block_dim` | - | - | optional shimmer, e.g. `{"from": "block", "map": {"Q": "q"}}` |
| `block_used` | 16x16 | 1 | block after it's hit |
| `ground` | 16x16 | 1 | tiled along the bottom |
| `brick` | 16x16 | 1 | sits either side of some blocks |
| `pipe` | 16 wide, up to 24 tall | 1 | obstacle the hero jumps |
| `cloud` | about 24x12 | 1 | sky decoration |
| `bush` | about 24x12 | 1 | ground decoration |
| `hill` | about 48x22 | 1 | background decoration |
| `flag` | about 12x10 | 1 | on the goal pole, hangs to the left |

Shortcuts instead of drawing:
- `{"from": "cloud", "map": {"W": "h"}}`: a copy of another sprite with its colours swapped (add `"flip": true` to mirror it)
- `{"shape": "mound", "w": 48, "h": 22, "fill": "g", "outline": "d", "spots": "d"}`: a generated hill
- `{"frames": [...], "scale": 3}`: override `pixel_scale` for one sprite

### Your own pictures
To replace any sprite with a PNG, put `<sprite name>.png` in the theme folder
(for example `hero_idle.png`). For animation, name the frames `hero_run_0.png`,
`hero_run_1.png` and so on. PNGs are drawn at their actual size and are not
scaled, so make them the size you want on screen. The screen is 480x320, and the
hero sprite is normally 32x32.

## Prompt for generating a new theme with Claude

> Make a new theme for my Retro Pomo app. It's a folder `themes/<name>/` with a
> `theme.json` that follows `themes/THEME_SPEC.md`, using `themes/mario/theme.json`
> as the reference. Theme: **<e.g. Sonic: blue speedy hedgehog hero, gold rings
> instead of coins, green-and-brown checkered ground, palm trees for bushes,
> spring for the pipe, signpost goal>**. Draw original pixel art in that style,
> not copies of official sprites. Keep every sprite row the same length.
> Afterwards, render it with `tools/screenshot.py <name>` and check the images,
> then commit and push.

On the Pi, run `~/retro-pomo/update.sh`, then tap the top-right corner to switch themes.
