# Microcopy

Interface text: buttons, labels, helper text, statuses, errors, empty states, confirmations. Preserve product truth, established terminology and locale.

## Workflow
1. Identify the action, the object, the consequence, and what the user is unsure about.
2. Write the shortest text that removes that uncertainty.
3. Judge it inside the real component - brevity out of context can lose meaning.
4. Keep visible text and accessible name aligned.
5. Check wrapping, long translations, plurals and dynamic values.
6. Read the whole flow for consistent terms (don't say "Sepet" on one screen and "Çanta" on the next).

## Patterns
| Context | Do | Before → After |
| --- | --- | --- |
| Action buttons | Verb + object when context doesn't supply it | "Tamam" → "Değişiklikleri kaydet" · "Submit" → "Create account" |
| Destructive confirm | Button names the consequence; body states scope | "Emin misiniz? [Evet] [Hayır]" → "3 fatura kalıcı olarak silinsin mi? [Faturaları sil] [Vazgeç]" |
| Form labels | Persistent label; format hint before errors happen | Placeholder-only "Telefon" → Label "Telefon" + hint "05XX XXX XX XX" |
| Errors | Specific problem + available fix, no blame; keep input; attach to field | "Hatalı giriş" → "Şifre en az 8 karakter olmalı." |
| Unknown failures | Say what failed and what to do; don't invent causes | "Bir şeyler ters gitti" → "Değişiklikler kaydedilemedi. Tekrar deneyin." (only if it *is* a save and retry works) |
| Empty states | Distinguish no data / no results / failed load; give the next step | "Veri yok" → "Henüz fatura yok. İlk faturanı oluştur." · "Aramanızla eşleşen sonuç yok. Filtreleri temizle." |
| Pending / success | Describe the real state; never claim success before confirmation | "Kaydedildi!" (optimistic) → "Kaydediliyor…" → "Kaydedildi" |
| Disabled controls | Explain the prerequisite next to the control (a tooltip on an unfocusable button doesn't count) | Gray "Devam" → "Devam etmek için koşulları kabul edin" under the button |
| Trust-sensitive | Make cost, renewal, permissions explicit; no false urgency, no guilt opt-outs | "Hayır, tasarruf etmek istemiyorum" → "Şimdi değil" · "Ücretsiz dene" → "7 gün ücretsiz, sonra ₺149,99/ay. İstediğin zaman iptal et." |

## Localization
- Use the project's i18n system and plural rules; never concatenate sentence fragments.
- Format numbers, currency and dates by locale (`₺1.234,50`, `30 Eyl 2026` for tr-TR).
- Allow ~30–40% text growth; German and Turkish strings often run longer than English.
- Turkish: mind case rules (`i/İ`, `ı/I` - use locale-aware `toLocaleUpperCase('tr-TR')`); watch vowel-harmony suffixes on dynamic values ("{name}'e/'a") - rephrase to avoid attaching suffixes to variables when possible.
- Pick one form of address (sen / siz) and keep it across the product.

## Tone
Errors: clear and calm. Success: restrained. Actions: direct. No jokes or decorative personality in critical instructions, payments, or data loss.
