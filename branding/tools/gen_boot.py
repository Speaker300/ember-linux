#!/usr/bin/env python3
"""Generate GRUB and Plymouth artwork for Ember Linux.

The backgrounds come from tools/gen_wallpapers.py; this script builds the
nine-slice theme pieces, Plymouth frames, and copies the finished assets into
the boot theme directories.

Original artwork, CC BY-SA 4.0.
"""
from __future__ import annotations

import math
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
GRUB = ROOT / "boot" / "grub"
PLYMOUTH = ROOT / "boot" / "plymouth" / "ember"
WALLS = ROOT / "wallpapers"
IDENTITY = ROOT / "identity"

EMBER = (242, 106, 61, 255)
AMBER = (255, 179, 92, 255)
FROST = (244, 246, 248, 255)
ASH = (166, 174, 187, 255)
INK = (20, 23, 28, 255)
BASALT = (27, 32, 39, 235)
LINE = (42, 49, 59, 255)


def nine_slice(prefix: str, fill, border, radius: int = 10, border_width: int = 1) -> None:
    """Create GRUB's nine-slice files from one rounded rectangle."""
    full = 64
    im = Image.new("RGBA", (full, full), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, full - 1, full - 1), radius=radius, fill=fill,
                        outline=border, width=border_width)
    # 16px corners, 4px edges and centre.
    parts = {
        "nw": (0, 0, 16, 16),
        "n": (16, 0, 32, 4),
        "ne": (48, 0, 64, 16),
        "w": (0, 16, 4, 32),
        "c": (16, 16, 32, 32),
        "e": (60, 16, 64, 32),
        "sw": (0, 48, 16, 64),
        "s": (16, 60, 32, 64),
        "se": (48, 48, 64, 64),
    }
    for name, box in parts.items():
        im.crop(box).save(GRUB / f"{prefix}_{name}.png")


def grub() -> None:
    GRUB.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(WALLS / "1920x1080" / "ember-grub-1920x1080.png", GRUB / "background.png")
    shutil.copyfile(IDENTITY / "ember-logo-256.png", GRUB / "logo.png")
    nine_slice("menu", BASALT, LINE, radius=12, border_width=1)
    nine_slice("select", (242, 106, 61, 245), (255, 179, 92, 255), radius=9, border_width=1)
    (GRUB / "theme.txt").write_text(
        """# Ember Linux — GRUB theme
# SPDX-License-Identifier: CC-BY-SA-4.0
#
# Install to /boot/grub/themes/ember/ and set in /etc/default/grub:
#   GRUB_THEME="/boot/grub/themes/ember/theme.txt"
#   GRUB_GFXMODE=1920x1080,auto
#   GRUB_GFXPAYLOAD_LINUX=keep

desktop-image: "background.png"
desktop-color: "#0A0C10"
terminal-font: "Unifont Regular 16"
title-text: ""
message-font: "Unifont Regular 16"
message-color: "#F4F6F8"
message-bg-color: "#1B2027"

+ label {
  left = 12%
  top = 15%
  width = 40%
  text = "Ember Linux"
  align = "left"
  font = "Unifont Regular 16"
  color = "#F4F6F8"
}

+ label {
  left = 12%
  top = 20%
  width = 40%
  text = "1.0 · Cinder"
  align = "left"
  font = "Unifont Regular 16"
  color = "#F26A3D"
}

+ label {
  left = 12%
  top = 25%
  width = 40%
  text = "GENTOO-BASED DESKTOP"
  align = "left"
  font = "Unifont Regular 16"
  color = "#A6AEBB"
}

+ image {
  left = 74%
  top = 23%
  width = 240
  height = 240
  file = "logo.png"
}

+ boot_menu {
  left = 12%
  top = 33%
  width = 46%
  height = 30%
  menu_pixmap_style = "menu_*.png"
  selected_item_pixmap_style = "select_*.png"
  item_font = "Unifont Regular 16"
  item_color = "#C3CAD5"
  selected_item_color = "#14171C"
  item_height = 38
  item_padding = 10
  item_icon_space = 0
  item_spacing = 2
  icon_width = 0
  icon_height = 0
  scrollbar = false
}

+ progress_bar {
  id = "__timeout__"
  left = 12%
  top = 70%
  width = 40%
  height = 8
  show_text = false
  bg_color = "#1B2027"
  fg_color = "#F26A3D"
  border_color = "#3A434F"
}

+ label {
  left = 12%
  top = 74%
  width = 76%
  text = "Up/Down: select    Enter: boot    E: edit    C: command line"
  align = "left"
  font = "Unifont Regular 16"
  color = "#7D8593"
}
""",
        encoding="utf-8",
    )
    print("GRUB theme written to", GRUB)


# --------------------------------------------------------------- Plymouth --


