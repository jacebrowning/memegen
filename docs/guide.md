# Constructing a Meme URL

This guide explains how to programmatically construct valid meme URLs from start to finish. It consolidates all necessary information from the API's metadata endpoint, Swagger documentation, and behavior specifics into one reference.

---

## 1. Start with the Templates List

All renderable meme templates are available at:

**https://api.memegen.link/templates/**

This is the authoritative source for what templates exist and what properties each one supports. Cache this list locally; refresh periodically.

### Example Template Metadata

A GET request for a single template returns JSON like this:

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

Four fields govern URL construction:

| Field | Meaning |
| :---- | :------ |
| `id` | Unique template identifier (used in the URL path) |
| `lines` | Maximum number of text lines accepted in the URL path |
| `overlays` | Number of overlay slots the template supports |
| `styles` | List of named styles available for this template |
| `blank` | URL to the empty template (background only) |
| `example` | A guaranteed-valid reference URL and text |

Everything else (`name`, `source`, `keywords`) is descriptive metadata.

---

## 2. URL Path Structure

A meme URL has the shape:

```
/images/{template_id}/{line_1}/{line_2}/.../{line_n}.{ext}
```

where:

- `{template_id}` — the `id` field from the template metadata
- `{line_n}` — up to `lines` `/`-separated text segments (in order)
- `{ext}` — an image format extension: `.png`, `.jpg`, `.gif`, or `.webp`
- fewer than `lines` segments is allowed (missing lines will be blank)
- more than `lines` segments gets truncated to the first `n` lines
- an **empty line** can be passed as a single underscore (`_`)
- all special characters are encoded using escape patterns (see Section 4)

### Worked Example

The "Daily Struggle" template (`ds`) has `lines: 3`, meaning it can display up to 3 text segments:

```
https://api.memegen.link/images/ds/The_dress_is_black_and_blue./The_dress_is_gold_and_white..jpg
```

This URL contains two text lines (segment 3 is blank). The trailing empty line could be explicitly passed as `_` for clarity:

```
https://api.memegen.link/images/ds/The_dress_is_black_and_blue./The_dress_is_gold_and_white./_/ .jpg
```

---

## 3. How Template Metadata Maps to the URL

### `lines`

This is the **maximum** number of text lines you can include in the path. Behavior:

- You may provide **fewer** lines than the maximum → missing lines are rendered as blank
- You may provide **more** lines than the maximum → only the first `n` lines are used (truncated)
- The only way to render an intentionally empty line is to pass `_`

Example: For a template with `lines: 3`, all three variations below are valid:

| URL segments | Result |
| :--- | :--- |
| `A/B` | Line 1 = "A", Line 2 = "B", Line 3 = blank |
| `A/B/C` | Line 1 = "A", Line 2 = "B", Line 3 = "C" |
| `A/B/C/D` | Line 1 = "A", Line 2 = "B", Line 3 = "C" (line "D" ignored) |

### `overlays`

A non-zero `overlays` value indicates the template supports an additional image overlay on top of the background. Overlays are controlled via the `style` query parameter (see below), and can be positioned and scaled with:

- `center=<float>,<float>` — coordinates of the overlay's center as a ratio of the image dimensions (default `0.5,0.5`)
- `scale=<float>` — size ratio of the overlay relative to the background (default `0.2`)

Example with overlay positioning:

```
https://api.memegen.link/images/pigeon/Engineer/_/Is_this_Photoshop~q.png?style=https://i.imgur.com/W0NXFpQ.png&center=0.25,0.75&scale=0.15
```

### `styles`

The `styles` array defines what values are accepted for the `style` query parameter:

- `style=default` — the template's default appearance (implicit when `style` is omitted)
- `style=maga` — a named variation of the template (e.g. "MAGA" version of `ds`)
- `style=<image_url>` — a custom image to use as an overlay (overrides named styles)

The list returned in the template metadata is **authoritative**. If a style name isn't listed, it's unsupported.

Example — switching between named styles on the `ds` template:

```
https://api.memegen.link/images/ds/The_dress_is_black_and_blue./The_dress_is_gold_and_white..jpg               # default
https://api.memegen.link/images/ds/The_dress_is_black_and_blue./The_dress_is_gold_and_white..jpg?style=maga   # MAGA style
```

### `blank`

The `blank` field is the canonical URL for the template with no text. This is the correct URL to fetch when you want the background only.

Example:

```
https://api.memegen.link/images/ds.jpg
```

### `example`

The `example.url` field is a guaranteed-valid URL for the template that serves as a reliable smoke test. All agents should check that this URL renders before attempting custom text.

Example:

```
https://api.memegen.link/images/ds/The_dress_is_black_and_blue./The_dress_is_gold_and_white..jpg
```

