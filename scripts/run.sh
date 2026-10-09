#!/usr/bin/env bash
set -euo pipefail

cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
export PORT="${PORT:-8080}"
exec python3 app.py
