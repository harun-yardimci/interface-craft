#!/usr/bin/env python3
"""Static scan for design-token drift.

Usage: python3 token_audit.py [path] [--grid 4] [--max N]

Collects literal font sizes, spacing and corner radii from SwiftUI, Compose,
CSS and Tailwind code. Reports:
  - how many distinct values each category uses (a sprawling set means there is
    no real scale, or the code bypasses it),
  - spacing values that fall off the grid (default 4),
  - fixed font sizes that do not scale with Dynamic Type / user font size.
Hits are leads, not verdicts: a few literals inside a token definition file are
expected. Confirm by reading the design tokens the project already has.
"""
import argparse
import os
import re
from collections import Counter, defaultdict

SKIP_DIRS = {".git", "node_modules", "build", "dist", ".next", "DerivedData", "Pods",
             ".build", "out", "coverage", ".gradle", "vendor", ".turbo", ".svelte-kit"}
NUM = r"(\d+(?:\.\d+)?)"

RULES = {
    ".swift": {
        "font": [re.compile(r"\.system\(\s*size:\s*" + NUM), re.compile(r"Font\.custom\([^)]*size:\s*" + NUM + r"(?![^)]*relativeTo)")],
        "spacing": [re.compile(r"\.padding\((?:\s*\.[a-zA-Z]+\s*,)?\s*" + NUM + r"\s*\)"),
                    re.compile(r"\bspacing:\s*" + NUM)],
        "radius": [re.compile(r"cornerRadius:\s*" + NUM), re.compile(r"\.cornerRadius\(\s*" + NUM)],
    },
    ".kt": {
        "font": [re.compile(r"fontSize\s*=\s*" + NUM + r"\.sp")],
        "spacing": [re.compile(r"(?:padding|spacedBy|Spacer\(Modifier\.(?:height|width))\([^)]*?" + NUM + r"\.dp")],
        "radius": [re.compile(r"RoundedCornerShape\(\s*" + NUM + r"\.dp")],
    },
    ".css": {
        "font": [re.compile(r"^\s*font-size\s*:\s*" + NUM + r"px")],
        "spacing": [re.compile(r"^\s*(?:padding|margin|gap|row-gap|column-gap)[a-z-]*\s*:\s*([^;]+)")],
        "radius": [re.compile(r"^\s*border(?:-[a-z]+)*-radius\s*:\s*" + NUM + r"px")],
    },
    ".tw": {
        "font": [re.compile(r"\btext-\[" + NUM + r"px\]")],
        "spacing": [re.compile(r"\b-?(?:p|px|py|pt|pb|pl|pr|ps|pe|m|mx|my|mt|mb|ml|mr|gap|gap-x|gap-y|space-x|space-y)-\[" + NUM + r"px\]")],
        "radius": [re.compile(r"\brounded(?:-[a-z]+)?-\[" + NUM + r"px\]")],
    },
}
FILE_KIND = {".swift": ".swift", ".kt": ".kt", ".kts": ".kt", ".css": ".css", ".scss": ".css",
             ".less": ".css", ".tsx": ".tw", ".jsx": ".tw", ".html": ".tw", ".vue": ".tw",
             ".svelte": ".tw", ".astro": ".tw"}
PX = re.compile(r"(-?\d+(?:\.\d+)?)px")


def walk(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for name in filenames:
            yield os.path.join(dirpath, name)


def fmt(v):
    return str(int(v)) if v == int(v) else str(v)


def main():
    ap = argparse.ArgumentParser(description="Static scan for design-token drift.")
    ap.add_argument("path", nargs="?", default=".")
    ap.add_argument("--grid", type=float, default=4, help="spacing grid in pt/px/dp (default 4)")
    ap.add_argument("--max", type=int, default=25, help="max listed hits per rule")
    opts = ap.parse_args()
    root, grid, max_hits = opts.path, opts.grid, opts.max

    values = defaultdict(Counter)          # category -> Counter(value)
    where = defaultdict(list)              # category -> [(path, line, value, snippet)]
    fixed_fonts = []                       # Swift/Compose fonts that ignore user text size
    offgrid = []

    for path in walk(root):
        kind = FILE_KIND.get(os.path.splitext(path)[1].lower())
        if not kind:
            continue
        try:
            lines = open(path, encoding="utf-8", errors="ignore").readlines()
        except OSError:
            continue
        rel = os.path.relpath(path, root)
        for i, line in enumerate(lines, 1):
            s = line.strip()
            if s.startswith(("//", "/*", "*", "--")) or re.match(r"^\s*--[\w-]+\s*:", line):
                continue  # comments and CSS custom-property (token) definitions
            # CSS declarations often share a line: `.card { padding: 12px; border-radius: 8px; }`
            pieces = re.split(r"[;{}]", line) if kind == ".css" else [line]
            for cat, rxs in RULES[kind].items():
                for rx in rxs:
                    for m in (m for piece in pieces for m in rx.finditer(piece)):
                        raw = m.group(1)
                        nums = [float(x) for x in PX.findall(raw)] if kind == ".css" and cat == "spacing" else [float(raw)]
                        for v in nums:
                            v = abs(v)
                            values[cat][v] += 1
                            where[cat].append((rel, i, v, s[:120]))
                            if cat == "spacing" and v >= grid and v % grid:
                                offgrid.append((rel, i, v, s[:120]))
                            if cat == "font" and kind == ".swift" and ".system(size:" in line.replace(" ", ""):
                                fixed_fonts.append((rel, i, v, s[:120]))

    if not any(values.values()):
        print("No literal font sizes, spacing or radii found.")
        return

    print(f"Design-token drift report for {os.path.abspath(root)} (grid = {fmt(grid)})\n")
    limits = {"font": 8, "spacing": 10, "radius": 5}
    for cat in ("font", "spacing", "radius"):
        c = values[cat]
        if not c:
            continue
        dist = ", ".join(f"{fmt(v)}×{n}" for v, n in sorted(c.items()))
        flag = "  <- sprawling: no clear scale" if len(c) > limits[cat] else ""
        print(f"{cat:8} {len(c):3} distinct literal values{flag}")
        print(f"         {dist}\n")

    if fixed_fonts:
        print(f"[WARN] fixed-font  {len(fixed_fonts)} × `.system(size:)` does not scale with Dynamic Type. "
              "Use text styles (.body, .headline) or a scaled custom font.")
        for rel, i, v, s in fixed_fonts[:max_hits]:
            print(f"       {rel}:{i}  > {s}")
        print()
    if offgrid:
        print(f"[WARN] off-grid    {len(offgrid)} spacing values not on the {fmt(grid)}pt grid")
        for rel, i, v, s in offgrid[:max_hits]:
            print(f"       {rel}:{i}  {fmt(v)}  > {s}")
        print()
    rare = [(cat, v) for cat in ("font", "radius") for v, n in values[cat].items() if n == 1]
    if rare:
        print("[INFO] one-off values (used once; likely drift from the scale):")
        for cat, v in rare[:max_hits]:
            loc = next(w for w in where[cat] if w[2] == v)
            print(f"       {cat:7} {fmt(v):>5}  {loc[0]}:{loc[1]}  > {loc[3]}")
        print()
    print("Hits are leads, not verdicts. Map literals to the project's existing tokens before changing them.")


if __name__ == "__main__":
    main()
