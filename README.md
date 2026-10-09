# Notes API

A small notes HTTP API written in Python (standard library only).

## What it does

- `GET /healthz` — health check, returns `OK`
- `GET /` — list all notes as JSON
- `POST /notes` — create a note, body `{"text": "..."}`
- `GET /notes/<id>` — retrieve one note (404 when missing)

Notes are stored in memory and are lost when the server stops. There is no
database or front end. Python 3 and Bash are required; no third-party Python
packages are needed. On Windows, use Git Bash or WSL for the scripts.

## How to run

```bash
./scripts/run.sh
```

Open `http://localhost:8080/`. Stop the service with Ctrl+C.

## Port

The service reads the `PORT` environment variable and defaults to port `8080`.

For example:

```bash
PORT=9000 ./scripts/run.sh
```

## How to test

```bash
./scripts/test.sh
```

Seven HTTP tests start the service on a free local port, check its responses,
and stop it afterwards. A successful run exits with code 0 and prints
`TESTS: 7/7`. A failing test exits nonzero. The tests also fail if `app.py`
is missing; they do not use a service you already have running.

Run the command twice to check that tests do not depend on leftover state.

## Continuous integration (M2)

`.github/workflows/ci.yml` runs `./scripts/test.sh` on pushes and pull requests
using Ubuntu 24.04 and Python 3.12. It uses Bash, read-only repository
permissions, release-pinned official actions, and a four-minute job timeout.
There are no third-party dependencies to install or cache.

The course requires a failed CI run followed by a successful run. Test this
on a separate branch by changing one expected response, then restore the
expectation. Keep the default branch working.

## Executable scripts on Windows

The executable bits must be committed to Git, not just set locally:

```bash
git update-index --chmod=+x scripts/run.sh scripts/test.sh
```

Commit and push the mode change. `.gitattributes` preserves Unix line endings.
