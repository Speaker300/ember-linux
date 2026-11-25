#!/usr/bin/env python3
"""Build documentation mockups for the Ember branding pack.

GRUB, Plymouth and the Calamares welcome window are rendered from the shipped
assets and palette. The desktop and greeter screenshots in mockups/ were
captured from the actual Openbox/tint2/GTK themes in a disposable Xvfb session;
this script does not try to fake those.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "mockups"
FONT = ROOT / "desktop" / "fonts" / "inter"

INK = (20, 23, 28)
BASALT = (27, 32, 39)
GRAPHITE = (38, 44, 54)
ASH = (166, 174, 187)
FROST = (244, 246, 248)
BODY = (195, 202, 213)
EMBER = (242, 106, 61)
AMBER = (255, 179, 92)


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT / name), size)


def text(draw, xy, s, f, fill, anchor=None):
    draw.text(xy, s, font=f, fill=fill, anchor=anchor)


def rounded(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def grub() -> None:
    bg = Image.open(ROOT / "boot" / "grub" / "background.png").convert("RGBA")
    bg = bg.resize((1920, 1080), Image.LANCZOS)
    layer = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # menu panel
    rounded(d, (228, 356, 1120, 680), 12, (27, 32, 39, 232), (42, 49, 59, 255), 2)

    f_title = font("Inter-Bold.ttf", 38)
    f_sub = font("Inter-SemiBold.ttf", 20)
    f_item = font("Inter-Regular.ttf", 22)
    f_hint = font("Inter-Regular.ttf", 16)

    text(d, (260, 148), "Ember Linux", f_title, FROST)
    text(d, (260, 198), "1.0 · Cinder", f_sub, EMBER)
    text(d, (260, 236), "GENTOO-BASED DESKTOP", font("Inter-SemiBold.ttf", 13), ASH)

    items = [
        "Ember Linux 1.0 (Cinder)",
        "Advanced options for Ember Linux",
        "Ember Linux 1.0 (recovery mode)",
        "Memory test (memtest86+)",
        "UEFI Firmware Settings",
    ]
    y = 386
    for i, item in enumerate(items):
        if i == 0:
            rounded(d, (246, y - 8, 1102, y + 44), 8, (242, 106, 61, 245), (255, 179, 92, 255), 2)
            text(d, (276, y), item, f_item, (20, 23, 28))
        else:
            text(d, (276, y), item, f_item, BODY)
        y += 46

    # timeout bar
    d.rounded_rectangle((260, 756, 1008, 768), radius=6, fill=(27, 32, 39, 255), outline=(58, 67, 79, 255), width=1)
    d.rounded_rectangle((262, 758, 700, 766), radius=4, fill=EMBER)
    text(d, (260, 800), "Up/Down: select    Enter: boot    E: edit    C: command line", f_hint, (125, 133, 147))

    logo = Image.open(ROOT / "boot" / "grub" / "logo.png").convert("RGBA").resize((240, 240), Image.LANCZOS)
    layer.alpha_composite(logo, (1420, 248))
    out = Image.alpha_composite(bg, layer).convert("RGB")
    out.save(OUT / "grub-menu-mockup.png", quality=95)
    print("wrote grub-menu-mockup.png")


def plymouth() -> None:
    bg = Image.open(ROOT / "boot" / "plymouth" / "ember" / "background.png").convert("RGBA")
    bg = bg.resize((1920, 1080), Image.LANCZOS)
    layer = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    logo = Image.open(ROOT / "boot" / "plymouth" / "ember" / "logo.png").convert("RGBA")
    layer.alpha_composite(logo, (850, 216))

    f_title = font("Inter-SemiBold.ttf", 30)
    f_sub = font("Inter-Regular.ttf", 17)
    f_msg = font("Inter-Regular.ttf", 15)

    text(d, (960, 548), "Ember Linux", f_title, FROST, anchor="ma")
    text(d, (960, 590), "starting the system", f_sub, (166, 174, 187), anchor="ma")

    track = Image.open(ROOT / "boot" / "plymouth" / "ember" / "progress_track.png").convert("RGBA")
    layer.alpha_composite(track, (750, 648))
    # 62% fill
    fill = Image.open(ROOT / "boot" / "plymouth" / "ember" / "progress-12.png").convert("RGBA")
    layer.alpha_composite(fill, (750, 648))

    throbber = Image.open(ROOT / "boot" / "plymouth" / "ember" / "throbber-00.png").convert("RGBA")
    layer.alpha_composite(throbber, (924, 696))

    text(d, (960, 792), "Starting NetworkManager…", f_msg, (200, 207, 218), anchor="ma")

    out = Image.alpha_composite(bg, layer).convert("RGB")
    out.save(OUT / "plymouth-boot-mockup.png", quality=95)
    print("wrote plymouth-boot-mockup.png")


def calamares_welcome() -> None:
    W, H = 800, 520
    im = Image.new("RGBA", (W, H), (20, 23, 28, 255))
    # wallpaper
    wp = Image.open(ROOT / "calamares" / "wallpaper.png").convert("RGBA").resize((W, H), Image.LANCZOS)
    im.alpha_composite(wp)
    d = ImageDraw.Draw(im)

    # sidebar
    d.rectangle((0, 0, 158, H), fill=(16, 19, 23, 255))
    d.line((158, 0, 158, H), fill=(42, 49, 59, 255), width=1)
    logo = Image.open(ROOT / "calamares" / "ember-logo.png").convert("RGBA").resize((64, 64), Image.LANCZOS)
    im.alpha_composite(logo, (47, 22))

    steps = ["Welcome", "Location", "Keyboard", "Stage 3", "Desktop", "Partitions", "Users", "Summary"]
    f_step = font("Inter-Regular.ttf", 13)
    y = 120
    for i, step in enumerate(steps):
        if i == 0:
            d.rounded_rectangle((10, y - 5, 148, y + 19), radius=5, fill=(242, 106, 61, 255))
            text(d, (22, y), step, f_step, (20, 23, 28))
        else:
            text(d, (22, y), step, f_step, (166, 174, 187))
        y += 34

    f_h = font("Inter-Bold.ttf", 25)
    f_body = font("Inter-Regular.ttf", 13)
    f_small = font("Inter-Regular.ttf", 11)
    text(d, (192, 58), "Welcome to Ember Linux", f_h, FROST)
    body = (
        "Ember is a careful desktop built on Gentoo. This installer sets up\n"
        "the partitions, a Gentoo stage3, your desktop and the bootloader.\n"
        "Most installs take 15–40 minutes and need an internet connection."
    )
    d.multiline_text((192, 104), body, font=f_body, fill=BODY, spacing=6)

    lock = Image.open(ROOT / "calamares" / "welcome.png").convert("RGBA")
    lock = lock.resize((410, int(lock.height * 410 / lock.width)), Image.LANCZOS)
    im.alpha_composite(lock, (192, 190))

    # secondary support buttons
    for label, x in (("Support", 192), ("Release notes", 278), ("Known issues", 396)):
        d.rounded_rectangle((x, 398, x + (86 if label == "Support" else 108), 424), radius=6,
                            fill=(35, 42, 51, 255), outline=(58, 67, 79, 255), width=1)
        text(d, (x + 12, 404), label, f_small, BODY)

    # next button
    d.rounded_rectangle((656, 442, 774, 478), radius=7, fill=EMBER)
    text(d, (715, 452), "Next", font("Inter-SemiBold.ttf", 13), INK, anchor="ma")

    # top progress line
    d.rectangle((158, 0, 800, 3), fill=(42, 49, 59, 255))
    d.rectangle((158, 0, 260, 3), fill=EMBER)

    im.convert("RGB").save(OUT / "calamares-welcome-mockup.png", quality=95)
    print("wrote calamares-welcome-mockup.png")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    grub()
    plymouth()
    calamares_welcome()
