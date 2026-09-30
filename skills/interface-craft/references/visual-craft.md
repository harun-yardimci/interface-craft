# Visual craft

Distilled from the make-interfaces-feel-better skill (typography, surfaces, animations, performance). Self-contained. The values below are **starting defaults**, not rules: the project's existing tokens and design language, accessibility needs, and what the rendered result actually looks like all take precedence. Adjust when inspection shows a better fit.

## Surfaces

**Concentric radius** - nested rounded surfaces: `outer = inner + padding`.
```css
.card  { border-radius: 20px; padding: 8px; } /* 12 + 8 */
.inner { border-radius: 12px; }
```
Tailwind: `rounded-2xl p-2` → child `rounded-lg` (16 − 8). If padding > 24px, treat layers as separate surfaces and choose radii independently.

**Optical alignment** - icon+text buttons: icon-side padding = text-side − 2px (`pl-4 pr-3.5`). Play triangles and other asymmetric icons: shift ~1–2px toward the point, or fix the SVG. Inspect the result.

**Shadows over borders** for cards/buttons that need depth (borders stay for dividers and inputs):
```css
:root {
  --shadow-border:       0 0 0 1px rgba(0,0,0,.06), 0 1px 2px -1px rgba(0,0,0,.06), 0 2px 4px 0 rgba(0,0,0,.04);
  --shadow-border-hover: 0 0 0 1px rgba(0,0,0,.08), 0 1px 2px -1px rgba(0,0,0,.08), 0 2px 4px 0 rgba(0,0,0,.06);
}
.dark {
  --shadow-border:       0 0 0 1px rgba(255,255,255,.08);
  --shadow-border-hover: 0 0 0 1px rgba(255,255,255,.13);
}
.card { box-shadow: var(--shadow-border); transition: box-shadow 150ms ease-out; }
```
In forced-colors / high-contrast mode shadows disappear - keep a transparent `outline` or border so the boundary survives.

**Image outlines** - `outline: 1px solid rgba(0,0,0,.1); outline-offset: -1px;` (dark: `rgba(255,255,255,.1)`). Start with pure black/white; tinted neutrals (slate/zinc) often read as dirt on the image edge - use them only if they look right in both themes. Skip for intentional edge-to-edge art.

**Hit areas** - web: at least 40×40px, 44×44 preferred; extend small controls with a pseudo-element; never let two hit areas overlap. iOS: 44×44pt. Android: 48×48dp.

## Typography
- Headings: `text-wrap: balance`. Short/medium body text: `text-wrap: pretty`. Skip both for very long text.
- macOS crispness: `-webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale;` on the root.
- Changing numbers (counters, prices, timers, table columns): `font-variant-numeric: tabular-nums`. Does not fix shifts from changing digit count - reserve width if needed.
- Keep a consistent weight scale and a comfortable measure (~45–75 characters for body text).

## Motion
| Pattern | Values |
| --- | --- |
| Interactive state change | CSS transitions (interruptible), 150–200ms `ease-out`. Keyframes only for one-shot sequences. |
| Enter | Split into semantic groups; stagger ~100ms (titles by word ~80ms). Each: opacity 0→1, `translateY(12px)`→0, optional `blur(4px)`→0, ~300–400ms. |
| Exit | Softer and shorter than enter: ~150ms `ease-in`, small fixed `translateY(-12px)`, never full height. |
| Icon swap | opacity 0→1, scale 0.25→1, blur 4px→0. Motion lib: `{ type: "spring", duration: 0.3, bounce: 0 }`. No lib: keep both icons in DOM, cross-fade 300ms `cubic-bezier(0.2, 0, 0, 1)`. Accessible name stays stable. |
| Press | `scale(0.96)`, 150ms; below ~0.95 usually feels exaggerated. Allow opt-out (`static` prop) where distracting; not on disabled controls. |
| First render | No incidental mount animation: `AnimatePresence initial={false}`. Check it does not kill intentional entrances. |
| Reduced motion | Under `prefers-reduced-motion: reduce`, drop translate/scale/blur; keep instant or opacity-only feedback. |

## Design-token consistency
Screens feel "off" when each one invents its own sizes. Examples: 11.5, 13, 15 and 17pt text on one screen; `padding(14)` next to `padding(16)`; radii of 9, 10, 12 and 14.
- Run `scripts/token_audit.py <ui-source-dir>`. It lists how many distinct literal font sizes, spacing values and radii the code uses, the spacing values off the grid (`--grid 4` by default, `--grid 2` for half-step systems), one-off values, and SwiftUI `.system(size:)` fonts that ignore Dynamic Type.
- Map each literal to the **existing** token or text style (`AppTheme.Space.m`, `.font(.headline)`, `var(--space-3)`, `MaterialTheme.typography.titleMedium`). Add a new token only when a real gap is confirmed, never one per literal.
- A healthy scale is small, typically ~6–8 text styles, ~6–10 spacing steps and ~3–5 radii. Literals inside the token definition file itself are expected.
- Typography should scale with the user's text size: text styles or `Font.custom(_:size:relativeTo:)` on iOS, `sp` on Android, `rem` on the web.

