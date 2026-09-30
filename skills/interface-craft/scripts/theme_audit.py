#!/usr/bin/env python3
"""Static scan for light/dark theme inconsistencies.

Usage: python3 theme_audit.py [path] [--max N]

Finds hardcoded colors, fixed-vs-adaptive color mixes, local color-scheme
overrides, asset colors without a dark variant and missing web color-scheme
declarations. Hits are leads, not verdicts: intentional brand surfaces are fine
when their foreground is fixed too. Always confirm by rendering both themes.
"""
import json
import os
import re
import sys

SKIP_DIRS = {".git", "node_modules", "build", "dist", ".next", "DerivedData", "Pods",
             ".build", "out", "coverage", ".gradle", "vendor", ".turbo", ".svelte-kit"}

# (rule id, severity, regex, message)
FIXED = r"(?:Color|UIColor|NSColor)\.(?:white|black)\b|Color\(\s*(?:red|white|hex|#colorLiteral)|UIColor\(\s*(?:red|white|hex)|(?<![\w.])\.(?:white|black)\b"
SWIFT = [
    ("fixed-bg", "warn", re.compile(r"\.(?:background|fill|presentationBackground|listRowBackground|containerBackground|scrollContentBackground)\((?![^)]*opacity)[^)]*(?:" + FIXED + ")"), "Opaque fixed background; its foreground must be fixed too, or use an adaptive surface token"),
    ("fixed-stroke", "info", re.compile(r"\.(?:stroke|strokeBorder|border|overlay)\((?![^)]*opacity)[^)]*Color\(\s*hex"), "Fixed border color; use a separator/outline token with a dark value"),
    ("scheme-override", "warn", re.compile(r"\.preferredColorScheme\(\s*\.(?:light|dark)|\.environment\(\s*\\\.colorScheme,\s*\.(?:light|dark)|overrideUserInterfaceStyle"), "Local color-scheme override; part of the UI may ignore the system theme"),
]
# A fixed background is only a bug when the content on it adapts. Look for an adaptive
# foreground (system roles or project tokens, i.e. anything that is not a fixed literal)
# within a few lines of the fixed background.
SWIFT_FIXED_BG = re.compile(r"\.(?:background|fill|presentationBackground|listRowBackground|containerBackground)\((?![^)]*opacity)[^)]*(?:" + FIXED + ")")
SWIFT_FG = re.compile(r"\.(?:foregroundStyle|foregroundColor)\(([^)]*)\)")
SWIFT_FIXED_ARG = re.compile(FIXED)
WINDOW = 15

KOTLIN = [
    ("fixed-color", "warn", re.compile(r"\bColor\.(?:White|Black)\b|\bColor\(0x[0-9A-Fa-f]{6,8}\)"), "Hardcoded color; use MaterialTheme.colorScheme roles"),
    ("scheme-override", "warn", re.compile(r"darkTheme\s*=\s*(?:true|false)\b|setDefaultNightMode\("), "Forced theme; make sure it is deliberate and app-wide"),
]
KOTLIN_FIXED_BG = re.compile(r"(?:background|containerColor|color)\s*[=(]\s*Color\.(?:White|Black)|Color\(0x")
KOTLIN_ADAPTIVE_FG = re.compile(r"MaterialTheme\.colorScheme\.on|LocalContentColor|contentColorFor")

XML = [
    ("fixed-color", "warn", re.compile(r"android:(?:background|textColor|tint|src)\s*=\s*\"#[0-9A-Fa-f]{3,8}\""), "Hex color in layout; use a theme attribute or color resource with a night variant"),
]

CSS = [
    ("fixed-color", "info", re.compile(r"^\s*(?!--)[a-z-]*(?:color|background|border|fill|stroke|shadow)[a-z-]*\s*:\s*[^;]*(?:#[0-9A-Fa-f]{3,8}\b|rgba?\(|hsla?\(|\bwhite\b|\bblack\b)"), "Literal color outside a custom property; prefer a theme token"),
]

TW_FIXED_BG = r"\bbg-(?:white|black|(?:gray|zinc|slate|neutral|stone)-\d{2,3})\b"
TW_ADAPTIVE_TEXT = r"\btext-(?!(?:white|black|transparent|current|inherit|left|right|center|justify|start|end|wrap|nowrap|balance|pretty|ellipsis|clip|xs|sm|base|lg|xl|[2-9]xl)\b|(?:gray|zinc|slate|neutral|stone|red|blue|green|amber|orange|yellow|indigo|violet|purple|pink|rose|sky|cyan|teal|emerald|lime|fuchsia)-\d|\[)[a-z][a-z-]*"
MARKUP = [
    ("tw-mix", "high", re.compile(r"(?=.*" + TW_FIXED_BG + r")(?=.*" + TW_ADAPTIVE_TEXT + r")"), "Fixed Tailwind background with a theme text token: text likely vanishes in one theme"),
    ("tw-no-dark", "warn", re.compile(r"\b(?:bg|text|border|ring|divide|fill|stroke)-(?:white|black|(?:gray|zinc|slate|neutral|stone)-\d{2,3})\b"), "Fixed Tailwind color without a dark: variant on this line"),
    ("inline-color", "info", re.compile(r"style=\{?\{?[^}]*(?:color|background)[^}]*(?:#[0-9A-Fa-f]{3,8}|rgba?\()"), "Inline literal color; prefer a theme token"),
    ("class-override", "info", re.compile(r"className=\"[^\"]*\b(?:light|dark)\b(?!:)"), "Hardcoded theme class on a subtree"),
]


