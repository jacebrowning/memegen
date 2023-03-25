# Setup

## Requirements

- Make:
  - macOS: `$ xcode-select --install`
  - Linux: [https://www.gnu.org](https://www.gnu.org/software/make)
  - Windows: `$ choco install make` [https://chocolatey.org](https://chocolatey.org/install)
- Python: `$ asdf install` (https://asdf-vm.com)[https://asdf-vm.com/guide/getting-started.html]
- Poetry: [https://python-poetry.org](https://python-poetry.org/docs/#installation)

To confirm these system dependencies are configured correctly:

```text
$ make bootstrap
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
$ make dev
```

# Deployment

## Heroku

This service is built to run on Heroku. Route traffic through a CDN to cache generated images.

## Containerization

You can also build this service as a container simply by running either of the following commands:

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

### Multi-Architecture Container Builds

If you want to build the image for multiple CPU architectures, you can either use `buildah` or `docker buildx`. Below are examples for both, and assume you're in the root of the memegen git repo.

#### System Requirements

On Debian/Ubuntu, you'll need to run:

```bash
sudo apt install -y podman buildah qemu-user-static
```

On any RHEL flavor OS, you'll need to run:

```bash
sudo yum install -y podman buildah qemu-user-static
```

On Arch or Manjaro Linux, you'll need to run:

```bash
sudo pacman -Sy podman buildah qemu-arch-extra
```

#### `docker buildx` Instructions

> This assumes you have [docker buildx](https://docs.docker.com/buildx/working-with-buildx/) already installed!

```bash
docker buildx build \
    --platform linux/amd64,linux/arm64 \
    --tag "ghcr.io/${GITHUB_USERNAME}/memegen:latest" \
    --push .
```

#### `buildah` Instructions

```bash
# Create a multi-architecture manifest
buildah manifest create memegen

# Build your amd64 architecture container
buildah bud \
    --tag "ghcr.io/${GITHUB_USERNAME}/memegen:latest" \
    --manifest memegen \
    --arch amd64 .

# Build your arm64 architecture container
buildah bud \
    --tag "ghcr.io/${GITHUB_USERNAME}/memegen:latest" \
    --manifest memegen \
    --arch arm64 .

# Enter your GitHub Personal Access Token below
read -s GITHUB_PERSONAL_ACCESS_TOKEN
# Log into your GitHub Container Registry
echo "${GITHUB_PERSONAL_ACCESS_TOKEN}" | buildah login --username danmanners --password-stdin ghcr.io

# Push the full manifest, with both CPU Architectures
buildah manifest push --all memegen \
  "docker://ghcr.io/${GITHUB_USERNAME}/memegen:latest"
```

> Please note that building the `--arch arm` build on an `amd64` (Intel/AMD) system can take nearly an hour.
