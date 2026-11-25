#!/usr/bin/env python3
"""Generate the Ember icon theme.

Original line-art icons, CC BY-SA 4.0. The set is deliberately small: the
menus use these generic names, while individual applications keep their own
icons. Anything not present falls back to Papirus/Adwaita/hicolor.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "desktop" / "icons" / "Ember"
SIZES = (16, 24, 32, 48, 64, 128, 256)
EMBER = "#F26A3D"
AMBER = "#FFB35C"
ASH = "#A6AEBB"
TEAL = "#3FA796"
DARK = "#1B2027"
LINE = "#2A313B"
FLAME = (
    "M256 36 C274 132 306 214 340 272 C368 320 356 388 314 426 "
    "C292 446 268 456 256 458 C238 454 214 440 196 418 "
    "C166 382 162 326 186 282 C214 232 238 152 256 36 Z"
)

# Each glyph lives in a 48x48 viewBox, drawn with 2.2 px strokes so it stays
# legible at 16 px.
GLYPHS: dict[str, str] = {
    "web-browser": f"""
      <circle cx="24" cy="24" r="14" fill="none" stroke="{EMBER}" stroke-width="2.4"/>
      <ellipse cx="24" cy="24" rx="6.5" ry="14" fill="none" stroke="{AMBER}" stroke-width="1.7"/>
      <path d="M10.5 19 H37.5 M10.5 29 H37.5" stroke="{ASH}" stroke-width="1.7"/>
      <circle cx="33" cy="14" r="3.2" fill="{AMBER}"/>
    """,
    "system-file-manager": f"""
      <path d="M8 15 C8 12.8 9.8 11 12 11 H20 L24 15 H36 C38.2 15 40 16.8 40 19 V34 C40 36.2 38.2 38 36 38 H12 C9.8 38 8 36.2 8 34 Z"
            fill="none" stroke="{AMBER}" stroke-width="2.4" stroke-linejoin="round"/>
      <path d="M8 21 H40" stroke="{EMBER}" stroke-width="2.2"/>
      <path d="M17 28 H31" stroke="{ASH}" stroke-width="1.8" stroke-linecap="round"/>
    """,
    "utilities-terminal": f"""
      <rect x="7" y="11" width="34" height="26" rx="5" fill="none" stroke="{ASH}" stroke-width="2.2"/>
      <path d="M13 20 L19 25 L13 30" fill="none" stroke="{EMBER}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M23 30 H32" stroke="{AMBER}" stroke-width="2.6" stroke-linecap="round"/>
    """,
    "system-search": f"""
      <circle cx="21" cy="21" r="10" fill="none" stroke="{EMBER}" stroke-width="2.6"/>
      <path d="M28.5 28.5 L38 38" stroke="{AMBER}" stroke-width="3" stroke-linecap="round"/>
      <path d="M17 21 H25 M21 17 V25" stroke="{ASH}" stroke-width="1.5" stroke-linecap="round" opacity="0.75"/>
    """,
    "multimedia-volume-control": f"""
      <path d="M10 20 H16 L23 14 V34 L16 28 H10 Z" fill="none" stroke="{EMBER}" stroke-width="2.3" stroke-linejoin="round"/>
      <path d="M28 19 C30.5 21.2 30.5 26.8 28 29" fill="none" stroke="{AMBER}" stroke-width="2.2" stroke-linecap="round"/>
      <path d="M32.5 15.5 C37 19.5 37 28.5 32.5 32.5" fill="none" stroke="{AMBER}" stroke-width="2" stroke-linecap="round" opacity="0.7"/>
    """,
    "network-wireless": f"""
      <path d="M10 21 C17.5 14 30.5 14 38 21" fill="none" stroke="{EMBER}" stroke-width="2.4" stroke-linecap="round"/>
      <path d="M14.5 26 C19.5 21.5 28.5 21.5 33.5 26" fill="none" stroke="{AMBER}" stroke-width="2.3" stroke-linecap="round"/>
      <path d="M19 31 C21.7 28.6 26.3 28.6 29 31" fill="none" stroke="{ASH}" stroke-width="2.2" stroke-linecap="round"/>
      <circle cx="24" cy="36" r="2.4" fill="{AMBER}"/>
    """,
    "preferences-system": f"""
      <path d="M10 16 H38 M10 24 H38 M10 32 H38" stroke="{ASH}" stroke-width="2.2" stroke-linecap="round"/>
      <circle cx="18" cy="16" r="3.2" fill="{DARK}" stroke="{EMBER}" stroke-width="2.2"/>
      <circle cx="30" cy="24" r="3.2" fill="{DARK}" stroke="{AMBER}" stroke-width="2.2"/>
      <circle cx="21" cy="32" r="3.2" fill="{DARK}" stroke="{TEAL}" stroke-width="2.2"/>
    """,
    "applications-system": f"""
      <rect x="10" y="10" width="12" height="12" rx="3" fill="none" stroke="{EMBER}" stroke-width="2.2"/>
      <rect x="26" y="10" width="12" height="12" rx="3" fill="none" stroke="{AMBER}" stroke-width="2.2"/>
      <rect x="10" y="26" width="12" height="12" rx="3" fill="none" stroke="{TEAL}" stroke-width="2.2"/>
      <rect x="26" y="26" width="12" height="12" rx="3" fill="none" stroke="{ASH}" stroke-width="2.2"/>
    """,
    "help-browser": f"""
      <circle cx="24" cy="24" r="14" fill="none" stroke="{AMBER}" stroke-width="2.4"/>
      <path d="M19.5 20 C19.5 16.8 22 15.5 24.2 15.5 C27 15.5 29 17.4 29 20 C29 23.8 24 24 24 28" fill="none" stroke="{EMBER}" stroke-width="2.6" stroke-linecap="round"/>
      <circle cx="24" cy="33" r="1.8" fill="{EMBER}"/>
    """,
    "help-about": f"""
      <circle cx="24" cy="24" r="14" fill="none" stroke="{AMBER}" stroke-width="2.4"/>
      <path d="M24 21 V33" stroke="{EMBER}" stroke-width="2.8" stroke-linecap="round"/>
      <circle cx="24" cy="15.8" r="1.9" fill="{EMBER}"/>
    """,
    "dialog-information": f"""
      <path d="M9 12 H39 C40.7 12 42 13.3 42 15 V30 C42 31.7 40.7 33 39 33 H25 L18 39 V33 H9 C7.3 33 6 31.7 6 30 V15 C6 13.3 7.3 12 9 12 Z"
            fill="none" stroke="{AMBER}" stroke-width="2.2" stroke-linejoin="round"/>
      <path d="M24 18 V27" stroke="{EMBER}" stroke-width="2.7" stroke-linecap="round"/>
      <circle cx="24" cy="29.6" r="1.5" fill="{EMBER}"/>
    """,
    "text-editor": f"""
      <path d="M12 8 H29 L37 16 V38 C37 39.7 35.7 41 34 41 H12 C10.3 41 9 39.7 9 38 V11 C9 9.3 10.3 8 12 8 Z"
            fill="none" stroke="{ASH}" stroke-width="2.2" stroke-linejoin="round"/>
      <path d="M29 8 V16 H37" fill="none" stroke="{ASH}" stroke-width="2.2" stroke-linejoin="round"/>
      <path d="M15 24 H31 M15 30 H27" stroke="{EMBER}" stroke-width="2" stroke-linecap="round"/>
    """,
    "system-shutdown": f"""
      <path d="M24 9 V24" stroke="{EMBER}" stroke-width="3" stroke-linecap="round"/>
      <path d="M15.5 15.5 C11 20 11.5 29 16.5 33.5 C21.5 38 29.5 37.5 34 32.5 C38 28 38 21 34 16.5"
            fill="none" stroke="{AMBER}" stroke-width="2.6" stroke-linecap="round"/>
    """,
    "ember-welcome": f"""
      <circle cx="24" cy="24" r="19" fill="{DARK}" stroke="{LINE}" stroke-width="1.4"/>
      <g transform="translate(6.7 7.7) scale(0.0664)">
        <path d="{FLAME}" fill="{EMBER}"/>
        <path d="M256 44 C248 166 246 324 258 450" fill="none" stroke="#14171C" stroke-opacity="0.3" stroke-width="10"/>
      </g>
      <circle cx="14" cy="17" r="1.8" fill="{AMBER}"/>
      <circle cx="34" cy="14" r="1.2" fill="{AMBER}"/>
    """,
    "ember-about": f"""
      <circle cx="24" cy="24" r="19" fill="{DARK}" stroke="{LINE}" stroke-width="1.4"/>
      <g transform="translate(7.6 8.4) scale(0.06)">
        <path d="{FLAME}" fill="none" stroke="{EMBER}" stroke-width="34"/>
      </g>
      <circle cx="24" cy="16" r="1.5" fill="{AMBER}"/>
    """,
}

ALIASES = {
    "applications-internet": "web-browser",
    "system-run": "system-search",
    "preferences-desktop": "preferences-system",
    "preferences-other": "preferences-system",
    "applications-other": "applications-system",
}


def svg(name: str, body: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48">
  <title>{name}</title>
  <g stroke-linecap="round" stroke-linejoin="round">{body}</g>
</svg>
"""


