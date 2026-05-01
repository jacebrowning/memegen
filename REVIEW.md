# Code Review — memegen

Full library review of `app/` (~3k LOC, ~25 source files + ~14 test files). Sanic 25.x, Python 3.13, mypy + black + isort + autoflake, pytest + describe + expecter. Mature codebase with strong test coverage and CI.

> **Verification caveat.** No Poetry / Python 3.13 environment was available in the worktree, so the test suite (`make test`) and `mypy` (`make check`) could not be re-run. Safe fixes were limited to mechanical changes that compile cleanly under `python3 -m py_compile`. **Please run `make check && make test` before merging.**

---

## Summary

| Severity | Count | Fixed inline |
|---|---|---|
| Bug — wrong behavior in production | 1 | ✅ 1 |
| Bug — latent / edge case | 5 | 0 |
| Consistency | 6 | ✅ 1 |
| Best practices & lint | 9 | ✅ 2 |
| Documentation | 7 | 0 |
| Open TODO debt | 8 | 0 |

Headline takeaways:
- One real **copy-paste bug** in user-facing error text ([app/views/fonts.py](app/views/fonts.py)) — fixed.
- One **comprehension shadowing** bug that works by accident ([app/views/examples.py](app/views/examples.py)) — fixed.
- A handful of **latent bugs** worth attention: a leaked async file handle on exception, a race-condition counter mutated from concurrent handlers, and silent recursion in `Template.get_image()` if the layout deleter no-ops.
- Three near-identical "redirect after stripping one query arg" blocks have been flagged with `# TODO: Move this pattern to utils` — worth a small dedicated refactor.
- Two render functions (`render_image`, `render_animation`) and two view functions (`custom_path`, `detail_text`) are long and deeply nested — flagged for follow-up only, not changed here.
- README has a small but real **broken example URL** pattern (display path includes `/images/`, href omits it).

---

## Fixed in this branch

| # | File | Change |
|---|---|---|
| 1 | [app/views/fonts.py:37](app/views/fonts.py:37) | Error message `"Template not found"` → `"Font not found"` for the `/fonts/<id>` 404. |
| 2 | [app/views/examples.py:35](app/views/examples.py:35) | Renamed comprehension variable: `[items[0] for items in items]` → `[item[0] for item in items]`. Removes shadowing of the function parameter. |
| 3 | [app/views/images.py:18](app/views/images.py:18) | `from .templates import generate_url` → import from canonical source `.helpers` (merged with existing `.helpers` import on line 9). The function is defined in `views/helpers.py`; `views/templates.py` only re-exports it as a side effect of its own `from .helpers import generate_url`. The previous import would silently break if `views/templates.py` removed the import. |
| 4 | [app/types.py:1,11](app/types.py:1) | `Align = Union[Literal["left"], Literal["center"], Literal["right"]]` → `Align = Literal["left", "center", "right"]`. Same type, idiomatic form, drops the now-unused `Union` import. Matches the rest of the codebase, which uses `\|` syntax. |

All four files compile under `python3 -m py_compile`. No test or behavior changes.

---

## 1. Bugs & correctness

### 1.1 Latent: leaked async file handle in `download()` — *not fixed*

[app/utils/http.py:54-56](app/utils/http.py:54)

```python
f = await aiofiles.open(path, mode="wb")  # type: ignore
await f.write(await response.read())
await f.close()
```

If `await f.write(...)` raises (disk full, permission flip, cancelled task), `f.close()` is never called and the file handle leaks. **Fix:** use `async with aiofiles.open(path, mode="wb") as f: await f.write(...)`. The `# type: ignore` becomes unnecessary because aiofiles' async context manager has proper stubs.

Not fixed inline because changing to `async with` could subtly affect cancellation behavior (the context manager will await close even if the surrounding task was cancelled). Worth verifying with the test suite first.

### 1.2 Latent: `REMOTE_TRACKING_ERRORS` race condition — *report only*

[app/utils/meta.py:36](app/utils/meta.py:36), [:66](app/utils/meta.py:66), [:132](app/utils/meta.py:132), [:160](app/utils/meta.py:160) all do `settings.REMOTE_TRACKING_ERRORS += 1`.

