#!/usr/bin/env python3
"""Generate the Ember Xcursor theme.

Original cursor artwork, CC BY-SA 4.0. Cursors are drawn at 4x and written to
the Xcursor binary format directly (no xcursorgen dependency). Only the common
shapes are replaced; everything else inherits Adwaita/Breeze via index.theme.
"""
from __future__ import annotations

import struct
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "desktop" / "icons" / "Ember" / "cursors"
SIZES = (24, 32, 48)
SS = 4  # supersampling

WHITE = (244, 246, 248, 255)
INK = (20, 23, 28, 255)
EMBER = (242, 106, 61, 255)
AMBER = (255, 179, 92, 255)
RED = (229, 72, 77, 255)


def canvas(size: int):
    return Image.new("RGBA", (size * SS, size * SS), (0, 0, 0, 0))


def scaled(points, size):
    return [(x * size * SS / 32.0, y * size * SS / 32.0) for x, y in points]


def outlined_polygon(draw, points, size, fill=WHITE, outline=INK, width=1.6):
    pts = scaled(points, size)
    draw.line(pts + [pts[0]], fill=outline, width=max(1, round(width * SS)), joint="curve")
    draw.polygon(pts, fill=fill)


def outlined_line(draw, points, size, color=WHITE, outline=INK, width=2.2):
    pts = scaled(points, size)
    draw.line(pts, fill=outline, width=max(1, round((width + 1.4) * SS)), joint="curve")
    draw.line(pts, fill=color, width=max(1, round(width * SS)), joint="curve")


def outlined_ellipse(draw, box, size, fill=None, outline=INK, width=1.6):
    b = [v * size * SS / 32.0 for v in box]
    draw.ellipse(b, fill=fill, outline=outline, width=max(1, round(width * SS)))


def draw_left_ptr(size):
    im = canvas(size)
    d = ImageDraw.Draw(im)
    pts = [(3, 2), (3, 25), (9, 19), (14, 30), (19, 28), (14, 17), (23, 17)]
    outlined_polygon(d, pts, size, WHITE, INK, 1.7)
    # A small ember glint at the tip keeps the set recognisably Ember.
    d.line(scaled([(3.2, 3), (3.2, 12)], size), fill=EMBER, width=max(1, round(1.1 * SS)))
    return im, (3, 2)


def draw_hand(size):
    im = canvas(size)
    d = ImageDraw.Draw(im)
    pts = [
        (10, 24), (10, 16), (12, 14), (14, 16), (14, 19),
        (15, 18), (15, 10), (17, 8), (19, 10), (19, 18),
        (20, 18), (20, 13), (22, 11), (24, 13), (24, 18),
        (25, 18), (25, 15), (27, 15), (28, 17), (28, 25),
        (26, 30), (20, 32), (15, 31), (11, 28),
    ]
    outlined_polygon(d, pts, size, WHITE, INK, 1.5)
    d.line(scaled([(16, 21), (16, 27)], size), fill=AMBER, width=max(1, round(0.9 * SS)))
    return im, (16, 8)


def draw_xterm(size):
    im = canvas(size)
    d = ImageDraw.Draw(im)
    # I-beam
    for box in [(12, 6, 20, 8), (12, 24, 20, 26)]:
        b = [v * size * SS / 32.0 for v in box]
        d.rectangle(b, fill=WHITE, outline=INK, width=max(1, round(1.2 * SS)))
    outlined_line(d, [(16, 7), (16, 25)], size, WHITE, INK, 1.8)
    d.line(scaled([(16, 12), (16, 20)], size), fill=EMBER, width=max(1, round(0.8 * SS)))
    return im, (16, 16)


def draw_crosshair(size):
    im = canvas(size)
    d = ImageDraw.Draw(im)
    outlined_line(d, [(16, 4), (16, 28)], size, WHITE, INK, 1.2)
    outlined_line(d, [(4, 16), (28, 16)], size, WHITE, INK, 1.2)
    b = [14 * size * SS / 32, 14 * size * SS / 32, 18 * size * SS / 32, 18 * size * SS / 32]
    d.ellipse(b, fill=EMBER, outline=INK, width=max(1, round(0.7 * SS)))
    return im, (16, 16)


def draw_watch(size):
    im = canvas(size)
    d = ImageDraw.Draw(im)
    outlined_ellipse(d, (7, 7, 25, 25), size, (27, 32, 39, 255), AMBER, 1.8)
    outlined_line(d, [(16, 16), (16, 10)], size, WHITE, INK, 1.4)
    outlined_line(d, [(16, 16), (21, 18)], size, WHITE, INK, 1.4)
    d.ellipse([15 * size * SS / 32, 15 * size * SS / 32, 17 * size * SS / 32, 17 * size * SS / 32], fill=EMBER)
    return im, (16, 16)