def walk(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for name in filenames:
            yield dirpath, name


def scan_lines(path, rules, hits, skip_line=None):
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            lines = fh.readlines()
    except OSError:
        return []
    for i, line in enumerate(lines, 1):
        if skip_line and skip_line(line):
            continue
        for rid, sev, rx, msg in rules:
            if rx.search(line):
                hits.append((sev, rid, path, i, line.strip()[:140], msg))
    return lines


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = args[0] if args else "."
    max_per_rule = 40
    if "--max" in sys.argv:
        max_per_rule = int(sys.argv[sys.argv.index("--max") + 1])

    hits = []
    has_color_scheme_decl = False
    web_files = 0
    night_values = False
    day_colors = []

    for dirpath, name in walk(root):
        path = os.path.join(dirpath, name)
        ext = os.path.splitext(name)[1].lower()
        if ext == ".swift":
            lines = scan_lines(path, SWIFT, hits, lambda l: l.strip().startswith("//"))
            covered = -1
            for i, line in enumerate(lines):
                if i <= covered or line.strip().startswith("//"):
                    continue
                stmt = line
                if line.count("(") > line.count(")"):
                    # modifier arguments split across lines: `.background(\n cond ? token : Color.white, ...`
                    stmt = " ".join(l.strip() for l in lines[i:i + 4])
                if not SWIFT_FIXED_BG.search(stmt):
                    continue
                if stmt is not line:
                    covered = i + 3
                # If the statement sets its own foreground, judge by that; otherwise look nearby.
                window = [stmt] if SWIFT_FG.search(stmt) else lines[max(0, i - WINDOW): i + WINDOW + 1]
                adaptive = []
                for w in window:
                    for arg in SWIFT_FG.findall(w):
                        # conditional styles ("a ? .white : token") count if any branch adapts
                        branches = re.split(r"[?:]", arg)[-2:] if "?" in arg else [arg]
                        if any(b.strip() and not SWIFT_FIXED_ARG.search(b) for b in branches):
                            adaptive.append(arg.strip())
                if adaptive:
                    hits.append(("high", "mix", path, i + 1, stmt.strip()[:140],
                                 f"Fixed background next to adaptive foreground ({adaptive[0][:50]}): text likely vanishes in one theme"))
        elif ext in (".kt", ".kts"):
            lines = scan_lines(path, KOTLIN, hits, lambda l: l.strip().startswith("//"))
            text = "".join(lines)
            if KOTLIN_FIXED_BG.search(text) and KOTLIN_ADAPTIVE_FG.search(text):
                hits.append(("high", "mix", path, 0, "", "Fixed background AND theme 'on' colors in the same file: likely a fixed/adaptive mix"))
        elif ext == ".xml":
            if os.sep + "layout" in dirpath:
                scan_lines(path, XML, hits)
            if os.path.basename(dirpath).startswith("values-night"):
                night_values = True
            if os.path.basename(dirpath) == "values" and name == "colors.xml":
                day_colors.append(path)
        elif ext in (".css", ".scss", ".sass", ".less"):
            web_files += 1
            lines = scan_lines(path, CSS, hits, lambda l: l.strip().startswith(("/*", "*", "//")))
            if any("color-scheme" in l for l in lines):
                has_color_scheme_decl = True
        elif ext in (".tsx", ".jsx", ".html", ".vue", ".svelte", ".astro"):
            web_files += 1
            lines = scan_lines(path, MARKUP, hits, lambda l: "dark:" in l)
            if any("color-scheme" in l for l in lines):
                has_color_scheme_decl = True
        elif name == "Contents.json" and dirpath.endswith(".colorset"):
            try:
                data = json.load(open(path))
                has_dark = any(
                    any(a.get("value") == "dark" for a in c.get("appearances", []))
                    for c in data.get("colors", [])
                )
                if not has_dark:
                    hits.append(("high", "asset-no-dark", dirpath, 0, "", "Color set has no Dark appearance"))
            except (OSError, ValueError):
                pass

    if day_colors and not night_values:
        hits.append(("warn", "android-no-night", day_colors[0], 0, "", "colors.xml found but no values-night/ resources"))
    if web_files and not has_color_scheme_decl:
        hits.append(("warn", "web-no-color-scheme", root, 0, "", "No `color-scheme` declaration found: native inputs and scrollbars may stay light in dark mode"))

    mixed = {(h[2], h[3]) for h in hits if h[1] in ("mix", "tw-mix")}
    hits = [h for h in hits if not (h[1] in ("fixed-bg", "tw-no-dark") and (h[2], h[3]) in mixed)]
    order = {"high": 0, "warn": 1, "info": 2}
    hits.sort(key=lambda h: (order[h[0]], h[1], h[2], h[3]))
    if not hits:
        print("No theme issues found by static scan. Still render both themes to confirm.")
        return
    counts = {}
    shown = {}
    for sev, rid, path, line, snippet, msg in hits:
        counts[(sev, rid)] = counts.get((sev, rid), 0) + 1
        if shown.get(rid, 0) >= max_per_rule:
            continue
        shown[rid] = shown.get(rid, 0) + 1
        loc = f"{os.path.relpath(path, root)}:{line}" if line else os.path.relpath(path, root)
        print(f"[{sev.upper():4}] {rid:18} {loc}")
        print(f"       {msg}")
        if snippet:
            print(f"       > {snippet}")
    print("\nSummary:")
    for (sev, rid), n in sorted(counts.items(), key=lambda kv: (order[kv[0][0]], kv[0][1])):
        print(f"  {sev:4} {rid:18} {n}")
    print("Hits are leads, not verdicts. Confirm by rendering both themes.")


if __name__ == "__main__":
    main()
