# Stage 1: Builder mit uv 
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# Then, use a final image without uv
FROM python:3.12-slim-bookworm
# It is important to use the image that matches the builder, as the path to the
# Python executable must be the same, e.g., using `python:3.11-slim-bookworm`
# will fail.

WORKDIR /app

# Dos2unix installieren, falls noch nicht vorhanden
RUN apt-get update && apt-get install -y \
    dos2unix \
    libgomp1 \
&& rm -rf /var/lib/apt/lists/*

# Copy the application from the builder
COPY --from=builder --chown=app:app /app /app

# Zeilenenden konvertieren
RUN dos2unix /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8050

# Run the plotly dash application by default
ENTRYPOINT ["/app/entrypoint.sh"]