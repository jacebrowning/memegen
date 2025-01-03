# Sample Code

Here are some popular apps and integrations to check out:

| Platforms   | Language   | Website                                        |
| :---------- | :--------- | :--------------------------------------------- |
| Slack       | Python     | <https://github.com/nicolewhite/slack-meme>    |
| Slack       | Go         | <https://github.com/CptSpaceToaster/slackbot>  |
| Hain        | JavaScript | <https://github.com/Metrakit/hain-plugin-meme> |
| Web         | Clojure    | <https://github.com/jasich/mighty-fine-memes>  |
| Web & Slack | --         | <https://memecomplete.com>                     |
| Discord     | JavaScript | <https://github.com/parshsee/discordbot>       |
| Legobot     | Python     | <https://github.com/drewpearce/legos.memes>    |

Additional clients can be found by searching for [code examples](https://github.com/search?o=desc&q=%22api.memegen.link%22+&ref=searchresults&s=indexed&type=Code&utf8=%E2%9C%93) on GitHub. Or create your own!

# Authentication

Unauthenticated API requests are watermarked and may be rate-limited or used as training data.
Individuals sponsoring this project at [$10/month](https://github.com/sponsors/jacebrowning/sponsorships?sponsor=jacebrowning&tier_id=55476&preview=false) or higher are welcome to an API key.
Please <a href="mailto:support@maketested.com?subject=memegen.link">contact support</a> to request one or inquire about pricing for your specific use case.

## HTTP Header

Authenticated requests can be made using a header:

```shell
$ curl "https://api.memegen.link/images/fry/http_header/example.png" \
  --header "X-API-KEY: myapikey42" --output http_header_example.png --location
```

## Query Parameter

If that's not an option, the API key can also be added as a query parameter:

```shell
$ curl "https://api.memegen.link/images/fry/query_parameter/example.png?api_key=myapikey42" \
  --output query_parameter_example.png --location
```

# Image Previews

If your client is going to show typeahead image previews, please use the `/images/preview.jpg` endpoint, which accepts URL-encoded parameters and returns smaller images to minimize bandwidth:

```javascript
var typingTimer

$("#form").keyup(function () {
  clearTimeout(typingTimer)
  typingTimer = setTimeout(updatePreview, 500)
})

function updatePreview() {
  var template = encodeURIComponent($("#template").val())
  var line_1 = encodeURIComponent($("#line_1").val() || " ")
  var line_2 = encodeURIComponent($("#line_2").val() || " ")

  var api = "https://api.memegen.link/images/preview.jpg"
  var url = `${api}?template=${template}&text[]=${line_1}&text[]=${line_2}`

  $("#preview").attr("src", url)
}

$(document).ready(updatePreview)
```

For example, <https://api.memegen.link/images/preview.jpg?template=iw&lines[]=live+preview&lines[]=while+typing> produces:

![Live Preview](https://api.memegen.link/images/preview.jpg?template=iw&lines[]=live+preview&lines[]=while+typing)

The `template=<str>` query parameter can be a template ID or URL:

| Mode              | Example                                                                                                                                                                                                                                                          |
| :---------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Template ID       | [/images/preview.jpg<wbr>?lines[]=first+line&lines[]=second+line<wbr>&template=fry](https://api.memegen.link/images/preview.jpg?lines[]=first+line&lines[]=second+line&template=fry)                                                                             |
| Template URL      | [/images/preview.jpg<wbr>?lines[]=first+line&lines[]=second+line<wbr>&template=https://api.memegen.link/images/fry.png](https://api.memegen.link/images/preview.jpg?lines[]=first+line&lines[]=second+line&template=https://api.memegen.link/images/fry.png)     |
| Custom Background | [/images/preview.jpg<wbr>?lines[]=first+line&lines[]=second+line<wbr>&template=http://www.gstatic.com/webp/gallery/1.png](https://api.memegen.link/images/preview.jpg?lines[]=first+line&lines[]=second+line&template=http://www.gstatic.com/webp/gallery/1.png) |

# Custom Watermark

Authenticated requests can also add their own watermark to images using the `watermark=<str>` query parameter.

For example, <https://api.memegen.link/images/puffin/custom_watermark/example.png?api_key=myapikey42&watermark=example.com> produces:

![](https://api.memegen.link/images/puffin/custom_watermark/example.png?api_key=myapikey42&watermark=example.com&width=800)

# Zapier Integration

Incorporate memes into your workflow automation: <https://zapier.com/apps/memegenlink>

<script type="module" src="https://cdn.zapier.com/packages/partner-sdk/v0/zapier-elements/zapier-elements.esm.js"></script>
<link rel="stylesheet" href="https://cdn.zapier.com/packages/partner-sdk/v0/zapier-elements/zapier-elements.css"/>
<div>
  <zapier-full-experience
    client-id="7T8bocHkmLpUuhGOLGQj9pSIxInNKEYWjkU9nypk"
    theme="light"
    intro-copy-display="hide"
    app-search-bar-display="show"
    app-exclusions="space-by-zapier,google-sheets"
    zap-call-to-action-display="hide"
    zap-create-from-scratch-display="show">
  </zapier-full-experience>
</div>
