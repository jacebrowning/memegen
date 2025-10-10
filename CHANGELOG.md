# Revision History

## 11.1

- Added emoji support.

## 11.0

- Removed support for legacy `alt` query parameter for custom backgrounds.

## 10.14

- Added template `keywords` to improve search results.

## 10.13

- Added support for `.webp` animated images.

## 10.12

- Added support for `color=<str>,<str>` query parameter to control the color of text.

## 10.11

- Updated `/images/custom` and `/templates/custom` to accept template IDs as `background`.

## 10.10

- Added support for `layout=<str>` to request text be positioned at the top of the image.

## 10.9

- Added support for `scale=<float>` query parameter to control the size of the overlay image.
- Added support for `center=<float>,<float>` query parameter to control the position of the overlay image.

## 10.8

- Added support for adding overlays on top of GIF backgrounds.
- Updated APIs to default to `.gif` if available and `extension` not specified.

## 10.7

- Added support for `start=<int,int>`/`stop=<int,int>` query parameters to control text animation.
- Added text animation to static backgrounds when `gif` is requested.

## 10.6

- Added `text[]` as as alias for `line[]` (preview) and `text_lines[]` (create).

## 10.5

- Added `font` parameter to override a template's font.
- Added a `/fonts` API to list the available fonts.

## 10.4

- Added `frames` parameter to manually reduce GIF sizes.

## 10.3

- Added support to `start`/`stop` text in GIFs.

## 10.2

- Added support for rotated overlay images.

## 10.1

- Added support for multiple overlays via comma-separated URLs in the `style` parameter.
- Added `overlays` count in `/templates` responses.

## 10.0

- Replaced `example` field in `/templates` responses with `{ "text": [str] , "url": str }`.

## 9.3

- Added `confidence` ratio to results from `/images/automatic`.

## 9.2

- Added redirect to `.gif` format when `style=animated` parameter is present.
- Added `animated` parameter to `/templates` to find templates supporting animation.

## 9.1

- Added escape characters for `<` and `>` as `~l` and `~g`, respectively.

## 9.0

- Renamed `image_url` body parameter to `background` to match the URL value.

## 8.5

- Added support for custom overlays when the `style` parameter is included in image URLs.

## 8.4

- Updated `/images/custom` to return previous results with `GET` requests.

## 8.3

- Added `filter` parameter to `/images` and `/templates` to query for matching names and examples.

## 8.2

- Added `/images/custom` as an alias for `/templates/custom`.
- Removed `POST /templates/*` from the documentation to clarify routes.

## 8.1

- Updated APIs that accept `text_lines[]` to support `/` as a placeholder for blank lines.

## 8.0

- Renamed `template_key` to `template_id` in APIs.

## 7.1

- Added support for the `X-API-KEY` header to disable watermarks.

## 7.0

- Renamed `sample` to `example` in template API responses.

## 6.3

- Added `lines` to `/templates/<key>` responses to indicate the maximum number of supported lines of text.

## 6.2

- Added `/images/preview.jpg` route for quicker responses when clients want to show live previews of a custom meme.

## 6.1

- Added `extension` parameter to specify image format when using POST endpoints.

## 6.0

- Initial release of the API rewrite using Sanic.

## 5.x

- Prior history: https://github.com/jacebrowning/memegen-flask/blob/main/CHANGELOG.md
