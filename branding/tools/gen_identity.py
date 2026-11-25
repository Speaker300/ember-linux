#!/usr/bin/env python3
"""Generate the Ember Linux identity (mark, badge, wordmark, lockups).

Original artwork, CC BY-SA 4.0. Requires fontTools (only for wordmark paths).
Run from the branding/ directory:  python3 tools/gen_identity.py
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "identity"
FONT_DIR = ROOT / "desktop" / "fonts" / "inter"

INK = "#14171C"
BASALT = "#1B2027"
FROST = "#F4F6F8"
EMBER = "#F26A3D"
AMBER = "#FFB35C"
SAND = "#FFD9A0"

FLAME = (
    "M256 36 "
    "C274 132 306 214 340 272 "
    "C368 320 356 388 314 426 "
    "C292 446 268 456 256 458 "
    "C238 454 214 440 196 418 "
    "C166 382 162 326 186 282 "
    "C214 232 238 152 256 36 Z"
)


def mark_defs() -> str:
    return f"""
  <defs>
    <linearGradient id="flameLeft" x1="170" y1="90" x2="270" y2="450" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#FFE1B4"/>
      <stop offset="0.32" stop-color="{AMBER}"/>
      <stop offset="0.72" stop-color="{EMBER}"/>
      <stop offset="1" stop-color="#E2502D"/>
    </linearGradient>
    <linearGradient id="flameRight" x1="342" y1="120" x2="240" y2="460" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#FF9A62"/>
      <stop offset="0.38" stop-color="{EMBER}"/>
      <stop offset="0.78" stop-color="#D8432A"/>
      <stop offset="1" stop-color="#A92E1E"/>
    </linearGradient>
    <linearGradient id="spark" x1="140" y1="160" x2="170" y2="200" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{SAND}"/>
      <stop offset="1" stop-color="{AMBER}"/>
    </linearGradient>
    <linearGradient id="badgeBg" x1="80" y1="40" x2="430" y2="480" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#222831"/>
      <stop offset="0.55" stop-color="{BASALT}"/>
      <stop offset="1" stop-color="#0F1216"/>
    </linearGradient>
    <filter id="softGlow" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="24"/>
    </filter>
    <radialGradient id="markGlow" cx="256" cy="330" r="205" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{EMBER}" stop-opacity="0.20"/>
      <stop offset="1" stop-color="{EMBER}" stop-opacity="0"/>
    </radialGradient>
    <clipPath id="leftHalf"><rect x="0" y="0" width="256" height="512"/></clipPath>
    <clipPath id="rightHalf"><rect x="256" y="0" width="256" height="512"/></clipPath>
  </defs>"""


def mark_group(with_glow: bool = False) -> str:
    glow = '<circle cx="256" cy="330" r="205" fill="url(#markGlow)"/>' if with_glow else ""
    return f"""
  <g id="ember-mark">
    {glow}
    <path d="{FLAME}" fill="url(#flameLeft)" clip-path="url(#leftHalf)"/>
    <path d="{FLAME}" fill="url(#flameRight)" clip-path="url(#rightHalf)"/>
    <path d="M256 44 C248 166 246 324 258 450" fill="none" stroke="{INK}" stroke-opacity="0.24" stroke-width="7" stroke-linecap="round"/>
    <path d="M256 38 C238 152 214 232 186 282 C162 326 166 382 196 418 C214 440 238 454 256 458" fill="none" stroke="#FFE7C4" stroke-opacity="0.30" stroke-width="4" stroke-linecap="round"/>
    <path d="M296 292 C300 354 286 404 262 436" fill="none" stroke="{SAND}" stroke-opacity="0.22" stroke-width="3" stroke-linecap="round"/>
    <path d="M264 186 C250 238 246 294 252 344" fill="none" stroke="{SAND}" stroke-opacity="0.50" stroke-width="3" stroke-linecap="round"/>
    <circle cx="156" cy="206" r="11" fill="url(#spark)"/>
    <circle cx="372" cy="162" r="7" fill="{AMBER}"/>
    <circle cx="398" cy="238" r="4" fill="{SAND}" opacity="0.9"/>
    <circle cx="126" cy="302" r="3.5" fill="{EMBER}" opacity="0.85"/>
  </g>"""


def svg_mark() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512" role="img" aria-label="Ember Linux mark">
  <title>Ember Linux mark</title>{mark_defs()}
{mark_group()}
</svg>
"""


def svg_badge() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512" role="img" aria-label="Ember Linux logo">
  <title>Ember Linux logo</title>{mark_defs()}
  <rect x="16" y="16" width="480" height="480" rx="108" fill="url(#badgeBg)"/>
  <rect x="16.75" y="16.75" width="478.5" height="478.5" rx="107.25" fill="none" stroke="#39414D" stroke-opacity="0.65" stroke-width="1.5"/>
  <path d="{FLAME}" transform="translate(64 54) scale(0.75)" fill="{EMBER}" opacity="0.22" filter="url(#softGlow)"/>
  <g transform="translate(56 42) scale(0.78)">
{mark_group()}
  </g>
  <path d="M156 92 C 220 54 310 58 366 104" fill="none" stroke="{FROST}" stroke-opacity="0.07" stroke-width="2"/>
</svg>
"""


def svg_mark_mono(color: str = FROST) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512" role="img" aria-label="Ember Linux mark (monochrome)">
  <title>Ember Linux mark, monochrome</title>
  <path d="{FLAME}" fill="{color}"/>
  <circle cx="152" cy="182" r="10" fill="{color}"/>
  <circle cx="374" cy="146" r="6.5" fill="{color}"/>
  <circle cx="400" cy="226" r="4" fill="{color}"/>
</svg>
"""


