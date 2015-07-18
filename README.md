# MemeGen

An API to generate meme images based solely on requested URLs.

[![Build Status](http://img.shields.io/travis/jacebrowning/memegen/master.svg)](https://travis-ci.org/jacebrowning/memegen)
[![Coverage Status](http://img.shields.io/coveralls/jacebrowning/memegen/master.svg)](https://coveralls.io/r/jacebrowning/memegen)
[![Scrutinizer Code Quality](http://img.shields.io/scrutinizer/g/jacebrowning/memegen.svg)](https://scrutinizer-ci.com/g/jacebrowning/memegen/?branch=master)

## Generating Images

Visit the live site at [http://memegen.link](http://memegen.link) to browse the API and view examples.

MemeGen URLs contain all the information necessary to generate the image. For example, http://memegen.link/buzz/memes/memes-everywhere.jpg produces:

![buzz](http://memegen.link/buzz/memes/memes-everywhere.jpg)

But, the site can also produce masked URLs to conceal the joke:

http://memegen.link/_YnV6egltZW1lcy9tZW1lcy1ldmVyeXdoZXJl.jpg

For any MemeGen image, lose the extension to see a list of all format options:

http://memegen.link/buzz/memes/memes-everywhere

### Special Characters

Spaces can be inserted using dashes or underscores:

* dash `-` → ` ` space
* underscore `_` → ` ` space
* dashes `--` → `-` dash
* underscores `__` → `_` underscore 

Reserved URL characters can be escaped:

* Tilde Q `~q` → `?` question mark
* Tilde E `~e` → `!` exclamation point

## Adding Templates 

To add a new template, please follow the [contributor instructions](CONTRIBUTING.md).

Thanks go to [danieldiekmeier/memegenerator](https://github.com/danieldiekmeier/memegenerator) for the inspiration!

## Slack Integration

Check out one of these options:

* [nicolewhite/slack-meme](https://github.com/nicolewhite/slack-meme)
* [CptSpaceToaster/slackbot](https://github.com/CptSpaceToaster/slackbot)
