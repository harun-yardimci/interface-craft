# Accessibility

A design and verification checklist, not a compliance certificate. Baseline is [WCAG 2.2](https://www.w3.org/TR/WCAG22/) AA plus the target platform's guidance. If an exact requirement is decisive (legal/compliance work), confirm it against the current official text.

## Key thresholds (WCAG 2.2 AA unless noted)
| Check | Threshold |
| --- | --- |
| Body text contrast | 4.5:1 (large text ≥ 24px, or ≥ 18.66px bold: 3:1) |
| Non-text contrast (input borders, icons, focus rings) | 3:1 against adjacent colors |
| Target size | AA minimum 24×24 CSS px (or enough spacing); AAA/enhanced 44×44. Platform: iOS 44pt, Android 48dp |
| Focus | Visible indicator; focused element not fully hidden by sticky headers/footers |
| Reflow / zoom | Works at 320 CSS px width and 200% text zoom without two-axis scrolling or clipped labels |
| Motion | Honor `prefers-reduced-motion`; nothing flashes more than 3 times per second |

## Checks
- **Semantics**: native controls (`button`, `a`, `input`, `select`) with correct name, role, state. No clickable `div`s when a button or link fits.
- **Keyboard**: every action reachable; logical focus order; visible focus. Modals: focus moves in, stays inside, `Esc` closes, focus returns to the trigger.
- **Forms**: every field has a programmatic label; helper text and errors linked via `aria-describedby`; required state not shown by color alone; errors announced and focus moved to the first invalid field on submit.
- **Color**: never the sole carrier of meaning (errors, status, selection). Shadow-only boundaries vanish in forced-colors mode - keep a transparent border/outline.
- **Dynamic status**: announce important async results with a polite live region (`role="status"`) without stealing focus; do not announce every keystroke-level update.
- **Images and icons**: informative images get useful alt text; decorative ones `alt=""`/hidden. Icon-only buttons get a name that describes the action ("Sil", not "çöp kutusu ikonu").
- **Native**: iOS - VoiceOver labels/traits, Dynamic Type up to accessibility sizes, Reduce Motion. Android - `contentDescription`, TalkBack order, 200% font scale.

## Priority rule
Meaningful labels, visible controls and working navigation beat minimalism and motion advice. Report which checks you actually ran (automated tool, keyboard pass, screen reader) and which you could not; automated checks alone do not prove usability or conformance.