def draw_resize(size, axis="h"):
    im = canvas(size)
    d = ImageDraw.Draw(im)
    if axis == "h":
        outlined_line(d, [(6, 16), (26, 16)], size, WHITE, INK, 1.8)
        outlined_polygon(d, [(3, 16), (8, 12), (8, 20)], size, WHITE, INK, 1.2)
        outlined_polygon(d, [(29, 16), (24, 12), (24, 20)], size, WHITE, INK, 1.2)
    elif axis == "v":
        outlined_line(d, [(16, 6), (16, 26)], size, WHITE, INK, 1.8)
        outlined_polygon(d, [(16, 3), (12, 8), (20, 8)], size, WHITE, INK, 1.2)
        outlined_polygon(d, [(16, 29), (12, 24), (20, 24)], size, WHITE, INK, 1.2)
    else:  # diagonal, bottom-left to top-right
        outlined_line(d, [(7, 25), (25, 7)], size, WHITE, INK, 1.7)
        outlined_polygon(d, [(4, 23), (6, 29), (10, 27)], size, WHITE, INK, 1.1)
        outlined_polygon(d, [(28, 9), (26, 3), (22, 5)], size, WHITE, INK, 1.1)
    return im, (16, 16)


def draw_fleur(size):
    im = canvas(size)
    d = ImageDraw.Draw(im)
    outlined_line(d, [(16, 5), (16, 27)], size, WHITE, INK, 1.6)
    outlined_line(d, [(5, 16), (27, 16)], size, WHITE, INK, 1.6)
    for pts in ([(16, 3), (12, 8), (20, 8)], [(16, 29), (12, 24), (20, 24)],
                [(3, 16), (8, 12), (8, 20)], [(29, 16), (24, 12), (24, 20)]):
        outlined_polygon(d, pts, size, WHITE, INK, 1.1)
    return im, (16, 16)


def draw_not_allowed(size):
    im = canvas(size)
    d = ImageDraw.Draw(im)
    outlined_ellipse(d, (6, 6, 26, 26), size, (27, 32, 39, 255), RED, 2.0)
    d.line(scaled([(9.5, 9.5), (22.5, 22.5)], size), fill=RED, width=max(1, round(2.0 * SS)))
    return im, (16, 16)


CURSORS = {
    "left_ptr": draw_left_ptr,
    "hand2": draw_hand,
    "xterm": draw_xterm,
    "crosshair": draw_crosshair,
    "watch": draw_watch,
    "left_side": lambda s: draw_resize(s, "h"),
    "right_side": lambda s: draw_resize(s, "h"),
    "top_side": lambda s: draw_resize(s, "v"),
    "bottom_side": lambda s: draw_resize(s, "v"),
    "sb_h_double_arrow": lambda s: draw_resize(s, "h"),
    "sb_v_double_arrow": lambda s: draw_resize(s, "v"),
    "top_left_corner": lambda s: draw_resize(s, "d"),
    "bottom_right_corner": lambda s: draw_resize(s, "d"),
    "fleur": draw_fleur,
    "not-allowed": draw_not_allowed,
}

ALIASES = {
    "default": "left_ptr",
    "arrow": "left_ptr",
    "top_left_arrow": "left_ptr",
    "context-menu": "left_ptr",
    "copy": "left_ptr",
    "alias": "left_ptr",
    "link": "left_ptr",
    "pointer": "hand2",
    "hand1": "hand2",
    "openhand": "hand2",
    "closedhand": "hand2",
    "text": "xterm",
    "vertical-text": "xterm",
    "progress": "watch",
    "wait": "watch",
    "move": "fleur",
    "all-scroll": "fleur",
    "col-resize": "sb_h_double_arrow",
    "row-resize": "sb_v_double_arrow",
    "ew-resize": "sb_h_double_arrow",
    "ns-resize": "sb_v_double_arrow",
    "nesw-resize": "top_left_corner",
    "nwse-resize": "bottom_right_corner",
}


def write_xcursor(path: Path, images: list[tuple[int, Image.Image, tuple[int, int]]]) -> None:
    """Write one Xcursor file with a single image per nominal size."""
    header = struct.pack("<IIII", 0x72756358, 16, 0x00010000, len(images))
    toc = b""
    payload = b""
    offset = 16 + 12 * len(images)
    chunks = []
    for nominal, im, (hx, hy) in images:
        w, h = im.size
        pixels = b"".join(
            struct.pack("<I", (a << 24) | (r << 16) | (g << 8) | b)
            for r, g, b, a in im.getdata()
        )
        chunk = struct.pack(
            "<IIIIIIIII", 36, 0xFFFD0002, nominal, 1, w, h, hx, hy, 50
        ) + pixels
        chunks.append((nominal, offset + len(payload), chunk))
        payload += chunk
    for nominal, position, _ in chunks:
        toc += struct.pack("<III", 0xFFFD0002, nominal, position)
    path.write_bytes(header + toc + payload)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in CURSORS.items():
        images = []
        for size in SIZES:
            im, (hx, hy) = fn(size)
            # Downsample from the supersampled canvas.
            im = im.resize((size, size), Image.LANCZOS)
            hx = min(size - 1, round(hx * size / 32.0))
            hy = min(size - 1, round(hy * size / 32.0))
            images.append((size, im, (hx, hy)))
        write_xcursor(OUT / name, images)
    for alias, target in ALIASES.items():
        p = OUT / alias
        if p.exists() or p.is_symlink():
            p.unlink()
        p.symlink_to(target)
    print(f"cursors written to {OUT} ({len(CURSORS)} shapes, {len(ALIASES)} aliases)")


if __name__ == "__main__":
    main()
