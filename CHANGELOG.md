# Revision History

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
