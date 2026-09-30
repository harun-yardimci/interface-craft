# Theming: light / dark consistency

Use for any UI review or change on a product that supports more than one appearance. A screen that looks right in one theme proves nothing about the other. Most theme bugs come from mixing **fixed** colors with **adaptive** ones, and they show up in overlays that are rarely opened in both themes.

Platform guidance: [Apple HIG: Dark Mode](https://developer.apple.com/design/human-interface-guidelines/dark-mode) · [Material 3: color roles](https://m3.material.io/styles/color/roles) · [Android: dark theme](https://developer.android.com/develop/ui/views/theming/darktheme) · MDN [`color-scheme`](https://developer.mozilla.org/en-US/docs/Web/CSS/color-scheme) and [`prefers-color-scheme`](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-color-scheme).

## The core rule: pair roles; verify any mix in both themes
By default, a foreground comes from the **same theme source** as the background it sits on:
- Adaptive background + adaptive "on" color: `surface`/`onSurface`, `systemBackground`/`label`, `bg-background`/`text-foreground`.
- Fixed background + fixed foreground, but only for deliberately theme-independent surfaces such as a brand-colored button or a photo overlay.
- **Risky:** a fixed background with an adaptive foreground, or the other way round. One side changes with the theme and the other doesn't, so contrast holds in one theme and can collapse in the other. Example: a sheet hardcoded to `.white` whose text uses `.primary` or `.secondary`. In dark mode the text turns white on white and disappears.
- A mix is acceptable only when its contrast is **verified in both themes** (4.5:1 for text, 3:1 for icons and borders). An example is a mid-tone brand surface whose adaptive text happens to pass in both. Even then, prefer pairing roles, because a later token change can break it silently.

## Common failure patterns
| Pattern | Symptom | Fix |
| --- | --- | --- |
| Hardcoded container, semantic text (`.background(.white)` + `.foregroundStyle(.secondary)`; `bg-white` + `text-muted-foreground`) | Unselected chips, labels and placeholders vanish in dark mode | Use a semantic surface (`Color(.systemBackground)`, `.regularMaterial`, `MaterialTheme.colorScheme.surface`, a `bg-card` token) |
| Semantic container, hardcoded text (`Color.black`, `#111`) | Text disappears in dark mode | Use the paired "on" role |
| Sheet / popover / menu / alert with custom background (`.presentationBackground(.white)`, custom dialog `Surface(color = Color.White)`) | The overlay stays light inside a dark app | Semantic presentation background; test every overlay in both themes |
| Asset color without a dark variant (Xcode color set with only "Any", missing `values-night`, a CSS variable missing under `.dark`) | One element stays light | Add the dark appearance for every color token |
| Opacity-based states (`white.opacity(0.3)` for disabled or unselected) | Invisible on light surfaces, or too loud on dark | Use role-based disabled and secondary colors, and check contrast in both themes |
| Borders and dividers hardcoded (`#e5e5e5`, `Color.gray.opacity(0.2)`) | Borders vanish or glare in one theme | Use separator/outline tokens (`Color(.separator)`, `outlineVariant`, `border-border`) |
| Shadow-only elevation | Cards merge into the background in dark mode | Dark: a subtle light ring or tonal elevation instead of a black shadow |
| Icons, SVGs and images with a fixed fill, or transparent PNGs with dark artwork | Icons disappear on dark surfaces | Template/`currentColor` icons, SF Symbols with semantic tint, dark-specific assets |
| Local `colorScheme` overrides (`.preferredColorScheme`, `.environment(\.colorScheme, .light)`, a `.light` class on a subtree) | Part of the screen ignores the system setting | Remove the override, or apply it to the whole scene deliberately |
| Web: no `color-scheme` declaration | Native inputs, selects, scrollbars and autofill stay light in dark mode | `:root { color-scheme: light dark; }` or `<meta name="color-scheme" content="light dark">` |
| Web: `dark:` variants only on some elements; toggle mode vs media query mismatch | Mixed panels after the user toggles the theme | One strategy (class or media); tokens rather than per-element `dark:` classes |
| Status bar / system UI style fixed | Unreadable status bar in one theme | Let the system choose, or set it per theme |
| Brand color reused as text on dark | Blue links or accents fail contrast on dark surfaces | Use a lighter tone of the brand color for dark (`primary` role per theme) |

## How to audit
1. **Static scan first.** Run `scripts/theme_audit.py <path>` if Python is available. It lists hardcoded colors and fixed-vs-adaptive pairings per platform (SwiftUI/UIKit, Compose/XML, CSS/Tailwind/JSX). Treat hits as leads, not verdicts: intentional brand surfaces are fine when their foreground is fixed too.
2. **Render both themes.** Check the same screen and state side by side:
   - Web: emulate `prefers-color-scheme` (Playwright `emulateMedia({ colorScheme })`, DevTools rendering) and also the app's own theme toggle if it has one.
   - SwiftUI: previews or snapshot tests with `.preferredColorScheme(.light/.dark)` on the **root** of the preview. On a simulator, use the project's own device. `xcrun simctl ui <device> appearance` with no argument reads the current value. Record it before changing it and restore it afterwards; never change appearance on a device another project may be using.
   - Compose: `@Preview(uiMode = Configuration.UI_MODE_NIGHT_YES)` next to the light preview; screenshot tests for both.
3. **Cover the rarely opened places:** sheets, filters, popovers, menus, alerts, toasts, pickers, keyboards and accessory bars, empty/error/loading states, skeletons, onboarding, paywalls, widgets, emails and web views.
4. **Every state in both themes:** default, selected, unselected, pressed, disabled, placeholder, error and focus. Text needs 4.5:1 contrast, and borders, icons and focus rings need 3:1, **in each theme**.
5. **Report with a theme column** (Light / Dark / Both), and say which themes and states you actually rendered.

## Prevent recurrence
- Keep all colors in one token source with light and dark values. Components reference tokens, never hex values or `.white`/`.black`.
- Add a lint or CI check, such as the static scan or a custom lint rule, for new hardcoded colors in UI code.
- Snapshot-test key screens and overlays in both themes.
