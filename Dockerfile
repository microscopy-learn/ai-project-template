FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy PYTHONUNBUFFERED=1

# Install dependencies first so code changes don't invalidate this layer.
COPY pyproject.toml uv.lock* README.md ./
RUN uv sync --no-dev --extra llm --no-install-project

COPY src ./src
COPY data ./data
RUN uv sync --no-dev --extra llm

# Run as a non-root user.
RUN useradd --create-home appuser
USER appuser

EXPOSE 8080
# Cloud Run sets PORT; default to 8080 locally.
CMD ["sh", "-c", "uv run --no-sync uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
