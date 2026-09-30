# Layout resilience, loading and media

Use when a screen has to survive real devices and real data: small and large screens, rotation, the keyboard, large text, slow networks and missing images. These bugs rarely appear on the one simulator and sample data used during development.

## Layout resilience

| Risk | Symptom | Web | SwiftUI | Compose |
| --- | --- | --- | --- | --- |
| Safe areas | Content or buttons under the notch, Dynamic Island or home indicator; bottom CTA hugging the edge | `padding-bottom: env(safe-area-inset-bottom)` + `viewport-fit=cover` | Respect safe areas by default; use `.ignoresSafeArea()` only for backgrounds; bottom bars with `.safeAreaInset(edge: .bottom)` | `WindowInsets.safeDrawing` / `Modifier.windowInsetsPadding(...)`; edge-to-edge with insets applied |
| Keyboard | Focused field or submit button hidden under the keyboard | `100dvh` not `100vh`; `scrollIntoView` on focus; `interactive-widget=resizes-content` where supported | Keep forms in a `ScrollView`; `.scrollDismissesKeyboard(.interactively)`; `@FocusState` + `ScrollViewReader` to reveal the focused field; don't `ignoresSafeArea(.keyboard)` on forms | `Modifier.imePadding()`; `BringIntoViewRequester` for the focused field |
| Narrow width | Horizontal scroll, clipped buttons, overlapping text at 320px / iPhone SE / split view | Test at 320px; `min-width: 0` on flex children; `flex-wrap`; `overflow-wrap: anywhere` for long tokens | `ViewThatFits` to switch HStack → VStack; `.minimumScaleFactor` only as a last resort for short labels | `FlowRow`; `Modifier.weight` + `softWrap`; test at 320dp |
| Wide / iPad / landscape | Phone layout stretched across a tablet; lines too long to read; landscape clips the content | `max-width` on content (~65–75ch for text); responsive grid columns | Size classes (`@Environment(\.horizontalSizeClass)`); `.frame(maxWidth: 700)` for reading content; `NavigationSplitView` on regular width; test Split View and Slide Over | Window size classes; `ListDetailPaneScaffold`; test foldables |
| Large text | Titles clipped, buttons overflow, fixed-height rows cut text at accessibility sizes | Test at 200% zoom and a 24px root font; avoid fixed heights on text containers | Test at `accessibilityExtraExtraExtraLarge`; use `dynamicTypeSize.isAccessibilitySize` to switch to a vertical layout; no fixed `frame(height:)` on text | Test at 200% font scale; avoid fixed `height` on text containers |
| Clipped controls | Chip or button text cut off, or truncated mid-word, in some languages | `white-space: nowrap` only with space reserved; allow wrapping in buttons | Allow 2 lines in buttons (`.lineLimit(2)`), or `ViewThatFits`; never `.fixedSize()` in a constrained row without a fallback | `maxLines = 2` or adaptive layout |
| Long / missing data | Very long names, 0 or 10,000 items, empty optional fields leave gaps | Test extremes; hide empty optional rows | Same; don't render empty labels | Same |

Verification: render the key screens at the smallest and largest supported widths, in landscape where supported, with the keyboard open on every form, at the largest text size, and with extreme data. On a simulator, use the project's own device, and read the current content size (`xcrun simctl ui <device> content_size`) before changing it. Record and restore it, and never change it on a device another project may be using.

## Loading and media

| Risk | Symptom | Fix |
| --- | --- | --- |
| Layout shift on load | Content jumps when data or images arrive; the user taps the wrong thing | Reserve space: fixed media `aspect-ratio`, known row heights, skeletons with the same dimensions as the loaded content |
| Skeleton mismatch | Skeleton has different line counts, sizes or spacing than the real item, so there is a visible jump on swap | Build the skeleton from the real component (`.redacted(reason: .placeholder)` in SwiftUI; the same composable with placeholder data in Compose; the same CSS classes on web) |
| Spinner for everything | Whole-screen spinner hides content the user could already see; long waits with no progress | Keep existing content visible; load sections independently; show progress for long, measurable work |
| Missing / broken image | Empty box, broken-image icon, or a collapsed card | Placeholder with the same ratio (brand tint, initials or icon); `AsyncImage` phase `.failure` handled; `onError` fallback on web |
| Slow image decode | Scrolling stutters or images pop in late | Correctly sized thumbnails; lazy loading below the fold; `loading="lazy"` / `decoding="async"`; cache |
| Images without dimensions (web) | Cumulative Layout Shift | `width`/`height` attributes or CSS `aspect-ratio` on every `img` |
| Stale vs fresh | Old data shown with no hint that it is refreshing | Subtle refreshing indicator; keep content; pull-to-refresh where expected |

Verification: throttle the network (DevTools "Slow 4G", Network Link Conditioner, or an artificial delay in previews), block image requests once to see the fallbacks, and compare skeleton and loaded states in the same screenshot position.

## Report
Name the device, width, orientation, text size and network condition for each finding, because these settings don't show in a screenshot. Say which conditions you actually rendered and which you only reviewed in code.
