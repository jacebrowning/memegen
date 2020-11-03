An API to programmatically generate memes based solely on requested URLs.

[![Build Status](https://img.shields.io/circleci/build/github/jacebrowning/memegen)](https://circleci.com/gh/jacebrowning/memegen)
[![Coverage Status](http://img.shields.io/coveralls/jacebrowning/memegen/main.svg)](https://coveralls.io/r/jacebrowning/memegen)
[![Swagger Validator](https://img.shields.io/swagger/valid/3.0?label=docs&specUrl=https%3A%2F%2Fapi.memegen.link%2Fdocs%2Fswagger.json)](https://api.memegen.link/docs/) <!--content-->
[![License](https://img.shields.io/badge/license-mit-blue)](https://github.com/jacebrowning/memegen/blob/main/LICENSE.txt)
[![GitHub Sponsors](https://img.shields.io/badge/server%20costs-%2412%2Fmonth-red)](https://github.com/sponsors/jacebrowning)

# Images

The API is stateless so URLs contain all the information necessary to generate meme images. For example, <https://api.memegen.link/images/buzz/memes/memes_everywhere.png> produces:

![Sample Image](https://api.memegen.link/images/buzz/memes/memes_everywhere.png?&width=600)

## Available Formats

Clients can request `.jpg` instead of `.png` for smaller files:

| Format | Example                                                          |
| :----- | :--------------------------------------------------------------- |
| PNG    | <https://api.memegen.link/images/ds/small_file/high_quality.png> |
| JPEG   | <https://api.memegen.link/images/ds/high_quality/small_file.jpg> |

## Custom Dimensions

Images can be scaled to a specific width via `?width=<int>` or a specific height via `?height=<int>`. If both parameters are provided (`?width=<int>&height=<int>`), the image will be padded to the exact dimensions.

For example, <https://api.memegen.link/images/both/width_or_height/why_not_both~q.png?height=350&width=600> produces:

![Custom Size](https://api.memegen.link/images/both/width_or_height/why_not_both~q.png?height=350&width=600)

## Special Characters

In URLs, spaces can be inserted using underscores or dashes:

- underscore (`_`) → space (` `)
- dash (`-`) → space (` `)
- 2 underscores (`__`) → underscore (`_`)
- 2 dashes (`--`) → dash (`-`)

Reserved URL characters can be include using escape patterns:

- tilde + Q (`~q`) → question mark (`?`)
- tilde + P (`~p`) → percentage (`%`)
- tilde + H (`~h`) → hashtag/pound (`#`)
- tilde + S (`~s`) → slash (`/`)
- tilde + B (`~b`) → backslash (`\`)
- 2 single quotes (`''`) → double quote (`"`)

For example, <https://api.memegen.link/images/doge/~hspecial_characters~q/underscore__-dash--.png> produces:

![Escaped Characters](https://api.memegen.link/images/doge/~hspecial_characters~q/underscore__-dash--.png?&width=600)

# Templates

The list of predefined meme templates is available here: <https://api.memegen.link/templates>

## Alternate Styles

Some memes come in multiple forms, which can be selected via `?style=<style>`.

For example, the <https://api.memegen.link/templates/ds> template provides these styles:

|                   `/images/ds.png`                    |                   `/images/ds.png?style=maga`                    |
| :---------------------------------------------------: | :--------------------------------------------------------------: |
| ![](https://api.memegen.link/images/ds.png?width=280) | ![](https://api.memegen.link/images/ds.png?style=maga&width=280) |

## Custom Backgrounds

You can also use your own image URL as the background. For example, <https://api.memegen.link/images/custom/_/my_background.png?background=http://www.gstatic.com/webp/gallery/1.png> produces:

![Custom Background](https://api.memegen.link/images/custom/_/my_background.png?background=http://www.gstatic.com/webp/gallery/1.png&width=600)

# Previews

If your client is going to show live previews of a custom meme, please use the `/images/preview.jpg` endpoint, which accepts URL-encoded parameters and returns smaller images to minimize bandwidth. For example:

```javascript
var key = encodeURIComponent($("#template").val())
var line_1 = encodeURIComponent($("#line_1").val()) || " "
var line_2 = encodeURIComponent($("#line_2").val()) || " "

var api = "https://api.memegen.link/images/preview.jpg"
var url = `${api}?template=${key}&lines[]=${line_1}&lines[]=${line_2}`

$("#preview").attr("src", url)
```

The `template` parameter can be a template key or URL:

| Mode              | Example                                                                                                                                 |
| :---------------- | :-------------------------------------------------------------------------------------------------------------------------------------- |
| Template Key      | <https://api.memegen.link/images/preview.jpg?lines[]=first+line&lines[]=second+line&template=fry>                                       |
| Template URL      | <https://api.memegen.link/images/preview.jpg?lines[]=first+line&lines[]=second+line&template=https://api.memegen.link/images/fry.png>   |
| Custom Background | <https://api.memegen.link/images/preview.jpg?lines[]=first+line&lines[]=second+line&template=http://www.gstatic.com/webp/gallery/1.png> |

# Documentation

The full interactive documentation is available here: <https://api.memegen.link/docs/>

Here are some sample clients to explore:

| Platforms   | Link                       | Source                                                                                |
| :---------- | :------------------------- | :------------------------------------------------------------------------------------ |
| Slack       | ---                        | Python: [nicolewhite/slack-meme](https://github.com/nicolewhite/slack-meme)           |
| Slack       | ---                        | Go: [CptSpaceToaster/slackbot](https://github.com/CptSpaceToaster/slackbot)           |
| Slack       | <http://www.memetizer.com> | ---                                                                                   |
| Hain        | ---                        | JavaScript: [Metrakit/hain-plugin-meme](https://github.com/Metrakit/hain-plugin-meme) |
| Web         | ---                        | Clojure: [jasich/mighty-fine-memes](https://github.com/jasich/mighty-fine-memes)      |
| Web & Slack | <https://memecomplete.com> | ---                                                                                   |
| Discord     | ---                        | JavaScript: [parshsee/discordbot](https://github.com/parshsee/discordbot)             |

Additional clients can be found by searching for [code examples on GitHub](https://github.com/search?o=desc&q=%22memegen.link%22+&ref=searchresults&s=indexed&type=Code&utf8=%E2%9C%93).
