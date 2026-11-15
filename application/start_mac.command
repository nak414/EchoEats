#!/bin/zsh
cd "$(dirname "$0")" || exit 1
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is required. Install Python 3 and try again."
  read -r '?Press Enter to close...'
  exit 1
fi
python3 -m pip install -r requirements.txt || exit 1
python3 run_echoeats.py