def main() -> None:
    scalable = OUT / "scalable" / "apps"
    scalable.mkdir(parents=True, exist_ok=True)
    sources: dict[str, str] = {}
    for name, body in GLYPHS.items():
        content = svg(name, body)
        (scalable / f"{name}.svg").write_text(content, encoding="utf-8")
        sources[name] = content
    for alias, target in ALIASES.items():
        (scalable / f"{alias}.svg").write_text(sources[target], encoding="utf-8")

    for size in SIZES:
        d = OUT / f"{size}x{size}" / "apps"
        d.mkdir(parents=True, exist_ok=True)
        for name, content in sources.items():
            tmp = Path("/tmp/opencode") / f"icon-{name}-{size}.svg"
            tmp.write_text(content, encoding="utf-8")
            subprocess.run(
                ["rsvg-convert", "-o", str(d / f"{name}.png"), "-w", str(size), "-h", str(size), str(tmp)],
                check=True,
            )
        for alias, target in ALIASES.items():
            subprocess.run(["cp", str(d / f"{target}.png"), str(d / f"{alias}.png")], check=True)

    dirs = ",".join([f"{s}x{s}/apps" for s in SIZES] + ["scalable/apps"])
    sections = "\n\n".join(
        f"""[{s}x{s}/apps]
Size={s}
Context=Applications
Type=Fixed"""
        for s in SIZES
    )
    sections += """

[scalable/apps]
Size=48
MinSize=16
MaxSize=512
Context=Applications
Type=Scalable"""
    (OUT / "index.theme").write_text(
        f"""[Icon Theme]
Name=Ember
Comment=Ember Linux icon theme
Inherits=Papirus,Adwaita,breeze_cursors,hicolor
Directories={dirs}

{sections}
""",
        encoding="utf-8",
    )
    print(f"icons written to {OUT} ({len(sources)} icons, {len(SIZES)} sizes)")


if __name__ == "__main__":
    main()