# ---------------------------------------------------------------- wordmark --


def text_paths(
    text: str,
    font_path: Path,
    size: float,
    x: float,
    baseline: float,
    tracking: float = 0.0,
) -> tuple[str, float]:
    font = TTFont(str(font_path))
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]
    upm = font["head"].unitsPerEm
    scale = size / upm
    parts: list[str] = []
    cursor = x
    for ch in text:
        name = cmap[ord(ch)]
        pen = SVGPathPen(glyph_set)
        tpen = TransformPen(pen, (scale, 0, 0, -scale, cursor, baseline))
        glyph_set[name].draw(tpen)
        parts.append(pen.getCommands())
        cursor += hmtx[name][0] * scale + tracking
    return " ".join(parts), cursor - x - tracking


def wordmark_svg(color: str = FROST, accent: str = EMBER, dark: bool = False) -> str:
    base = 190
    path, width = text_paths("ember", FONT_DIR / "Inter-Bold.ttf", 156, 24, base, tracking=-3.2)
    sub_path, sub_width = text_paths(
        "LINUX", FONT_DIR / "Inter-SemiBold.ttf", 39, 31, base + 58, tracking=15.5
    )
    total_w = max(width + 48, sub_width + 64, 640)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {int(total_w)} 300" width="{int(total_w)}" height="300" role="img" aria-label="Ember Linux wordmark">
  <title>Ember Linux wordmark</title>
  <path d="{path}" fill="{color}"/>
  <path d="{sub_path}" fill="{accent}"/>
</svg>
"""


def lockup_svg(dark: bool = False) -> str:
    fg = INK if dark else FROST
    badge = svg_badge()
    # Inline the badge group only (drop the outer <svg>).
    inner = badge.split(">", 1)[1].rsplit("</svg>", 1)[0]
    base = 226
    path, width = text_paths("ember", FONT_DIR / "Inter-Bold.ttf", 150, 300, base, tracking=-3.0)
    sub_path, _ = text_paths("LINUX", FONT_DIR / "Inter-SemiBold.ttf", 37, 307, base + 56, tracking=15)
    total_w = int(max(width + 340, 900))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_w} 320" width="{total_w}" height="320" role="img" aria-label="Ember Linux">
  <title>Ember Linux</title>
  <g transform="translate(28 20) scale(0.546875)">
{inner}
  </g>
  <path d="{path}" fill="{fg}"/>
  <path d="{sub_path}" fill="{EMBER}"/>
</svg>
"""


# ------------------------------------------------------------------- build --


def render(svg: str, out: Path, width: int | None = None, height: int | None = None) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".tmp.svg")
    tmp.write_text(svg, encoding="utf-8")
    cmd = ["rsvg-convert", "-o", str(out)]
    if width:
        cmd += ["-w", str(width)]
    if height:
        cmd += ["-h", str(height)]
    cmd.append(str(tmp))
    subprocess.run(cmd, check=True)
    tmp.unlink()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    files = {
        "ember-mark.svg": svg_mark(),
        "ember-logo.svg": svg_badge(),
        "ember-mark-mono-light.svg": svg_mark_mono(FROST),
        "ember-mark-mono-dark.svg": svg_mark_mono(INK),
        "ember-wordmark.svg": wordmark_svg(FROST),
        "ember-wordmark-dark.svg": wordmark_svg(INK),
        "ember-lockup.svg": lockup_svg(False),
        "ember-lockup-dark.svg": lockup_svg(True),
    }
    for name, content in files.items():
        (OUT / name).write_text(content, encoding="utf-8")

    # Square mark/badge PNGs at the sizes desktop environments ask for.
    for size in (1024, 512, 256, 128, 64, 48, 32):
        render(svg_badge(), OUT / f"ember-logo-{size}.png", size, size)
    for size in (512, 256, 128, 64, 48, 32):
        render(svg_mark(), OUT / f"ember-mark-{size}.png", size, size)

    render(svg_badge(), OUT / "ember-logo.png", 512, 512)
    render(svg_mark(), OUT / "ember-mark.png", 512, 512)

    # Wordmark and lockup rasters (transparent).
    for dark in (False, True):
        suffix = "-dark" if dark else ""
        render(wordmark_svg(INK if dark else FROST), OUT / f"ember-wordmark{suffix}.png", 1200)
        render(lockup_svg(dark), OUT / f"ember-lockup{suffix}.png", 1600)

    # 16:9 social / README banner with the badge centred on the brand ink.
    banner = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 500" width="1600" height="500">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1600" y2="500" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#101317"/><stop offset="0.55" stop-color="{BASALT}"/><stop offset="1" stop-color="#201512"/>
    </linearGradient>
    <radialGradient id="glow" cx="800" cy="330" r="520" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{EMBER}" stop-opacity="0.22"/><stop offset="1" stop-color="{EMBER}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="1600" height="500" fill="url(#bg)"/>
  <rect width="1600" height="500" fill="url(#glow)"/>
  <g transform="translate(560 60) scale(0.742)">{svg_badge().split('>',1)[1].rsplit('</svg>',1)[0]}</g>
  <text x="800" y="472" text-anchor="middle" font-family="Inter, Noto Sans, sans-serif" font-size="26" letter-spacing="14" fill="{AMBER}" opacity="0.9">GENTOO-BASED · BUILT WITH CARE</text>
</svg>
"""
    render(banner, OUT / "ember-banner.png", 1600, 500)
    print("identity written to", OUT)


if __name__ == "__main__":
    main()
