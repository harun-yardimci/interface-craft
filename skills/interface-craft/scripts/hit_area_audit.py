#!/usr/bin/env python3
"""Static scan for tap areas that do not match what the user sees.

Usage: python3 hit_area_audit.py [path] [--max N]

SwiftUI:
  clip-overflow   An image or view scaled to fill (or offset/scaled) and then
                  `.clipped()` / `.clipShape(...)` with no `.contentShape(...)`.
                  Clipping cuts the drawing, not the hit area: the invisible
                  overflow keeps catching taps and can cover the controls above
                  or below it (worst on wide/iPad layouts, where fill-scaling
                  overflows most).
  small-target    A Button / NavigationLink / onTapGesture whose label is framed
                  smaller than 44x44 pt and has no `.contentShape`.
  hidden-hit      `.opacity(0)` or `.hidden()`-style views that still take
                  taps (no `.allowsHitTesting(false)` nearby).
Compose:
  small-target    `Modifier.size(<48.dp)` on a clickable without
                  `minimumInteractiveComponentSize`.
Web (CSS/markup):
  overlay-hit     Absolutely/fixed positioned layers covering their parent
                  (`inset: 0` / `inset-0`) without `pointer-events: none`.

Hits are leads, not verdicts. Confirm on a device at the widest and narrowest
layouts by tapping each control next to media and at its visible edges.
"""
import os
import re
import sys

SKIP_DIRS = {".git", "node_modules", "build", "dist", ".next", "DerivedData", "Pods",
             ".build", "out", "coverage", ".gradle", "vendor", ".turbo", ".svelte-kit"}

SW_CLIP = re.compile(r"\.(?:clipped\(|clipShape\()")
# Only content that is actually larger than its frame: fill-scaled images,
# scaled/offset layers, and image loaders that fill by default.
SW_FILL = re.compile(r"contentMode:\s*\.fill|\.scaledToFill\(\)|\.scaleEffect\(|\.offset\(\s*x|AsyncImage\(")
SW_CONTENT_SHAPE = re.compile(r"\.contentShape\(|\.allowsHitTesting\(false\)")
SW_TAPPABLE = re.compile(r"\bButton\s*[({]|NavigationLink\s*[({]|\.onTapGesture|Menu\s*\{")
SW_SMALL_FRAME = re.compile(r"\.frame\(\s*width:\s*(\d+(?:\.\d+)?)\s*,\s*height:\s*(\d+(?:\.\d+)?)\s*\)")
SW_INVISIBLE = re.compile(r"\.opacity\(\s*0(?:\.0)?\s*\)")

KT_SMALL = re.compile(r"Modifier[^\n]*\.size\(\s*(\d+)\.dp\s*\)[^\n]*\.clickable|\.clickable[^\n]*\.size\(\s*(\d+)\.dp\s*\)")
KT_MIN = re.compile(r"minimumInteractiveComponentSize")

CSS_OVERLAY = re.compile(r"position\s*:\s*(?:absolute|fixed)")
CSS_INSET = re.compile(r"inset\s*:\s*0\b|top\s*:\s*0[^;]*;[^}]*left\s*:\s*0")
CSS_PE_NONE = re.compile(r"pointer-events\s*:\s*none")
TW_OVERLAY = re.compile(r"\b(?:absolute|fixed)\b[^\"']*\binset-0\b|\binset-0\b[^\"']*\b(?:absolute|fixed)\b")
TW_PE_NONE = re.compile(r"\bpointer-events-none\b")

LOOKBACK = 10
LOOKAHEAD = 3


