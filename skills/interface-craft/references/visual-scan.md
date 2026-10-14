# Visual scan: measure first, then read every region

Looking at a whole screenshot once finds the 4-5 loudest problems and misses the rest. Small things (a 3px misalignment, one card with different padding, a gray that is almost the right gray, a dark-mode border that disappeared) only show up when you **measure** the page and then **read it region by region at zoom**. This file covers both steps for the web.

## 1. Measure the rendered page (`scripts/render_audit.mjs`)

Run it whenever the UI can be opened in a browser (a URL, a local dev server, a static `.html`).

One-time setup: `cd <skill>/scripts && npm install`. It uses the installed Chrome or Edge, so nothing else is downloaded.

```bash
node <skill>/scripts/render_audit.mjs http://localhost:3000/checkout --out ui-audit
```

- The default runs cover 375×812, 768×1024 and 1440×900, each in light and dark. Narrow the set with `--viewports 375x812,1440x900` or `--themes light`.
- If the app switches themes with a class or an attribute rather than `prefers-color-scheme`, add `--dark-class dark` or `--dark-attr data-theme=dark`. The report says so when light and dark render the same.
- For pages behind a login, use `--storage-state auth.json` (Playwright storage state). Never type real credentials yourself.
- For pages that render late, use `--wait-for "<selector>"`.
- **`--stress`** adds a run per viewport with ~40% longer Turkish text and one with doubled text size. The report lists what **appears only under stress**.
- **`--states empty,error,loading`** audits each state through `?__state=…`. To make states reachable, see [stress and states](stress-and-states.md). Otherwise drive the browser to the state first and audit that page.

Output, for each run (e.g. `ui-audit/375x812-dark/`):
- `viewport.png`: the first screen as the user sees it.
- `annotated.png`: the whole page, with numbered boxes that match the IDs in `report.md`.
- `tiles/rNNcN.png`: zoomed crops for step 2.

`report.md` groups the findings across all runs, so you can see whether a problem is everywhere or only on "375-dark". It also includes a token inventory: distinct font sizes, colors, radii and spacing, plus off-grid values.

**Hits are leads, not verdicts.** Open `annotated.png` and confirm each error and warning. Drop false positives and give the reason, for example "text-clipped on the ticker: intentional rotating word". The usual false positives:
- Decorative illustrations built from DOM.
- Deliberately stacked cards.
- Marquee/ticker windows.
- `contrast-on-image` items: the audit can't measure these, so judge them on the tile in both themes.

`full.png` and `annotated.png` show fixed and sticky elements once, at their scroll-0 position.

If the user sent a screenshot rather than a running page, still cut it into tiles:
```bash
node <skill>/scripts/render_audit.mjs --tile-image screenshot.png --out ui-audit
```

## 2. Region scan (every tile, every lens)

**Pass A: whole screen, 10 seconds** (`viewport.png` in each theme). Write down:
- What draws the eye first, and whether that is the primary action.
- Whether the hierarchy reads (title → key content → action).
- Anything that looks broken from a distance: a heavy block, a hole, something misaligned against the grid, a surface that is the wrong color in one theme.

**Pass B: tile by tile.** Open every tile in order, with the Read tool, one tile at a time. Check each tile against the lenses below and write at least one line per tile. "Clean" is allowed only after every lens has been checked. Record each candidate as `run / tile / where in the tile / what`.

| Lens | Look for |
| --- | --- |
| Edges and alignment | Left edges that almost line up; icons not vertically centred on their text; baselines of side-by-side text not matching; numbers not right-aligned in tables; optical misalignment (play icons, chevrons, circular avatars next to square ones) |
| Spacing | One gap that differs among equal siblings; padding inside a component larger than the space around it; a cramped corner or an oddly empty one; a section break that is no bigger than the gap between items |
| Text | Truncation hiding key information; one orphan word on the last line of a heading; inconsistent capitalisation (Title Case vs Sentence case); typos; untranslated or mixed-language strings; leaked values (`undefined`, `NaN`, `null`, `[object Object]`, `{{name}}`, raw i18n keys like `auth.login.title`, `Lorem ipsum`); wrong locale formats (TR: `1.234,56 ₺`, `13.10.2026`) |
| Color and contrast | Faint text or icons; two almost-identical grays side by side; a color that is not in the palette; red or green used for something that is not an error or success; links that look like body text |
| Consistency with siblings | The same component drawn differently: radius, shadow, border, height, icon style (outline vs filled), icon size, stroke width, button sizes in one row |
| Affordance and state | Things that look clickable but are not, and the reverse; disabled vs enabled not distinguishable; no visible selected/active state; focus ring missing or clipped |
| Surfaces and borders | Double borders where two boxes meet; dividers that stop short or run inconsistently; nested radii that are not concentric; shadows cut off by `overflow: hidden`; a surface that barely separates from the page |
| Imagery and icons | Blurry, stretched or badly cropped images (cut-off faces, cut-off text in images); icons from different sets; misaligned or off-centre glyphs |
| Data and states | Very long names or numbers; empty values shown inconsistently (blank vs "-" vs "0"); zero and one-item cases; placeholder content left in |
| Theme (dark tiles) | Pure-white panels, chips or images with white backgrounds in dark; borders that vanish; dark icons on dark surfaces; a logo that does not adapt; shadows doing nothing on dark (elevated surfaces need a lighter tone and a 1px light ring instead) |

Zoom further when a tile is dense: run `--tile-image` on that tile.

**Pass C: across tiles and runs.**
- Compare the same component across tiles: a card in r02 against the same card in r05.
- Compare the same tile across runs: light vs dark, phone vs desktop.
- Check that spacing and type sizes repeat. Use the token inventory: similar-but-different values (13/14px, 10/12px radius) are the usual cause of "something looks off".

**Pass D: fresh eyes and personas.** Do this for broad reviews, and whenever the user says things slip past.

A reviewer who has seen your findings looks for the same things you did. Get a second look that has not.

1. If the environment can start a subagent (Agent/Task tool), give it **only** the screenshots or tiles, the screen's purpose and the main task. Do not give it your findings or the audit report. Ask for problems ranked by severity, from these personas:
   - **First-timer**: what is unclear, what would they tap first, where would they get stuck?
   - **Power user**: what slows down a task done 50 times a day? Extra clicks, motion, confirmation dialogs.
   - **Low vision / keyboard user**: contrast, focus, text size, targets.
   - **Distracted phone user**: one-handed reach, glanceability, interruptions mid-task.
   - **Stress tester**: what breaks with real data, slow network, a double tap, or the back button?
2. Without subagents, do the persona pass yourself, *after* writing your own list. Spend one sentence per persona per screen.
3. Merge the lists. Anything the fresh pass found that you missed is a hint about which lens you skipped. Re-check that lens on the other tiles.

## 3. Reconcile
- Merge the measured findings you confirmed with the region-scan findings. One problem with one fix is one row.
- For every finding, give the run (viewport + theme) and the tile or annotated ID, so it can be found again.
- List which runs and tiles you actually opened. Never write "no issues" for a tile you did not open.
- Keep a short **"Considered and rejected"** list (audit hits or ideas you dropped, each with its reason), so the reader can see they were looked at.
- After fixing, re-run the audit with the same arguments and compare the counts per rule. A fix must not add new hits in another run (typically dark or 375px).
