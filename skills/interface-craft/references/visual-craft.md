# Visual craft

Distilled from make-interfaces-feel-better and jakubkrehel/skills (Jakub Krehel), emilkowalski/skills (Emil Kowalski) and Impeccable (Paul Bakaus), paraphrased and reconciled; see NOTICE. Self-contained. The values below are **starting defaults**, not rules: the project's existing tokens and design language, accessibility needs, and what the rendered result actually looks like all take precedence. Adjust when inspection shows a better fit.

## Surfaces

**Concentric radius** - nested rounded surfaces: `outer = inner + padding`.
```css
.card  { border-radius: 20px; padding: 8px; } /* 12 + 8 */
.inner { border-radius: 12px; }
```
Tailwind: `rounded-2xl p-2` → child `rounded-lg` (16 − 8). If padding > 24px, treat layers as separate surfaces and choose radii independently.

**Optical alignment** - icon+text buttons: icon-side padding = text-side − 2px (`pl-4 pr-3.5`). Play triangles and other asymmetric icons: shift ~1–2px toward the point, or fix the SVG. Inspect the result.

**Separating surfaces: tone, line, shadow, each with its own job.**
| Need | Use | Avoid |
| --- | --- | --- |
| Regions at rest (page / sidebar / panel / card) | A **tone step**: the surface 1 step lighter or darker than its parent (dark: surfaces step up ~3-5% lightness per level, e.g. OKLCH L 0.15 / 0.19 / 0.23) | Big soft shadows on cards that never move; borders on every box |
| Boundaries people must find (inputs, selects, table cells, dividers, dense data UI) | A **1px line** from a border/outline token; input boundaries need 3:1 against the surface (WCAG 1.4.11), which a tone step alone rarely reaches | Removing field borders for "clean" looks |
| Things above the content (menu, popover, dialog, toast, dragged item, a bar that sticks once you scroll) | **Shadow = elevation.** Bigger offset/blur = higher; dark mode: lighter surface + 1px light ring, because black shadows vanish on dark | Shadow on resting elements as decoration |
| A resting card that needs a crisp edge on a same-tone background | A shadow-as-border ring (one 1px spread layer + at most a tiny contact shadow) | A 1px border **plus** a wide shadow on the same element; hard offset shadows; colored side stripes thicker than 1px |

Shadow-as-border ring, when you need one:
```css
:root { --ring: 0 0 0 1px rgb(0 0 0 / .06), 0 1px 2px -1px rgb(0 0 0 / .06), 0 2px 4px 0 rgb(0 0 0 / .04); }
.dark { --ring: 0 0 0 1px rgb(255 255 255 / .08); }
.card { box-shadow: var(--ring); }
```
In forced-colors / high-contrast mode shadows disappear - keep a transparent `outline` or border so the boundary survives.

**Image outlines** - `outline: 1px solid rgba(0,0,0,.1); outline-offset: -1px;` (dark: `rgba(255,255,255,.1)`). Start with pure black/white; tinted neutrals (slate/zinc) often read as dirt on the image edge - use them only if they look right in both themes. Skip for intentional edge-to-edge art.

**Hit areas** - web: at least 40×40px, 44×44 preferred; extend small controls with a pseudo-element; never let two hit areas overlap. iOS: 44×44pt. Android: 48×48dp.

## Typography
- Headings: `text-wrap: balance`. Short/medium body text: `text-wrap: pretty`. Skip both for very long text.
- macOS crispness: `-webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale;` on the root.
- Changing numbers (counters, prices, timers, table columns): `font-variant-numeric: tabular-nums`. Does not fix shifts from changing digit count - reserve width if needed.
- Keep a consistent weight scale and a comfortable measure (~45–75 characters for body text).
- **Line height by role** (unitless): display ~1.1, headings 1.2–1.3, body 1.5–1.6; anything that wraps to 3+ lines needs ≥ 1.4. Light text on dark: +0.05.
- **Tracking**: headings ≥ 24px -0.01 to -0.02em (never tighter than -0.04em); small uppercase labels (≤ 14px) +0.05em.
- **Weight**: ≥ 400 below 18px; thin weights (100–300) only at ≥ 28px.
- **Size floors**: body 16px (dense app UI 14px), captions 13px, rarely anything below 12px. **Inputs ≥ 16px on mobile web** or iOS Safari zooms the page on focus.
- **Scale**: ~5–7 sizes on one ratio (1.2–1.333 for apps, up to 1.5 for marketing); 2–3 sizes do the visible work on one screen. Similar-but-different sizes (13 and 14px side by side) read as mistakes.
- `text-wrap: balance` is ignored past ~6 lines - headings only. `text-box: trim-both cap alphabetic` centres text optically in buttons and badges where supported.

