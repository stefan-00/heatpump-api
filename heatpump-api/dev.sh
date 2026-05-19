#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
  .venv/bin/pip install -q -r requirements.txt
fi

: "${HEATPUMP_URL:?Set HEATPUMP_URL (e.g. http://192.168.1.x)}"
: "${HEATPUMP_USERNAME:?Set HEATPUMP_USERNAME}"
: "${HEATPUMP_PASSWORD:?Set HEATPUMP_PASSWORD}"

exec .venv/bin/python -m app.main
