#!/bin/bash
# Launch Retro Pomo. Restarts it if it crashes, but not when you quit on purpose.
cd "$(dirname "$0")"
LOG="$HOME/.local/share/retro-pomo/log.txt"
mkdir -p "$(dirname "$LOG")"
[ -f "$LOG" ] && tail -n 300 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"
sleep "${RETRO_POMO_DELAY:-0}"
while true; do
  python3 main.py "$@" >>"$LOG" 2>&1
  code=$?
  [ "$code" -eq 0 ] && break
  echo "$(date) exited with code $code, restarting in 5s" >>"$LOG"
  sleep 5
done
