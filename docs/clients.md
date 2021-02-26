# Authentication

Unauthenticated API requests are watermarked and may be rate limited. To request an API key please <a href="mailto:support@maketested.com?subject=memegen.link">contact us</a> to inquire about pricing for your specific use case. Authenticated requests can be made via HTTP header:

```shell
$ curl "https://api.memegen.link/images/fry/http_header/example.png" --header  "X-API-KEY: ???" --output http_header_example.png
```

or query parameter:

```shell
$ curl "https://api.memegen.link/images/fry/query_parameter/example.png?api_key=???" --output query_parameter_example.png
```

# Image Previews

If your client is going to show image previews, please use the `/images/preview.jpg` endpoint, which accepts URL-encoded parameters and returns smaller images to minimize bandwidth. For example:

```javascript
var id = encodeURIComponent($("#template").val())
var line_1 = encodeURIComponent($("#line_1").val()) || " "
var line_2 = encodeURIComponent($("#line_2").val()) || " "

var api = "https://api.memegen.link/images/preview.jpg"
var url = `${api}?template=${id}&lines[]=${line_1}&lines[]=${line_2}`

$("#preview").attr("src", url)
```

The `template` parameter can be a template ID or URL:

| Mode              | Example                                                                                                                                                                                                                                                          |
| :---------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Template ID       | [/images/preview.jpg<wbr>?lines[]=first+line&lines[]=second+line<wbr>&template=fry](https://api.memegen.link/images/preview.jpg?lines[]=first+line&lines[]=second+line&template=fry)                                                                             |
| Template URL      | [/images/preview.jpg<wbr>?lines[]=first+line&lines[]=second+line<wbr>&template=https://api.memegen.link/images/fry.png](https://api.memegen.link/images/preview.jpg?lines[]=first+line&lines[]=second+line&template=https://api.memegen.link/images/fry.png)     |
| Custom Background | [/images/preview.jpg<wbr>?lines[]=first+line&lines[]=second+line<wbr>&template=http://www.gstatic.com/webp/gallery/1.png](https://api.memegen.link/images/preview.jpg?lines[]=first+line&lines[]=second+line&template=http://www.gstatic.com/webp/gallery/1.png) |

# Sample Code

Here are some sample clients to explore:

| Platforms   | Language   | Website                                        |
| :---------- | :--------- | :--------------------------------------------- |
| Slack       | Python     | <https://github.com/nicolewhite/slack-meme>    |
| Slack       | Go         | <https://github.com/CptSpaceToaster/slackbot>  |
| Slack       |            | <http://www.memetizer.com>                     |
| Hain        | JavaScript | <https://github.com/Metrakit/hain-plugin-meme> |
| Web         | Clojure    | <https://github.com/jasich/mighty-fine-memes>  |
| Web & Slack |            | <https://memecomplete.com>                     |
| Discord     | JavaScript | <https://github.com/parshsee/discordbot>       |

Additional clients can be found by searching for [code examples on GitHub](https://github.com/search?o=desc&q=%22api.memegen.link%22+&ref=searchresults&s=indexed&type=Code&utf8=%E2%9C%93).

# Zapier Integration

The beta integration is available here: <https://zapier.com/apps/memegenlink>
