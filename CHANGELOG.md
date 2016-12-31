# Revision History

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
