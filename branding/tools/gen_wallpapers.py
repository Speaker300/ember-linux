#!/usr/bin/env python3
"""Generate Ember Linux wallpapers and boot/session backgrounds.

All artwork is original vector work, CC BY-SA 4.0.
Usage: python3 tools/gen_wallpapers.py
"""
from __future__ import annotations

import math
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "wallpapers"

INK = "#14171C"
BASALT = "#1B2027"
EMBER = "#F26A3D"
AMBER = "#FFB35C"
SAND = "#FFD9A0"
TEAL = "#3FA796"
FLAME = (
    "M256 36 "
    "C274 132 306 214 340 272 "
    "C368 320 356 388 314 426 "
    "C292 446 268 456 256 458 "
    "C238 454 214 440 196 418 "
    "C166 382 162 326 186 282 "
    "C214 232 238 152 256 36 Z"
)


def defs() -> str:
    return f"""
  <defs>
    <linearGradient id="base" x1="0" y1="0" x2="0" y2="1080" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#0A0D11"/>
      <stop offset="0.46" stop-color="{INK}"/>
      <stop offset="0.82" stop-color="#1B1716"/>
      <stop offset="1" stop-color="#221712"/>
    </linearGradient>
    <radialGradient id="warm" cx="1460" cy="930" r="1050" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{EMBER}" stop-opacity="0.34"/>
      <stop offset="0.38" stop-color="#D8432A" stop-opacity="0.13"/>
      <stop offset="0.72" stop-color="#8C2F20" stop-opacity="0.04"/>
      <stop offset="1" stop-color="#8C2F20" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="cool" cx="240" cy="90" r="980" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{TEAL}" stop-opacity="0.12"/>
      <stop offset="0.55" stop-color="{TEAL}" stop-opacity="0.035"/>
      <stop offset="1" stop-color="{TEAL}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="vignette" cx="960" cy="540" r="1080" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#000000" stop-opacity="0"/>
      <stop offset="0.62" stop-color="#000000" stop-opacity="0.04"/>
      <stop offset="1" stop-color="#000000" stop-opacity="0.62"/>
    </radialGradient>
    <linearGradient id="emberLine" x1="0" y1="0" x2="1920" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{EMBER}" stop-opacity="0"/>
      <stop offset="0.42" stop-color="{AMBER}" stop-opacity="0.28"/>
      <stop offset="0.78" stop-color="{EMBER}" stop-opacity="0.18"/>
      <stop offset="1" stop-color="{EMBER}" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="rightFade" x1="0" y1="0" x2="1920" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#000000" stop-opacity="0"/>
      <stop offset="0.55" stop-color="#000000" stop-opacity="0"/>
      <stop offset="1" stop-color="#000000" stop-opacity="0.22"/>
    </linearGradient>
    <linearGradient id="markFade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{AMBER}" stop-opacity="0.10"/>
      <stop offset="1" stop-color="{EMBER}" stop-opacity="0.015"/>
    </linearGradient>
    <filter id="blur18" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="18"/>
    </filter>
  </defs>"""


def ridge_lines(count: int = 19, opacity: float = 0.14) -> str:
    """Hand-drawn-looking contour lines across the lower third."""
    parts = []
    for i in range(count):
        base = 700 + i * 19
        amp = 10 + i * 2.1
        phase = i * 0.55
        points = []
        for step in range(0, 49):
            x = -120 + step * 45
            y = (
                base
                + amp * math.sin(x / 230.0 + phase)
                + amp * 0.45 * math.sin(x / 91.0 + phase * 1.7)
                + amp * 0.18 * math.sin(x / 37.0 + phase * 2.3)
            )
            points.append(f"{x:.1f},{y:.1f}")
        # A couple of deliberately broken lines keep it from looking generated.
        if i in (5, 12):
            pts = " ".join(points[:28] + points[33:])
        else:
            pts = " ".join(points)
        o = opacity * (1.0 - i / (count + 3))
        parts.append(
            f'<polyline points="{pts}" fill="none" stroke="{AMBER}" '
            f'stroke-opacity="{o:.3f}" stroke-width="{1.35 if i % 3 else 1.9:.1f}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>'
        )
    return "\n  ".join(parts)


def specks(seed: int = 7, count: int = 26, max_y: int = 780) -> str:
    parts = []
    x = seed * 137
    for i in range(count):
        x = (x * 1103515245 + 12345 + i * 7919) % 1920
        y = (i * 149 + seed * 83 + (i * i * 37)) % max_y
        r = 0.9 + ((i * 17) % 9) / 4.0
        o = 0.10 + ((i * 13) % 11) / 45.0
        parts.append(
            f'<circle cx="{x}" cy="{y + 60}" r="{r:.1f}" fill="{AMBER}" opacity="{o:.2f}"/>'
        )
    return " ".join(parts)