## Spacing and grouping
- **Gap between groups ≥ 2× the gap inside a group** (8px inside → 16px+ between). A section break that is no bigger than an item gap makes the page read as one list.
- **More space above a heading than below it**: the heading belongs to what follows.
- Inner padding ≤ the space around the component.
- Controls: ~12px between bordered controls; ~24px between borderless glyph buttons.
- Scroll hints: let the next item peek 16–32px past a horizontal scroll edge.
- Sticky header: `scroll-padding-top` / `scroll-margin-top` equal to its height, so anchors and focused fields do not land under it.

## Motion
Motion explains (where something came from, what changed) and gives feedback. "It looks nice" is not a reason for something people see 50 times a day.

**1. Decide whether to animate (frequency gate)**
| How often the user sees it | Motion |
| --- | --- |
| Constantly (command palette, keyboard shortcuts, typing, list navigation, tab switches in a tool) | None, or ≤ 150ms opacity/color only. **Never animate actions started from the keyboard.** |
| Often (hover, toggles, menus) | Short and subtle, 100–200ms |
| Occasionally (dialogs, drawers, toasts, page sections) | Standard enter/exit |
| Rarely (onboarding, success moments, empty-state first run) | Room for one expressive moment |

**2. Easing.** Never `ease-in` in UI: it starts slow, so the response to a click shows up late (50ms into a 150ms move, CSS `ease-in` has covered ~16% of the distance; the strong ease-out below ~88%). Built-in CSS keywords are weak; use tokens:
```css
:root {
  --ease-out: cubic-bezier(0.23, 1, 0.32, 1);      /* enter AND exit, presses, popovers */
  --ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);  /* things moving/morphing on screen */
  --ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);   /* sheets and drawers (iOS-like) */
}
```
Constant motion (marquee, progress, spinners): `linear`. No bounce/elastic curves on product UI; springs with bounce 0.1–0.3 only for drag-release or playful surfaces.

**3. Durations by component** (keep UI motion under ~300ms; exits ~70–75% of the enter)
| Element | Enter | Notes |
| --- | --- | --- |
| Press feedback | 100–160ms | `scale(0.97)` (0.95–0.98) on `:active`, `transform 160ms var(--ease-out)`; not on disabled controls |
| Tooltip / small popover | 125–200ms | Start at `scale(0.97)` + opacity 0. Once one tooltip is open, neighbours open instantly with no animation |
| Dropdown / menu | 150–250ms | Scale from the trigger: `transform-origin: var(--radix-dropdown-menu-content-transform-origin)` (Radix/Base UI expose this) |
| Dialog / drawer | 200–500ms | Dialogs stay centred (origin centre); drawers `translateY(100%)` with `--ease-drawer` |
| List / section entrance | 300ms each | Stagger **30–80ms** per item, `translateY(8px)`→0; never block input while it plays; cap total stagger |

