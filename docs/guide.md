# Constructing meme URLs

A reference for humans and automated clients on how to build valid memegen URLs from template metadata. The goal is a single page you can read top-to-bottom and emit a correct URL on the first try, without consulting the README, the OpenAPI spec, and a per-template metadata response separately.

The OpenAPI specification at [`/docs/openapi.json`](https://api.memegen.link/docs/openapi.json) is the source of truth for endpoint shapes and parameter names. This guide is derived from those descriptions and adds worked examples, edge-case behavior, and a recipe for automated clients that doesn't fit cleanly inside the spec itself.

## The shape of a meme URL

A rendered meme URL has the form:

```
https://api.memegen.link/images/{template_id}/{line_1}/{line_2}/.../{line_n}.{ext}
```

where `{template_id}` is the `id` field from `/templates/`, each `{line_i}` is one segment of text escaped per the rules below, `n` is at most the template's `lines` value, and `{ext}` is one of `png`, `jpg`, `gif`, or `webp`. A blank template (no text) is available at `/images/{template_id}.{ext}` — this is the value of the `blank` field on the template's metadata response.

## Source of truth: the templates endpoint

`GET /templates/` returns the full list of renderable templates. Each entry has the form:

```json
{
  "id": "ds",
  "name": "Daily Struggle",
  "lines": 3,
  "overlays": 1,
  "styles": ["default", "maga"],
  "blank": "https://api.memegen.link/images/ds.jpg",
  "example": {
    "text": ["The dress is black and blue.", "The dress is gold and white."],
    "url": "https://api.memegen.link/images/ds/The_dress_is_black_and_blue./The_dress_is_gold_and_white..jpg"
  },
  "source": "https://knowyourmeme.com/memes/daily-struggle",
  "keywords": []
}
```

For URL construction, four fields are load-bearing:

| Field | Role in the URL |
|-------|-----------------|
| `id` | Goes into the path immediately after `/images/` |
| `lines` | Maximum number of `/`-separated text segments accepted in the path |
| `overlays` | Number of overlay image slots the template defines |
| `styles` | Allowed values for the `style=` query parameter |

The remaining fields (`name`, `blank`, `example`, `source`, `keywords`) are descriptive — useful for discovery, search, and validation, but not for URL construction.

For automated clients, the recommended bootstrap is to fetch `/templates/` once at startup, cache it, and construct URLs locally. Refresh on a long interval; the template list is stable.

## Path segments and the `lines` field

The number of `/`-separated text segments after `{template_id}` may range from zero (the blank template) up to the template's `lines` value. Trailing lines may be omitted; to skip an earlier line while populating a later one, pass an underscore (`_`) as the segment to render an empty line in that position.

For example, on the Ancient Aliens Guy template (`aag`, `lines: 2`):

```
/images/aag/aliens.png            -> top line "aliens", bottom line empty
/images/aag/_/aliens.png          -> top line empty, bottom line "aliens"
/images/aag/why/aliens.png        -> both lines populated
```

If you pass more segments than `lines`, the surplus is currently ignored. Agents should treat over-passing as an error and trim to `template.lines` before constructing the URL rather than relying on silent truncation as a contract.

## Escaping text segments

Text segments live inside a URL path, so a small escape table substitutes ASCII-safe sequences for characters that would otherwise need percent-encoding or break path parsing:

| Character | Escape |
|-----------|--------|
| Space | `_` |
| Underscore | `__` |
| Newline | `~n` |
| `?` | `~q` |
| `&` | `~a` |
| `%` | `~p` |
| `#` | `~h` |
| `/` | `~s` |
| `\` | `~b` |
| `<` | `~l` |
| `>` | `~g` |
| `"` | `''` |

Emoji are supported via shortcode aliases — for example, `:thumbsup:` renders 👍.

If you'd rather not implement the escape table client-side, `POST` to `/images/` with a JSON body containing `template_id` and a `text` array of raw strings. The response includes a `url` field with the canonical, escaped URL. Automated clients can `POST` raw text and use the returned URL verbatim instead of maintaining the escape table themselves.

## Styles and the `styles` field

Many templates support visual variants, exposed via the `styles` field on `/templates/{id}`. Selection is via the `style=` query parameter:

```
/images/ds/The_dress_is_black_and_blue./The_dress_is_gold_and_white..jpg?style=maga
```

The default style is implicit when `style=` is omitted.

The `style=` parameter has a second mode: passing an HTTPS URL instead of a name treats the URL as a custom overlay image and composites it onto the template. This dual purpose — named style or arbitrary overlay URL — is easy to miss when reading the spec. For templates with `overlays > 1`, supply multiple `style=` values to set each overlay slot independently.

## Overlays

A template's `overlays` field counts the compositing slots the template defines — for example, the Drake template defines two regions where reaction images go. When `overlays > 0`, each slot can be filled either with the template's default content (no `style=` needed) or with a custom image URL via `style=<url>`.

Two query parameters fine-tune overlay placement, most useful when supplying custom images:

- `center=<x>,<y>` — fractional coordinates (0.0–1.0) for the overlay center within its slot
- `scale=<float>` — multiplier applied to the overlay's default size

## Rendering options

The following query parameters apply to all path-based image endpoints. Combining them is allowed; later parameters compose with the path-derived defaults.

### Format

The file extension on the path determines the response format. `png` and `jpg` are static. `gif` and `webp` produce animated output when the template's background is animated, and a static-background-with-animated-text variant otherwise.

### Dimensions

`width=<int>` and `height=<int>` set the output dimensions in pixels. If both are supplied, the image is padded to fit while preserving aspect ratio. Values between 1 and 9 are rejected as too small (the size is silently set back to 0,0 and the response status is 422).

### Layout

`layout=top` places all text at the top of the image rather than spreading it across the template's default text regions. The `default` layout is implicit when `layout=` is omitted.

### Font

`font=<name>` overrides the template's default font. The full list of available fonts is at `GET /fonts/`. Named aliases include `thick`, `comic`, `he` (Hebrew), and `jp` (Japanese).

### Color

`color=<text>,<outline>` is a comma-separated pair, each value either an HTML color name or a hex code. Hex codes may be supplied with or without a leading `#`. Example: `color=white,black`.

### Custom background

`background=<url>` uses an arbitrary image as the template background. It composes with `style=<url>` overlays as expected.

### Animation frames

`frames=<int>` caps the number of frames rendered in animated output (`gif`/`webp`). The default of `0` means no cap. Use this to bound response size and render time on long animations.

### Status override

`status=<int>` overrides the HTTP response status code on the rendered image. This is primarily used internally by the `POST /images/` → redirect flow to propagate a `201 Created` semantic to the final image fetch. Most clients should not need to set this directly.

## Worked examples

A few complete URLs covering common cases:

```
# Two-line meme on a standard template
https://api.memegen.link/images/aag/Why_can''t/I_post_memes.png

# Non-default style
https://api.memegen.link/images/ds/Wikipedia_says_no/My_LLM_says_yes.jpg?style=maga

# Custom dimensions and font
https://api.memegen.link/images/aag/agile/standups.png?width=800&font=thick

# Empty top line (skip the first segment)
https://api.memegen.link/images/aag/_/aliens.png

# Multi-line text via newline escape
https://api.memegen.link/images/aag/first_line~nsecond_line/bottom.png

# Custom background
https://api.memegen.link/images/custom/top_text/bottom_text.png?background=https://example.com/img.jpg
```

## Notes for automated clients

A handful of points that are obvious in retrospect but cost an agent several round-trips to discover:

1. **Bootstrap once, cache.** `GET /templates/` is the single source of truth for renderable templates. Fetch at startup and refresh on a long interval; don't query per-meme.
2. **`POST` raw, read back the URL.** All `POST` endpoints normalize special characters into the escape forms above and return the canonical URL in the `url` field. Agents that don't want to maintain the escape table client-side can `POST` raw strings and use the returned URL verbatim.
3. **`example.url` is a free smoke test.** Each template's `example.url` is guaranteed to render, so a `HEAD` request against that URL is the cheapest way to validate that a `template_id` is live before constructing a derived URL.
4. **Validate `style` against `template.styles`.** Passing an unknown style name returns HTTP 422, not a default render, so client-side validation prevents user-visible errors. Likewise, validate `font=` against `GET /fonts/` before sending — an unknown font also returns 422.
5. **Trim text segments to `lines`.** Don't rely on silent truncation; trim client-side to `template.lines` before joining.

## Edge cases

| Situation | Current behavior |
|-----------|------------------|
| More text segments than `lines` | Extra segments are ignored; the meme renders with the first `lines` segments |
| Fewer text segments than `lines` | Missing trailing lines render as empty |
| Unknown `style=` name (not a URL) | Returns HTTP 422 |
| Unknown `font=` value | Returns HTTP 422; the image still renders using the template's default font |
| Path text segment >200 bytes | Returns HTTP 414 (`Custom text too long`) |
| Unknown image extension | Defaults to PNG, returns HTTP 422 |
| `width` or `height` between 1 and 9 | Returns HTTP 422 (size silently set back to 0,0) |
| Unknown `template_id` | Returns HTTP 404 |
| `style=<url>` that can't be downloaded | Returns HTTP 415 |
| `id=custom` with no or un-downloadable `background=` URL | Returns HTTP 422 (missing) or HTTP 415 (un-downloadable) |
| Invalid `color=` value | Returns HTTP 422 |

## Reference

- Templates list — `GET /templates/`
- Per-template metadata — `GET /templates/{id}`
- Fonts — `GET /fonts/`
- OpenAPI spec — [`/docs/openapi.json`](https://api.memegen.link/docs/openapi.json)
- Interactive client — [`/docs`](https://api.memegen.link/docs)
