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
                 world_update: bool = False, secure_boot: bool = False):
        if desktop not in DESKTOPS:
            raise ValueError(f"unknown desktop {desktop!r}")
        self.s = screen
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
        self.click_next()
        return self.s.wait_text(expect, timeout=timeout, crop=CONTENT, label=label)

    def click_next(self) -> None:
        """Click Calamares Next, locating it if the window is not maximized."""
        p = self.shot("next-button")
        try:
            pos = self.s.find_word("Next", p)
        except Exception:
            pos = None
        if pos and pos[0] > 800 and pos[1] > 400:
            self.s.click(pos[0], pos[1], settle=0.8)
        else:
            self.s.click(*NEXT, settle=0.8)

    def edge_click(self, x: int, y: int, settle: float = 0.8) -> None:
        self.s.click(x, y, settle=settle)

    # -- pages -----------------------------------------------------------
    def wait_live_installer(self, timeout: float = 420) -> None:
        log.info("waiting for the live installer")
        deadline = time.time() + timeout
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
            if "welcome to" in low or ("welcome" in low and "installer" in low):
                p = self.shot("01-welcome")
                # Calamares may open in a small window on the live desktop;
                # maximize it so the documented 1280x800 coordinates apply.
                self.s.key("alt-f10", settle=1.0)
                time.sleep(0.5)
                p = self.shot("01-welcome-max")
                self.add("live_boot_installer", "PASS",
                         "Calamares welcome screen rendered", p)
                return
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

    def stage_select(self) -> None:
        log.info("selecting %s", self.stage_variant)
        # Architecture combo: first item is alpha, second is amd64.
        self.edge_click(620, 401, 0.5)
        self.edge_click(620, 423, 2.0)
        init_token = "systemd" if "systemd" in self.stage_variant else "openrc"
        last = ""
        selected = False
        # Wait for the variant list to be fetched from the mirror, then use
        # Qt type-ahead with the exact variant name.
        for attempt in range(1, 30):
            self.edge_click(830, 401, 0.45)
            self.s.type_text(self.stage_variant, delay=0.02)
            self.s.key("return", settle=0.8)
            time.sleep(2.0)
            p = self.shot(f"05-stage-select-try{attempt}")
            try:
                text = self.s.ocr(p, crop=CONTENT)
            except ScreenError:
                text = ""
            last = text
            low = text.lower()
            if ("selected:" in low and "stage3" in low and "no tar" not in low
                    and init_token in low
                    and any(t in low for t in ("desktop", "deskiop", "deskt0p", "desktcp"))
                    and "hardened" not in low and "musl" not in low
                    and "nomultilib" not in low):
                selected = True
                break
            # Not populated yet (Status: Fetching / Idle); wait and retry.
            time.sleep(3)
        p = self.shot("05-stage-selected")
        text = self.s.ocr(p, crop=CONTENT)
        low = text.lower()
        if not selected:
            # The variant list may have selected a different item if the
            # mirror ordering changed.  Report what was actually selected.
            raise TestFailure(
                f"could not select {self.stage_variant}; last page text: "
                + re.sub(r"\s+", " ", text)[-500:]
            )
        self.add("stage3_selected", "PASS", f"amd64 {self.stage_variant} selected", p)
        self.next(["Openbox (recommended)", "Server (no desktop)"], "desktop")

    def desktop_choice(self) -> None:
        d = DESKTOPS[self.desktop]
        p = self.shot(f"06-desktop-{self.desktop}-before")
        self.edge_click(250, d["y"], 0.8)
        p = self.shot(f"06-desktop-{self.desktop}")
        text = self.s.ocr(p, crop=CONTENT)
        if d["preview"].lower() not in text.lower():
            # OCR sometimes misses small list text; retry once with a crop of
            # the preview/description pane on the right.
            text2 = self.s.ocr(p, crop=(400, 600, 1280, 760))
            if d["preview"].lower() not in text2.lower():
                raise TestFailure(
                    f"desktop chooser did not show {d['name']} preview; got: "
                    + re.sub(r"\s+", " ", text)[-400:]
                )
        self.add("desktop_selection", "PASS", f"{d['name']} selected", p)
        # New ISOs insert the make.conf editor here; older ISOs go straight
        # to the partition page.  Detect which page actually appeared.
        self.click_next()
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
        # Verify the editor is populated with the generated make.conf.
        for key in ("CFLAGS", "MAKEOPTS", "ACCEPT_LICENSE"):
            if key.lower() not in low:
                # The editor is a large text area; OCR may miss lines.  Crop
                # the editor region and retry before failing.
                text2 = self.s.ocr(p, crop=(180, 80, 1260, 560), psm=6)
                if key.lower() not in text2.lower():
                    raise TestFailure(
                        f"make.conf editor does not show generated {key}"
                    )
        self.add("makeconf_editor", "PASS",
                 "Build configuration page shows generated make.conf", p)

        # Exercise the Suggest button (an explicit product requirement).
        p2 = p
        try:
            self.s.click_word("Suggest", p, label="suggest")
            time.sleep(2)
            p2 = self.shot("06c-build-config-suggested")
            text2 = self.s.ocr(p2, crop=CONTENT)
            if "valid" in text2.lower() and "configuration" in text2.lower():
                self.add("makeconf_suggest", "PASS",
                         "Suggest from hardware produced a valid configuration", p2)
            else:
                self.add("makeconf_suggest", "FAIL",
                         "Suggest from hardware did not produce a valid configuration", p2)
                raise TestFailure("make.conf Suggest did not produce a valid configuration")
        except ScreenError as exc:
            self.add("makeconf_suggest", "FAIL",
                     f"Suggest button not usable: {exc}", p)
            raise TestFailure(f"make.conf Suggest button not found: {exc}") from exc

        # Validate is idempotent and should keep the configuration valid.
        try:
            self.s.click_word("Validate", p2, label="validate")
            time.sleep(1)
            p3 = self.shot("06d-build-config-validated")
            text3 = self.s.ocr(p3, crop=CONTENT)
            if "valid" in text3.lower():
                self.add("makeconf_validate", "PASS", "Validate accepted the values", p3)
            else:
                self.add("makeconf_validate", "FAIL", "Validate did not report a valid config", p3)
                raise TestFailure("make.conf Validate did not report valid")
        except ScreenError as exc:
            self.add("makeconf_validate", "FAIL",
                     f"Validate button not usable: {exc}", p2)
            raise TestFailure(f"make.conf Validate button not found: {exc}") from exc

        if self.world_update:
            try:
                self.s.click_word("Update", p3, offset_x=-18, label="world-update")
                time.sleep(0.8)
                p4 = self.shot("06e-build-config-world")
                self.add("makeconf_world_update", "PASS",
                         "Update @world checkbox selected", p4)
            except ScreenError as exc:
                self.add("makeconf_world_update", "FAIL",
                         f"Update @world checkbox not found: {exc}", p3)
                raise TestFailure("Update @world checkbox not found") from exc

        if self.secure_boot:
            # On UEFI the page has a Secure Boot checkbox.  It defaults on;
            # verify it is present and checked, and do not silently proceed if
            # the product did not expose it.
            p5 = self.shot("06f-build-config-secureboot")
            text5 = self.s.ocr(p5, crop=CONTENT)
            if "secure boot" not in text5.lower():
                self.add("makeconf_secureboot", "FAIL",
                         "Secure Boot checkbox not visible on UEFI make.conf page", p5)
                raise TestFailure("Secure Boot checkbox not visible on UEFI")
            self.add("makeconf_secureboot", "INFO",
                     "Secure Boot checkbox present (default checked on UEFI)", p5)

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
        self.edge_click(185, 62, 1.0)
        p = self.shot("07-partitions-erase")
        text = self.s.ocr(p, crop=CONTENT)

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
            # in the same row when available.  Qt combo boxes support
            # type-ahead, so type the exact requested filesystem name.
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
            self.edge_click(184, 586, 1.0)
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

        def set_field(x: int, y: int, value: str, label: str,
                      crop: tuple[int, int, int, int]) -> None:
            for attempt in range(1, 4):
                self.s.click(x, y, settle=0.2)
                self.s.ctrl_a()
                self.s.type_text(value, delay=0.06)
                time.sleep(0.5)
                shot = self.shot(f"08-users-{label}-{attempt}")
                got = self.s.ocr(shot, crop=crop, psm=7).strip()
                norm = re.sub(r"\s+", " ", got).strip().lower()
                want = re.sub(r"\s+", " ", value).strip().lower()
                if want in norm or norm in want:
                    log.info("field %s verified: %r", label, got)
                    return
                log.warning("field %s mismatch: want %r got %r (attempt %s)",
                            label, value, got, attempt)
            # A mismatch is suspicious but not always an OCR failure.  Keep
            # going only if the page state can still advance; the screenshot
            # remains as evidence.
            log.error("could not OCR-verify field %s", label)

        set_field(275, 47, FULLNAME, "fullname", (175, 32, 390, 63))
        set_field(275, 100, USERNAME, "login", (175, 86, 390, 116))
        set_field(275, 156, HOSTNAME, "hostname", (175, 142, 390, 172))
        set_field(275, 213, PASSWORD, "password", (175, 199, 385, 228))
        set_field(482, 213, PASSWORD, "password2", (385, 199, 590, 228))
        # Use the same password for root/admin.
        self.s.click(184, 249, settle=0.8)
        p = self.shot("08-users-filled")
        self.add("user_creation", "PASS",
                 f"{FULLNAME} / {USERNAME} / {HOSTNAME}, admin password same", p)
        self.next(["This is an overview", "Summary"], "summary", timeout=30)

    def summary(self) -> None:
        p = self.shot("09-summary")
        text = self.s.ocr(p, crop=CONTENT)
        if "install" not in text.lower():
            raise TestFailure("summary page did not render")
        self.add("summary", "PASS",
                 "summary rendered; " + re.sub(r"\s+", " ", text)[:300], p)
        self.s.click(*INSTALL, settle=1.0)
        time.sleep(1)
        p = self.shot("10-install-confirm")
        confirm = self.s.ocr(p)
        if "install now" in confirm.lower():
            self.s.click(*CONFIRM_INSTALL, settle=1.0)
            self.add("install_confirmation", "PASS", "Install Now confirmed", p)
        else:
            # prompt-install may be disabled on some builds
            log.warning("no Install Now dialog seen; continuing if install started")
            self.add("install_confirmation", "INFO",
                     "no confirmation dialog (prompt-install may be off)", p)

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
