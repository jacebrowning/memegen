# memegen.link

An API to programatically generate memes based solely on requested URLs.

[![Unix Build Status](http://img.shields.io/travis/jacebrowning/memegen/master.svg?label=unix)](https://travis-ci.org/jacebrowning/memegen)
[![Windows Build Status](https://img.shields.io/appveyor/ci/jacebrowning/memegen/master.svg?label=windows)](https://ci.appveyor.com/project/jacebrowning/memegen)
[![Coverage Status](http://img.shields.io/coveralls/jacebrowning/memegen/master.svg)](https://coveralls.io/r/jacebrowning/memegen)
[![Scrutinizer Code Quality](http://img.shields.io/scrutinizer/g/jacebrowning/memegen.svg)](https://scrutinizer-ci.com/g/jacebrowning/memegen/?branch=master)
[![GitHub Sponsor](https://img.shields.io/badge/server%20costs-%2430%2Fmonth-red)](https://github.com/sponsors/jacebrowning)

<!--content-->

## Generating Images

The API is stateless so URLs contain all the information necessary to generate meme images. For example, https://memegen.link/buzz/memes/memes_everywhere.jpg produces:

![Sample Image](https://memegen.link/buzz/memes/memes_everywhere.jpg?watermark=none)

But, the site can also produce masked URLs to conceal the joke:

https://memegen.link/_YnV6egltZW1lcy9tZW1lcy1ldmVyeXdoZXJl.jpg

For any image, lose the extension to see a list of all format options:

https://memegen.link/buzz/memes/memes_everywhere

### Special Characters

In URLs, spaces can be inserted using underscores, dashes, or mixed case:

* underscore (`_`) → space (` `)
* dash (`-`) → space (` `)
* 2 underscores (`__`) → underscore (`_`)
* 2 dashes (`--`) → dash (`-`)
* "weLoveMemes" → "we love memes"

Reserved URL characters can be escaped:

* tilde + Q (`~q`) → question mark (`?`)
* tilde + P (`~p`) → percentage (`%`)
* tilde + H (`~h`) → hashtag/pound (`#`)
* tilde + S (`~s`) → slash (`/`)
* 2 single qutoes (`''`) → double quote (`"`)

For example, https://memegen.link/doge/~hspecial_characters~q/underscore__-dash--.jpg produces:

![Escaped Characters](https://memegen.link/doge/~hspecial_characters~q/underscore__-dash--.jpg?watermark=none)

### Alternate Styles

Some memes come in multiple forms, which can be selected via `?alt=<style>`:

<img src="https://memegen.link/static/images/template.png" alt="Template with Styles" style="width: 600px;"/>

For example: [https://memegen.link/sad-biden/sad_joe_biden/doesn't_think_you'll_vote.jpg?alt=scowl](https://memegen.link/sad-biden/sad_joe_biden/doesn't_think_you'll_vote.jpg?alt=scowl)

Or, you can use your own image URL as the style. For example, https://memegen.link/custom/my_pretty/background.jpg?alt=http://www.gstatic.com/webp/gallery/1.jpg produces:

![Custom Background](https://memegen.link/custom/my_pretty/background.jpg?alt=http://www.gstatic.com/webp/gallery/1.jpg&watermark=none)

### Alternate Fonts

Additional fonts are available (see: https://memegen.link/api/fonts) and can be selected via `?font=<name>`.

For example, https://memegen.link/joker/pick_a_different_font/people_lose_their_minds.jpg?font=typoline-demo produces:

![Custom Font](https://memegen.link/joker/pick-a-different-font/people-lose-their-minds.jpg?font=typoline-demo&watermark=none)

### Custom sizes

Images can be scaled to a specific width via `?width=<int>` or a specific height via `?height=<int>`. If both parameters are provided (`?width=<int>&height=<int>`), the image will be padded to the exact dimensions.

For example, https://memegen.link/both/width_or_height/why_not_both~q.jpg?height=350&width=600 produces:

![Custom Size](https://memegen.link/both/width_or_height/why_not_both~q.jpg?height=350&width=600&watermark=none)

### Preview Images

API clients that want to show a preview of an image while the user is still typing should disable caching and analytics via `?preview=true`.

### Social Media

Add `?share=true` to get HTML with images optimized for sharing on social media.

## Adding Templates

To add a new template, please follow the [contributor instructions](CONTRIBUTING.md).

Thanks go to [danieldiekmeier/memegenerator](https://github.com/danieldiekmeier/memegenerator) for the inspiration!

## Sample Clients

| Platforms | Link | Source | 
| :-: | :-- | :-- |
| Slack | --- | Python: [nicolewhite/slack-meme](https://github.com/nicolewhite/slack-meme) | --- |
| Slack | --- | Go: [CptSpaceToaster/slackbot](https://github.com/CptSpaceToaster/slackbot) | --- |
| Slack | http://www.memetizer.com | --- |
| Hain | --- | JavaScript: [Metrakit/hain-plugin-meme](https://github.com/Metrakit/hain-plugin-meme) |
| Web | ---| Clojure: [jasich/mighty-fine-memes](https://github.com/jasich/mighty-fine-memes) |
| Web, Slack | https://memecomplete.com | --- |

Additional clients can be found by searching for [code examples on GitHub](https://github.com/search?o=desc&q=%22memegen.link%22+&ref=searchresults&s=indexed&type=Code&utf8=%E2%9C%93).
