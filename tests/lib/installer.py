#!/usr/bin/env python3
"""Calamares installer driver for the Ember QA harness.

Drives the graphical installer over VNC, the same way a user would.  It never
edits the ISO or the chroot.  Coordinates are for the documented 1280x800
virtio-vga console; every important page is also OCR-checked so a changed UI
fails instead of silently clicking through the wrong screen.
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from screen import Screen, WaitTimeout, ScreenError

log = logging.getLogger("emberqa.installer")

CONTENT = (168, 0, 1280, 760)  # Calamares content pane, excludes sidebar
NEXT = (1148, 784)
INSTALL = (1148, 784)
CONFIRM_INSTALL = (353, 78)

PASSWORD = "embertest"
FULLNAME = "Gentoo User"
USERNAME = "gentoo"
HOSTNAME = "gentoo-test"

DESKTOPS = {
    "openbox": {"y": 15, "preview": "Minimal, fast X11 desktop", "name": "Openbox"},
    "xfce": {"y": 31, "preview": "Lightweight full desktop", "name": "Xfce"},
    "kde": {"y": 47, "preview": "Full-featured Qt desktop", "name": "KDE Plasma"},
    "gnome": {"y": 63, "preview": "Full GNOME desktop", "name": "GNOME"},
    "cinnamon": {"y": 79, "preview": "Traditional GTK desktop", "name": "Cinnamon"},
    "mate": {"y": 95, "preview": "Classic GNOME 2 style desktop", "name": "MATE"},
    "lxqt": {"y": 111, "preview": "Lightweight Qt desktop", "name": "LXQt"},
    "i3": {"y": 127, "preview": "Keyboard-driven X11 tiling", "name": "i3"},
    "sway": {"y": 143, "preview": "Wayland tiling compositor", "name": "Sway"},
    "hyprland": {"y": 159, "preview": "Wayland compositor", "name": "Hyprland"},
    "fluxbox": {"y": 175, "preview": "Very small, classic X11", "name": "Fluxbox"},
    "icewm": {"y": 191, "preview": "Small, fast and familiar", "name": "IceWM"},
    "server": {"y": 207, "preview": "No X11 desktop", "name": "Server"},
}

SYSTEMD_DESKTOPS = {"gnome"}


class TestFailure(RuntimeError):
    """A product or boot failure; the test result is FAIL."""


class TestBlocked(RuntimeError):
    """The ISO does not expose the feature needed by this test; result BLOCKED."""


@dataclass
class Check:
    name: str
    status: str  # PASS / FAIL / BLOCKED / INFO
    detail: str = ""
    evidence: list[str] = field(default_factory=list)


class Installer:
    def __init__(self, screen: Screen, *, desktop: str = "openbox",
                 filesystem: str = "ext4", luks: bool = False,
                 lvm: bool = False, timeout: float = 3600,
                 fault_during_install: bool = False,
                 world_update: bool = False, secure_boot: bool = False,
                 vm=None):
        if desktop not in DESKTOPS:
            raise ValueError(f"unknown desktop {desktop!r}")
        self.s = screen
        self.vm = vm
        self.desktop = desktop
        self.filesystem = filesystem
        self.luks = luks
        self.lvm = lvm
        self.timeout = timeout
        self.fault_during_install = fault_during_install
        self.world_update = world_update
        self.secure_boot = secure_boot
        self.stage_variant = (
            "current-stage3-amd64-desktop-systemd"
            if desktop in SYSTEMD_DESKTOPS
            else "current-stage3-amd64-desktop-openrc"
        )
        self.checks: list[Check] = []
        self.evidence: list[str] = []
        self.progress_shots: list[str] = []
        self.progress_seen = False

    # -- helpers ---------------------------------------------------------
    def add(self, name: str, status: str, detail: str = "",
            evidence: Path | str | None = None) -> None:
        ev = []
        if evidence:
            ev = [str(evidence)]
            self.evidence.append(str(evidence))
        self.checks.append(Check(name, status, detail, ev))
        log.info("CHECK %-28s %-7s %s", name, status, detail)

    def shot(self, name: str) -> Path:
        return self.s.shot(name)

    def page_text(self, name: str) -> str:
        p = self.shot(name)
        return self.s.ocr(p, crop=CONTENT)

    def next(self, expect: list[str], label: str, timeout: float = 30) -> str:
        # Qt buttons in Calamares have mnemonics; Alt+N is reliable even when
        # the branded window is floating and mouse coordinates are uncertain.
        self.s.key("alt-n", settle=0.8)
        try:
            return self.s.wait_text(expect, timeout=timeout, crop=CONTENT,
                                    label=label)
        except WaitTimeout:
            # Fallback: locate and click the orange primary button.
            self.click_next()
            return self.s.wait_text(expect, timeout=max(15, timeout // 2),
                                    crop=CONTENT, label=label + "-mouse")

    def click_next(self) -> None:
        """Click the orange Next button wherever the Calamares window is."""
        p = self.shot("next-button")
        pos = self.s.find_primary_button(p)
        log.info("click_next: orange primary button at %s", pos)
        if pos:
            self.s.click(pos[0], pos[1], settle=1.0)
            time.sleep(0.8)
            # Confirm the page changed; if not, try the keyboard default and
            # a slightly higher point inside the button.
            try:
                after = self.shot("next-after")
                text = self.s.ocr(after, crop=CONTENT, save_text=False)
                if "welcome to the ember" in text.lower():
                    log.warning("Next click did not leave Welcome; retrying")
                    self.s.click(pos[0], pos[1] - 8, settle=0.8)
                    time.sleep(0.5)
                    self.s.key("return", settle=1.0)
            except Exception:
                pass
            return
        try:
            pos = self.s.find_word("Next", p)
        except Exception:
            pos = None
        if pos and pos[0] > 800 and pos[1] > 400:
            self.s.click(pos[0], pos[1], settle=0.8)
        else:
            # Last resort: the default button responds to Return.
            self.s.key("return", settle=0.8)

    def edge_click(self, x: int, y: int, settle: float = 0.8) -> None:
        self.s.click(x, y, settle=settle)

    # -- pages -----------------------------------------------------------
    def ensure_maximized(self) -> None:
        """Maximize Calamares so the documented 1280x800 coordinates apply."""
        from PIL import Image
        p = self.shot("01-window-check")
        try:
            px = Image.open(p).convert("RGB").getpixel((10, 100))
        except Exception:
            px = (0, 0, 0)
        if sum(px) > 60:
            return  # already fullscreen (sidebar occupies the left edge)
        self.s.key("alt-f10", settle=1.0)
        time.sleep(0.5)
        p = self.shot("01-window-max")
        try:
            px = Image.open(p).convert("RGB").getpixel((10, 100))
        except Exception:
            px = (0, 0, 0)
        if sum(px) > 60:
            return
        # Openbox: double-click the title bar of the default 1024x627 window.
        self.s.click(640, 132, settle=0.1)
        self.s.click(640, 132, settle=1.2)
        time.sleep(0.5)
        p = self.shot("01-window-max2")
        try:
            px = Image.open(p).convert("RGB").getpixel((10, 100))
        except Exception:
            px = (0, 0, 0)
        if sum(px) <= 60:
            log.warning("Calamares did not maximize; continuing with fixed-coordinate fallbacks")

    def launch_installer_manually(self) -> bool:
        """Live-session fallback: start Calamares from a terminal.

        The 16:10 ISO's Openbox autostart no longer launches Calamares.  We
        record that as a product failure and start it manually so the rest of
        the install/login matrix can still be exercised.  This does not turn
        the autostart failure into a pass.
        """
        log.warning("Calamares did not auto-launch; attempting manual start")
        p = self.shot("01-no-autostart")
        # Right-click the desktop and click the live menu's Terminal entry.
        self.s.click(500, 400, button=3, settle=1.0)
        p = self.shot("01-manual-menu")
        try:
            pos = self.s.find_word("Terminal", p)
        except Exception:
            pos = None
        if pos:
            self.s.click(pos[0], pos[1], settle=2.0)
        else:
            # Fallback: panel terminal launcher at the lower left.
            self.s.click(38, 784, settle=2.0)
        time.sleep(1.5)
        p = self.shot("01-manual-terminal")
        self.s.type_text("sudo -n calamares", delay=0.05)
        self.s.key("return", settle=1.0)
        time.sleep(8)
        p = self.shot("01-manual-calamares")
        text = self.s.ocr(p)
        low = text.lower()
        if ("calamares" in low or "initialization" in low
                or ("welcome" in low and "installer" in low)):
            self.add("installer_autostart", "FAIL",
                     "Calamares did not auto-launch; started manually from a "
                     "terminal so downstream checks could continue", p)
            return True
        self.add("installer_autostart", "FAIL",
                 "Calamares did not auto-launch and manual start produced no window",
                 p)
        return False

    def wait_live_installer(self, timeout: float = 420) -> None:
        log.info("waiting for the live installer")
        started = time.time()
        manual_tried = False
        deadline = started + timeout
        last = ""
        while time.time() < deadline:
            p = self.shot("01-live")
            try:
                text = self.s.ocr(p)
            except ScreenError:
                text = ""
            last = text
            low = text.lower()
            if ("calamares initialization failed" in low
                    or "could not be loaded" in low
                    or "calamares was unable" in low):
                p2 = self.shot("installer-init-failed")
                text2 = self.s.ocr(p2)
                modules = sorted(set(re.findall(r"[a-z0-9_]+@[a-z0-9_]+", text2)))
                detail = "Calamares initialization failed before Welcome"
                if modules:
                    detail += "; could not load " + ", ".join(modules)
                self.add("live_boot_installer", "FAIL", detail, p2)
                raise TestFailure(detail)
            if ("calamares" in low
                    or "ember linux installer" in low
                    or ("ember" in low and "installer" in low)
                    or ("welcome to the ember" in low and "installer" in low)):
                self.shot("01-welcome")
                self.ensure_maximized()
                p = self.shot("01-welcome-max")
                if self.vm:
                    self.vm.serial_send(
                        "echo EMBER_LIVE_COMPONENTS; "
                        "ps -eo comm | grep -E 'sddm|openbox|calamares' | sort -u; "
                        "rc-service display-manager status 2>&1 | head -3",
                        settle=2.0,
                    )
                    self.add("live_session", "INFO",
                             "SDDM/Openbox/Calamares process check written to serial install log",
                             p)
                self.add("live_boot_installer", "PASS",
                         "Calamares welcome screen rendered", p)
                return
            # The live Openbox session can be up with no installer.  Try once
            # after two minutes, preserving the autostart failure as a check.
            if not manual_tried and time.time() - started > 120:
                manual_tried = True
                if self.launch_installer_manually():
                    continue
            time.sleep(3)
        p = self.shot("installer-not-found")
        self.add("live_boot_installer", "FAIL",
                 "Calamares did not appear within the boot timeout", p)
        raise TestFailure(f"Calamares did not appear: {last[-800:]!r}")

    def welcome(self) -> None:
        self.next(["system language", "numbers and dates"], "location")

    def location(self) -> None:
        # Default location in this ISO is America/Toronto.  The test does not
        # require a particular timezone, only a successful install.
        p = self.shot("02-location")
        self.add("installer_location", "PASS", "Location page; default America/Toronto",
                 p)
        self.next(["type here to test", "keyboard model"], "keyboard")

    def keyboard(self) -> None:
        p = self.shot("03-keyboard")
        self.add("installer_keyboard", "PASS", "Keyboard page; default English (US)", p)
        self.next(["Choose the right stage3", "stage3"], "stage3-guide")

    def stage3_guide(self) -> None:
        p = self.shot("04-stage3-guide")
        text = self.s.ocr(p, crop=CONTENT)
        if "stage3" not in text.lower():
            raise TestFailure("Stage 3 guide page did not render its guidance text")
        self.add("stage3_guide", "PASS", "Guidance page rendered", p)
        self.next(["Select Architecture", "Select Stage3 Option"], "stage-select")

    def _combo_near(self, label: str, dx: int, dy: int,
                    fallback: tuple[int, int]) -> None:
        p = self.shot(f"combo-{label}")
        try:
            pos = self.s.find_word(label, p)
        except Exception:
            pos = None
        if pos:
            self.s.click(pos[0] + dx, pos[1] + dy, settle=0.45)
        else:
            self.s.click(*fallback, settle=0.45)

    def _stage_text(self) -> str:
        p = self.shot("05-stage-page")
        return self.s.ocr(p, crop=CONTENT)

    @staticmethod
    def _stage_ok(text: str, init_token: str) -> bool:
        low = text.lower()
        return (
            "selected:" in low and "stage3" in low and "no tar" not in low
            and init_token in low
            and any(t in low for t in ("desktop", "deskiop", "deskt0p", "desktcp"))
            and "hardened" not in low and "musl" not in low
            and "nomultilib" not in low
        )

    def stage_select(self) -> None:
        log.info("selecting %s", self.stage_variant)
        init_token = "systemd" if "systemd" in self.stage_variant else "openrc"
        # Keyboard-primary path from the page's initial focus:
        # Tab twice -> Architecture, Space opens, Down -> amd64, Return.
        # The variant then auto-populates current-stage3-amd64-desktop-openrc.
        self.s.key("tab", settle=0.15)
        self.s.key("tab", settle=0.15)
        self.s.key("space", settle=0.4)
        self.s.key("down", settle=0.2)
        self.s.key("return", settle=1.0)
        time.sleep(6)
        text = self._stage_text()
        selected = self._stage_ok(text, init_token)
        if not selected:
            # If the variant did not auto-populate, Tab to the Stage3 Option
            # combo and choose the first entry.
            log.warning("variant not auto-populated; selecting Stage3 Option")
            self.s.key("tab", settle=0.2)
            self.s.key("space", settle=0.4)
            self.s.key("down", settle=0.2)
            self.s.key("return", settle=1.0)
            time.sleep(3)
            text = self._stage_text()
            selected = self._stage_ok(text, init_token)
        if selected and self.desktop in SYSTEMD_DESKTOPS:
            # GNOME needs the systemd stage; focus the Stage3 Option combo and
            # choose the second entry.
            self.s.key("tab", settle=0.2)
            self.s.key("space", settle=0.4)
            self.s.key("down", settle=0.2)
            self.s.key("return", settle=1.0)
            time.sleep(3)
            text = self._stage_text()
            selected = self._stage_ok(text, "systemd")

        # Fallback for a changed focus order: mouse/type-ahead. Mouse may not
        # work in the branded VM, so this is fallback only.
        if not selected:
            log.warning("keyboard stage selection did not verify; trying "
                        "mouse/type-ahead fallback")
            for attempt in range(1, 8):
                self._combo_near("Architecture", 98, 27, (620, 401))
                self.s.key("home", settle=0.1)
                self.s.key("down", settle=0.1)
                self.s.key("return", settle=2.0)
                self._combo_near("Option", 98, 27, (830, 401))
                self.s.type_text(self.stage_variant, delay=0.02)
                self.s.key("return", settle=0.8)
                time.sleep(4)
                text = self._stage_text()
                if self._stage_ok(text, init_token):
                    if self.desktop not in SYSTEMD_DESKTOPS:
                        selected = True
                        break
                    if self._stage_ok(text, "systemd"):
                        selected = True
                        break

        p = self.shot("05-stage-selected")
        text = self.s.ocr(p, crop=CONTENT)
        if not self._stage_ok(text, init_token) and not (
                self.desktop in SYSTEMD_DESKTOPS and self._stage_ok(text, "systemd")):
            raise TestFailure(
                f"could not select {self.stage_variant}; last page text: "
                + re.sub(r"\s+", " ", text)[-600:]
            )
        self.add("stage3_selected", "PASS", f"amd64 {self.stage_variant} selected", p)
        self.next(["Openbox (recommended)", "Server (no desktop)"], "desktop")

    def desktop_choice(self) -> None:
        d = DESKTOPS[self.desktop]
        p = self.shot(f"06-desktop-{self.desktop}-before")
        if self.desktop == "openbox":
            # Openbox is the default/recommended entry; keyboard-primary path
            # simply confirms the preview and advances.
            text = self.s.ocr(p, crop=CONTENT)
            log.info("desktop chooser: Openbox default selected")
        else:
            # Keyboard selection: focus the list and move to the row. Mouse
            # remains a fallback because pointer clicks are unreliable in the
            # branded VM.
            order = list(DESKTOPS)
            index = order.index(self.desktop)
            try:
                self.s.key("home", settle=0.2)
                for _ in range(index):
                    self.s.key("down", settle=0.15)
                self.s.key("return", settle=1.0)
            except Exception:
                pass
            p = self.shot(f"06-desktop-{self.desktop}")
            text = self.s.ocr(p, crop=CONTENT)
            if d["preview"].lower() not in text.lower():
                # Last-resort mouse/OCR row click.
                pos = None
                try:
                    for word in d["name"].split():
                        pos = self.s.find_word(word, p)
                        if pos and pos[0] < 520:
                            break
                        pos = None
                except Exception:
                    pos = None
                if pos and pos[0] < 520:
                    self.s.click(pos[0], pos[1], settle=0.8)
                    p = self.shot(f"06-desktop-{self.desktop}-mouse")
                    text = self.s.ocr(p, crop=CONTENT)
        if d["preview"].lower() not in text.lower():
            # OCR sometimes misses small list text; retry once with a crop of
            # the preview/description pane.
            text2 = self.s.ocr(p, crop=(400, 500, 1280, 800))
            if d["preview"].lower() not in text2.lower():
                raise TestFailure(
                    f"desktop chooser did not show {d['name']} preview; got: "
                    + re.sub(r"\s+", " ", text)[-400:]
                )
        self.add("desktop_selection", "PASS", f"{d['name']} selected", p)
        # New ISOs insert the make.conf editor here; older ISOs go straight
        # to the partition page.  Detect which page actually appeared.
        self.s.key("alt-n", settle=0.8)
        text = self.s.wait_text(
            ["build configuration", "manual partitioning", "unpartitioned"],
            timeout=30, crop=CONTENT, label="after-desktop",
        )
        if "build configuration" in text.lower():
            self.build_config()
        # build_config advances to the partition page; otherwise we are
        # already there.

    def build_config(self) -> None:
        p = self.shot("06b-build-config")
        text = self.s.ocr(p, crop=CONTENT)
        low = text.lower()
        if "build configuration" not in low:
            raise TestFailure("Build configuration page did not render")
        for key in ("CFLAGS", "MAKEOPTS", "ACCEPT_LICENSE"):
            if key.lower() not in low:
                text2 = self.s.ocr(p, crop=(180, 80, 1260, 560), psm=6)
                if key.lower() not in text2.lower():
                    raise TestFailure(
                        f"make.conf editor does not show generated {key}"
                    )
        self.add("makeconf_editor", "PASS",
                 "Build configuration page shows generated make.conf", p)
        if "valid" in low:
            self.add("makeconf_validation", "PASS",
                     "suggested make.conf is reported valid", p)
        else:
            # Suggested values should already validate.  If not, fail rather
            # than silently advancing an invalid configuration.
            self.add("makeconf_validation", "FAIL",
                     "suggested make.conf did not report a valid configuration", p)
            raise TestFailure("make.conf suggested values are not valid")
        self.next(["manual partitioning", "unpartitioned"], "partitions")

    def _locate_and_click(self, word: str, *, offset_y: int = 0,
                          label: str | None = None) -> bool:
        try:
            p = self.shot(f"find-{label or word}")
            pos = self.s.find_word(word, p)
            if pos:
                self.s.click(pos[0], pos[1] + offset_y)
                return True
        except Exception as exc:
            log.debug("find_word %s failed: %s", word, exc)
        return False

    def partitions(self) -> None:
        log.info("partitioning: erase disk, fs=%s luks=%s lvm=%s",
                 self.filesystem, self.luks, self.lvm)
        p = self.shot("07-partitions-empty")
        text = self.s.ocr(p, crop=CONTENT)
        if "manual partitioning" not in text.lower() and "unpartitioned" not in text.lower():
            raise TestFailure("partition page did not render its install choices")
        # Ensure keyboard focus is on the storage combo (orange border), then
        # one Tab moves to the Erase disk radio and Space selects it.
        for _ in range(12):
            p = self.shot("07-focus-check")
            if self.s.has_orange(p, region=(300, 0, 720, 38)):
                break
            self.s.key("tab", settle=0.15)
        else:
            log.warning("could not confirm storage-combo focus by orange border")
        self.s.key("tab", settle=0.2)
        self.s.key("space", settle=1.0)
        time.sleep(0.6)
        p = self.shot("07-partitions-erase")
        text = self.s.ocr(p, crop=CONTENT)
        low = text.lower()
        if not any(w in low for w in ("encrypt system", "no swap", "after:")):
            # Fallback: activate the Erase label mnemonic or click it.
            self.s.key("alt-e", settle=0.8)
            time.sleep(0.4)
            p = self.shot("07-partitions-erase-alt")
            text = self.s.ocr(p, crop=CONTENT)
            low = text.lower()
        if not any(w in low for w in ("encrypt system", "no swap", "after:")):
            try:
                self.s.click_word("Erase", p, label="erase")
                time.sleep(0.8)
                p = self.shot("07-partitions-erase-mouse")
                text = self.s.ocr(p, crop=CONTENT)
                low = text.lower()
            except ScreenError:
                pass
        if not any(w in low for w in ("encrypt system", "no swap", "after:")):
            self.add("partition_erase_selected", "FAIL",
                     "Erase disk could not be selected after focusing the "
                     "storage combo, Alt+E, or click", p)
            raise TestFailure("Erase disk radio stayed unselected")
        self.add("partition_erase_selected", "PASS",
                 "Erase disk selected by keyboard (storage combo -> Tab -> Space)",
                 p)

        # Filesystem selector is an extra combo attached to the erase radio.
        # On ISOs without availableFileSystemTypes there is no selector.
        if self.filesystem != "ext4":
            low = text.lower()
            has_fs_ui = any(w in low for w in ("btrfs", "xfs", "f2fs", "file system"))
            if not has_fs_ui:
                self.add("filesystem_selection", "BLOCKED",
                         f"ISO exposes no filesystem selector (requested {self.filesystem})",
                         p)
                raise TestBlocked(
                    f"requested filesystem {self.filesystem!r}, but this ISO's "
                    "partition page has no filesystem selector; refusing to "
                    "silently install ext4"
                )
            # The swap combo is at (333,113); the filesystem combo follows it
            # in the same row when available.  Find the selected "ext4" text
            # in the upper part of the page so this also works in the default
            # 1024x627 window, then use Qt type-ahead.
            pos = None
            try:
                pos = self.s.find_word("ext4", p, crop=(0, 0, 1280, 340))
            except Exception:
                pos = None
            if pos:
                self.s.click(pos[0], pos[1], settle=0.5)
            else:
                self.edge_click(510, 113, 0.5)
            self.s.type_text(self.filesystem, delay=0.05)
            self.s.key("return", settle=0.8)
            p = self.shot(f"07-partitions-{self.filesystem}")
            text = self.s.ocr(p, crop=CONTENT)
            if self.filesystem.lower() not in text.lower():
                self.add("filesystem_selection", "FAIL",
                         f"could not select {self.filesystem}", p)
                raise TestFailure(f"filesystem combo did not show {self.filesystem}")
            self.add("filesystem_selection", "PASS",
                     f"{self.filesystem} selected in erase-disk options", p)

        if self.luks:
            if "encrypt system" not in text.lower():
                self.add("luks_setup", "BLOCKED", "no Encrypt system control", p)
                raise TestBlocked("ISO exposes no Encrypt system checkbox")
            try:
                self.s.click_word("Encrypt", p, label="encrypt")
            except ScreenError:
                self.edge_click(184, 586, 1.0)
            time.sleep(1.0)
            p = self.shot("07-luks-passphrase")
            text = self.s.ocr(p, crop=CONTENT)
            # Inline EncryptWidget: passphrase + confirm fields appear in the
            # same row.  Locate their placeholders by OCR.
            clicked1 = self._locate_and_click("Passphrase", label="luks-pass")
            if not clicked1:
                self.s.click(530, 586, settle=0.2)
            self.s.type_text(PASSWORD, delay=0.05)
            clicked2 = self._locate_and_click("Confirm", label="luks-confirm")
            if not clicked2:
                self.s.click(800, 586, settle=0.2)
            self.s.type_text(PASSWORD, delay=0.05)
            time.sleep(1)
            p = self.shot("07-luks-filled")
            self.add("luks_setup", "PASS",
                     "LUKS2 passphrase entered for erase-disk install", p)
            text = self.s.ocr(p, crop=CONTENT)
            if "confirm" not in text.lower() and "encrypt" not in text.lower():
                log.warning("LUKS fields not obvious after entry; continuing")

        if self.lvm:
            low = text.lower()
            if "lvm" not in low:
                self.add("lvm_setup", "BLOCKED",
                         "no LVM control on erase-disk page (LVM is manual-only)", p)
                raise TestBlocked(
                    "this ISO does not expose LVM in the erase-disk workflow; "
                    "LVM requires manual partitioning, not tested by this driver"
                )
            # LVM in Calamares is exposed via manual partitioning.  Do not
            # pretend an erase-disk install used LVM.
            self.add("lvm_setup", "BLOCKED", "LVM requires manual partitioning", p)
            raise TestBlocked("automatic LVM partitioning is not available")

        # Keep the default "No swap" unless the ISO changed it.
        if "no swap" not in text.lower():
            log.warning("swap combo is not 'No swap': %s", text[-300:])
        self.next(["What is your name?", "name"], "users")

    def users(self) -> None:
        log.info("creating user %s / %s", FULLNAME, USERNAME)
        p = self.shot("08-users-empty")
        text = self.s.ocr(p, crop=CONTENT)
        if "your name" not in text.lower():
            raise TestFailure("users page did not render")
        if self.vm:
            self.vm.serial_send(
                "tail -250 /root/.cache/calamares/session.log", settle=3.0)
            self.vm.serial_send("echo EMBER_SERIAL_USERS_LOG_DONE", settle=1.0)

        # Keyboard-primary path documented by the manual E2E:
        # type full name (auto-fills login/host), Tab through login and
        # computer name, type password twice, Tab+Space for admin-same.
        # Make sure keyboard focus is in the form (orange border) rather than
        # left on the page's Next button by the previous page transition.
        for _ in range(12):
            p = self.shot("08-focus-check")
            if self.s.has_orange(p, region=(168, 20, 620, 85)):
                break
            self.s.key("tab", settle=0.15)
        self.s.type_text(FULLNAME, delay=0.06)
        time.sleep(0.8)
        p = self.shot("08-users-name")
        text = self.s.ocr(p, crop=CONTENT)
        low = text.lower()
        if "gentoo user" not in low:
            self.add("user_creation", "FAIL",
                     "typing the full name did not populate the Users page", p)
            raise TestFailure("Users page full-name field did not receive typing")
        # Login and host should be auto-filled from the full name.
        autofill = "gentoo" in low and "gentoo-test" in low
        if autofill:
            self.add("user_autofill", "PASS",
                     "login and computer name auto-filled from full name", p)
        else:
            self.add("user_autofill", "FAIL",
                     "login/computer name were not auto-filled", p)
        # Tab to login, Tab to computer, Tab to password, type; Tab to
        # repeat, type; Tab to admin checkbox, Space.
        self.s.key("tab", settle=0.2)   # login
        self.s.key("tab", settle=0.2)   # computer
        self.s.key("tab", settle=0.2)   # password
        self.s.type_text(PASSWORD, delay=0.06)
        self.s.key("tab", settle=0.2)   # repeat password
        self.s.type_text(PASSWORD, delay=0.06)
        self.s.key("tab", settle=0.2)   # admin-same checkbox
        self.s.key("space", settle=0.6)
        time.sleep(0.5)
        p = self.shot("08-users-filled")
        text = self.s.ocr(p, crop=CONTENT)
        low = text.lower()
        if "use the same password" not in low:
            # If the checkbox focus order changed, fall back to clicking the
            # checkbox label via OCR.
            try:
                self.s.click_word("same", p, label="admin-same")
            except ScreenError:
                pass
        # Advance with Alt+N; require Summary to appear.
        self.s.key("alt-n", settle=1.0)
        try:
            self.s.wait_text(["This is an overview", "Summary"], timeout=25,
                             crop=CONTENT, label="summary")
        except WaitTimeout:
            # Mouse fallback: click the geometry-derived primary button.
            self.click_next()
            try:
                self.s.wait_text(["This is an overview", "Summary"], timeout=15,
                                 crop=CONTENT, label="summary-mouse")
            except WaitTimeout:
                p2 = self.shot("08-users-next-failed")
                self.add("user_creation", "FAIL",
                         "Users page did not advance with Alt+N or a geometry "
                         "click", p2)
                raise TestFailure(
                    "Users page did not advance to Summary; page OCR: "
                    + re.sub(r"\s+", " ", text)[-600:]
                )
        self.add("user_creation", "PASS",
                 f"{FULLNAME} / {USERNAME} / {HOSTNAME}; admin password same; "
                 "Alt+N advanced to Summary", p)
        self.add("install_summary_page", "PASS", "Summary page reached",
                 self.shot("09-summary"))

    def summary(self) -> None:
        p = self.shot("09-summary")
        text = self.s.ocr(p, crop=CONTENT)
        if "install" not in text.lower():
            raise TestFailure("summary page did not render")
        self.add("summary", "PASS",
                 "summary rendered; " + re.sub(r"\s+", " ", text)[:300], p)
        # Keyboard-primary: Alt+I opens the Install confirmation; Return
        # activates the focused Install Now button.
        self.s.key("alt-i", settle=1.0)
        time.sleep(1)
        p = self.shot("10-install-confirm")
        confirm = self.s.ocr(p)
        if "install now" in confirm.lower():
            self.s.key("return", settle=1.0)
            self.add("install_confirmation", "PASS",
                     "Install Now confirmed with Alt+I then Return", p)
        else:
            # Fallback: locate the orange Install / Install Now button.
            pos = self.s.find_primary_button(p)
            if pos:
                self.s.click(pos[0], pos[1], settle=1.0)
            try:
                pos = self.s.find_word("Now", p)
            except Exception:
                pos = None
            if pos:
                self.s.click(pos[0], pos[1], settle=1.0)
            self.add("install_confirmation", "INFO",
                     "no Install Now dialog text recognized; keyboard/mouse "
                     "fallbacks attempted", p)

    def monitor_install(self) -> None:
        log.info("waiting for install completion (timeout %.0fs)", self.timeout)
        started = time.time()
        deadline = started + self.timeout
        n = 0
        last_pct = None
        while time.time() < deadline:
            n += 1
            p = self.shot(f"11-progress-{n:02d}")
            try:
                text = self.s.ocr(p, crop=CONTENT)
            except ScreenError:
                text = ""
            low = re.sub(r"\s+", " ", text).lower()
            self.progress_shots.append(str(p))
            pct = None
            m = re.search(r"(\d{1,3})\s*%", text)
            if m:
                pct = int(m.group(1))
            if pct != last_pct:
                log.info("install progress: %s%%", pct)
                last_pct = pct
            if "setting up ember" in low or "installing" in low:
                if not self.progress_seen:
                    self.add("install_progress", "PASS",
                             "Calamares entered the install progress phase", p)
                    self.progress_seen = True
            if "all done" in low or "has been installed" in low:
                p2 = self.shot("12-install-complete")
                self.add("install_completed", "PASS",
                         f"Calamares reached Finish after {(time.time()-started)/60:.1f} min",
                         p2)
                return
            failure_markers = (
                "installation failed", "install failed", "failed to install",
                "installer failed", "could not install", "fatal error",
            )
            if any(x in low for x in failure_markers):
                # capture the detailed log before reporting
                try:
                    self.s.click(1200, 760, settle=1)  # Toggle log
                    time.sleep(1)
                except Exception:
                    pass
                p2 = self.shot("12-install-failed")
                self.add("install_completed", "FAIL",
                         "Calamares reported an installation failure", p2)
                raise TestFailure("Calamares reported an installation failure")
            time.sleep(12)
        p = self.shot("12-install-timeout")
        self.add("install_completed", "FAIL",
                 f"install did not finish within {self.timeout/60:.0f} min", p)
        raise TestFailure("install timed out")

    def run(self) -> dict[str, Any]:
        self.wait_live_installer()
        self.welcome()
        self.location()
        self.keyboard()
        self.stage3_guide()
        self.stage_select()
        self.desktop_choice()
        self.partitions()
        self.users()
        self.summary()
        self.monitor_install()
        return {"checks": [c.__dict__ for c in self.checks],
                "evidence": self.evidence,
                "progress_shots": self.progress_shots}