def plymouth() -> None:
    PLYMOUTH.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(WALLS / "1920x1080" / "ember-plymouth-1920x1080.png", PLYMOUTH / "background.png")
    # Logo: the Ember mark on a transparent canvas, plus a soft halo.
    logo = Image.new("RGBA", (220, 220), (0, 0, 0, 0))
    mark = Image.open(IDENTITY / "ember-mark-512.png").convert("RGBA").resize((150, 150), Image.LANCZOS)
    logo.alpha_composite(mark, (35, 30))
    logo.save(PLYMOUTH / "logo.png")

    # 21 progress frames (0..100%) plus 12 rotating throbber frames. Swapping
    # pre-rendered images keeps the Plymouth script simple and reliable.
    track = Image.new("RGBA", (420, 10), (27, 32, 39, 210))
    d = ImageDraw.Draw(track)
    d.rounded_rectangle((0, 0, 419, 9), radius=5, fill=(27, 32, 39, 220),
                        outline=(58, 67, 79, 255), width=1)
    track.save(PLYMOUTH / "progress_track.png")
    for i in range(21):
        frame = track.copy()
        f = ImageDraw.Draw(frame)
        width = max(8, int(404 * i / 20))
        if i > 0:
            f.rounded_rectangle((2, 2, 2 + width, 7), radius=3, fill=(242, 106, 61, 255))
        frame.save(PLYMOUTH / f"progress-{i:02d}.png")

    for i in range(12):
        frame = Image.new("RGBA", (72, 72), (0, 0, 0, 0))
        f = ImageDraw.Draw(frame)
        angle = i * (2 * math.pi / 12)
        for j in range(8):
            a = angle + j * (2 * math.pi / 8)
            alpha = max(30, 245 - j * 26)
            cx = 36 + 21 * math.cos(a)
            cy = 36 + 21 * math.sin(a)
            r = 3.4
            f.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(242, 106, 61, alpha))
        frame.save(PLYMOUTH / f"throbber-{i:02d}.png")

    (PLYMOUTH / "ember.plymouth").write_text(
        """[Plymouth Theme]
Name=Ember
Description=Ember Linux boot splash
ModuleName=script

[script]
ImageDir=/usr/share/plymouth/themes/ember
ScriptFile=/usr/share/plymouth/themes/ember/ember.script
""",
        encoding="utf-8",
    )
    (PLYMOUTH / "ember.script").write_text(
        r"""# Ember Linux Plymouth theme
# SPDX-License-Identifier: CC-BY-SA-4.0
#
# Stable Plymouth script APIs only: sprites, pre-rendered frames, text and
# SetBootProgressFunction. The layout is proportional so it survives a mode
# change from firmware to the KMS driver.

screen_width = Window.GetWidth();
screen_height = Window.GetHeight();

background = Image("background.png");
background_sprite = Sprite(background);
background_sprite.SetX(screen_width / 2 - background.GetWidth() / 2);
background_sprite.SetY(screen_height / 2 - background.GetHeight() / 2);
background_sprite.SetZ(-100);

logo = Image("logo.png");
logo_sprite = Sprite(logo);
logo_sprite.SetX(screen_width / 2 - logo.GetWidth() / 2);
logo_sprite.SetY(screen_height * 0.20);
logo_sprite.SetZ(10);

title = Image.Text("Ember Linux", 0.956, 0.965, 0.973, 1.0);
title_sprite = Sprite(title);
title_sprite.SetX(screen_width / 2 - title.GetWidth() / 2);
title_sprite.SetY(screen_height * 0.50);
title_sprite.SetZ(10);

subtitle = Image.Text("starting the system", 0.65, 0.68, 0.73, 1.0);
subtitle_sprite = Sprite(subtitle);
subtitle_sprite.SetX(screen_width / 2 - subtitle.GetWidth() / 2);
subtitle_sprite.SetY(screen_height * 0.535);
subtitle_sprite.SetZ(10);

track = Image("progress_track.png");
track_sprite = Sprite(track);
track_sprite.SetX(screen_width / 2 - track.GetWidth() / 2);
track_sprite.SetY(screen_height * 0.60);
track_sprite.SetZ(10);

progress_images = [];
for (i = 0; i < 21; i++) {
    if (i < 10) {
        progress_images[i] = Image("progress-0" + i + ".png");
    } else {
        progress_images[i] = Image("progress-" + i + ".png");
    }
}

progress_sprite = Sprite();
progress_sprite.SetZ(11);
progress_sprite.SetX(screen_width / 2 - track.GetWidth() / 2);
progress_sprite.SetY(screen_height * 0.60);
progress_sprite.SetImage(progress_images[0]);

throbber_images = [];
for (i = 0; i < 12; i++) {
    if (i < 10) {
        throbber_images[i] = Image("throbber-0" + i + ".png");
    } else {
        throbber_images[i] = Image("throbber-" + i + ".png");
    }
}

throbber_sprite = Sprite(throbber_images[0]);
throbber_sprite.SetX(screen_width / 2 - 36);
throbber_sprite.SetY(screen_height * 0.645);
throbber_sprite.SetZ(11);

message_sprite = Sprite();
message_sprite.SetZ(10);

frame = 0;

fun refresh_callback ()
{
    frame = frame + 1;
    throbber_sprite.SetImage(throbber_images[frame % 12]);
}

fun progress_callback (duration, progress)
{
    index = Math.Int(progress * 20);
    if (index < 0) { index = 0; }
    if (index > 20) { index = 20; }
    progress_sprite.SetImage(progress_images[index]);
}

fun message_callback (text)
{
    message = Image.Text(text, 0.78, 0.82, 0.87, 1.0);
    message_sprite.SetImage(message);
    message_sprite.SetX(screen_width / 2 - message.GetWidth() / 2);
    message_sprite.SetY(screen_height * 0.70);
}

Plymouth.SetRefreshFunction(refresh_callback);
Plymouth.SetBootProgressFunction(progress_callback);
Plymouth.SetMessageFunction(message_callback);
""",
        encoding="utf-8",
    )
    print("Plymouth theme written to", PLYMOUTH)


if __name__ == "__main__":
    grub()
    plymouth()
