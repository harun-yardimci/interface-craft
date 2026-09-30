---
name: interface-craft
description: Review, improve, or build a whole interface across usability, task flow, microcopy, system states, accessibility, theming, layout resilience and visual polish. Use for broad requests like "review this screen/UX", "improve this interface", "make this form/onboarding/checkout better", "UX audit", "fix the empty/error/loading states", "check dark/light mode", "cards have different heights", "keyboard covers the button", "breaks on iPad/small screens", "inconsistent spacing/fonts", "arayüzü iyileştir", "bu ekranı incele", "dark/light mode tutarsızlıklarını denetle", "kartlar aynı boyda değil". For narrow requests prefer a narrower installed skill (design:ux-copy for copy only, make-interfaces-feel-better for visual polish, design:accessibility-review for WCAG audits, ui-compliance for HIG/Material compliance); if none is installed, handle it here with only the relevant reference. Not for backend-only work or marketing copy.
---

# Interface Craft

Infer the mode from the request; do not present a menu:
- **Review**: report actionable issues; do not edit.
- **Improve**: review, implement scoped fixes, verify.
- **Create**: build the screen or component with these principles from the start.

**Scope the scan to the request.** Broad requests ("review this screen", "improve this flow"): scan all seven dimensions below. Narrow requests ("only microcopy", "just the error states", "keep the layout"): check only those dimensions plus states directly affected by your change (e.g. a longer label must still fit and stay accessible). In both cases change only what has a real problem.

**Theme consistency is always in scope** when the product supports light and dark appearances and the task touches UI colors, surfaces, overlays or a screen review. Invisible or low-contrast text in one theme is a priority-1 accessibility issue. Use the [theming](references/theming.md) reference.

## Workflow
1. **Inspect** the interface, relevant code, design tokens, existing components, user-facing text, and the main task. For screenshots, separate what is visible from behavior you cannot see. Ask only when missing information blocks the work.
2. **Scan** the in-scope dimensions (all seven for broad work): task/flow, information & decision load, microcopy, interaction, visual craft, system states (empty/loading/error/success), accessibility. For broad reviews, walk all ten Nielsen heuristics (interaction reference).
3. **Diagnose**: each issue = observed trigger → user consequence → concrete fix. Mark hypotheses as hypotheses. Never claim conversion gains or user testing from an expert review.
4. **Prioritize**: (1) task blockers and accessibility, (2) errors, ambiguity, decision burden, (3) wording, hierarchy, consistency, (4) decorative polish. Merge overlapping findings into one fix.
   Static lead-finders (paths relative to this skill; confirm every hit visually or in code):
   - `python3 scripts/theme_audit.py <ui-source-dir>` when the product has light and dark appearances.
   - `python3 scripts/token_audit.py <ui-source-dir>` on broad reviews or "inconsistent spacing/fonts" complaints: it finds literal font sizes, off-grid spacing, one-off radii and fonts that ignore Dynamic Type.
5. **Implement** with the existing design language, tokens, components and dependencies. Before using a platform or library API, check the project's deployment target / dependency versions and confirm availability in current docs; use a compatible alternative or an availability guard when needed. When advice conflicts: user intent > accessibility > platform conventions > existing system > aesthetics. Do not add a library just for polish.
6. **Verify** proportionally. Use preview/browser/simulator and project checks when available; never claim a check you did not run. Visual work: narrow + wide layouts, long text, and **both light and dark**, including overlays (sheets, menus, alerts) and every chip/button state. For layout and loading (see [layout resilience](references/layout-resilience.md)): smallest and largest widths, landscape/iPad where supported, keyboard open on forms, largest text size, slow network and a failed image load. For repeated content (carousels, grids, lists), render the shortest and longest real items side by side and check equal heights, reserved text lines and fixed media ratios. Never change simulator or device appearance on a shared device without recording and restoring the previous value. Interaction work: keyboard/focus, loading/success/error, recovery paths.

