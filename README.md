# Notes API

A small notes HTTP API written in Python (standard library only).

## What it does
- `GET /healthz` — health check, returns `OK`
- `GET /` — list all notes as JSON
- `POST /notes` — create a note, body `{"text": "..."}`

## How to run
```bash
./scripts/run.sh
