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

## Lists and settings screens
Profile, settings and task lists drift into a "junk drawer": every destination is one equal row, every row carries every field. Hierarchy should follow how often and why people come here.

**Screen structure (profile, account, settings)**
- **Rank by frequency.** The 2–3 destinations people open most (orders, wallet, saved) can become larger tiles that show their state ("2 aktif", "₺42,50", "18 ürün"). Everything else goes into grouped, inset lists. Base the ranking on usage data or the product's core task; never invent an 80/20 split.
- **Group, then merge the rare.** Help, About, Privacy Policy and Terms are rarely opened. One "Yardım ve yasal" row is easier to scan than four. Legal pages stay reachable in one tap from that row.
- **Promotions don't own the top of a utility screen.** A "Profilini tamamla, 50 puan kazan!!!" banner above the account content pushes the task down. If loyalty status matters, show it as real data (points, tier, distance to next tier), not as a nag.

**Rows show their value.** A row that only names a destination forces a tap to learn the current state. Show it in the trailing slot: "Adresler · 2 kayıtlı", "Ödeme yöntemleri · Visa ·· 4242", "Dil · Türkçe". A single binary setting is an inline toggle on the row, not a drill-in screen with one switch. Trailing values truncate before the label does, and the row's accessible name includes the value.

**Task and navigation lists: one title, one meta line.** Content lists (messages, mail, notifications, search results) are different: a preview line is the content, so keep their natural height (see the repeated-content section in visual craft).
- Descriptions, tags, avatars and full timestamps on every row turn a list into a wall. Keep the title plus one short meta line ("17:00 · İş"); move the rest to the detail view (progressive disclosure, never hiding cost or consequence).
- **Don't repeat what the context already says.** Under a "Bugün" header, each row needs the time, not "Due: 10/24/2026 5:00 PM". Use relative and contextual dates (Bugün, Yarın, Cuma) and full dates only where ambiguity starts.
- **Filter by the axis people navigate by.** Find the axis from usage or the product's main task rather than assuming it; for many task lists it is time (Tümü / Bugün / Yaklaşan) rather than priority. Show a secondary attribute (priority, label) as a small indicator on the row; an indicator that differs only by color also needs a text or accessible label (e.g. `accessibilityLabel("Yüksek öncelik")`), or a different shape.
- **Add actions where the list ends.** A FAB that covers the last row's content or controls is a layering bug; an inline "Görev ekle" row at the end of a short list, or bottom padding equal to the FAB height plus margin, fixes it.

Check: count the distinct colors, type sizes and fields per row before and after.

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
