# Make GTA 6 Cover Art

Entry for make.fun competition `gta6-cover-art-01` — "Make GTA 6 Cover Art".

## What it is, paduka

A web app that turns any photo into a GTA 6 cover: Vice City sunset
grade, "GRAND THEFT AUTO VI" title block, "VICE CITY • 2026" tagline.
Runs fully in the browser — no photo is uploaded anywhere.

## Run the app, paduka

```sh
node main.ts --serve 8080
# open http://localhost:8080/
```

1. Upload your photo.
2. Pick a preset: Sunset / Neon Night / Beach Day.
3. Export PNG: 1080×1080, 1080×1350, or 1920×1080.

## Sample exports, paduka

Built offline and deterministically with `build_cover.py`
(Pillow + DejaVu fonts, no network, same input -> same bytes):

```sh
python3 build_cover.py
node main.ts   # validates PNG size + dimensions, copies to out/
```

| File | Size | Bytes | SHA-256 |
|---|---|---|---|
| out/cover-1080x1080.png | 1080×1080 | 153,624 | bd9a1d542d059adc61ae0e19dd9dde79865af3aa92e4cee90ef3e38989df97eb |
| out/cover-1080x1350.png | 1080×1350 | 155,740 | 66c18081d380be33b3adb1bb923d9ebcda34b4f93183140e7ec36f1abe71c704 |
| out/cover-1920x1080.png | 1920×1080 | 263,099 | 95cc991b977eece4a74d20ad23adbf25eba80a0b30243b6056448cdaa60c1fac |

Screenshots in `screenshots/`: the three covers plus a 1280×800
UI preview (`ui-1280x800.png`) — 4 screenshots total.

## Files, paduka

- `main.ts` — Node 22, standard library only. Validates exports, copies them to `$MAKEFUN_OUTPUT_DIR`, or serves `app/` with `--serve`.
- `app/` — `index.html`, `styles.css`, `app.js` (vanilla, no dependencies).
- `build_cover.py` — deterministic sample-cover generator.
- `out/` — the three PNG exports. `screenshots/` — 4 screenshots.
- `.makefun/owner.json` — wallet DCb2...yYuz.

## License

MIT — see LICENSE.