## Repeated content: rows, grids, carousels
Items shown side by side (cards in a carousel, grid cells, list rows with media) must share a **consistent shape** whatever their content. Heights that jump with title length, or a title truncated in one card while its neighbor is a line shorter, read as broken layout.

| Rule | Web | SwiftUI | Compose |
| --- | --- | --- | --- |
| Reserve text lines: a clamped title always takes N lines, even when shorter | `line-clamp: 2` + `min-height: calc(2 * 1lh)` (or `2lh`) | `.lineLimit(2, reservesSpace: true)` (iOS 16+; older: fixed `frame(height:)` from the font's line height) | `Text(maxLines = 2, minLines = 2, overflow = TextOverflow.Ellipsis)` |
| Equal height in a row: stretch cards to the tallest | Grid `grid-auto-rows: 1fr`, or flex `align-items: stretch` + card `height: 100%; display: flex; flex-direction: column` | Non-lazy `HStack` + `.fixedSize(horizontal: false, vertical: true)` on the stack, `.frame(maxHeight: .infinity, alignment: .top)` on each card. `LazyHStack` can't measure siblings, so reserve lines instead | `Row(Modifier.height(IntrinsicSize.Min))` + `Modifier.fillMaxHeight()` on cards (non-lazy); `LazyRow`: reserve lines |
| Fixed media ratio | `aspect-ratio: 16 / 10; object-fit: cover` | `.aspectRatio(16/10, contentMode: .fill).clipped()` | `Modifier.aspectRatio(16f / 10f)` + `ContentScale.Crop` |
| Pin secondary content to the bottom | `margin-top: auto` on the footer | `Spacer(minLength: 0)` before the footer | `Spacer(Modifier.weight(1f))` |

Guardrails:
- **Truncation must not lose information.** The full title stays reachable: accessibility label, tooltip or detail view. Prefer shorter copy over heavy clamping.
- **Accessibility text sizes win.** At large Dynamic Type or 200% zoom, allow more lines or switch to a vertical layout. Never clip text to preserve equal heights.
- **Test with extreme content:** the shortest and longest real titles side by side, a missing image, a long translation (Turkish and German run long), and the largest text size. Sample data with similar-length titles hides this bug.

## Performance
- Never `transition: all`. Name properties: `transition-property: scale, opacity`. Tailwind: `transition-transform` or `transition-[scale,opacity,filter]`.
- `will-change` only for `transform`/`opacity`/`filter`, only after seeing first-frame stutter. Never `will-change: all`.
- Reserve media dimensions to prevent layout shift; hover/active/focus/selected states must not change layout.

## Native equivalents (SwiftUI / Jetpack Compose)
Several APIs below need recent OS or library versions (e.g. `ConcentricRectangle` is iOS 26+; symbol/numeric content transitions and named springs like `.snappy` are newer SwiftUI APIs). Check the project's deployment target and Compose/Material versions, confirm availability in current docs (Context7/Apple/Android docs), and use `if #available` guards or older equivalents (`RoundedRectangle(style: .continuous)`, `.spring(response:dampingFraction:)`, opacity cross-fades) when needed.

| Web technique | SwiftUI | Compose |
| --- | --- | --- |
| Concentric radius | `RoundedRectangle(cornerRadius:, style: .continuous)`; outer = inner + padding; iOS 26+: `ConcentricRectangle` / `.containerShape` | `RoundedCornerShape(outer = inner + padding)` |
| Layered shadow | Prefer system materials and grouped backgrounds; if needed `.shadow(color: .black.opacity(0.06), radius: 2, y: 1)` - subtle, one or two layers | `Modifier.shadow(elevation)` / M3 tonal elevation over custom shadows |
| Tabular numbers | `.monospacedDigit()`; animate with `.contentTransition(.numericText())` | `fontFeatureSettings = "tnum"` |
| Press scale | `ButtonStyle` with `.scaleEffect(configuration.isPressed ? 0.96 : 1)` + `.animation(.snappy)` | `interactionSource` + `animateFloatAsState(if (pressed) 0.96f else 1f)` |
| Icon swap | `.contentTransition(.symbolEffect(.replace))` on SF Symbols | `AnimatedContent` with fade + scale |
| Enter stagger | `.transition(.opacity.combined(with: .offset(y: 12)))` with incremental `.delay` | `AnimatedVisibility` with staggered `delayMillis` |
| Interruptible motion | Springs (`.snappy`, `.smooth`) are interruptible by default | `animate*AsState` / `spring()` retargets automatically |
| Reduced motion | `@Environment(\.accessibilityReduceMotion)` | Check animator duration scale / reduce-motion setting |
| Text scaling | Dynamic Type text styles (`.font(.body)`), test at accessibility sizes | `sp` units, test at 200% font scale |
| Hit area | `.frame(minWidth: 44, minHeight: 44)` + `.contentShape(Rectangle())` | `Modifier.minimumInteractiveComponentSize()` (48dp) |

Font smoothing, `text-wrap`, `will-change` and `transition-property` have no native equivalent - skip them on native.

## Checklist before reporting visual work
Hover, active, focus-visible, disabled and selected states render without layout shift; both themes checked; narrow and wide widths checked; long/translated text does not clip; repeated items (cards, grid cells, rows) keep equal height and media ratio with the shortest and longest real content side by side. Report only what you actually inspected.
