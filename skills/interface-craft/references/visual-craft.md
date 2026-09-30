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
Hover, active, focus-visible, disabled and selected states render without layout shift; both themes checked; narrow and wide widths checked; long/translated text does not clip. Report only what you actually inspected.