## Platform routing
- **Web (HTML/CSS/React/Tailwind)**: visual-craft values are the starting point; existing tokens and observed rendering win.
- **Native iOS (SwiftUI/UIKit) / Android (Compose)**: use the SwiftUI/Compose column in visual-craft; follow HIG/Material 3 over web values. For component-level platform compliance, also load `ui-compliance` if available; otherwise apply HIG/Material 3 directly.
- If `make-interfaces-feel-better` is installed and the task is heavy on web animation/surface code, load its reference files for full code samples.

## Reference routing (load only what the task needs)
- [Visual craft](references/visual-craft.md): design-token consistency (`scripts/token_audit.py`), concrete values for radius, shadows, typography, motion, hit areas, performance - web and native.
- [Interaction and feedback](references/interaction-and-feedback.md): ten Nielsen heuristics, forms, navigation, states, recovery, help.
- [Cognitive principles](references/cognitive-principles.md): Laws of UX - choice, memory, grouping, progress, attention.
- [Microcopy](references/microcopy.md): labels, buttons, helper text, errors, empty states, confirmations, localization (incl. Turkish).
- [Theming](references/theming.md): light/dark consistency - fixed vs adaptive color pairing, overlays, assets, audit procedure, `scripts/theme_audit.py`.
- [Layout resilience](references/layout-resilience.md): safe areas, keyboard, narrow/wide/iPad/landscape, large text, clipped controls, extreme data; loading states, skeleton parity, layout shift, image fallbacks.
- [Accessibility](references/accessibility.md): semantics, keyboard, focus, contrast, targets, reduced motion, screen readers.

## Hard rules
- Every change must solve a named problem.
- Never: fake progress, false urgency, guilt-based opt-outs, hidden costs, hover-only actions, placeholder-as-label, arbitrary "max 7 items" menus, animating everything.
- Never pair a fixed color with an adaptive one on the same surface (e.g. `Color.white` background with a dynamic text token, `bg-white` with `text-foreground`). Background and foreground come from the same theme source.
- Never trade readable labels, discoverability, user control or accessibility for decoration.
- Preserve product claims, prices and business behavior unless changing them is in scope.
- For library/framework API details, use the environment's documentation workflow (e.g. Context7); do not rely on remembered syntax.

## Output
Lead with the outcome in one or two sentences. Respond in the user's language; keep the interface's existing locale unless asked.

For substantial reviews or edits, one table sorted by priority. Omit dimensions with no findings - never pad. Then list verification actually performed and remaining limitations.

Example (review of a sign-up form):

| # | Priority | Location | Before | After | User impact |
| --- | --- | --- | --- | --- | --- |
| 1 | Blocker | `SignUp.tsx:42` | Submit stays enabled while pending; repeated taps send repeated requests | Disable during request, show spinner + "Hesap oluşturuluyor…" | Reduces repeat submissions while pending; visible status. Not verified: whether the backend deduplicates (idempotency) - flag for follow-up |
| 2 | A11y | `SignUp.tsx:18` | Email field has placeholder only, no label | Persistent `<label>` "E-posta"; placeholder `ornek@alanadi.com` | Label stays visible while typing; screen readers announce it |
| 3 | Error | `validation.ts:9` | "Invalid input" | "E-posta adresinde @ işareti eksik." next to the field | User knows exactly what to fix |
| 4 | A11y (Dark) | `FilterSheet.swift:120` | Sheet uses `Color(hex: "F8FAFC")` and chips `Color.white`, but text uses the adaptive `ink` token → white on white in dark mode | Surface and chip backgrounds use adaptive surface tokens; verified in both themes | Chip labels and section titles readable in dark mode |
| 5 | Polish | `Card.tsx:7` | `rounded-xl` on card and inner button with `p-2` | Card `rounded-2xl` (8 + 8), button `rounded-lg` | Nested corners look concentric |

For a small copy edit: the revised text plus one line of reasoning is enough.
