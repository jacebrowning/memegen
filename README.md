An API to programmatically generate memes based solely on requested URLs.

[![Build Status](https://img.shields.io/circleci/build/github/jacebrowning/memegen)](https://circleci.com/gh/jacebrowning/memegen)
[![Coverage Status](http://img.shields.io/coveralls/jacebrowning/memegen/main.svg)](https://coveralls.io/r/jacebrowning/memegen)
[![Swagger Validator](https://img.shields.io/swagger/valid/3.0?label=docs&specUrl=https%3A%2F%2Fapi.memegen.link%2Fdocs%2Fswagger.json)](https://api.memegen.link/docs/)
[![License](https://img.shields.io/badge/license-mit-blue)](https://github.com/jacebrowning/memegen/blob/main/LICENSE.txt)
[![GitHub Sponsors](https://img.shields.io/badge/requests-20M/month-red)](https://github.com/sponsors/jacebrowning)

[Buy me a coffee to help keep this site running!](https://www.buymeacoffee.com/jacebrowning)

---

# Images

The API is stateless so URLs contain all the information necessary to generate meme images. For example, <https://api.memegen.link/images/buzz/memes/memes_everywhere.png> produces:

![Example Image](https://api.memegen.link/images/buzz/memes/memes_everywhere.png?token=6c7ek23718r0gwdt254l)

## Available Formats

Clients can request `.jpg` instead of `.png` for smaller files:

| Format | Example                                                                                                  |
| :----- | :------------------------------------------------------------------------------------------------------- |
| PNG    | [/images/ds/small_file/high_quality.png](https://api.memegen.link/images/ds/small_file/high_quality.png) |
| JPEG   | [/images/ds/high_quality/small_file.jpg](https://api.memegen.link/images/ds/high_quality/small_file.jpg) |

## Custom Dimensions

Images can be scaled to a specific width via `?width=<int>` or a specific height via `?height=<int>`. If both parameters are provided (`?width=<int>&height=<int>`), the image will be padded to the exact dimensions.

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
- 2 single quotes (`''`) → double quote (`"`)

For example, <https://api.memegen.link/images/doge/~hspecial_characters~q/underscore__-dash--.png> produces:

![Escaped Characters](https://api.memegen.link/images/doge/~hspecial_characters~q/underscore___dash--.png?token=y4w9t5ii3m5euar7gjiz)

All of the `POST` endpoints will return image URLs with speical characters replaced with these alternatives.

# Templates

The list of predefined meme templates is available here: <https://api.memegen.link/templates/>

## Alternate Styles

Some memes come in multiple forms, which can be selected via `?style=<style>`.

For example, the <https://api.memegen.link/templates/ds/> template provides these styles:

|                     `/images/ds.png`                     |                      `/images/ds.png?style=maga`                      |
| :------------------------------------------------------: | :-------------------------------------------------------------------: |
| ![Default Style](https://api.memegen.link/images/ds.png) | ![Alternate Style](https://api.memegen.link/images/ds.png?style=maga) |

## Custom Backgrounds

You can also use your own image URL as the background. For example, <https://api.memegen.link/images/custom/_/my_background.png?background=http://www.gstatic.com/webp/gallery/1.png> produces:

![Custom Background](https://api.memegen.link/images/custom/_/my_background.png?background=http://www.gstatic.com/webp/gallery/1.png&token=ahby9x2nlsbk0gxdmpo5)

# Sample Code

Here are some popular apps and integrations to check out:

| Platforms   | Language   | Website                                        |
| :---------- | :--------- | :--------------------------------------------- |
| Slack       | Python     | <https://github.com/nicolewhite/slack-meme>    |
| Slack       | Go         | <https://github.com/CptSpaceToaster/slackbot>  |
| Slack       | --         | <http://www.memetizer.com>                     |
| Hain        | JavaScript | <https://github.com/Metrakit/hain-plugin-meme> |
| Web         | Clojure    | <https://github.com/jasich/mighty-fine-memes>  |
| Web & Slack | --         | <https://memecomplete.com>                     |
| Discord     | JavaScript | <https://github.com/parshsee/discordbot>       |

Additional clients can be found by searching for [code examples](https://github.com/search?o=desc&q=%22api.memegen.link%22+&ref=searchresults&s=indexed&type=Code&utf8=%E2%9C%93) on GitHub.

Ready to build your own? Check out the [client page](clients).
