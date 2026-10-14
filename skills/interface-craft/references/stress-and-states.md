# Stress, states and variants: look at the UI the way real data will hit it

Most bugs that "slip past the eye" are not visible with the sample data the screen was built with. They appear with:
- a long Turkish name;
- an empty list or 10,000 rows;
- a failed request;
- a user who has large text turned on.

Reviewing only the happy path is the main reason subtle problems get through.

Adapted from the "break", "state-machine" and "variant" skills in jakubkrehel/skills (MIT) and the harden/onboard passes of Impeccable (Apache-2.0); paraphrased. See NOTICE.

## 1. Free stress runs on the existing page (web)

```bash
node <skill>/scripts/render_audit.mjs <url> --stress
```

For each viewport, this adds two runs:
- **`-pseudo`**:
  - Every text gets ~40% longer, using Turkish characters (ğüşıöçİ).
  - Every 7th text longer than 12 characters also gets a long unbreakable compound word.
  - Short numbers become `1.234.567,89`.
  - Placeholders get longer.
- **`-large-text`**:
  - The root font size is doubled.
  - Text set in `px` does not grow and is reported (`fixed-px-text`). That text ignores the user's text-size setting.

Stress runs use the first theme in `--themes` (light by default). `report.md` then lists **"Appears only under stress"**: clipping, overflow, overlap and unequal cards that are waiting for real data, a translation or a large-text user. Treat these as real findings. Real content will be at least that long.

## 2. Break harness: a scratch page with worst-case content

Use this when a component matters (cards, list rows, headers, forms, tables, chips, toasts) or when you are building it.

1. **Read the props/data shape.** Every string, number, list, optional field, image and status in the component is an axis.
2. **Pick scenarios per axis.** Only add what the props make possible:
   | Axis | Scenarios |
   | --- | --- |
   | Text | empty · 1 character · one word · typical · 3× typical · one 40-character unbreakable word (`Hesapdoğrulamaişlemlerinizdeki`) · Turkish casing (`İSTANBUL`, `ışık`) · emoji · RTL/mixed (`<bdi>`) |
   | Numbers / money | 0 · 1 · negative · `1.234.567,89 ₺` · very long decimals · missing value (blank, "-" or "0"? pick one and make it consistent) |
   | Lists | 0 · 1 · 2 · many (100+) · one item much longer than the rest |
   | Media | missing · broken URL · extreme ratio (panorama, tall portrait) · transparent PNG on a dark theme |
   | Status | loading · error · disabled · selected · pending forever |
   | Container | 320px · squeezed in a narrow column · very wide (1920px+) |
3. **Render them side by side on a scratch route**, using the project's own tooling:
   - Storybook story, if the project has Storybook (preferred).
   - Next.js: `app/__stress/page.tsx`.
   - Vite/React Router: a route `/__stress`.
   - Anything else: a static page that imports the component.

   Use real components and real tokens, never re-implemented markup.
4. **Audit the scratch page** with `render_audit.mjs` (all viewports, both themes). Then run the region scan from [visual scan](visual-scan.md) on its tiles.
5. **Clean up.** Delete the scratch route, or leave it behind a dev-only flag if the user wants to keep it. Never commit it to production paths unasked.

## 3. State workbench: every reachable state, one switch

Screens have more states than anyone opens by hand: first run, empty, partial, loading, refreshing, error, offline, no permission, trial ended, feature flag off, a very long account name.

1. **List the states from the code**, not from memory:
   - data fetching (loading, error, empty, partial, stale);
   - auth and role;
   - plan/flags;
   - form states (pristine, invalid, submitting, submitted, server error).
2. **Make each state reachable through a URL** in development: `?__state=empty`, `?__state=error`, … Use mock data shaped like the product, not "John Doe / Lorem / 99.99%". Hold pending states still (never resolve them on a timer), so they can be inspected and screenshotted.
3. **Audit every state** in one call:
   ```bash
   node <skill>/scripts/render_audit.mjs http://localhost:3000/invoices --states empty,loading,error,partial --stress
   ```
   Run names get a state prefix (`empty-375x812-dark`), so the report shows which state breaks where. If the project already uses another query parameter for states, pass it with `--state-param mock`.
4. **Check that skeletons match the loaded layout.** Compare the `loading` and loaded tiles at the same position. A skeleton with different line counts, heights or spacing causes a visible jump.

If the project can't expose states by URL, drive the browser to each state, run the audit on that page, and say which states you could not reach.

## 4. Variants on one axis (build mode, or when the user is unsure)

When something looks generic or "fine but flat", one more round of polish rarely helps. Comparing real alternatives does.
- Make **3 variants that each take a different position on a single axis**: structure (list vs cards vs table), density (compact vs comfortable), emphasis (what is primary), type (scale contrast), or voice (copy).
- Show them in the real page behind a switch (`?__variant=a|b|c`). Every variant meets the same accessibility floor and uses the same tokens.
- Describe each one's trade-off in one line. Do not pick a favourite before the user has looked.
- Remove the losers afterwards.

## Report
For every finding, say which scenario, state and run produced it ("only with 0 items", "only in `-pseudo` at 375px"). List the states and scenarios you rendered and the ones you could not reach.
