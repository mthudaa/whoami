# whoami

Personal profile and portfolio of M. Taufiqul Huda, published with GitHub Pages at
<https://mthudaa.github.io/whoami/>.

The page is a single static `index.html`, generated from `cv.json`.

## Update the site

1. Edit `cv.json` (all text, dates, links and metrics come from it).
2. Run `python3 build.py` (standard library only, no dependencies).
3. Commit `cv.json` and the regenerated `index.html`, then push `main`.

Layout and styling live in `build.py`. `index.html` is generated, so don't edit it by hand.

## Animations

A faint routing grid with signal pulses sits behind the page, the hero fades in, sections reveal on
scroll, the metric numbers count up, and the "Current research" card runs an illustrative 14-step SAR
conversion. All of it is plain CSS and JavaScript inside `index.html`.

The nav has a pause/play button for all animations (remembered in the browser). Visitors whose system
asks for reduced motion get the static page by default, and print output has no animation.

## Files

| File | Purpose |
| --- | --- |
| `cv.json` | Source data (schema 1.0). Everything in it is published. |
| `build.py` | `cv.json` to `index.html`, deterministic output |
| `index.html` | Generated page served by GitHub Pages |
| `Huda-formal.png` | Original portrait |
| `Huda-formal-640.jpg` | 640 px square crop of the portrait used on the page and in link previews |

## Privacy

`cv.json` is public. Keep out of it anything that shouldn't be: street address, student ID,
internal notes, or unpublished research details.

## License

See `LICENSE`.
