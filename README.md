# Retro Pomo

A retro-game Pomodoro timer for a Raspberry Pi with a small screen (built for a
Pi 3B and a 3.5" MPI3508 display at 480x320). It's written in Python and Pygame,
with no browser, and uses about 40 MB of RAM.

- Focus for 25 min, break for 5, and take a 15 min long break after every 4 sessions
- Two views: **Level run**, where the hero runs a level and reaches the flag at
  00:00, and **Big clock**, where the ? blocks pop coins as you complete sessions
- Tracks today's count and your day streak
- Themes are single JSON files of text pixel art (see `themes/THEME_SPEC.md`)

## Install on the Pi

```
sudo apt install -y git
git clone https://github.com/PacificSeedsAustralia/retro-pomo.git ~/retro-pomo
~/retro-pomo/install.sh
sudo reboot
```

To update later, run `~/retro-pomo/update.sh`.

## Controls

| Action | Touch / mouse | Keyboard |
|---|---|---|
| Start / pause | tap the middle | Space |
| Skip phase | tap the right edge twice | S |
| Reset phase | - | R |
| Switch view | tap bottom-left, or swipe | V or ← → |
| Next theme | tap top-right | T |
| Quit | hold top-left for 2 s | Esc |

## Settings

Edit `~/.config/retro-pomo/settings.json` (durations, `auto_start_break`,
`auto_start_focus`, `long_every`, `view`, `theme`), then restart the app.
Stats are kept in `~/.local/share/retro-pomo/stats.json`, and the log is in `log.txt` next to it.

## Develop on a computer

```
pip install pygame
python3 main.py --windowed --fast        # --fast makes 1 minute pass in 1 second
python3 tools/screenshot.py mario shots  # renders every view to PNG
```

## Adding a widget

Subclass `widgets/base.py:Widget` and add it to `App.pages` in `main.py`.
Swipe left or right, or use the arrow keys, to move between pages. The timer
keeps running in the background and jumps back to the front when a phase ends.