def wallpaper_ridge() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" width="1920" height="1080">
  <title>Ember Ridge</title>{defs()}
  <rect width="1920" height="1080" fill="url(#base)"/>
  <rect width="1920" height="1080" fill="url(#cool)"/>
  <rect width="1920" height="1080" fill="url(#warm)"/>
  <g transform="translate(1452 250) scale(2.05) rotate(-6 256 256)">
    <path d="{FLAME}" fill="url(#markFade)"/>
    <path d="{FLAME}" fill="none" stroke="{AMBER}" stroke-opacity="0.10" stroke-width="2.2"/>
    <path d="M256 44 C248 166 246 324 258 450" fill="none" stroke="{AMBER}" stroke-opacity="0.08" stroke-width="2"/>
  </g>
  <ellipse cx="1460" cy="1005" rx="720" ry="120" fill="{EMBER}" opacity="0.10" filter="url(#blur18)"/>
  <path d="M-80 812 C 340 760 620 828 980 800 C 1300 774 1590 806 2000 770"
        fill="none" stroke="url(#emberLine)" stroke-width="2"/>
  <g>{ridge_lines()}</g>
  <rect width="1920" height="1080" fill="url(#rightFade)" opacity="0.5"/>
  <g>{specks()}</g>
  <rect width="1920" height="1080" fill="url(#vignette)"/>
</svg>
"""


def wallpaper_halo() -> str:
    rings = []
    for i in range(7):
        r = 268 + i * 58
        rings.append(
            f'<circle cx="1490" cy="286" r="{r}" fill="none" stroke="{AMBER}" '
            f'stroke-opacity="{0.060 - i * 0.006:.3f}" stroke-width="1.1"/>'
        )
    stars = []
    for i in range(34):
        x = (i * 353 + 91) % 1880 + 20
        y = (i * 197 + 37) % 620 + 30
        if (x - 1490) ** 2 + (y - 286) ** 2 < 240**2:
            continue
        o = 0.10 + ((i * 7) % 9) / 60.0
        r = 0.8 + ((i * 11) % 5) / 5.0
        stars.append(f'<circle cx="{x}" cy="{y}" r="{r:.1f}" fill="{SAND}" opacity="{o:.2f}"/>')
    hill = "M0 878 C 260 838 470 892 700 872 C 940 850 1110 792 1350 806 C 1600 820 1770 868 1920 850 L1920 1080 L0 1080 Z"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" width="1920" height="1080">
  <title>Ember Halo</title>{defs()}
  <rect width="1920" height="1080" fill="#0A0C10"/>
  <rect width="1920" height="1080" fill="url(#cool)" opacity="0.5"/>
  <rect width="1920" height="1080" fill="url(#warm)" opacity="0.30"/>
  <circle cx="1490" cy="286" r="196" fill="{AMBER}" opacity="0.30" filter="url(#blur18)"/>
  <circle cx="1490" cy="286" r="182" fill="#0B0E12" stroke="{AMBER}" stroke-opacity="0.62" stroke-width="2"/>
  <circle cx="1490" cy="286" r="188" fill="none" stroke="{SAND}" stroke-opacity="0.18" stroke-width="8" filter="url(#blur18)"/>
  <path d="M1352 178 A 182 182 0 0 1 1632 230" fill="none" stroke="{SAND}" stroke-opacity="0.55" stroke-width="2.2" stroke-linecap="round"/>
  <g>{''.join(rings)}</g>
  <g>{''.join(stars)}</g>
  <path d="{hill}" fill="#07090C" opacity="0.94"/>
  <path d="{hill}" fill="none" stroke="url(#emberLine)" stroke-width="1.7"/>
  <path d="M0 960 C 340 930 620 972 920 954 C 1240 934 1560 968 1920 944"
        fill="none" stroke="{EMBER}" stroke-opacity="0.10" stroke-width="1.1"/>
  <g transform="translate(240 560) scale(0.52) rotate(6 256 256)">
    <path d="{FLAME}" fill="none" stroke="{AMBER}" stroke-opacity="0.10" stroke-width="4"/>
  </g>
  <rect width="1920" height="1080" fill="url(#vignette)" opacity="0.9"/>
</svg>
"""


def wallpaper_login() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" width="1920" height="1080">
  <title>Ember login background</title>{defs()}
  <rect width="1920" height="1080" fill="url(#base)"/>
  <rect width="1920" height="1080" fill="url(#cool)" opacity="0.7"/>
  <rect width="1920" height="1080" fill="url(#warm)"/>
  <g transform="translate(1320 318) scale(1.28) rotate(-5 256 256)">
    <path d="{FLAME}" fill="url(#markFade)" opacity="0.8"/>
    <path d="{FLAME}" fill="none" stroke="{AMBER}" stroke-opacity="0.13" stroke-width="2"/>
  </g>
  <g>{ridge_lines(13, 0.10)}</g>
  <rect x="0" y="0" width="1920" height="1080" fill="#05070A" opacity="0.28"/>
  <rect width="1920" height="1080" fill="url(#vignette)"/>
