# Use latest official Python image
FROM python:bullseye
# Copy code into workdir
WORKDIR /usr/src/memegen
COPY . .
# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && ln -s /root/.local/bin/poetry /usr/bin/poetry
# Install dependencies and build site
RUN make doctor && make install && make site
# Expose web port 5000
EXPOSE 5000
# Run server command. I'm sure it can be prettier than this, though.
ENTRYPOINT ["/usr/src/memegen/.venv/bin/gunicorn", "app.main:app", "--bind", "0.0.0.0:5000", "--worker-class", "uvicorn.workers.UvicornWorker", "--max-requests", "0", "--max-requests-jitter", "0", "--timeout","25"]
