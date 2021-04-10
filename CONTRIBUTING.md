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

1. Visit http://localhost:5000/images/<my_new_template_id>
2. Add a `default.png` (or JPG) background image in `templates/<my_new_template_id>` directory
3. Update `config.yml` in the `templates/<my_new_template_id>` directory
4. Refresh http://localhost:5000/images/<my_new_template_id> to see the example meme
5. Visit http://localhost:5000/templates to validate all templates

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