- **Exit**: the same strong ease-out, shorter (≈150ms for a 200ms enter), smaller travel (fixed ~8–12px, never full height), opacity + optional `blur(2-4px)`.
- **Never start from `scale(0)`**: real objects do not appear from nothing. Enter from `scale(0.95)` + opacity 0.
- **Interruptible**: anything that can toggle quickly uses CSS transitions or springs (they retarget mid-way); keyframes restart from zero and jump. Keyframes only for one-shot sequences.
- **Icon swap**: opacity 0→1, scale 0.25→1, blur 4px→0; spring `{ duration: 0.3, bounce: 0 }` or 300ms `cubic-bezier(0.2, 0, 0, 1)`; both icons stay in the DOM; the accessible name stays stable.
- **First render**: no incidental mount animation (`AnimatePresence initial={false}`); enter animations via `@starting-style` (fallback: a `data-mounted` attribute).
- **Hover motion** only under `@media (hover: hover) and (pointer: fine)`; touch devices get stuck hover states otherwise.
- **Theme switch**: disable transitions while toggling the theme (add a class that sets `transition: none` for one frame), or every color animates.
- **Reduced motion** means gentler, not nothing: keep opacity and color changes, drop movement, scale and parallax.
- **Review motion slowed down** (DevTools animations panel at 10-25%, or step frame by frame) and on a mid-range phone, not only on a fast laptop.

**Gestures (drawers, sheets, swipe-to-dismiss)**
- Dismiss on distance **or** velocity: e.g. ~25% of the sheet height, or a flick faster than ~0.4 px/ms (toasts: ~45px or 0.11 px/ms).
- Past the limit, damp instead of stopping hard (logarithmic friction).
- Capture the pointer once a drag starts; ignore extra touches; do not start a drag while text is selected, right after opening (~500ms) or right after the content scrolled.
- Toasts: pause timers while the tab is hidden and while hovered; keep a hover bridge between stacked toasts so expanding them does not lose hover.

## Design-token consistency
Screens feel "off" when each one invents its own sizes. Examples: 11.5, 13, 15 and 17pt text on one screen; `padding(14)` next to `padding(16)`; radii of 9, 10, 12 and 14.
- Run `scripts/token_audit.py <ui-source-dir>`. It lists how many distinct literal font sizes, spacing values and radii the code uses, the spacing values off the grid (`--grid 4` by default, `--grid 2` for half-step systems), one-off values, and SwiftUI `.system(size:)` fonts that ignore Dynamic Type.
- Map each literal to the **existing** token or text style (`AppTheme.Space.m`, `.font(.headline)`, `var(--space-3)`, `MaterialTheme.typography.titleMedium`). Add a new token only when a real gap is confirmed, never one per literal.
- A healthy scale is small, typically ~6–8 text styles, ~6–10 spacing steps and ~3–5 radii. Literals inside the token definition file itself are expected.
- Typography should scale with the user's text size: text styles or `Font.custom(_:size:relativeTo:)` on iOS, `sp` on Android, `rem` on the web.

## Repeated content: rows, grids, carousels
**Comparable cards shown side by side** (a carousel, one grid row, a row of plans or products) should share a **consistent shape** whatever their content. Heights that jump with title length, or a title truncated in one card while its neighbor is a line shorter, read as broken layout.

**Vertical lists are different:** rows with variable content (messages, notifications, search results) may keep their natural height. Clamping them to equal heights hides information. In lists, keep media size, leading alignment and spacing consistent instead.

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
- Animate `transform` and `opacity` by default. Animate a `filter: drop-shadow()` rather than `box-shadow`; keep animated blur under ~20px (expensive, especially in Safari).
- Per-frame updates (drag, pointer tracking): write to `element.style` through a ref, not React state; do not drive them through an inherited CSS variable, because every descendant recalculates styles.
- Framer Motion: the shorthand `x`/`y`/`scale` props run on the main thread; a full `transform` string can be hardware-accelerated. Motion that runs during navigation or data loading belongs in CSS/WAAPI, which survive a busy main thread.
- Frame budget is ~8ms on 120Hz screens; judge smoothness on a mid-range phone.
- Accordions: animate `grid-template-rows: 0fr → 1fr` instead of `height`.

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
Motion passes the frequency gate and uses no ease-in; hover, active, focus-visible, disabled and selected states render without layout shift; both themes checked; narrow and wide widths checked; long/translated text does not clip; repeated items (cards, grid cells, rows) keep equal height and media ratio with the shortest and longest real content side by side. Report only what you actually inspected.