def walk(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for name in filenames:
            yield dirpath, name


def read(path):
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            return fh.readlines()
    except OSError:
        return []


def is_comment(line):
    s = line.strip()
    return s.startswith("//") or s.startswith("*") or s.startswith("/*")


def scan_swift(path, hits):
    lines = read(path)
    for i, line in enumerate(lines):
        if is_comment(line):
            continue
        if SW_CLIP.search(line):
            # The hit shape may be set just before or after the clip in the same chain.
            chain = "".join(lines[max(0, i - 3):i + LOOKAHEAD + 1])
            if SW_CONTENT_SHAPE.search(chain):
                continue
            before = "".join(l for l in lines[max(0, i - LOOKBACK):i] if not is_comment(l))
            if SW_FILL.search(before) or SW_FILL.search(line):
                hits.append(("high", "clip-overflow", path, i + 1, line.strip()[:140],
                             "Clipped fill/offset content without .contentShape: the overflow still takes taps and can cover nearby controls"))
        m = SW_SMALL_FRAME.search(line)
        if m and float(m.group(1)) < 44 and float(m.group(2)) < 44:
            before = "".join(lines[max(0, i - 6):i])
            after = "".join(lines[i:i + 6])
            if SW_TAPPABLE.search(before) and not SW_CONTENT_SHAPE.search(before + after) \
                    and "minHeight: 44" not in after and "frame(minWidth: 44" not in after:
                hits.append(("warn", "small-target", path, i + 1, line.strip()[:140],
                             f"Tappable label is {m.group(1)}x{m.group(2)} pt: pad to 44x44 or add .contentShape on a larger frame"))
        if SW_INVISIBLE.search(line):
            around = "".join(lines[max(0, i - 3):i + 4])
            if "allowsHitTesting(false)" not in around and "accessibilityHidden" not in around:
                hits.append(("info", "hidden-hit", path, i + 1, line.strip()[:140],
                             "Invisible view still receives taps unless .allowsHitTesting(false)"))


def scan_kotlin(path, hits):
    lines = read(path)
    for i, line in enumerate(lines):
        if is_comment(line):
            continue
        m = KT_SMALL.search(line)
        if m:
            size = int(m.group(1) or m.group(2))
            if size < 48 and not KT_MIN.search("".join(lines[max(0, i - 3):i + 4])):
                hits.append(("warn", "small-target", path, i + 1, line.strip()[:140],
                             f"Clickable is {size}.dp: use minimumInteractiveComponentSize() or 48.dp"))


def scan_css(path, hits):
    text = "".join(read(path))
    for block in re.finditer(r"([^{}]+)\{([^}]*)\}", text):
        body = block.group(2)
        if CSS_OVERLAY.search(body) and CSS_INSET.search(body) and not CSS_PE_NONE.search(body):
            line = text[:block.start()].count("\n") + 1
            hits.append(("info", "overlay-hit", path, line, block.group(1).strip()[:140],
                         "Full-cover positioned layer takes pointer events; add pointer-events: none if decorative"))


def scan_markup(path, hits):
    for i, line in enumerate(read(path)):
        if TW_OVERLAY.search(line) and not TW_PE_NONE.search(line) and not re.search(r"<(?:button|a|input|label)\b", line):
            hits.append(("info", "overlay-hit", path, i + 1, line.strip()[:140],
                         "absolute inset-0 layer without pointer-events-none: it may swallow taps meant for what is underneath"))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = args[0] if args else "."
    max_per_rule = 40
    if "--max" in sys.argv:
        max_per_rule = int(sys.argv[sys.argv.index("--max") + 1])

    hits = []
    for dirpath, name in walk(root):
        path = os.path.join(dirpath, name)
        ext = os.path.splitext(name)[1].lower()
        if ext == ".swift":
            scan_swift(path, hits)
        elif ext in (".kt", ".kts"):
            scan_kotlin(path, hits)
        elif ext in (".css", ".scss", ".sass", ".less"):
            scan_css(path, hits)
        elif ext in (".tsx", ".jsx", ".html", ".vue", ".svelte", ".astro"):
            scan_markup(path, hits)

    order = {"high": 0, "warn": 1, "info": 2}
    hits.sort(key=lambda h: (order[h[0]], h[1], h[2], h[3]))
    if not hits:
        print("No hit-area issues found by static scan. Still tap-test controls next to media on the widest layout.")
        return
    counts, shown = {}, {}
    for sev, rid, path, line, snippet, msg in hits:
        counts[(sev, rid)] = counts.get((sev, rid), 0) + 1
        if shown.get(rid, 0) >= max_per_rule:
            continue
        shown[rid] = shown.get(rid, 0) + 1
        print(f"[{sev.upper():4}] {rid:14} {os.path.relpath(path, root)}:{line}")
        print(f"       {msg}")
        if snippet:
            print(f"       > {snippet}")
    print("\nSummary:")
    for (sev, rid), n in sorted(counts.items(), key=lambda kv: (order[kv[0][0]], kv[0][1])):
        print(f"  {sev:4} {rid:14} {n}")
    print("Hits are leads, not verdicts. Confirm by tapping on a device (see layout-resilience.md, Hit areas).")


if __name__ == "__main__":
    main()
