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
- **Validate on blur**, not on every keystroke. Re-validate on input once a field has shown an error.
- **Optimistic UI** only for low-stakes, easily reversible actions (likes, toggles), never for payments or deletions.
- Prefer the platform: `<dialog>` (focus trap, `Esc`, top layer), the Popover API, `inert` for background content, CSS anchor positioning for popovers where supported, `overscroll-behavior: contain` on scrollable overlays so the page behind does not scroll.
- Lists of options with arrow-key navigation (menus, tabs, radio groups) use roving `tabindex`.

## Efficiency and help
Offer shortcuts and batch actions when repeated usage justifies them, retaining a visible standard route. Place examples or help beside the confusing field rather than forcing a tutorial. Test with a realistic task, invalid input, interrupted work and back navigation. A heuristic pass cannot replace observed user research.
