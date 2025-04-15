FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/app/.venv/bin:$PATH"

# UV installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# UV project copy
COPY pyproject.toml .
COPY uv.lock .

RUN uv sync --frozen --all-groups

COPY films_backend films_backend

CMD ["uv", "run", "uvicorn", "films_backend.api.main:app", "--host", "0.0.0.0", "--port", "8080", "--forwarded-allow-ips='nginx'"]
