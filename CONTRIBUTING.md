# Setup

## Requirements

- Make:
  - macOS: `$ xcode-select --install`
  - Linux: [https://www.gnu.org/software/make](https://www.gnu.org/software/make)
  - Windows: [https://mingw.org/download/installer](https://mingw.org/download/installer)
- Python: `$ pyenv install`
- Poetry: [https://poetry.eustace.io/docs/#installation](https://poetry.eustace.io/docs/#installation)

To confirm these system dependencies are configured correctly:

```text
$ make doctor
```

## Installation

Install project dependencies into a virtual environment:

```text
$ make install
```

# Local Development

To start the API server and static site:

```text
$ make run
```

## Preview image rendering

View all example images: http://localhost:5000/examples

View test images with automatic reload: http://localhost:5000/test

To view a specific image with automatic reload, simply drop the file extension.

## Add a new meme template

1. Visit http://localhost:5000/<my_new_template_id>
2. Add a `default.png` (or JPG) background image in `templates/<my_new_template_id>` directory
3. Update `config.yml` in the `templates/<my_new_template_id>` directory
4. Refresh http://localhost:5000/images/<my_new_template_id> to see the example
5. Adjust `config.yml` as necessary to position and style the text
6. Visit http://localhost:5000/templates to validate all templates

# Continuous Integration

## Manual

Run the tests:

```text
$ make test
```

Run static analysis:

```text
$ make check
```

## Automatic

Keep all of the above tasks running on change:

```text
$ make watch
```

# Deployment

## Heroku

This service is built to run on Heroku. Route traffic through a CDN to cache generated images.

## Containerization

You can also build this service as a container by running the following command:

```bash
# Using Podman:
podman build -t memegen -f Containerfile .

# Using Docker:
docker build -t memegen -f Containerfile .
```

You can then run the container by running:

```bash
# Run the container
podman run -p 5000:5000 -e DOMAIN="set.your.domain" memegen

# Validate functionality
$ curl http://127.0.0.1:5000/docs/ -sI
HTTP/1.1 200 OK
date: Sun, 24 Oct 2021 19:16:07 GMT
server: uvicorn
last-modified: Sun, 24 Oct 2021 18:27:30 GMT
content-type: text/html; charset=utf-8
access-control-allow-origin: *
```
