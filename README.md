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

## Container image (M3)

The root `Dockerfile` uses `python:3.12-slim-bookworm` and runs as the non-root
user `10001:10001`. It copies only `app.py` and the startup script. There are
no external Python dependencies or build tools to install. `.dockerignore`
also excludes Git history, environment files, keys and caches.

Build and run locally when Docker is available:

```bash
docker build -t notes-api:dev .
docker run --rm -e PORT=9090 -p 9090:9090 notes-api:dev
```

From another terminal, `curl --fail http://localhost:9090/healthz` returns
`OK`. `PORT` controls the port inside the container; both sides of `-p`
must match the port used in this example. Notes remain in memory only.

### Build, scan and publish

On pull requests and branch pushes the existing test job runs. Only pushes
to `main` can run the `publish` job, and `needs: tests` makes it wait for a
successful test job. The publish job:

1. Builds a `linux/amd64` image with cached Docker layers.
2. Checks that the image runs as non-root and is smaller than 500 MB.
3. Starts it on `PORT=9123` and checks `/healthz`.
4. Scans it with Trivy; fixable CRITICAL vulnerabilities fail the job.
5. Publishes that exact tested image, without rebuilding, to
   `ghcr.io/almabaynurdaulet/notes-api` with the full commit SHA and `latest`.

Only the publish job receives `packages: write`. Registry login uses the
temporary `GITHUB_TOKEN`, not a personal password. Third-party actions are
pinned to full commit SHAs. Trivy's cache stays outside the build context.
New pushes do not cancel an in-progress publication on `main`.

### Public access and verification

After the first successful publish, open the repository's package, then
**Package settings > Change visibility > Public**. GitHub creates packages
as private, even in a public repository. Making a package public is
irreversible; the marker needs anonymous pull access.

On an up-to-date checkout of `main`, test the image for that exact commit:

```bash
IMAGE=ghcr.io/almabaynurdaulet/notes-api
SHA=$(git rev-parse HEAD)
docker pull --platform linux/amd64 "$IMAGE:$SHA"
docker run --rm --platform linux/amd64 -e PORT=9090 -p 9090:9090 "$IMAGE:$SHA"
```

Run the teacher's marker from `inf345-week6-lab` with Python and PyYAML:

```bash
python3 mark_m3.py --repo https://github.com/AlmabayNurdaulet/notes-api
```

Use `--offline` for file checks only. It cannot confirm publication or that
the image runs, so a partial offline score is not a complete M3 result.

## Executable scripts on Windows

The executable bits must be committed to Git, not just set locally:

```bash
git update-index --chmod=+x scripts/run.sh scripts/test.sh
```

Commit and push the mode change. `.gitattributes` preserves Unix line endings.