---

## 4. Rendering Options Reference

All options are passed as query parameters on the meme URL.

### Image Formats

| Format | Extension | Notes |
| :--- | :--- | :--- |
| PNG | `.png` | Default format. Lossless, static. |
| JPEG | `.jpg` | Smaller files, lossy. |
| GIF | `.gif` | Animated if the template background is animated, or used to animate static backgrounds with `?animate=true`. |
| WebP | `.webp` | Same animation rules as `.gif`. Better compression. |

### Custom Dimensions

- `width=<int>` — Scale the image to this width in pixels, aspect ratio preserved unless `height` is also provided.
- `height=<int>` — Scale the image to this height in pixels, aspect ratio preserved unless `width` is also provided.
- If **both** `width` and `height` are provided → the image is padded to the exact dimensions (letterboxing/pillarboxing as needed).

Example — fixed 800×450 canvas:

```
https://api.memegen.link/images/both/width_or_height/why_not_both~q.png?height=450&width=800
```

### Alternate Layouts

- `layout=top` — Positions all text at the top of the image instead of the default center/bottom placement.

Only `top` is currently documented as a valid option.

Example:

```
https://api.memegen.link/images/rollsafe/When_you_have_a_really_good_idea.webp?layout=top
```

### Special Characters

Memegen uses tilde-based escape sequences for characters that are unsafe in URL paths.

#### Whitespace

| Input | Renders as |
| :--- | :--- |
| `_` (single underscore) | space (` `) |
| `-` (dash) | space (` `) |
| `__` (double underscore) | underscore (`_`) |
| `--` (double dash) | dash (`-`) |

#### Reserved / Punctuation

