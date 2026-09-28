#!/bin/bash
# Pull the latest code from GitHub and restart the app.
cd "$(dirname "$0")"
DIR="$(pwd)"
git pull --ff-only || { echo "Update failed (see above)."; exit 1; }
pkill -f "retro-pomo/run.sh" 2>/dev/null
pkill -f "python3 main.py" 2>/dev/null
sleep 1
setsid nohup "$DIR/run.sh" >/dev/null 2>&1 &
echo "Updated. Retro Pomo is restarting."
