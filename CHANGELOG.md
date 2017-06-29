# Revision History

## 5.1

- Added `?watermark=<str>` option to include name of supported clients.

## 5.0

- Removed `/api/magic` route.

## 4.6

- Switch to underscores as the default space character.

## 4.5

- Added `?share=true` to force clients to receive HTML on image URLs.
- Added `?width=<int>` to scale images to a specific width.
- Added `?height=<int>` to scale images to a specific height.
- Added `?width=<int>&height=<int>` to pad an image to specified dimensions.

## 4.4

- Added `?preview=true` option to images to disable caching and analytics for clients that show partial image previews.

## 4.3

- Added `{"redirect": false}` option on POST to `/api/templates/<key>`.

## 4.2

- Added special character support on POST to `/api/templates/<key>`.

## 4.1

- Added `/api/search/<query>` to support more advanced clients.

## 4.0

- Moved all API routes to nest under `/api/*`
    + `/templates/*` is still supported for now via redirect
- Removed the shorthand `/m/*` redirect to `/magic/*`

## 3.0

- Removed `'date'` key from `/api`.

## 2.3

- Added support for custom fonts: `/custom/test.jpg?font=impact`

## 2.2

- Added support for custom backgrounds: `/custom/test.jpg?alt=http://image.jpg`

## 2.1

- Redirecting `/aliases/?name=<query>` to `/aliases/<query>`.

## 2.0

- Switched to a placeholder image for unknown templates.

## 1.0

- Added revision history (`/changes`).
