# Avoiding the generic look (create and redesign work)

Generated UIs drift to the same template: a small uppercase label over a gradient headline, three icon cards, purple accents, a soft card with a border and a big shadow. Users have learned to read that as "nobody designed this". This reference is for **building** new screens and for reviews where the complaint is "it looks generic / AI-made".

Ideas drawn from Taste Skill (Leonxlnx/taste-skill, MIT) and Impeccable (pbakaus/impeccable, Apache-2.0), paraphrased and reconciled with the rest of this skill. See NOTICE.

## 1. Know the surface first
Many "rules" online are written for marketing pages and are wrong for product UI. Decide which surface you are on before applying anything below:
| Surface | Goal | What changes |
| --- | --- | --- |
| **Operate** (apps, dashboards, back offices, payments flows) | Speed, accuracy, scanning | Density is fine; borders and dividers are necessary; system fonts or the brand font are fine; motion minimal; consistency beats novelty. Most tells below are still worth avoiding, but taste bans on fonts/palettes do not apply over an existing brand system. |
| **Persuade** (landing, pricing, campaign pages) | Clarity of one idea, one action | Tells matter most here; one strong typographic idea, one accent, generous section spacing, one authored motion moment. |
| **Read** (docs, help, articles) | Comfortable reading | Measure 60–75ch, body 16–18px, line height ~1.6, quiet chrome. |

An existing design system or brand **always** wins over these heuristics. They apply to choices the system leaves open.

## 2. Direction before code (new screens and redesigns)
Write these down before touching code, in 4–6 lines, and keep them in the reply:
1. **Who and what for**: the audience and the one task or decision this screen serves.
2. **The one thing that matters most** on the first screen, and the single primary action.
3. **What makes this product unlike its competitors.** Take it from the product's own world: its data, materials, vocabulary, users. A style trend is not a reason.
4. **Type**: one family (two at most), a scale with clear contrast (display ≥ 3× body on marketing; 1.2–1.333 ratio in apps), and the weights in use.
5. **Color strategy**: restrained (neutrals plus one accent on the primary action) is the default for apps. Bolder strategies are a deliberate choice for brand surfaces.
6. **One signature move** at most: a single memorable detail, not five.

Then check it against two tests:
- **Category test**: could someone guess this look from the product category alone ("fintech = navy + gradient cards")? Then it is a default, not a decision.
- **Logo test**: cover the logo. Could a competitor ship this page unchanged?

## 3. Tells (the render audit flags the measurable ones as "Generic-look tells")
| Tell | Instead |
| --- | --- |
| Small tracked uppercase label (eyebrow) above every heading; pill badge above the hero headline | Let the heading stand alone; use an eyebrow only for real navigation context (breadcrumb, category link) |
| Gradient-filled headline text; one accent-colored word in a headline | Solid ink; emphasis through size, weight or wording |
| Three or six identical cards with icon + heading + two lines | Vary by content: a list, a comparison, one large feature with smaller supporting ones, real screenshots |
| Purple/indigo or cyan-violet gradients; cream + terracotta + serif "warm editorial"; near-black + neon glow | A palette derived from the brand and the product's world; tinted neutrals + one accent |
| Glassmorphism panels and floating pill navigation bars by default | Solid surfaces separated by tone; a normal header |
| Card inside a card; 1px border **plus** a wide soft shadow; colored side stripe on callouts | One container level; tone step or line (see the surfaces table in visual craft) |
| Emoji as icons; decorative blobs, grid/dot backgrounds, sketchy SVG doodles | The product's icon set; real imagery or nothing |
| Monospace text as a "technical" costume; 01 / 02 / 03 section numbers with no real sequence | Monospace only for code and data; numbers only for real steps |
| Fake dashboards made of gray bars; hero metrics nobody can verify ("10x faster", "99.99%") | Real screenshots or honest illustrations; real, sourced numbers |
| Everything centered | Left-aligned text with 2–4 shared left edges; centre only short, isolated statements |
| Pulsing dots, marquees, hover-zoom on every image, a different entrance animation per section | One motion idea, used consistently |

## 4. Copy tells (EN / TR)
- **Inflated verbs and nouns**: unlock, seamless, elevate, empower, supercharge, revolutionize, next-level · *kesintisiz, sorunsuz, güçlendirin, bir üst seviyeye taşıyın, devrim niteliğinde, uçtan uca çözüm*.
- **Template shapes**: "Not just X, it's Y" / *"Sadece X değil, aynı zamanda Y"*; three-word triplets ("Fast. Secure. Simple." / *"Hızlı. Güvenli. Kolay."*); a question headline answered by the subhead.
- **Empty CTAs**: "Get started", "Learn more" / *"Hemen başla", "Daha fazla bilgi"* when the action can be named ("Faturayı oluştur", "Fiyatları gör").
- **Punctuation tics**: stacked em dashes, exclamation marks in product UI.
- **Placeholder data**: John Doe, Acme Inc., Lorem ipsum, 99.99%, $1,234 · *Ahmet Yılmaz* everywhere. Use realistic, varied, locale-correct data (names of different lengths, `₺12.480,50`, real-looking dates).

## 5. Before shipping new UI
- Run `render_audit.mjs`. Resolve the "Generic-look tells" that apply to this surface, or justify them in one line.
- Score yourself honestly. If any tell from section 3 is still visible on a Persuade surface, do not call the design "done". Name it and say why it stays.