| Escape | Character | Example |
| :--- | :--- | :--- |
| `~n` | newline (`\n`) | `Line~none~nTwo` → `Line one` `Line two` |
| `~q` | question mark (`?`) | `Is_this_real~q` → `Is this real?` |
| `~a` | ampersand (`&`) | `You~a_Me` → `You & Me` |
| `~p` | percent (`%`) | `100~p` → `100%` |
| `~h` | hash (`#`) | `~h idioms` → `# idioms` |
| `~s` | forward slash (`/`) | `Path~sto~sfile` → `Path/to/file` |
| `~b` | backslash (`\`) | `C~bWindows` → `C\Windows` |
| `~l` | less-than (`<`) | `~l3` → `<3` |
| `~g` | greater-than (`>`) | `Bigger~g` → `Bigger>` |
| `''` (two single quotes) | double quote (`"`) | `She_said~q''Hi~q~n` → `She said "Hi` |

#### Emoji

- Raw Unicode characters are accepted: 👍
- Colon-prefixed aliases are also supported: `:thumbsup:` → 👍

All standard emoji shortcodes (GitHub / EmojiCheat style) work.

#### Example — combining many escapes:

```
https://api.memegen.link/images/ugandanknuck/~hspecial_characters~q/underscore__-dash--_:thumbsup:.png
```

Renders: `#special characters?` `underscore_ -dash-- 👍`

### Custom Fonts

The list of available fonts is live at: **https://api.memegen.link/fonts/**

Apply with `font=<str>`:

| Font Name | ID | Alias |
| :--- | :--- | :--- |
| Titillium Web Black | `font=titilliumweb` | `font=thick` |
| Kalam Regular | `font=kalam` | `font=comic` |
| Impact | `font=impact` | — |
| Noto Sans Bold | `font=notosans` | — |
| Noto Sans Bold Hebrew | `font=notosanshebrew` | `font=he` |
| HG Mincho B | `font=hgminchob` | `font=jp` |

Example:

```
https://api.memegen.link/images/buzz/memes/memes_everywhere.webp?font=titilliumweb&width=800
```

### Custom Colors

`color=<str>,<str>` — sets colors for the text lines.

- Supply **one** color → all lines use that color
- Supply **multiple** comma-separated colors → each line gets the corresponding color (line 1 = first color, line 2 = second color, etc.)

Colors may be:

- HTML color names: `red`, `blue`, `DarkSeaGreen`
- 3-, 6-, or 8-digit hex codes (no `#` prefix): `FFF`, `DEADBEEF`, `FF80ED`

Example — alternating colors:

```
https://api.memegen.link/images/ds/Fear_is_the_path/To_the_dark_side.png?color=FFD700,FF0000
```

### Custom Backgrounds

`background=<url>` — replaces the template background with an arbitrary image URL.

This is compatible with custom overlays (below). The custom background is loaded first, then any `style=<image_url>` overlay is applied on top.

Example:

```
https://api.memegen.link/images/custom/_/my_background.png?background=http://www.gstatic.com/webp/gallery/1.png
```

### Image Overlays (revisited)

When `overlays > 0`, you can add an overlay image on top of the background:

```
?style=<image_url>&center=<x>,<y>&scale=<ratio>
```

- `style=<image_url>` — overlay image (can also be one of the template's named styles)
- `center` — overlay center as `(0..1, 0..1)` where `(0,0)` = top-left, `(1,1)` = bottom-right (default: `0.5,0.5`)
- `scale` — overlay size as a fraction of the background's smaller dimension (default: `0.2`)

Example — custom overlay with custom positioning:

```
https://api.memegen.link/images/pigeon/Engineer/_/Is_this_Photoshop~q.png?style=https://i.imgur.com/W0NXFpQ.png&center=0.25,0.75&scale=0.15
```

---

## 5. For Automated Clients (Aggs, Bots, Scripts)

### Recommended Bootstrap Procedure

1. **One-time fetch**: `GET https://api.memegen.link/templates/` → build a local cache of all templates
2. **Lookup**: For a given template ID, read its `id`, `lines`, `overlays`, and `styles` to know what parameters are valid
3. **Construct**: Build the URL path with proper escaping, add query parameters from the reference above
4. **Validate (optional)**: Fetch the template's `example.url` to ensure the template is still live before attempting custom text

### POST Endpoints Normalize Special Characters

All `POST` endpoints (e.g. `/images/`, `/meme/`) accept raw text and return a fully-formed URL in the response. The returned URL uses canonical tilde-based escaping, so agents can skip implementing the escape table themselves and just pass `POST` responses to clients directly.

Example POST:

```bash
curl -X POST "https://api.memegen.link/images/ds" \
  -H "Content-Type: application/json" \
  -d '{"text":["Line 1","Line 2?","Line 3 & more"]}'
```

Response includes the fully-escaped URL:

```json
{
  "url": "https://api.memegen.link/images/ds/Line_1/Line_2~q/Line_3_~a_more.png"
}
```

### Validation & Error Behavior

| Condition | Result |
| :--- | :--- |
| Unknown `template_id` | **404 Not Found** |
| Too many text lines (exceeds `lines`) | Extra lines are **truncated** silently |
| `style=<name>` with an unsupported name | Falls back to the *default* style (no error) |
| Missing `style` parameter | Uses default style |
| `layout=<name>` with unknown value | Falls back to default layout (ignored) |
| `background` URL fails to load | Blank background appears (error logged server-side) |
| `font` / `color` with invalid value | Falls back to template defaults (no error) |

### Example Workflow for an Agent

```python
# 1. Bootstrap
templates = requests.get("https://api.memegen.link/templates/").json()
template = templates["ds"]

# 2. Build text lines
lines = ["Hello world?", "This & that", "_"]
escaped_lines = [escape(line) for line in lines]  # implement or use POST

# 3. Assemble URL
base = f"/images/{template['id']}/{'/'.join(escaped_lines)}.png"
url = "https://api.memegen.link" + base

# 4. Add options
if template['styles']:
    url += "?style=default"  # or pick style=template['styles'][0]
```

Or skip steps 2–3 by posting to the creation endpoint:

```bash
POST /images/ds
{"text": ["Hello world?", "This & that", ""]}
→ {"url": "https://api.memegen.link/images/ds/Hello_world~q/This_~a_that/_.png"}
```

---

## 6. Quick Reference Summary

1. **Discover**: `GET /templates/` → get `lines`, `styles`, `overlays` per template
2. **URL pattern**: `/images/{id}/{line1}/{line2}/.../{lineN}.png` (N ≤ `lines`)
3. **Empty line**: pass `_`
4. **Escapes**: `_ → space`, `__ → _`, `~q → ?`, `~a → &`, `~n → \n`, etc.
5. **Styles**: `?style=<name>` from the `styles` array, or a direct image URL for overlays
6. **Overlay adjust**: `?center=0.5,0.5&scale=0.2`
7. **Layout**: `?layout=top`
8. **Font**: `?font=<font_id>` or alias
9. **Color**: `?color=name,name…` or `?color=hex,hex…`
10. **Size**: `?width=800&height=450` (both → padded), `?width=800` (aspect preserved)
11. **Background**: `?background=<url>`
12. **Validate**: `GET` the template's `example.url`
13. **Simplify**: `POST /images/{id}` with JSON → get back the canonical URL

---

## 7. Links

- **Templates list**: <https://api.memegen.link/templates/>
- **Full API docs (Swagger)**: <https://api.memegen.link/docs/>
- **Live fonts list**: <https://api.memegen.link/fonts/>
- **Source code**: <https://github.com/jacebrowning/memegen>
