ARG ARG_PORT=5000
ARG ARG_MAX_REQUESTS=0
ARG ARG_MAX_REQUESTS_JITTER=0

# Prep everything
FROM docker.io/python:3.12.0-bullseye as build

# Install webp dependencies
RUN apt update && apt install -y webp cmake

# Create the memegen user
RUN useradd -md /opt/memegen -u 1000 memegen
USER memegen

# Set the Working Directory to /opt/memegen
WORKDIR /opt/memegen

# Copy Directories
COPY --chown=memegen templates /opt/memegen/templates
COPY --chown=memegen scripts /opt/memegen/scripts
COPY --chown=memegen fonts /opt/memegen/fonts
COPY --chown=memegen docs /opt/memegen/docs
COPY --chown=memegen bin /opt/memegen/bin
COPY --chown=memegen app /opt/memegen/app

# Copy Specific Files
COPY --chown=memegen requirements.txt /opt/memegen
COPY --chown=memegen pyproject.toml /opt/memegen/
COPY --chown=memegen CHANGELOG.md /opt/memegen/CHANGELOG.md

# Install Python Requirements
RUN pip install wheel && \
    pip install -r /opt/memegen/requirements.txt

# Set the environment variables
ENV PATH="/opt/memegen/.local/bin:${PATH}"
ENV PORT="${ARG_PORT:-5000}"
ENV MAX_REQUESTS="${ARG_MAX_REQUESTS:-0}"
ENV MAX_REQUESTS_JITTER="${ARG_MAX_REQUESTS_JITTER:-0}"

# Set the entrypoint
ENTRYPOINT gunicorn --bind "0.0.0.0:$PORT" \
    --worker-class uvicorn.workers.UvicornWorker  \
    --max-requests="$MAX_REQUESTS" \
    --max-requests-jitter="$MAX_REQUESTS_JITTER" \
    --timeout=20  \
    app.main:app
