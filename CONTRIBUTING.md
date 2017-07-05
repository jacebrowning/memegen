# To Contribute a Meme Template

## Setup

### Requirements

* Python 3.6+
    * Windows: https://www.python.org/downloads
    * macOS: `$ brew install python3`
    * Linux: `python3.6` and `python3.6-dev` packages
* pipenv: http://docs.pipenv.org
* Make:
    * Windows: http://mingw.org/download/installer
    * Mac: http://developer.apple.com/xcode
    * Linux: http://www.gnu.org/software/make
* OpenJPEG:
    * Windows: ?
    * macOS: `$ brew install openjpeg`
    * Linux: ?
* libfreetype:
    * Windows: ?
    * macOS: `$ brew install freetype`
    * Linux: ?

### Installation

Install project dependencies into a virtual environment:

```sh
$ make install
```

## Adding Templates

In the [`data/templates`](data/templates) directory, use the example to create your own template directory. The name of the directory will be the primary alias for that meme.

### Serving

Run the server locally:

```sh
$ make run
```

or also launch it in your browser:

```sh
$ make launch
```

### Validation

Run the checks to ensure your new template does not conflict with others:

```sh
$ make validate
```

### Pull Request

After checks pass, create a pull request to be merged after review.

# To Contribute Code

## Setup

### Requirements

### Installation

After cloning the repository, create a virtualenv:

```sh
$ make install
```

## Development

### Testing and Static Analysis

Manually run the tests and checkers:

```sh
$ make ci
```

or keep them running on change:

```sh
$ make watch
```

> In order to have OS X notifications, `brew install terminal-notifier`.

### Pull Request

After checks pass, create a pull request to be merged after review.
