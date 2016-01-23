# To Contribute a Meme Template

## Setup

### Requirements

* Python 3.5+
    * Windows: https://www.python.org/downloads
    * Mac: `$ brew install python3`
    * Linux: `python3.5` and `python3.5-dev` packages
* Make:
    * Windows: http://cygwin.com/install.html
    * Mac: https://developer.apple.com/xcode
    * Linux: http://www.gnu.org/software/make (likely already installed)

### Installation

Create a virtual environment:

```
$ make env
```

## Adding Templates

In the [`data/templates`](data/templates) directory, use the example to create your own template directory. The name of the directory will be the primary alias for that meme.

### Serving

Run the server locally:

```
$ make run
```

or also launch it in your browser:

```
$ make launch
```

### Validation

Run the checks to ensure your new template does not conflict with others:

```
$ make validate
```

### Pull Request

After checks pass, create a pull request to be merged after review.

# To Contribute Code

## Setup

### Requirements

Everything from above with the addition of:

* Pandoc: http://johnmacfarlane.net/pandoc/installing.html
* Graphviz: http://www.graphviz.org/Download.php

### Installation

After cloning the repository, create a virtualenv:

```
$ make env
```

## Development

### Testing and Static Analysis

Manually run the tests and checkers:

```
$ make ci
```

or keep them running on change:

```
$ make watch
```

> In order to have OS X notifications, `brew install terminal-notifier`.

### Pull Request

After checks pass, create a pull request to be merged after review.