</svg>
"""


def wallpaper_grub() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" width="1920" height="1080">
  <title>Ember GRUB background</title>{defs()}
  <rect width="1920" height="1080" fill="#0A0C10"/>
  <rect width="1920" height="1080" fill="url(#warm)" opacity="0.55"/>
  <rect x="0" y="0" width="1120" height="1080" fill="#0B0E12" opacity="0.72"/>
  <g transform="translate(1280 260) scale(1.55) rotate(-8 256 256)">
    <path d="{FLAME}" fill="url(#markFade)"/>
    <path d="{FLAME}" fill="none" stroke="{AMBER}" stroke-opacity="0.16" stroke-width="2.4"/>
  </g>
  <path d="M1120 0 V1080" stroke="{EMBER}" stroke-opacity="0.12" stroke-width="1.4"/>
  <g>{specks(23, 16, 760)}</g>
  <rect width="1920" height="1080" fill="url(#vignette)" opacity="0.55"/>
</svg>
"""


def wallpaper_plymouth() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" width="1920" height="1080">
  <title>Ember Plymouth background</title>{defs()}
  <rect width="1920" height="1080" fill="#0A0C10"/>
  <rect width="1920" height="1080" fill="url(#warm)" opacity="0.42"/>
  <ellipse cx="960" cy="520" rx="420" ry="300" fill="{EMBER}" opacity="0.05" filter="url(#blur18)"/>
  <path d="M0 890 C 420 856 700 906 960 886 C 1260 864 1580 900 1920 870"
        fill="none" stroke="url(#emberLine)" stroke-width="1.2"/>
  <g>{specks(31, 12, 500)}</g>
  <rect width="1920" height="1080" fill="url(#vignette)" opacity="0.7"/>
</svg>
"""


def wallpaper_calamares() -> str:
    """16:10 product wallpaper for the installer window (800x520 @2x)."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1040" width="1600" height="1040">
  <title>Ember Calamares background</title>
  <defs>
    <linearGradient id="cbg" x1="0" y1="0" x2="0" y2="1040" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#0D1014"/><stop offset="0.62" stop-color="#14171C"/><stop offset="1" stop-color="#1A1513"/>
    </linearGradient>
    <radialGradient id="cglow" cx="1360" cy="940" r="900" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{EMBER}" stop-opacity="0.20"/>
      <stop offset="0.55" stop-color="{EMBER}" stop-opacity="0.04"/>
      <stop offset="1" stop-color="{EMBER}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="cmark" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="{AMBER}" stop-opacity="0.10"/>
      <stop offset="1" stop-color="{EMBER}" stop-opacity="0.01"/>
    </radialGradient>
  </defs>
  <rect width="1600" height="1040" fill="url(#cbg)"/>
  <rect width="1600" height="1040" fill="url(#cglow)"/>
  <g transform="translate(1090 210) scale(1.35) rotate(-8 256 256)">
    <path d="{FLAME}" fill="url(#cmark)"/>
    <path d="{FLAME}" fill="none" stroke="{AMBER}" stroke-opacity="0.08" stroke-width="2"/>
  </g>
  <path d="M0 1012 C 360 980 620 1018 960 996 C 1230 978 1460 1004 1600 986"
        fill="none" stroke="url(#emberLine)" stroke-width="1.2" opacity="0.6"/>
</svg>
"""


def render(svg: str, name: str, width: int, height: int) -> None:
    d = OUT / f"{width}x{height}"
    d.mkdir(parents=True, exist_ok=True)
    tmp = Path("/tmp/opencode") / f"{name}-{width}.svg"
    tmp.write_text(svg, encoding="utf-8")
    subprocess.run(
        ["rsvg-convert", "-o", str(d / f"{name}-{width}x{height}.png"),
         "-w", str(width), "-h", str(height), str(tmp)],
        check=True,
    )


def main() -> None:
    # Desktop wallpapers in both requested sizes.
    for name, svg in (("ember-ridge", wallpaper_ridge()), ("ember-halo", wallpaper_halo())):
        for w, h in ((1920, 1080), (2560, 1440)):
            render(svg, name, w, h)

    # Session and boot backgrounds.
    for name, svg in (
        ("ember-login", wallpaper_login()),
        ("ember-grub", wallpaper_grub()),
        ("ember-plymouth", wallpaper_plymouth()),
    ):
        render(svg, name, 1920, 1080)
        render(svg, name, 2560, 1440)

    render(wallpaper_calamares(), "ember-calamares", 1600, 1040)
    print("wallpapers written to", OUT)


if __name__ == "__main__":
    main()
