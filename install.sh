#!/bin/bash
# One-time setup on the Pi: packages, autostart on boot, no screen blanking.
set -e
cd "$(dirname "$0")"
DIR="$(pwd)"

echo "== Installing packages"
sudo apt-get update
sudo apt-get install -y python3-pygame git
chmod +x run.sh update.sh

echo "== Menu entry + autostart"
mkdir -p ~/.config/autostart ~/.local/share/applications
cat > ~/.local/share/applications/retro-pomo.desktop <<DESK
[Desktop Entry]
Type=Application
Name=Retro Pomo
Comment=Retro Pomodoro timer
Exec=$DIR/run.sh
Icon=alarm-clock
Categories=Utility;
DESK
cat > ~/.config/autostart/retro-pomo.desktop <<DESK
[Desktop Entry]
Type=Application
Name=Retro Pomo
Exec=env RETRO_POMO_DELAY=3 $DIR/run.sh
DESK

# Newer Pi OS desktops use labwc. Its user autostart file replaces the system one,
# so copy the system file first to keep the taskbar and desktop working.
if [ -f /etc/xdg/labwc/autostart ]; then
  mkdir -p ~/.config/labwc
  [ -f ~/.config/labwc/autostart ] || cp /etc/xdg/labwc/autostart ~/.config/labwc/autostart
  grep -q "retro-pomo" ~/.config/labwc/autostart || \
    echo "env RETRO_POMO_DELAY=3 $DIR/run.sh &" >> ~/.config/labwc/autostart
fi

echo "== Keeping the screen awake"
if command -v raspi-config >/dev/null; then
  sudo raspi-config nonint do_blanking 1 || true
fi

echo
echo "Done. Reboot to start automatically:  sudo reboot"
echo "Or start it now:                      $DIR/run.sh &"
