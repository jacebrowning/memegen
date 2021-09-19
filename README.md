An API to programmatically generate memes based solely on requested URLs.

<span class="badges"><!-- badges -->
[![Build Status](https://img.shields.io/circleci/build/github/jacebrowning/memegen)](https://circleci.com/gh/jacebrowning/memegen)
[![Coverage Status](http://img.shields.io/coveralls/jacebrowning/memegen/main.svg)](https://coveralls.io/r/jacebrowning/memegen)
[![Swagger Validator](https://img.shields.io/swagger/valid/3.0?label=docs&specUrl=https%3A%2F%2Fapi.memegen.link%2Fdocs%2Fswagger.json)](https://api.memegen.link/docs/)
[![License](https://img.shields.io/badge/license-mit-blue)](https://github.com/jacebrowning/memegen/blob/main/LICENSE.txt)
[![GitHub Sponsors](https://img.shields.io/badge/requests-15M/month-red)](https://github.com/sponsors/jacebrowning)
</span>

[Buy me a coffee to help keep this site running!](https://www.buymeacoffee.com/jacebrowning)

---

# Images

The API is stateless so URLs contain all the information necessary to generate meme images. For example, <https://api.memegen.link/images/buzz/memes/memes_everywhere.png> produces:

![Example Image](https://api.memegen.link/images/buzz/memes/memes_everywhere.png?token=6c7ek23718r0gwdt254l)

## Available Formats

Clients can request `.jpg` instead of `.png` for smaller files or `.gif` if an animated background is available:

| Format | Example                                                                                                  |
| :----- | :------------------------------------------------------------------------------------------------------- |
| PNG    | [/images/ds/small_file/high_quality.png](https://api.memegen.link/images/ds/small_file/high_quality.png) |
| JPEG   | [/images/ds/high_quality/small_file.jpg](https://api.memegen.link/images/ds/high_quality/small_file.jpg) |
| GIF    | [/images/oprah/you_get/animated_text.gif](https://api.memegen.link/oprah/you_get/animated_text.gif)      |

## Custom Dimensions

Images can be scaled to a specific width or height using the `width=<int>` and `height=<int>` query parameters. If both are provided (`width=<int>&height=<int>`), the image will be padded to the exact dimensions.

For example, <https://api.memegen.link/images/both/width_or_height/why_not_both~q.png?height=350&width=600> produces:

![Custom Size](https://api.memegen.link/images/both/width_or_height/why_not_both~q.png?height=350&width=600&token=e3ctlu471cv4k0hx698p)

## Special Characters

In URLs, spaces can be inserted using underscores or dashes:

- underscore (`_`) → space (` `)
- dash (`-`) → space (` `)
- 2 underscores (`__`) → underscore (`_`)
- 2 dashes (`--`) → dash (`-`)
- tilde + N (`~n`) → newline character

Reserved URL characters can be included using escape patterns:

- tilde + Q (`~q`) → question mark (`?`)
- tilde + A (`~a`) → ampersand (`&`)
- tilde + P (`~p`) → percentage (`%`)
- tilde + H (`~h`) → hashtag/pound (`#`)
- tilde + S (`~s`) → slash (`/`)
- tilde + B (`~b`) → backslash (`\`)
- tilde + L (`~l`) → less-than sign (`<`)
- tilde + G (`~g`) → greater-than sign (`>`)
- 2 single quotes (`''`) → double quote (`"`)

For example, <https://api.memegen.link/images/doge/~hspecial_characters~q/underscore__-dash--.png> produces:

![Escaped Characters](https://api.memegen.link/images/doge/~hspecial_characters~q/underscore___dash--.png?token=y4w9t5ii3m5euar7gjiz)

All of the `POST` endpoints will return image URLs with speical characters replaced with these alternatives.

# Templates

The list of predefined meme templates is available here: <https://api.memegen.link/templates/>

## Alternate Styles

Some memes come in multiple forms, which can be selected using the `style=<str>` query parameter.

For example, the <https://api.memegen.link/templates/ds/> template provides these styles:

|                     `/images/ds.png`                     |                      `/images/ds.png?style=maga`                      |
| :------------------------------------------------------: | :-------------------------------------------------------------------: |
| ![Default Style](https://api.memegen.link/images/ds.png) | ![Alternate Style](https://api.memegen.link/images/ds.png?style=maga) |

## Custom Overlays

The `style=<str>` query parameter can also be an image URL to overlay on the default background image.

For example, <https://api.memegen.link/images/pigeon/Engineer/_/Is_this_Photoshop~q.png?style=https://i.imgur.com/W0NXFpQ.png> produces:

![Custom Overlay](https://api.memegen.link/images/pigeon/Engineer/_/Is_this_Photoshop~q.png?style=https://i.imgur.com/W0NXFpQ.png&token=cy49tv234bu3jzgw587o)

## Custom Backgrounds

You can also use your own image URL as the background.

For example, <https://api.memegen.link/images/custom/_/my_background.png?background=http://www.gstatic.com/webp/gallery/1.png> produces:

![Custom Background](https://api.memegen.link/images/custom/_/my_background.png?background=http://www.gstatic.com/webp/gallery/1.png&token=ahby9x2nlsbk0gxdmpo5)
