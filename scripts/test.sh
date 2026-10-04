#!/bin/bash
set -euo pipefail

PORT="${PORT:-8080}"
BASE="http://localhost:${PORT}"


python3 app.py &
SERVER_PID=$!


trap "kill $SERVER_PID 2>/dev/null || true" EXIT

sleep 2

PASS=0
TOTAL=3


CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/healthz")
if [ "$CODE" = "200" ]; then PASS=$((PASS + 1)); fi


if curl -s "$BASE/" | grep -q "notes"; then PASS=$((PASS + 1)); fi


RESP=$(curl -s -X POST "$BASE/notes" -H "Content-Type: application/json" -d '{"text":"test"}')
if echo "$RESP" | grep -q "test"; then PASS=$((PASS + 1)); fi

echo "TESTS: ${PASS}/${TOTAL}"
[ "$PASS" -eq "$TOTAL" ] && exit 0 || exit 1