In an async server, multiple coroutines can read-modify-write this module-level integer concurrently. The pattern under-counts errors, which is the opposite of the desired safety behavior (the counter is used to disable tracking after `REMOTE_TRACKING_ERRORS_LIMIT` consecutive failures — under-counting delays that disablement). Same applies to `settings.TRACK_REQUESTS = False` at [app/utils/meta.py:137](app/utils/meta.py:137).

**Recommendation:** wrap the counter behind a small helper, e.g. `meta._increment_error()`, backed by `asyncio.Lock` or `itertools.count`. Or keep it simple and accept slight under-counting — but document the choice. Either way, mutating `settings.*` from async code is a smell.

### 1.3 Latent: potential recursion in `Template.get_image()` — *report only*

[app/models/template.py:158-170](app/models/template.py:158)

```python
if style == "default" and not animated:
    return ...placeholder...
if animated:
    logger.info(...)
else:
    logger.warning(...)
    del self.layout
return self.get_image()
```

The `layout` deleter at [app/models/template.py:101-104](app/models/template.py:101) is a no-op when `self.source` is a URL schema. So if a custom-style URL fails to match any path *and* the source is a URL, the recursive call re-enters with the same `style`/`layout`. Tracing through, the next iteration falls through to the `style == "default"` branch and returns the placeholder — so it terminates today. But the termination depends on `style` becoming `"default"` after `del self.layout`, which depends on a quiet contract between `layout`'s deleter and `get_image()`'s style-derivation logic. **Recommendation:** add a depth guard (e.g. `def get_image(self, style="default", *, animated=False, _depth=0)`) or assert termination explicitly.

### 1.4 Latent: ignored download return value — *report only*

[app/models/template.py:397](app/models/template.py:397)

```python
logger.info(f"Saving overlay {url} to {foreground}")
await utils.http.download(url, foreground)
```

`utils.http.download()` returns `bool` indicating success, but the return value is dropped. The next try/except guards `embed`/`merge`, but if the download silently failed the foreground file may not exist — `embed_foreground_path()` will be passed a nonexistent path and Pillow will raise, which IS caught by `EXCEPTIONS`. So the failure mode is observable but the error message is misleading. **Recommendation:** check the return and log a clearer "skipping overlay X because download failed" message.

### 1.5 Latent: bare `assert` swallowed by `EXCEPTIONS` tuple — *report only*

[app/utils/http.py:9-18](app/utils/http.py:9)

```python
EXCEPTIONS = (
    aiohttp.client_exceptions.ClientConnectionError,
    ...
    AssertionError,
    asyncio.TimeoutError,
    UnicodeError,
)
```

`AssertionError` has been in this tuple since the file's introduction (verified via `git log -p`). It catches asserts raised by aiohttp internals or yarl URL validation. There are no `assert` statements in the `try` blocks themselves, so it's not catching local asserts. **This is intentional but undocumented** — add a comment noting which library raises asserts here, or replace with the specific exception type once identified.

### 1.6 Latent: misleading test name — *report only*

[app/tests/test_views_clients.py:34](app/tests/test_views_clients.py:34)

```python
def it_handles_invalid_keys(expect, client, path, unknown_template):
    request, response = client.get(path + f"?template={unknown_template.id}")
```

The test is named `it_handles_invalid_keys` (suggests API key handling), but it's actually testing handling of invalid **template IDs**. Rename to `it_handles_unknown_templates` for clarity.

---

## 2. Consistency

### 2.1 Inconsistent error-message format across blueprints

