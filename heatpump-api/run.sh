#!/usr/bin/env bash
# Config is read from /data/options.json (HA add-on) or env vars (local dev) by app/config.py.
set -e
exec python -m app.main
