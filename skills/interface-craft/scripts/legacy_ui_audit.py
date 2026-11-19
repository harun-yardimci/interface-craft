#!/usr/bin/env python3
"""Static scan for web UI code that rebuilds, in JavaScript or with CSS hacks, what the
platform now does natively - and does it worse for keyboard, IME, autofill or zoom users.

Usage: python3 legacy_ui_audit.py [path] [--max N]

Rules (web: HTML/JSX/TSX/Vue/Svelte/Astro, JS/TS, CSS/SCSS):
  zoom-disabled        Viewport meta with user-scalable=no or maximum-scale=1: blocks pinch
                       zoom (WCAG 1.4.4). Remove both.
  positive-tabindex    tabindex="1".."9": overrides the DOM focus order. Use 0 / -1 and fix
                       the source order.
  autocomplete-off     autocomplete="off" on a credential, contact, address or payment field:
                       breaks password managers and autofill. Use the standard token.
  password-no-token    type="password" whose autocomplete has neither current-password nor
                       new-password: the browser cannot tell sign-in from sign-up.
  enter-no-ime-guard   An Enter keydown handler with no isComposing / keyCode 229 check near
                       it: Japanese, Chinese and Korean users submit half-typed words.
                       (React: the flag is on e.nativeEvent.)
  dialog-target-click  A click listener comparing event.target to the dialog for light
                       dismiss: closes when a text selection drag ends on the backdrop.
                       Use <dialog closedby="any">; fallback: close only when both pointerdown
                       and pointerup land outside the dialog's rect.
  textarea-autosize-js Height set from scrollHeight: `field-sizing: content` does it in CSS
                       (keep the JS as the fallback where unsupported).
  max-height-hack      Transition on max-height with a large guess (>= 500px): the animation
                       timing is wrong and content can clip. Use grid-template-rows 0fr->1fr,
                       or interpolate-size: allow-keywords / ::details-content.
  premature-invalid    :invalid styling with no :user-invalid in the project: required fields
                       show as errors before the user has touched them.
  parent-class-toggle  JS adds/removes a class on a parent or ancestor to mirror a child's
                       state (checked, focus, open): `:has()` expresses it in CSS.
  scheme-duplication   Three or more prefers-color-scheme: dark blocks in one stylesheet:
                       usually one value per token pair belongs in light-dark().

Each rule drops its hits when the replacement sits next to it (in the same handler or rule
block; for premature-invalid, anywhere in the project), so a guarded fallback is not reported. Hits are leads, not verdicts:
open each one, check the project's browser support target (its Baseline target or
browserslist), and keep a fallback where the replacement is not yet available to its users.
"""
import argparse
import os
import re

SKIP_DIRS = {".git", "node_modules", "build", "dist", ".next", "DerivedData", "Pods", ".build", "out",
             "coverage", ".gradle", "vendor", ".turbo", ".svelte-kit", ".nuxt", ".output", "public/build",
             "bower_components", "third_party", "vendors", ".venv", "venv", "__pycache__"}
MARKUP = {".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte", ".astro", ".php", ".erb", ".hbs", ".njk", ".twig"}
SCRIPT = {".js", ".mjs", ".cjs", ".ts", ".jsx", ".tsx", ".vue", ".svelte", ".astro"}
STYLE = {".css", ".scss", ".sass", ".less"}

ZOOM_CONTENT = re.compile(r"user-scalable\s*=\s*(no|0)\b|maximum-scale\s*=\s*1(\.0*)?(?![\d.])", re.I)
POS_TABINDEX = re.compile(r"\btab[iI]ndex\s*=\s*\{?\s*[\"']?\s*([1-9]\d*)\b")
SENSITIVE_FIELD = re.compile(r"type\s*=\s*[\"'](password|email|tel)[\"']|(name|id)\s*=\s*[\"'][^\"']*(pass|email|e-?mail|phone|tel|address|adres|street|city|zip|postal|card|cc-|cvc|cvv|iban|otp|one-?time)[^\"']*[\"']", re.I)
ENTER = re.compile(r"""(\.key\s*===?\s*['"]Enter['"]|['"]Enter['"]\s*===?\s*\w+\.key|\.keyCode\s*===?\s*13\b|\.which\s*===?\s*13\b)""")
IME_GUARD = re.compile(r"isComposing|keyCode\s*[!=]==?\s*229|229\s*[!=]==?\s*[\w.]*keyCode")
DIALOG_TARGET = re.compile(r"""\b(e|ev|evt|event)\.target\s*===?\s*(\w*[dD]ialog\w*|this|modal\w*|\w*[mM]odal\b|[\w.]*(ref|Ref)\.current)""")
DIALOG_CTX = re.compile(r"<dialog|showModal\(|HTMLDialogElement|\bdialog\b", re.I)
CLOSEDBY = re.compile(r"closedby", re.I)
SCROLLHEIGHT = re.compile(r"style\.height\s*=\s*[^;]*scrollHeight|height\s*:\s*[^;,}]*scrollHeight")
FIELD_SIZING = re.compile(r"field-sizing|fieldSizing")
MAXH = re.compile(r"max-height\s*:\s*(\d{3,})px", re.I)
MAXH_TRANSITION = re.compile(r"transition[^;]*\b(max-height|all)\b", re.I)
INTERPOLATE = re.compile(r"interpolate-size|calc-size\(|::details-content|grid-template-rows\s*:\s*0fr")
INVALID_SEL = re.compile(r"(?<!-):invalid\b|(?<![\w-])invalid:")
USER_INVALID = re.compile(r":user-invalid|user-invalid:")
PARENT_TOGGLE = re.compile(r"\.(parentElement|parentNode|closest\([^)]*\))\s*(\?\.|\.)\s*classList\.(toggle|add|remove)\(")
HAS_SEL = re.compile(r":has\(")
DARK_MQ = re.compile(r"prefers-color-scheme\s*:\s*dark")
LIGHT_DARK = re.compile(r"light-dark\(")


