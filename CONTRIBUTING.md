# Contributing Templates

## Add a New Template

In the [`data/templates`](data/templates) directory, use the example to create your own template directory. The name of the directory will be the primary alias for that meme.

## Create a Pull Request

Create a pull request to be merged after review.

# Contributing Code

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

After cloning the repository, create a virtualenv:

```sh
$ make install
```

## Development

### Run the application

Run the server locally:

```sh
$ make run
```

or also launch it in your browser:

```sh
$ make launch
```

### Run the tests

Manually run the tests and checkers:

```sh
$ make ci
```

or keep them running on change:

```sh
$ make watch
```

> In order to have OS X notifications, `brew install terminal-notifier`.

### Create a Pull Request

After checks pass, create a pull request to be merged after review.
