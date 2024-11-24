An API to programmatically generate memes based solely on requested URLs.

<span class="badges"><!-- badges -->
[![Build Status](https://img.shields.io/circleci/build/github/jacebrowning/memegen)](https://circleci.com/gh/jacebrowning/memegen)
[![Coverage Status](http://img.shields.io/coveralls/jacebrowning/memegen/main.svg)](https://coveralls.io/r/jacebrowning/memegen)
[![Swagger Validator](https://img.shields.io/swagger/valid/3.0?label=docs&specUrl=https%3A%2F%2Fapi.memegen.link%2Fdocs%2Fopenapi.json)](https://api.memegen.link/docs/)
[![License](https://img.shields.io/badge/license-mit-blue)](https://github.com/jacebrowning/memegen/blob/main/LICENSE.txt)
[![GitHub Sponsors](https://img.shields.io/endpoint?url=https://memecomplete.com/api/memes/badge.json)](https://github.com/sponsors/jacebrowning)
</span>

[Buy me a coffee to help keep this service running!](https://www.buymeacoffee.com/jacebrowning)

---

# Images

The API is stateless so URLs contain all the information necessary to generate meme images. For example, <https://api.memegen.link/images/buzz/memes/memes_everywhere.webp> produces:

![Example Image](https://api.memegen.link/images/buzz/memes/memes_everywhere.webp?token=wxgjeu3jll4dt9q6fihy&width=800)

## Available Formats

Clients can request `.jpg` instead of `.png` for smaller files. The `.gif` and `.webp` extensions can be used if an animated background is available or to animate text on static backgrounds:

| Format                     | Example                                                                                                     |
| :------------------------- | :---------------------------------------------------------------------------------------------------------- |
| PNG                        | [/images/ds/small_file/high_quality.png](https://api.memegen.link/images/ds/small_file/high_quality.png)    |
| JPEG                       | [/images/ds/high_quality/small_file.jpg](https://api.memegen.link/images/ds/high_quality/small_file.jpg)    |
| GIF (animated background)  | [/images/oprah/you_get/animated_text.gif](https://api.memegen.link/oprah/you_get/animated_text.gif)         |
| GIF (static background)    | [/images/iw/animates_text/in_production.gif](https://api.memegen.link/iw/animates_text/in_production.gif)   |
| WebP (animated background) | [/images/oprah/you_get/animated_text.webp](https://api.memegen.link/oprah/you_get/animated_text.webp)       |
| WebP (static background)   | [/images/iw/animates_text/in_production.webp](https://api.memegen.link/iw/animates_text/in_production.webp) |

## Custom Dimensions

Images can be scaled to a specific width or height using the `width=<int>` and `height=<int>` query parameters. If both are provided (`width=<int>&height=<int>`), the image will be padded to the exact dimensions.

For example, <https://api.memegen.link/images/both/width_or_height/why_not_both~q.png?height=450&width=800> produces:

![Custom Size](https://api.memegen.link/images/both/width_or_height/why_not_both~q.png?height=450&width=800&token=6alj86spiq9iyevbknm3)

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

Emojis are also supported, both as characters (👍) and aliases (`:thumbsup:`).

For example, <https://api.memegen.link/images/ugandanknuck/~hspecial_characters~q/underscore__-dash--_:thubsup:.png> produces:

![Escaped Characters](https://api.memegen.link/images/ugandanknuck/~hspecial_characters~q/underscore__-dash-- :thumbsup:.png?width=800&token=offeqniqbh09p5m2bedu)

All of the `POST` endpoints will return image URLs with special characters replaced with these alternatives.

# Templates

The list of predefined meme templates is available here: <https://api.memegen.link/templates/>

## Alternate Styles

Some memes come in multiple forms, which can be selected using the `style=<str>` query parameter.

For example, the <https://api.memegen.link/templates/ds/> template provides these styles:

|                          `/images/ds.png`                          |                           `/images/ds.png?style=maga`                           |
| :----------------------------------------------------------------: | :-----------------------------------------------------------------------------: |
| ![Default Style](https://api.memegen.link/images/ds.png?width=375) | ![Alternate Style](https://api.memegen.link/images/ds.png?width=375&style=maga) |

## Custom Overlays

The `style=<str>` query parameter can also be an image URL to overlay on the default background image.

For example, <https://api.memegen.link/images/pigeon/Engineer/_/Is_this_Photoshop~q.png?style=https://i.imgur.com/W0NXFpQ.png> produces:

![Custom Overlay](https://api.memegen.link/images/pigeon/Engineer/_/Is_this_Photoshop~q.png?style=https://i.imgur.com/W0NXFpQ.png&width=800&token=mbckgprafgz8o4l1adct)

The overlay image can be customized with the following additional query parameters:

| Name     | Type              | Description                                         |
| -------- | ----------------- | --------------------------------------------------- |
| `center` | `<float>,<float>` | Position of overlay relative to the top-left corner |
| `scale`  | `<float>`         | Ratio of the background image's dimensions          |

## Custom Backgrounds

You can also use your own image URL as the background.

For example, <https://api.memegen.link/images/custom/_/my_background.png?background=http://www.gstatic.com/webp/gallery/1.png> produces:

![Custom Background](https://api.memegen.link/images/custom/_/my_background.png?background=http://www.gstatic.com/webp/gallery/1.png&width=800&token=kxxlu7wzoxgp5l2iruta)

This can be combined with [custom overlays](#custom-overlays) to augment the background image.

# Layouts

Add the `layout=<str>` query parameter to switch between the default and `top` text positioning.

For example, <https://api.memegen.link/images/rollsafe/When_you_have_a_really_good_idea.webp?layout=top> produces:

![Top Layout](https://api.memegen.link/images/rollsafe/When_you_have_a_really_good_idea.webp?layout=top&width=800&token=orgyyu0tuzir7n4ktwvc)

# Fonts

The list of fonts is available here: <https://api.memegen.link/fonts/>

Add the `font=<str>` query parameter to customize the look of your meme:

| Name                                                                   | ID                  | Alias        |
| ---------------------------------------------------------------------- | ------------------- | ------------ |
| [Titillium Web Black](https://fonts.google.com/specimen/Titillium+Web) | `font=titilliumweb` | `font=thick` |
| [Kalam Regular](https://fonts.google.com/specimen/Kalam)               | `font=kalam`        | `font=comic` |
| [Impact](https://www.dafontfree.io/impact-font/)                       | `font=impact`       | -            |
| [Noto Sans Bold](https://fonts.google.com/noto/specimen/Noto+Sans)     | `font=notosans`     | -            |
| [HG Mincho B](https://japanesefonts.org/hg-mincho-b.html)              | `font=hgminchob`    | `font=jp`    |

<br>

Explore the full API here: <https://api.memegen.link/docs/>