def walk(root):
    if os.path.isfile(root):
        yield os.path.dirname(root) or ".", os.path.basename(root)
        return
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in fns:
            yield dp, fn


def tag_at(lines, i, start, limit=4000):
    """The tag starting at lines[i][start:], up to its real end: a `>` outside quotes and
    JSX braces (so `onChange={e => f(e)}` does not end it)."""
    chunk = "\n".join([lines[i][start:]] + lines[i + 1:])[:limit]
    quote, depth = None, 0
    for k, ch in enumerate(chunk):
        if quote:
            if ch == quote:
                quote = None
        elif ch in "\"'`":
            quote = ch
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth = max(0, depth - 1)
        elif ch == ">" and depth == 0:
            return chunk[:k + 1].replace("\n", " ")
    return chunk.replace("\n", " ")


def attr(tag, name):
    """Value of an exact attribute (case-insensitive, not data-<name>), with JSX literals
    such as autoComplete={"off"} unwrapped. None when absent."""
    m = re.search(r"(?<![\w-])%s\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|\{\s*[\"'`]([^\"'`]*)[\"'`]\s*\}|\{([^}]*)\}|([^\s>]+))" % name, tag, re.I)
    return None if not m else next(g for g in m.groups() if g is not None)


def scan_file(path, ext, text, hits, project):
    lines = text.splitlines()
    add = lambda sev, rid, n, snip, msg: hits.append((sev, rid, path, n, snip.strip()[:150], msg))

    if ext in MARKUP:
        for i, l in enumerate(lines):
            n = i + 1
            for mt in re.finditer(r"<meta\b", l, re.I):
                tag = tag_at(lines, i, mt.start())
                if (attr(tag, "name") or "").lower() == "viewport" and ZOOM_CONTENT.search(attr(tag, "content") or ""):
                    add("high", "zoom-disabled", n, tag, "Pinch zoom is blocked; remove user-scalable=no and maximum-scale=1.")
            m = POS_TABINDEX.search(l)
            if m:
                add("warn", "positive-tabindex", n, l, f"tabindex={m.group(1)} reorders focus; use 0 or -1 and fix the DOM order.")
            for mt in re.finditer(r"<(input|textarea|select)\b", l, re.I):
                tag = tag_at(lines, i, mt.start())
                norm = re.sub(r"=\s*\{\s*([\"'])([^\"']*)\1\s*\}", r'="\2"', tag)
                ac = (attr(norm, "autocomplete") or "").lower()
                if ac.strip() == "off" and SENSITIVE_FIELD.search(norm):
                    add("high", "autocomplete-off", n, tag,
                        "autocomplete=off on a field autofill should fill; use the standard token (email, tel, "
                        "street-address, cc-number, one-time-code, current-password / new-password).")
                elif (attr(norm, "type") or "").lower() == "password" and not re.search(r"\b(current|new)-password\b", ac):
                    add("warn", "password-no-token", n, tag,
                        "Password field without current-password (sign-in) or new-password (sign-up) in autocomplete.")

    if ext in SCRIPT:
        for i, l in enumerate(lines):
            # the guard must sit in the same handler, not merely somewhere in the file
            if ENTER.search(l) and re.search(r"key(down|press)|onKey(Down|Press)|handleKey|keydown", " ".join(lines[max(0, i - 6):i + 1]), re.I) \
                    and not IME_GUARD.search(" ".join(lines[max(0, i - 8):i + 3])):
                add("warn", "enter-no-ime-guard", i + 1, l,
                    "Enter handler without an IME guard; return early when e.isComposing || e.keyCode === 229 "
                    "(React: e.nativeEvent.isComposing).")
        if DIALOG_CTX.search(text) and not CLOSEDBY.search(text):
            for i, l in enumerate(lines):
                if DIALOG_TARGET.search(l):
                    add("info", "dialog-target-click", i + 1, l,
                        "Light dismiss by event.target comparison; use <dialog closedby=\"any\">, with a fallback that "
                        "requires both pointerdown and pointerup outside the dialog's rect.")
        if not FIELD_SIZING.search(text):
            for i, l in enumerate(lines):
                if SCROLLHEIGHT.search(l):
                    add("info", "textarea-autosize-js", i + 1, l,
                        "Auto-growing height from scrollHeight; field-sizing: content does it in CSS (keep JS as fallback).")
        if not HAS_SEL.search(text):
            for i, l in enumerate(lines):
                if PARENT_TOGGLE.search(l):
                    add("info", "parent-class-toggle", i + 1, l,
                        "Parent class mirrors a child's state; a :has() selector can replace the script.")

    if ext in STYLE or ext in MARKUP:
        for i, l in enumerate(lines):
            m = MAXH.search(l)
            if m and int(m.group(1)) >= 500:
                block = " ".join(lines[max(0, i - 12):i + 12])
                # a replacement next to this rule means it is a guarded fallback
                if MAXH_TRANSITION.search(block) and not INTERPOLATE.search(block):
                    add("warn", "max-height-hack", i + 1, l,
                        "max-height transition with a guessed size; use grid-template-rows 0fr->1fr or interpolate-size.")
        if not project["user_invalid"]:
            for i, l in enumerate(lines):
                if INVALID_SEL.search(l) and not l.strip().startswith(("//", "/*", "*")):
                    add("warn", "premature-invalid", i + 1, l,
                        ":invalid matches untouched required fields; use :user-invalid (or style aria-invalid after blur/submit).")
    if ext in STYLE and not LIGHT_DARK.search(text):
        blocks = [i for i, l in enumerate(lines) if DARK_MQ.search(l)]
        if len(blocks) >= 3:
            add("info", "scheme-duplication", blocks[0] + 1, lines[blocks[0]],
                f"{len(blocks)} prefers-color-scheme: dark blocks; light-dark() keeps each token's pair in one place.")


