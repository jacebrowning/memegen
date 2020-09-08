# api.memegen.link

An API to programatically generate memes based solely on requested URLs.

[![Build Status](https://img.shields.io/circleci/build/github/jacebrowning/memegen)](https://circleci.com/gh/jacebrowning/memegen)
[![Coverage Status](http://img.shields.io/coveralls/jacebrowning/memegen/main.svg)](https://coveralls.io/r/jacebrowning/memegen)
[![Swagger Validator](https://img.shields.io/swagger/valid/3.0?label=docs&specUrl=https%3A%2F%2Fapi.memegen.link%2Fdocs%2Fswagger.json)](https://api.memegen.link/docs/) <!--content-->
[![License](https://img.shields.io/badge/license-mit-blue)](https://github.com/jacebrowning/memegen/blob/main/LICENSE.md)
[![GitHub Sponsora](https://img.shields.io/badge/server%20costs-%2412%2Fmonth-red)](https://github.com/sponsors/jacebrowning)

# Generating Images

The API is stateless so URLs contain all the information necessary to generate meme images. For example, https://api.memegen.link/images/buzz/memes/memes_everywhere.png produces:

![Sample Image](https://api.memegen.link/images/buzz/memes/memes_everywhere.png?&height=400)

## Special Characters

In URLs, spaces can be inserted using underscores, dashes, or mixed case:

* underscore (`_`) → space (` `)
* dash (`-`) → space (` `)
* 2 underscores (`__`) → underscore (`_`)
* 2 dashes (`--`) → dash (`-`)

Reserved URL characters can be escaped:

* tilde + Q (`~q`) → question mark (`?`)
* tilde + P (`~p`) → percentage (`%`)
* tilde + H (`~h`) → hashtag/pound (`#`)
* tilde + S (`~s`) → slash (`/`)
* 2 single qutoes (`''`) → double quote (`"`)

For example, https://api.memegen.link//images/doge/~hspecial_characters~q/underscore__-dash--.png produces:

![Escaped Characters](https://api.memegen.link/images/doge/~hspecial_characters~q/underscore__-dash--.png?&height=400)

## Alternate Styles

Some memes come in multiple forms, which can be selected via `?style=<style>`.

For example, these are two styles provided by the https://api.memegen.link/templates/ds template:

`/images/ds.png`             |  `/images/ds.png?style=maga`
:-------------------------:|:-------------------------:
![](https://api.memegen.link/images/ds.png?width=200)  |  ![](https://api.memegen.link/images/ds.png?style=maga&width=200)

## Custom Backgrounds

You can also use your own image URL as the background. For example, https://api.memegen.link/images/custom/_/my_background.png?background=http://www.gstatic.com/webp/gallery/1.png produces:

![Custom Background](https://api.memegen.link/images/custom/_/my_background.png?background=http://www.gstatic.com/webp/gallery/1.png&height=400)

## Image Sizing

Images can be scaled to a specific width via `?width=<int>` or a specific height via `?height=<int>`. If both parameters are provided (`?width=<int>&height=<int>`), the image will be padded to the exact dimensions.

For example, https://api.memegen.link/images/both/width_or_height/why_not_both~q.png?height=350&width=600 produces:

![Custom Size](https://api.memegen.link/images/both/width_or_height/why_not_both~q.png?height=350&width=600)

Clients can also request `.jpg` instead of `.png` for smaller files.

# API Documentation

The full interactive documentation is available here: https://api.memegen.link/docs/

Here are some sample clients to explore:

| Platforms | Link | Source |
| :-: | :-- | :-- |
| Slack | --- | Python: [nicolewhite/slack-meme](https://github.com/nicolewhite/slack-meme) | --- |
| Slack | --- | Go: [CptSpaceToaster/slackbot](https://github.com/CptSpaceToaster/slackbot) | --- |
| Slack | http://www.memetizer.com | --- |
| Hain | --- | JavaScript: [Metrakit/hain-plugin-meme](https://github.com/Metrakit/hain-plugin-meme) |
| Web | ---| Clojure: [jasich/mighty-fine-memes](https://github.com/jasich/mighty-fine-memes) |
| Web, Slack | https://memecomplete.com | --- |

Additional clients can be found by searching for [code examples on GitHub](https://github.com/search?o=desc&q=%22memegen.link%22+&ref=searchresults&s=indexed&type=Code&utf8=%E2%9C%93).
