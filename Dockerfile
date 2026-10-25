FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid app --no-create-home app

# The application uses only the Python standard library.
COPY --chown=10001:10001 app.py ./
COPY --chown=10001:10001 --chmod=755 scripts/run.sh ./scripts/run.sh

USER 10001:10001
EXPOSE 8080

CMD ["./scripts/run.sh"]