def main():
    ap = argparse.ArgumentParser(description="Static scan for legacy web UI patterns the platform now handles natively.")
    ap.add_argument("path", nargs="?", default=".")
    ap.add_argument("--max", type=int, default=40, help="max listed hits per rule")
    opts = ap.parse_args()
    if opts.max < 1:
        ap.error("--max must be a positive integer")
    root = opts.path

    files = []
    for dp, fn in walk(root):
        ext = os.path.splitext(fn)[1].lower()
        if ext in MARKUP | SCRIPT | STYLE:
            path = os.path.join(dp, fn)
            try:
                with open(path, encoding="utf-8", errors="ignore") as f:
                    text = f.read()
            except OSError:
                continue
            if len(text) > 2_000_000 or ".min." in fn:
                continue
            files.append((path, ext, text))

    project = {"user_invalid": any(USER_INVALID.search(t) for _, _, t in files)}
    hits = []
    for path, ext, text in files:
        scan_file(path, ext, text, hits, project)

    order = {"high": 0, "warn": 1, "info": 2}
    hits.sort(key=lambda h: (order[h[0]], h[1], h[2], h[3]))
    if not hits:
        print("No legacy UI patterns found by static scan.")
        return
    counts, shown = {}, {}
    for sev, rid, path, line, snippet, msg in hits:
        counts[(sev, rid)] = counts.get((sev, rid), 0) + 1
        if shown.get(rid, 0) >= opts.max:
            continue
        shown[rid] = shown.get(rid, 0) + 1
        rel = os.path.relpath(path, root) if os.path.isdir(root) else os.path.basename(path)
        print(f"[{sev.upper():4}] {rid:20} {rel}:{line}")
        print(f"       {msg}")
        if snippet:
            print(f"       > {snippet}")
    print("\nSummary:")
    for (sev, rid), n in sorted(counts.items(), key=lambda kv: (order[kv[0][0]], kv[0][1])):
        print(f"  {sev:4} {rid:20} {n}")
    print("Hits are leads, not verdicts. Check the browser support target and keep fallbacks (see interaction-and-feedback.md, Platform first).")


if __name__ == "__main__":
    main()
