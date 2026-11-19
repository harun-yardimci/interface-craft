# Interaction and feedback

Attribution: Jakob Nielsen, [10 Usability Heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/). The ten named heuristics below are the coverage framework; implementation guidance is adapted for this skill rather than copied examples.

| Heuristic | Implementation prompt |
| --- | --- |
| Visibility of system status | Can the user distinguish pending, completed and failed actions? |
| Match between system and real world | Do terms and control mappings match the audience's understanding? |
| User control and freedom | Can an accidental action be escaped or reversed? |
| Consistency and standards | Do equivalent controls and terms behave consistently? |
| Error prevention | Which expensive mistake can validation or a safe default prevent? |
| Recognition rather than recall | Can needed information stay visible at the decision point? |
| Flexibility and efficiency of use | Are frequent tasks efficient without obscuring the ordinary path? |
| Aesthetic and minimalist design | Which elements compete with the main task without helping it? |
| Error diagnosis and recovery | Does the error offer an achievable next action? |
| Help and documentation | Is task-specific help available where confusion occurs? |

## Task flows
Use when forms, dialogs, navigation or multi-step work expose friction. Map the user's start, next action, completion and recovery path. Progressive disclosure should defer optional complexity, not essential prices, consequences, or required fields. Verify discoverability by finding the deferred option through its visible trigger.

## Controls and mapping
A signifier should communicate the action before interaction. Use established button/link behavior, persistent labels and selected states. Verify hover, keyboard, touch and disabled states; hover must not be the only path to an action. Do not make an entire card clickable when nested controls create ambiguous targets.

## State and recovery
Build the states that the real data flow needs: initial, empty, loading, partial, success and failure. Preserve input after recoverable errors; offer retry when meaningful. Prevent duplicate submissions while pending, but communicate why an action is unavailable. Only claim completion after confirmed success. Undo is often less disruptive than repeated confirmation; use explicit consequence confirmation for costly irreversible actions.

## Interactive states and modern primitives
- Every control has **8 states** to design and check: default, hover, focus-visible, active, disabled, loading, error, success.
- Focus ring via `:focus-visible`: 2px outline, 2px offset, ≥ 3:1 against the background **in both themes**. Never `outline: none` without a replacement.
- Hover styles only under `@media (hover: hover)`. Touch devices need the same affordance through the default style.
- **One primary action per view.** More than ~3 secondary actions go into a menu.
- **Emphasis follows intent, not danger.** A routine destructive action (log out, remove from list) is a quiet text or tinted button at the end of its section, in the danger color as text. A full-width filled red button is reserved for the confirmation step of a costly, irreversible action. Check that danger-colored text still reaches 4.5:1 on its surface in both themes.
- **Validate on blur**, not on every keystroke. Re-validate on input once a field has shown an error.
- **Optimistic UI** only for low-stakes, easily reversible actions (likes, toggles), never for payments or deletions.
- Lists of options with arrow-key navigation (menus, tabs, radio groups) use roving `tabindex`.

## Platform first (web)
Hand-built overlays, auto-growing fields and validation timing usually miss a case the browser already handles: IME input, drag-selecting text, autofill, voice control, the Android back gesture. Use the native primitive and keep the old code only as a fallback. `python3 scripts/legacy_ui_audit.py <ui-source-dir>` finds the common hand-built versions.

**Check the support target first.** Read the project's browser target (a stated Baseline target such as "Baseline 2024" in `AGENTS.md`/`CLAUDE.md`, `browserslist`, or the oldest browser in its analytics). With none stated, assume **Baseline Widely available** (interoperable for 30+ months). A Newly available or single-engine feature then needs `@supports` / a feature check and a fallback that still works, never a broken path. Confirm each feature's status in current docs (MDN, web.dev Baseline) rather than memory.

| Hand-built | Platform replacement | Note |
| --- | --- | --- |
| Overlay `div` + focus-trap script | `<dialog>` + `showModal()` (focus moves in, `Esc`, top layer, `::backdrop`); `<form method="dialog">` closes it | `show()` is non-modal: no trap, no inert background. Always keep a visible close button: voice-control and switch users cannot "click outside". |
| Click-outside listener comparing `e.target` to the dialog | `<dialog closedby="any">` | The listener closes the dialog when a text-selection drag ends on the backdrop. Fallback where `closedBy` is missing (`!('closedBy' in HTMLDialogElement.prototype)`): close only when both `pointerdown` and `pointerup` land outside the dialog's bounding rect. |
| Menu / tooltip / picker with outside-click and `Esc` handlers | `popover` + `popovertarget` (light dismiss, `Esc`, top layer); position with CSS anchor positioning where supported | Non-modal; do not call `showModal()` on a popover. Tooltips on hover alone fail touch and keyboard. |
| Button wired to open/close by script | Invoker commands (`commandfor` + `command="show-modal"` / `"close"` / `"toggle-popover"`) | Newer: feature-check and keep the script path. |
| Accordion script | `<details>`/`<summary>`; `name="group"` makes one-open-at-a-time | Nothing interactive inside `<summary>`. If you hide the marker, show another open/closed cue. |
| Page scroll locked with `body.style.overflow` toggles | `html:has(dialog[open]:modal) { overflow: hidden }` + `overscroll-behavior: contain` on the overlay's scroller | Restore exactly what was there; `scrollbar-gutter: stable` stops the page shifting sideways when the scrollbar goes. |
| Background made unreachable with `aria-hidden` + tabindex juggling | `inert` on the content behind a drawer | `showModal()` already does this for dialogs. |
| Parent class toggled from a child's state | `:has(:checked)`, `:has(:focus-visible)`, `:has(:user-invalid)` | Don't nest `:has()` or put pseudo-elements in it. |
| Textarea auto-grow from `scrollHeight` | `field-sizing: content` + `min-block-size` / `max-block-size` | Keep the script where unsupported. |

## Forms the browser can help with
- **Error timing**: style `:user-invalid` / `:user-valid`, not `:invalid`. `:invalid` paints every untouched required field red on load; `:user-invalid` waits until the user changed the field or submitted. Same logic as "validate on blur" above.
- **Autofill tokens**: every sign-in, sign-up, address, contact and payment field gets its `autocomplete` token (`email`, `username`, `current-password` vs `new-password`, `one-time-code`, `name`, `tel`, `street-address`, `postal-code`, `cc-number`, `cc-exp`…) plus the matching `type`/`inputmode`. Never `autocomplete="off"` on those: it breaks password managers and makes people type card numbers by hand.
- **Enter to send** (chat, search, inline edit): return early when `e.isComposing || e.keyCode === 229` (React's synthetic event has no `isComposing`: use `e.nativeEvent.isComposing`), or Japanese, Chinese and Korean users submit a half-typed word when they confirm a character.
- Buttons that are not meant to submit get `type="button"`. A field outside its `<form>` element can join it with `form="id"`. `<datalist>` gives suggestions without a custom combobox.
- **Autofill styling**: browsers paint autofilled fields with their own background; check `:autofill` in both themes so the text stays readable.

## Efficiency and help
Offer shortcuts and batch actions when repeated usage justifies them, retaining a visible standard route. Place examples or help beside the confusing field rather than forcing a tutorial. Test with a realistic task, invalid input, interrupted work and back navigation. A heuristic pass cannot replace observed user research.