| File | Pattern |
|---|---|
| [app/views/templates.py:53](app/views/templates.py:53) | `f"Template not found: {id}"` |
| [app/views/fonts.py:37](app/views/fonts.py:37) | `f"Font not found: {id}"` *(after fix #1)* |
| [app/views/shortcuts.py:43](app/views/shortcuts.py:43) | `f"Template not found: {template_id}"` |
| [app/views/shortcuts.py:59](app/views/shortcuts.py:59) | `f"Template not found: {template_id}"` |
| [app/views/shortcuts.py:165](app/views/shortcuts.py:165) | `f"Template not found: {template_id}"` |

Consistent enough already, but worth standardizing the variable name (`id` vs `template_id` in path params).

### 2.2 Inconsistent payload-extraction patterns — *report only*

`generate_url` in [app/views/helpers.py:11-33](app/views/helpers.py:11) does payload extraction one way; `create_automatic` in [app/views/images.py:69-81](app/views/images.py:69) does it another (no `request.form` check, no `[]`-suffix handling); `clients.preview` at [app/views/clients.py:35-43](app/views/clients.py:35) yet a third way.

If you want one uniform "extract payload from form OR JSON" helper, this is the consolidation point. Three call sites = exactly the threshold where extracting a helper is worth it.

### 2.3 Three near-identical "redirect with one arg removed" blocks — *report only*

Already flagged in code with `# TODO: Move this pattern to utils`:

- [app/views/images.py:165-176](app/views/images.py:165) — strip `style=animated`, redirect to `.gif`.
- [app/views/images.py:202-214](app/views/images.py:202) — same, but for the `detail_text` route.
- [app/views/images.py:230-240](app/views/images.py:230) — strip `watermark`, redirect.

A `utils.urls.redirect_without(request, route_name, **path_kwargs, drop=("style",))` helper would collapse all three into one-liners. Trivial refactor; pure win.

### 2.4 Two near-identical overlay error-handling blocks — *report only*

[app/utils/images.py:170-175](app/utils/images.py:170) (`embed`) and [app/utils/images.py:195-200](app/utils/images.py:195) (`merge`) have the exact same `try/except IndexError` boilerplate around `template.overlay[index]`. Extract a `_get_overlay_or_last(template, index)` helper.

### 2.5 Inconsistent `request: Request` typing across view handlers — *report only*

Some handlers annotate (`async def index(request: Request)`), some don't (`async def detail(request, id)`). All views are typed elsewhere. Examples missing the annotation:

- [app/views/fonts.py:33](app/views/fonts.py:33) — `async def detail(request, id)`
- [app/views/templates.py:49](app/views/templates.py:49) — `async def detail(request, id)`
- [app/views/templates.py:65](app/views/templates.py:65) — `async def build(request, id)`
- [app/views/shortcuts.py:20,53,68,80,155,175](app/views/shortcuts.py:20) — most handlers in this file

Mechanical fix; safe to apply, but requires running mypy to confirm no downstream surprises.

### 2.6 Inconsistent generic-import-vs-specific-import — *report only*

The codebase mixes `from .. import utils` then `utils.text.encode(...)` with `from ..utils.text import encode`. Both styles are present (e.g., `views/helpers.py` uses the module form; `models/template.py` uses both: `from .. import utils` and `utils.text.fingerprint(...)`). Pick one. Module-style is more common in this repo and a tiny bit easier to grep.

---

## 3. Best practices & lint

### 3.1 Mutable module-level state in `settings.py` — *report only*

[app/settings.py:136-139](app/settings.py:136):
```python
TRACK_REQUESTS = True
REMOTE_TRACKING_URL = os.getenv("REMOTE_TRACKING_URL")
REMOTE_TRACKING_ERRORS = 0
```

`TRACK_REQUESTS` is flipped to `False` from [app/utils/meta.py:137](app/utils/meta.py:137); `REMOTE_TRACKING_ERRORS` is incremented in four places. Mutating a module imported elsewhere is fragile (and breaks once you have multiple workers — gunicorn `--workers 2` means each worker has its own counter). See §1.2.

### 3.2 Hardcoded sentinel API key — *report only*

[app/utils/meta.py:49](app/utils/meta.py:49):
```python
if api_key == "myapikey42" and not url.startswith(...):
```

`"myapikey42"` is the documented public example key (referenced in [app/tests/test_utils_meta.py:36](app/tests/test_utils_meta.py:36) and presumably docs). Pull it into `settings.SAMPLE_API_KEY` for clarity.

### 3.3 Indirect import via re-export — *fixed (#3)*

Was: `views/images.py` imported `generate_url` from `.templates`. Now imports from canonical `.helpers`.

### 3.4 Variable shadowing in comprehension — *fixed (#2)*

Was: `urls = [items[0] for items in items]` rebinds `items` per iteration.

### 3.5 Magic `assert` in `utils/html.py:106` — *report only*

```python
def gallery(urls, *, columns: bool, refresh: int, query_string: str = "") -> str:
    ...
    if columns:
        ...
    assert refresh
    return _grid_debug(urls, refresh, extra)
```

If `columns=False` and `refresh=0`, this asserts. With `python -O` the assert vanishes and `_grid_debug` is called with `refresh=0`, which would then divide-by-zero in `REFRESH_SCRIPT.replace("{interval}", str(refresh * 1000))` (no, that's fine — produces `"0"`). The `assert` is enforcing a caller contract and should be a `ValueError` or removed if the contract is documented.

### 3.6 `Pilmoji` lifecycle in a context manager — *report only*

[app/utils/images.py:646-652](app/utils/images.py:646):
```python
@contextmanager
def emoji_support(image, draw, text):
    if emoji.emoji_count(text):
        pilmoji = Pilmoji(image, render_discord_emoji=False, emoji_scale_factor=0.8)
        yield pilmoji
        pilmoji.close()
    else:
        yield draw
```

If the `yield`'s body raises, `pilmoji.close()` is never called. Use try/finally or `with Pilmoji(...) as pilmoji:` if it supports the protocol. (Quick check: pilmoji does — it's a context manager.)

### 3.7 `Image.open(stream).convert("RGBA")` reassigning `background` — *report only*

[app/utils/images.py:213](app/utils/images.py:213):
```python
background = Image.open(stream).convert("RGBA")  # type: ignore[assignment]
```

`background` was just used as the iteration target for `ImageSequence.Iterator(background)` two lines above. Reassigning it inside the loop is confusing — the iterator already captured the original. Rename the inner variable to `frame_image` or similar. (No bug — but the `# type: ignore` is masking a legitimate typing tell.)

### 3.8 Wasted dict-rebuild in `generate_url` — *report only*

[app/views/helpers.py:18-21](app/views/helpers.py:18):
```python
payload = dict(request.form)
for key in list(payload.keys()):
    if "style" not in key and "text" not in key:
        payload[key] = payload.pop(key)[0]
```

`payload.pop(key)` followed by `payload[key] =` does a removal+reinsertion that's equivalent to `payload[key] = payload[key][0]`. Functionally identical, less code:
```python
for key in list(payload.keys()):
    if "style" not in key and "text" not in key:
        payload[key] = payload[key][0]
```

### 3.9 `Align = Union[Literal[...], ...]` instead of `Literal[...]` — *fixed (#4)*

---

## 4. Documentation

### 4.1 README example URLs are missing `/images/` — *report only*

[README.md](README.md) (the table under "Available Formats") shows e.g.:

```
| GIF (animated background) | [/images/oprah/you_get/animated_text.gif](https://api.memegen.link/oprah/you_get/animated_text.gif) |
```

The link **text** is `/images/oprah/...` but the **href** is `/oprah/...` (missing `/images/`). The shortcut blueprint redirects the bare path to `/images/...`, so the link technically resolves — but it's still a 302, breaks `curl --fail`-style usage, and the display/href mismatch is confusing. Same issue on four rows: `oprah` GIF, `iw` GIF, `oprah` WebP, `iw` WebP.

### 4.2 README font table is missing two fonts — *report only*

[README.md](README.md) "Custom Fonts" table lists 6 fonts. [app/models/font.py:55-64](app/models/font.py:55) defines 8:

| Missing from README | ID | Alias |
|---|---|---|
| Titillium Web SemiBold | `titilliumweb-thin` | `thin` |
| Segoe UI Bold | `segoe` | `tiny` |

### 4.3 No docstrings on view handlers — *report only*

All Sanic route handlers under `app/views/` rely entirely on `@openapi.summary(...)` decorators for documentation. There are zero Python docstrings in `app/views/`. Mypy and IDEs don't read OpenAPI strings, so hover/help shows nothing. Adding one-liner docstrings mirroring the OpenAPI summary is a low-risk improvement; not applied here only because it's bulky and would inflate the diff without test verification.

### 4.4 Stale TODO with broken issue link wording — *report only*

[app/utils/urls.py:75-77](app/utils/urls.py:75):
```python
# TODO: Fix Sanic bug?
# https://github.com/jacebrowning/memegen/issues/799
url = url.replace("::", ":")
```

The link points to the project's own issue tracker. Verify whether issue #799 is still open; if closed/fixed in current Sanic, this workaround can be removed.

### 4.5 OpenAPI `description` parameter inconsistency — *report only*

[app/views/images.py:108-109](app/views/images.py:108) uses `description="..."`:
```python
@openapi.response(
    201, {"application/json": MemeResponse},
    description="Successfully created a meme from a custom image",
)
```

But every other `@openapi.response(...)` in the codebase passes the description as a third positional argument:
```python
@openapi.response(201, {...}, "Successfully created a meme")
```

Both work, but pick one style. The third-positional form is by far the dominant pattern.

### 4.6 `CONTRIBUTING.md` mentions Heroku — *report only*

The deployment section refers to Heroku free dynos which were discontinued in late 2022. Verify the deployment story still matches reality (the `Procfile` and `heroku local web` Makefile target suggest it does, but the language could mislead new contributors).

### 4.7 Coverage gap: `Template.position`, `Template.customize`, `Template.animate` — *report only*

These three methods on `Template` (lines 445-514 of [app/models/template.py](app/models/template.py)) are reached indirectly through `Template.clone()`, but there are no direct unit tests asserting they handle malformed input correctly (e.g., what happens when `start="abc,def"`?). The `try/except ValueError` paths just log and bail — easy to test, would pin down current behavior.

---

## 5. Open TODO debt (8 instances)

Inventory for triage; none worth fixing in this review:

| File | Line | TODO |
|---|---|---|
| [app/views/images.py](app/views/images.py:169) | 169, 206, 232 | "Move this pattern to utils" — see §2.3 |
| [app/utils/http.py](app/utils/http.py:45) | 45 | "Figure out which sites use 3xx as errors" |
| [app/utils/urls.py](app/utils/urls.py:75) | 75 | "Fix Sanic bug?" — see §4.4 |
| [app/utils/images.py](app/utils/images.py:347) | 347 | "Implement a proper solution using trigonometry" (debug overlay positioning) |
| [app/models/template.py](app/models/template.py:400) | 400 | "Can 'merge' and 'embed' be combined?" |
| [app/tests/test_utils_images.py](app/tests/test_utils_images.py:140) | 140 | "Support using same background GIF to create animated text" |

---

## 6. Recommended follow-ups (deferred refactors)

These are the medium-sized changes worth doing as separate PRs:

1. **Extract redirect-with-arg-removed helper** (§2.3). Touches `app/views/images.py` and `app/utils/urls.py`. Small. Pure DRY win.
2. **Refactor `render_image` and `render_animation`** ([app/utils/images.py:260-521](app/utils/images.py:260)) — 109 + 153 LOC each, with two near-duplicated overlay-collection loops and overlapping watermark/size logic. Extract helpers for: timed-overlay collection, debug overlay drawing, watermark suppression for small images. High value, but needs care and a strong test gate.
3. **Refactor `views/helpers.py:render_image`** (111 LOC orchestration with state-machine-style status codes). Split into: validate-extension, resolve-template, validate-color, validate-font, validate-size, render. Each ~10 lines.
4. **Refactor `views/shortcuts.py:custom_path`** ([app/views/shortcuts.py:80-144](app/views/shortcuts.py:80), 65 LOC, 7+ levels of `if/elif` on string-suffix conditions). Most of the body is "URL repair" — extract a `_repair_text_path(text_paths) -> (text_paths, params)` helper.
5. **Make analytics counters thread-safe or document the deliberate looseness** (§1.2, §3.1). Choose one.
6. **Add a `/images/<template>/<text>` integration test that exercises the cancellation path** (helps confirm the aiofiles `async with` change in §1.1 is safe).
7. **Add docstrings to public view handlers** (§4.3). Mechanical, but bulky.

---

## Appendix: scope coverage

| Directory | Files reviewed | LOC reviewed | Notes |
|---|---|---|---|
| `app/` (root) | main.py, config.py, settings.py, helpers.py, types.py | 397 | All read |
| `app/models/` | font.py, overlay.py, text.py, template.py, __init__.py | 762 | All read |
| `app/utils/` | http.py, html.py, images.py, meta.py, text.py, urls.py | 1,452 | All read |
| `app/views/` | clients.py, examples.py, fonts.py, helpers.py, images.py, schemas.py, shortcuts.py, templates.py | ~970 | All read |
| `app/tests/` | conftest + 13 test files | 1,710 | All read |
| Tooling | Makefile, .circleci/config.yml, pyproject.toml, .deepsource.toml, .coveragerc, .verchew.ini, .tool-versions | — | Read |
| Docs | README.md, CHANGELOG.md, CONTRIBUTING.md (header), docs/ index | — | Spot-checked |

Total Python LOC reviewed: ~5,290.
