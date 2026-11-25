#!/usr/bin/env python3
"""Installed-system boot/login/terminal/network checks for Ember QA."""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from screen import Screen, WaitTimeout, ScreenError
from installer import PASSWORD, USERNAME, FULLNAME, Check, TestFailure, TestBlocked

log = logging.getLogger("emberqa.postboot")

LIGHTDM_PASSWORD = (690, 405)
LIGHTDM_LOGIN = (750, 452)


class PostBoot:
    def __init__(self, screen: Screen, vm, *, desktop: str,
                 network_fault: bool = False, luks: bool = False):
        self.s = screen
        self.vm = vm
        self.desktop = desktop
        self.network_fault = network_fault
        self.luks = luks
        self.luks_unlocks = 0
        self.checks: list[Check] = []
        self.evidence: list[str] = []

    def add(self, name: str, status: str, detail: str = "",
            evidence: Path | str | None = None) -> None:
        ev = [str(evidence)] if evidence else []
        if evidence:
            self.evidence.append(str(evidence))
        self.checks.append(Check(name, status, detail, ev))
        log.info("CHECK %-28s %-7s %s", name, status, detail)

    def shot(self, name: str) -> Path:
        return self.s.shot(name)

    def wait_boot(self, timeout: float = 360) -> str:
        log.info("waiting for installed system (%s)", self.desktop)
        deadline = time.time() + timeout
        last = ""
        greeter_markers = (
            "login:", "gentoo login", "lightdm", "sddm", "gdm", "tuigreet",
            "username:", "password:", "gentoo user",
        )
        while time.time() < deadline:
            p = self.shot("19-boot")
            try:
                text = self.s.ocr(p)
            except ScreenError:
                text = ""
            last = text
            low = text.lower()
            if self.luks and self.luks_unlocks < 6:
                if ("passphrase" in low or "luks" in low
                        or "encrypted" in low or "crypt" in low):
                    p2 = self.shot(f"19-luks-prompt-{self.luks_unlocks + 1}")
                    self.add("luks_unlock_prompt", "INFO",
                             "LUKS passphrase prompt handled", p2)
                    self.s.type_text(PASSWORD, delay=0.06)
                    self.s.key("return", settle=2.0)
                    self.luks_unlocks += 1
                    time.sleep(5)
                    continue
            if self.desktop == "server":
                if "login:" in low or "gentoo login" in low:
                    self.add("disk_boot", "PASS",
                             "installed disk booted to a text login prompt", p)
                    return text
            else:
                if any(m in low for m in greeter_markers):
                    self.add("disk_boot", "PASS",
                             f"installed disk booted to a login screen ({self.desktop})", p)
                    return text
            # GRUB may still be on screen; give it time to auto-boot.
            time.sleep(3)
        self.shot("19-boot-timeout")
        raise TestFailure(f"installed system did not reach a login prompt: {last[-800:]!r}")

    def _greeter_visible(self, text: str) -> bool:
        low = text.lower()
        return any(m in low for m in ("lightdm", "sddm", "gdm", "tuigreet",
                                      "password:", "username:", "login:"))

    def login_lightdm(self) -> None:
        log.info("logging in through LightDM")
        last = ""
        for attempt in range(1, 5):
            p = self.shot(f"20-lightdm-{attempt}")
            text = self.s.ocr(p)
            last = text
            # Some greeters hide the password row until the user is selected
            # or the screen is touched.
            if "gentoo user" not in text.lower():
                self.s.click(640, 360, settle=0.5)
                time.sleep(2)
                p = self.shot(f"20-lightdm-wake-{attempt}")
                text = self.s.ocr(p)
            self.s.click(*LIGHTDM_PASSWORD, settle=0.25)
            self.s.ctrl_a()
            self.s.type_text(PASSWORD, delay=0.06)
            self.s.key("return", settle=1.0)
            time.sleep(10)
            p = self.shot(f"21-after-login-{attempt}")
            text = self.s.ocr(p)
            if not self._greeter_visible(text):
                self.add("login", "PASS",
                         f"{FULLNAME} logged into {self.desktop} via LightDM", p)
                return
            log.warning("LightDM still visible after attempt %s", attempt)
            time.sleep(3)
        self.shot("21-login-failed")
        raise TestFailure(f"LightDM login failed; last OCR: {last[-600:]!r}")

    def login_generic(self, field: tuple[int, int], name: str) -> None:
        log.info("logging in through %s", name)
        last = ""
        for attempt in range(1, 5):
            p = self.shot(f"20-{name.lower()}-{attempt}")
            last = self.s.ocr(p)
            self.s.click(*field, settle=0.3)
            self.s.ctrl_a()
            self.s.type_text(PASSWORD, delay=0.06)
            self.s.key("return", settle=1.0)
            time.sleep(15)
            p = self.shot(f"21-after-login-{attempt}")
            text = self.s.ocr(p)
            if not self._greeter_visible(text):
                self.add("login", "PASS",
                         f"{FULLNAME} logged into {self.desktop} via {name}", p)
                return
            log.warning("%s still visible after attempt %s", name, attempt)
            time.sleep(3)
        raise TestFailure(f"{name} login failed; last OCR: {last[-600:]!r}")

    def login_greetd(self) -> None:
        log.info("logging in through greetd/tuigreet")
        self.s.type_text(USERNAME, delay=0.06)
        self.s.key("return", settle=0.8)
        self.s.type_text(PASSWORD, delay=0.06)
        self.s.key("return", settle=3.0)
        time.sleep(12)
        p = self.shot("21-after-greetd")
        text = self.s.ocr(p)
        if self._greeter_visible(text):
            raise TestFailure("greetd login did not reach the desktop")
        self.add("login", "PASS",
                 f"{FULLNAME} logged into {self.desktop} via greetd/tuigreet", p)

    def login_console(self) -> None:
        log.info("logging in at the text console")
        p = self.shot("20-console-login")
        text = self.s.ocr(p)
        if "login:" not in text.lower():
            try:
                self.s.wait_text(["login:"], timeout=60, label="server-login",
                                 every=3)
            except WaitTimeout as exc:
                raise TestFailure(f"no text login prompt: {exc}") from exc
        self.s.type_text(USERNAME, delay=0.06)
        self.s.key("return", settle=0.8)
        self.s.type_text(PASSWORD, delay=0.06)
        self.s.key("return", settle=3.0)
        p = self.shot("21-console-after-login")
        text = self.s.ocr(p)
        if "incorrect" in text.lower() or "login:" in text.lower():
            raise TestFailure("text console login was rejected")
        self.add("login", "PASS", f"{FULLNAME} logged in at the text console", p)

    def _terminal_present(self) -> bool:
        p = self.shot("22-terminal-check")
        text = self.s.ocr(p, crop=(0, 0, 1280, 780))
        low = text.lower()
        return ("gentoo@" in low or "~$" in low or "bash" in low
                or "ember-qa-start" in low)

    def open_terminal(self) -> None:
        log.info("opening a terminal in %s", self.desktop)
        if self.desktop == "server":
            self.add("terminal", "PASS", "text console is the terminal", self.shot("22-console"))
            return

        term = {
            "openbox": "xterm", "xfce": "xfce4-terminal", "kde": "konsole",
            "gnome": "gnome-terminal", "cinnamon": "gnome-terminal",
            "mate": "mate-terminal", "lxqt": "qterminal", "i3": "xterm",
            "sway": "foot", "hyprland": "kitty", "fluxbox": "xterm",
            "icewm": "xterm",
        }.get(self.desktop, "xterm")

        if self.desktop in ("openbox", "fluxbox", "icewm"):
            self.s.click(700, 400, button=3, settle=1.0)
            p = self.shot(f"22-{self.desktop}-menu")
            pos = None
            for word in ("Terminal", term, "xterm"):
                try:
                    pos = self.s.find_word(word, p)
                except Exception:
                    pos = None
                if pos:
                    break
            if pos:
                self.s.click(pos[0], pos[1], settle=2.5)
            else:
                self.s.click(675, 411, settle=2.5)
        elif self.desktop == "i3":
            # desktop_setup writes Mod4+Return -> xterm.
            self.s.key("super-return", settle=3.0)
        elif self.desktop in ("sway", "hyprland"):
            # Wayland compositor default Mod4+Return.
            self.s.key("super-return", settle=3.0)
        elif self.desktop == "lxqt":
            # Try the common shortcut first, then the runner.
            self.s.key("ctrl-alt-t", settle=3.0)
            if not self._terminal_present():
                self.s.key("alt-f2", settle=1.0)
                self.s.type_text(term, delay=0.05)
                self.s.key("return", settle=3.0)
        else:
            self.s.key("alt-f2", settle=1.2)
            self.s.type_text(term, delay=0.05)
            self.s.key("return", settle=3.5)

        time.sleep(2)
        p = self.shot("22-terminal-open")
        text = self.s.ocr(p, crop=(0, 0, 1280, 780))
        if not self._terminal_present():
            raise TestFailure(
                f"terminal did not open in {self.desktop}; OCR: "
                + re.sub(r"\s+", " ", text)[-500:]
            )
        self.add("terminal", "PASS", f"terminal opened in {self.desktop}", p)
        # Maximize X11 terminals so terminal output is readable and OCR-able.
        if self.desktop not in ("sway", "hyprland"):
            self.s.key("alt-f10", settle=1.0)
            time.sleep(0.5)
            self.shot("22-terminal-maximized")

    def _run(self, command: str, *, settle: float = 1.0) -> None:
        self.s.type_text(command, delay=0.04)
        self.s.key("return", settle=settle)

    def _terminal_text(self, name: str) -> tuple[Path, str]:
        p = self.shot(name)
        # Terminal may be light or dark; OCR preprocessing auto-inverts.
        text = self.s.ocr(p, crop=(0, 0, 1280, 780), scale=2.0, psm=6)
        return p, text

    def ping(self) -> None:
        log.info("running ping from the installed system")
        self._run("clear", settle=0.5)
        self._run("echo EMBER-QA-START", settle=0.5)
        self._run("ping -c 1 9.9.9.9; echo EMBER_PING_RC=$?", settle=14.0)
        p, text = self._terminal_text("23-ping")
        low = text.lower()
        self.evidence.append(str(p))
        ok = (
            "1 received" in low
            or "0% packet loss" in low
            or re.search(r"ember_ping_rc\s*[=:]\s*0", low) is not None
        )
        if not ok:
            # One retry is allowed for a transient slirp hiccup, but the first
            # failure is preserved as evidence and the result says so.
            log.warning("first ping check did not verify; retrying once")
            self._run("ping -c 1 9.9.9.9; echo EMBER_PING_RC=$?", settle=14.0)
            p2, text2 = self._terminal_text("23-ping-retry")
            low2 = text2.lower()
            ok2 = (
                "1 received" in low2
                or "0% packet loss" in low2
                or re.search(r"ember_ping_rc\s*[=:]\s*0", low2) is not None
            )
            if ok2:
                self.add("ping", "PASS",
                         "ping -c1 9.9.9.9 succeeded on retry (first attempt unverified)",
                         p2)
                return
            self.add("ping", "FAIL", "ping -c1 9.9.9.9 did not succeed", p2)
            raise TestFailure("ping failed from the installed system")
        self.add("ping", "PASS", "ping -c1 9.9.9.9: 1 received, 0% loss", p)

    def services_and_desktop(self) -> None:
        log.info("checking default services and desktop process")
        procs = {
            "openbox": "openbox", "xfce": "xfce4-session", "kde": "plasmashell",
            "gnome": "gnome-shell", "cinnamon": "cinnamon", "mate": "mate-session",
            "lxqt": "lxqt-session", "i3": "i3", "sway": "sway",
            "hyprland": "Hyprland", "fluxbox": "fluxbox", "icewm": "icewm",
        }
        proc = procs.get(self.desktop, "")
        if proc:
            self._run(f"pgrep -a {proc}", settle=1.0)
            p, text = self._terminal_text(f"24-{proc}")
            low = text.lower()
            if proc.lower() in low:
                self.add("desktop_process", "PASS", f"{proc} is running", p)
            else:
                self.add("desktop_process", "FAIL", f"{proc} is not running", p)
                raise TestFailure(f"{proc} is not running after login")
        if self.desktop == "gnome":
            self._run("systemctl is-system-running", settle=2.0)
            p, text = self._terminal_text("25-systemd-state")
            low = text.lower()
            if "running" in low:
                self.add("services", "PASS", "systemd reports running", p)
            elif "degraded" in low:
                self.add("services", "FAIL", "systemd reports degraded", p)
                raise TestFailure("systemd reports degraded after boot")
            else:
                self.add("services", "INFO", "systemd state not clearly OCR-able", p)
        elif self.desktop != "server":
            # OpenRC default runlevel (Openbox/Xfce/KDE/Cinnamon/MATE/LXQt/i3...)
            self._run("rc-status default", settle=2.0)
            p, text = self._terminal_text("25-rc-status")
            low = text.lower()
            started = "started" in low
            failed = "crashed" in low or "failed" in low
            if started and not failed:
                self.add("services", "PASS", "rc-status default has started services", p)
            elif failed:
                self.add("services", "FAIL", "a default service is not started", p)
                raise TestFailure("default runlevel has a failed service")
            else:
                self.add("services", "INFO", "rc-status output not clearly OCR-able", p)

    def network_fault_test(self) -> None:
        log.info("testing network failure and resume")
        self.vm.set_link(False)
        time.sleep(2)
        self._run("ping -c 1 -W 2 9.9.9.9; echo EMBER_DOWN_RC=$?", settle=6.0)
        p, text = self._terminal_text("26-network-down")
        low = text.lower()
        down_ok = (
            re.search(r"ember_down_rc\s*[=:]\s*[1-9]", low) is not None
            or "100% packet loss" in low
            or "unreachable" in low
            or "network is down" in low
        )
        if down_ok:
            self.add("network_down", "PASS",
                     "ping fails while the QEMU link is down", p)
        else:
            self.add("network_down", "FAIL",
                     "ping unexpectedly succeeded or gave no clear failure while link down", p)
            self.vm.set_link(True)
            raise TestFailure("could not verify network-down state")
        self.vm.set_link(True)
        time.sleep(8)
        self._run("ping -c 1 9.9.9.9; echo EMBER_RESUME_RC=$?", settle=14.0)
        p, text = self._terminal_text("27-network-resumed")
        low = text.lower()
        up_ok = (
            "1 received" in low
            or "0% packet loss" in low
            or re.search(r"ember_resume_rc\s*[=:]\s*0", low) is not None
        )
        if up_ok:
            self.add("network_resume", "PASS",
                     "network recovers after QMP link down/up", p)
        else:
            self.add("network_resume", "FAIL",
                     "network did not recover after link up", p)
            raise TestFailure("network did not resume after link up")

    def run(self) -> dict[str, Any]:
        self.wait_boot()
        if self.desktop == "server":
            self.login_console()
        elif self.desktop in ("sway", "hyprland"):
            self.login_greetd()
            time.sleep(3)
            self.shot("21-desktop")
        elif self.desktop == "kde":
            self.login_generic((690, 400), "SDDM")
            time.sleep(3)
            self.shot("21-desktop")
        elif self.desktop == "gnome":
            self.login_generic((690, 450), "GDM")
            time.sleep(3)
            self.shot("21-desktop")
        else:
            self.login_lightdm()
            time.sleep(3)
            self.shot("21-desktop")
        self.open_terminal()
        self.ping()
        self.services_and_desktop()
        if self.network_fault:
            self.network_fault_test()
        return {"checks": [c.__dict__ for c in self.checks],
                "evidence": self.evidence}
