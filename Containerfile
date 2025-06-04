ARG ARG_PORT=5000
ARG ARG_MAX_REQUESTS=0
ARG ARG_MAX_REQUESTS_JITTER=0

FROM docker.io/python:3.13.3-bullseye as build

# Install system dependencies
RUN apt update && apt install --yes webp cmake
RUN pip install poetry

# Create the memegen user
RUN useradd -md /opt/memegen -u 1000 memegen
USER memegen

# Set the working directory
WORKDIR /opt/memegen

# Copy project files
COPY --chown=memegen templates /opt/memegen/templates
COPY --chown=memegen scripts /opt/memegen/scripts
COPY --chown=memegen fonts /opt/memegen/fonts
COPY --chown=memegen docs /opt/memegen/docs
COPY --chown=memegen bin /opt/memegen/bin
COPY --chown=memegen app /opt/memegen/app
COPY --chown=memegen pyproject.toml /opt/memegen/
COPY --chown=memegen poetry.lock /opt/memegen/
COPY --chown=memegen CHANGELOG.md /opt/memegen/CHANGELOG.md

# Install project dependencies
RUN poetry install --only=main

# Set environment variables
ENV PATH="/opt/memegen/.local/bin:${PATH}"
ENV PORT="${ARG_PORT:-5000}"
ENV MAX_REQUESTS="${ARG_MAX_REQUESTS:-0}"
ENV MAX_REQUESTS_JITTER="${ARG_MAX_REQUESTS_JITTER:-0}"

# Set the entrypoint
ENTRYPOINT poetry run gunicorn --bind "0.0.0.0:$PORT" \
    --worker-class uvicorn.workers.UvicornWorker  \
    --max-requests="$MAX_REQUESTS" \
    --max-requests-jitter="$MAX_REQUESTS_JITTER" \
    --timeout=20  \
    app.main:app
