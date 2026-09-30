# Cognitive principles

Source catalog: Jon Yablonski's [Laws of UX](https://lawsofux.com/), consulted 2026-09-30. These are decision aids, not predictions for a specific product; behavioral effects are hypotheses until measured.

## Primary principles
| Principle | Symptom → fix | Don't |
| --- | --- | --- |
| [Fitts's law](https://lawsofux.com/fittss-law/) | Small, distant or mis-tapped controls → bigger targets, more spacing, primary action near the thumb/cursor path | Let enlarged targets overlap |
| [Hick's law](https://lawsofux.com/hicks-law/) | Slow or stalled decisions → clearer categories, ranked options, a sensible default | Delete useful options just to lower the count |
| [Jakob's law](https://lawsofux.com/jakobs-law/) | Unfamiliar controls → platform and product conventions (standard tab bar, back gesture, cart icon) | Copy another product wholesale |
| [Miller's law](https://lawsofux.com/millers-law/) | User must remember across screens → chunk info, keep needed context visible | Cap menus at "7±2" items |
| [Zeigarnik effect](https://lawsofux.com/zeigarnik-effect/) | Interrupted tasks lost → autosave drafts, visible "continue where you left off" | Nag or manufacture unfinished tasks |
| [Goal-gradient effect](https://lawsofux.com/goal-gradient-effect/) | Long bounded flows feel endless → truthful step indicator ("Adım 2/4") | Fake progress or add steps for a progress bar |
| [Von Restorff effect](https://lawsofux.com/von-restorff-effect/) | Several equally loud buttons → one primary action, others secondary/tertiary | Highlight multiple things at once |
| [Tesler's law](https://lawsofux.com/teslers-law/) | Users re-enter derivable data → defaults, autofill, computed values (city from postcode) | Hide the inference; always keep it editable |
| [Aesthetic-usability effect](https://lawsofux.com/aesthetic-usability-effect/) | Inconsistent visuals erode trust → coherent spacing, type, color | Let polish hide broken flows; test function separately |
| [Doherty threshold](https://lawsofux.com/doherty-threshold/) | Actions feel unresponsive → acknowledge within ~100ms (pressed state), show pending state for longer work, skeletons for content | Add artificial delay |
| [Peak-end rule](https://lawsofux.com/peak-end-rule/) | Weak or confusing endings → clear confirmation with a useful next step (receipt, "view order") | Cover a broken flow with confetti |

## Grouping
When relationships are unclear, use proximity first (spacing), then common region (containers), then similarity (repeated style). Too many containers add clutter - a spacing change often suffices. Check unrelated actions don't look grouped (e.g. "Delete" sitting in the same cluster as "Save").

Reduce cognitive load: don't make users remember values from a previous screen, avoid redundant interpretation, order information around the task. Progressive disclosure defers genuinely secondary options - never prices, consequences or required fields.

## Secondary catalog (apply only with a concrete fit)
| Concept | Use when / limit |
| --- | --- |
| Choice overload | Hard comparisons → comparison tables, filters. Large sets aren't automatically overwhelming. |
| Mental model | Surprising behavior → explain in the user's terms; validate assumptions. |
| Serial position | Long lists → put key items first or last; don't bury critical content. |
| Flow | Sustained work → fewer interruptions, but keep exits and important warnings. |
| Postel's law | Accept harmless format variations (spaces in IBAN/phone); never silently reinterpret ambiguous dates, amounts, identities. |
| Occam's razor | Prefer the simpler adequate interaction; don't remove needed capability. |
| Pareto principle | Prioritize tasks shown to be frequent/high-impact; never invent an 80/20 split. |
| Parkinson's law | Remove unnecessary effort; never impose artificial time pressure. |

## Using a principle in a finding
State: observed problem → principle → proposed change → what could be lost → how to check. Optimize for understandable, successful completion - never use progress, attention or memory techniques to hide costs or pressure users.
