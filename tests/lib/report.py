#!/usr/bin/env python3
"""Build qa/REPORT-<iso-sha>.md from QA run results."""

from __future__ import annotations

import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from emberqa import QA, RUNS, iso_info, read_json, snapshot_iso, stamp, utcnow

log = logging.getLogger("emberqa.report")

# The intended full matrix.  Rows that were not executed are reported as
# NOT RUN; they are never treated as passes.
MATRIX = [
    (f"{fw}-{desktop}-ext4", fw, desktop, "ext4", False)
    for fw in ("bios", "uefi")
    for desktop in (
        "openbox", "xfce", "kde", "gnome", "cinnamon", "mate", "lxqt",
        "i3", "sway", "hyprland", "fluxbox", "icewm", "server",
    )
] + [
    ("bios-openbox-btrfs", "bios", "openbox", "btrfs", False),
    ("bios-openbox-xfs", "bios", "openbox", "xfs", False),
    ("bios-openbox-f2fs", "bios", "openbox", "f2fs", False),
    ("uefi-openbox-btrfs", "uefi", "openbox", "btrfs", False),
    ("uefi-openbox-xfs", "uefi", "openbox", "xfs", False),
    ("uefi-openbox-f2fs", "uefi", "openbox", "f2fs", False),
    ("bios-openbox-luks", "bios", "openbox", "ext4", True),
    ("uefi-openbox-luks", "uefi", "openbox", "ext4", True),
    ("bios-openbox-lvm", "bios", "openbox", "ext4", False),
    ("uefi-openbox-lvm", "uefi", "openbox", "ext4", False),
    ("uefi-openbox-secureboot", "uefi", "openbox", "ext4", False),
    ("bios-openbox-netfault", "bios", "openbox", "ext4", False),
    ("uefi-openbox-netfault", "uefi", "openbox", "ext4", False),
    ("bios-openbox-worldupdate", "bios", "openbox", "ext4", False),
]


def _load_results(iso_sha: str, run_filter: list[str] | None) -> dict[str, dict]:
    out = {}
    if not RUNS.exists():
        return out
    for d in RUNS.iterdir():
        if not d.is_dir():
            continue
        if run_filter and d.name not in run_filter:
            continue
        p = d / "result.json"
        if not p.exists():
            continue
        try:
            r = read_json(p)
        except Exception:
            continue
        if r.get("iso", {}).get("sha256") != iso_sha:
            continue
        out[d.name] = r
    return out


def _check(result: dict, name: str) -> str:
    for c in result.get("checks", []):
        if c.get("name") == name:
            return c.get("status", "INFO")
    # phase-specific fallbacks
    for c in result.get("postboot_checks", []):
        if c.get("name") == name:
            return c.get("status", "INFO")
    for c in result.get("install_checks", []):
        if c.get("name") == name:
            return c.get("status", "INFO")
    return "—"


def _duration(result: dict) -> str:
    try:
        start = datetime.fromisoformat(result["started"].replace("Z", "+00:00"))
        end = datetime.fromisoformat(result["finished"].replace("Z", "+00:00"))
        mins = (end - start).total_seconds() / 60
        return f"{mins:.1f}m"
    except Exception:
        return "—"


def _rel(path: str) -> str:
    p = Path(path)
    try:
        return str(p.relative_to(Path.cwd()))
    except ValueError:
        return str(p)


def build_report(*, iso: Path, run_filter: list[str] | None = None,
                 title: str | None = None) -> Path:
    info = snapshot_iso(iso)
    sha = info["sha256"]
    results = _load_results(sha, run_filter)
    QA.mkdir(exist_ok=True)
    path = QA / f"REPORT-{sha[:8]}.md"

    now = utcnow()
    lines: list[str] = []
    lines.append(f"# {title or 'Ember Linux QA matrix'} — `{sha[:12]}`")
    lines.append("")
    lines.append(f"- Generated: `{now}`")
    lines.append(f"- ISO source path (at capture): `{info['path']}`")
    if info.get("snapshot"):
        lines.append(f"- Tested immutable snapshot: `{info['snapshot']}`")
    lines.append(f"- ISO size: `{info['size']:,}` bytes ({info['size']/1024**3:.2f} GiB)")
    lines.append(f"- ISO mtime: `{info['mtime']}`")
    lines.append(f"- ISO SHA-256: `{sha}`")
    lines.append("- The build output may have been rebuilt after this snapshot was")
    lines.append("  captured; QEMU booted the immutable snapshot, and its SHA above is")
    lines.append("  the tested artifact.")
    lines.append("- Harness: `tests/ember-qa.py` (QEMU/KVM, VNC, OCR-driven installer)")
    lines.append("- Rules: one VM at a time; no test is weakened to pass. Product")
    lines.append("  failures are recorded as FAIL. BLOCKED means the ISO does not expose")
    lines.append("  the feature under test, not that it passed.")
    lines.append("")
    lines.append("## Result summary")
    lines.append("")
    lines.append("| Test | Firmware | Desktop | Filesystem | Install | Login | Terminal | Ping | Status | Time |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    # Executed tests first, in start order.
    ordered = sorted(results.values(), key=lambda r: r.get("started", ""))
    executed_ids = {r.get("test_id") for r in ordered}
    counts: dict[str, int] = {}
    for r in ordered:
        spec = r.get("spec", {})
        st = r.get("status", "FAIL")
        counts[st] = counts.get(st, 0) + 1
        fs = spec.get("filesystem", "ext4")
        if spec.get("luks"):
            fs += "+LUKS"
        if spec.get("lvm"):
            fs += "+LVM"
        if spec.get("secure_boot"):
            fs += "+SecureBoot"
        test = r.get("test_id", r["run_name"])
        install_status = _check(r, "install_completed")
        if install_status == "—":
            install_status = _check(r, "live_boot_installer")
        lines.append(
            f"| {test} | {spec.get('firmware','?')} | {spec.get('desktop','?')} | "
            f"{fs} | {install_status} | {_check(r,'login')} | "
            f"{_check(r,'terminal')} | {_check(r,'ping')} | **{st}** | {_duration(r)} |"
        )
    for test_id, fw, desktop, fs, luks in MATRIX:
        if test_id in executed_ids:
            continue
        suffix = "+LUKS" if luks else ""
        lines.append(
            f"| {test_id} | {fw} | {desktop} | {fs}{suffix} | — | — | — | — | "
            "NOT RUN | — |"
        )
    lines.append("")
    if counts:
        lines.append("Executed: " + ", ".join(f"**{k}** {v}" for k, v in sorted(counts.items())))
    else:
        lines.append("No completed runs for this ISO SHA yet.")
    lines.append("")

    init_failures = [
        r for r in ordered
        if "initialization failed" in (r.get("error", {}).get("message", "").lower())
        or "could not be loaded" in (r.get("error", {}).get("message", "").lower())
    ]
    init_ids = [r.get("test_id") for r in init_failures]
    if init_failures:
        lines.append("> **Global blocker:** Calamares fails during initialization before the")
        lines.append("> Welcome page (`Calamares Initialization Failed`, missing")
        lines.append("> `shellprocess@postinstall`). No desktop package install, disk boot, login,")
        lines.append("> terminal, or ping can start for any chooser entry. Rows below marked")
        lines.append("> NOT RUN are blocked by this installer defect, not skipped to make a test pass.")
        desktop_ids = {
            f"{fw}-{d}-ext4"
            for fw in ("bios", "uefi")
            for d in (
                "openbox", "xfce", "kde", "gnome", "cinnamon", "mate", "lxqt",
                "i3", "sway", "hyprland", "fluxbox", "icewm", "server",
            )
        }
        executed_desktops = {r.get("test_id") for r in ordered} & desktop_ids
        lines.append(">")
        lines.append(f"> Desktop rows attempted: **{len(executed_desktops)}/{len(desktop_ids)}**; "
                     f"all {len(init_ids)} completed rows hit this same failure.")
        lines.append("> The remaining desktop rows cannot reach the chooser either; they are "
                     "NOT RUN rather than guessed.")
        # Root-cause evidence: inspect the Calamares config in the tested
        # snapshot.  This is read-only and does not modify the product.
        try:
            from emberqa import iso_calamares_file
            import yaml
            snap = info.get("snapshot", info["path"])
            post = iso_calamares_file(Path(snap), "modules/postinstall.conf")
            try:
                yaml.safe_load(post)
            except Exception as yaml_exc:
                first = str(yaml_exc).splitlines()
                detail = " ".join(first[:4]).replace("\n", " ")
                lines.append("")
                lines.append("**Root cause evidence:** the tested ISO's "
                             "`etc/calamares/modules/postinstall.conf` does not parse "
                             "as YAML, so Calamares cannot load "
                             "`shellprocess@postinstall`:")
                lines.append("")
                lines.append(f"```\n{detail}\n```")
        except Exception as exc:
            log.debug("could not build root-cause evidence: %s", exc)
        lines.append("")

    failures = [r for r in ordered if r.get("status") in ("FAIL", "BLOCKED")]
    lines.append("## Product failures / blockers")
    lines.append("")
    if not failures:
        lines.append("None recorded in the executed rows.")
    else:
        others = [r for r in failures if r.get("test_id") not in init_ids]
        if init_ids:
            lines.append(
                "- **Global — Calamares initialization failure** in "
                f"{len(init_ids)} executed row(s): "
                + ", ".join(f"`{x}`" for x in init_ids)
            )
            lines.append("  - module `shellprocess@postinstall` could not be loaded; "
                         "no installer page after startup was reachable")
        for r in others:
            err = r.get("error") or {}
            msg = err.get("message", "no message")
            if "calamares initialization failed" in msg.lower():
                msg = ("Calamares Initialization Failed before the Welcome page; "
                       "module `shellprocess@postinstall` could not be loaded")
            lines.append(f"- **{r.get('test_id')} — {r.get('status')}**: "
                         f"{err.get('kind','?')}: {msg}")
            if err.get("phase"):
                lines.append(f"  - phase: `{err['phase']}`")
    lines.append("")

    lines.append("## Per-test evidence")
    lines.append("")
    for r in ordered:
        spec = r.get("spec", {})
        lines.append(f"### {r.get('test_id')} — {r.get('status')}")
        lines.append("")
        lines.append(f"- Run dir: `{r.get('artifacts',{}).get('dir','?')}`")
        lines.append(f"- Firmware: `{spec.get('firmware')}`; desktop: `{spec.get('desktop')}`; "
                     f"filesystem: `{spec.get('filesystem')}`; LUKS: `{spec.get('luks')}`; "
                     f"LVM: `{spec.get('lvm')}`; Secure Boot: `{spec.get('secure_boot')}`")
        lines.append(f"- Started/finished: `{r.get('started')}` → `{r.get('finished')}`")
        if r.get("error"):
            err = r["error"]
            msg = err.get("message", "no message")
            if "calamares initialization failed" in msg.lower():
                msg = ("Calamares Initialization Failed before the Welcome page; "
                       "module `shellprocess@postinstall` could not be loaded")
            lines.append(f"- Error: **{err.get('kind')}** ({err.get('phase')}): "
                         f"{msg}")
        lines.append("")
        lines.append("| Check | Result | Detail |")
        lines.append("|---|---|---|")
        for c in r.get("checks", []):
            detail = (c.get("detail") or "").replace("|", "\\|").replace("\n", " ")
            lines.append(f"| {c.get('name')} | {c.get('status')} | {detail[:300]} |")
        lines.append("")
        shots = r.get("artifacts", {}).get("screenshots")
        if shots:
            lines.append(f"Screenshots: `{shots}`")
            lines.append("")
        logs = []
        for key in ("serial_install", "serial_disk", "qmp_install", "qmp_disk"):
            p = r.get("artifacts", {}).get(key)
            if p and Path(p).exists():
                logs.append(f"[{key}]({_rel(p)})")
        if logs:
            lines.append("Logs: " + ", ".join(logs))
            lines.append("")
        # Show a handful of key screenshots inline when present.
        for name in ("01-welcome.png", "installer-init-failed.png",
                     "installer-not-found.png", "06-desktop-openbox.png",
                     "06-desktop-xfce.png", "06-desktop-kde.png",
                     "06-desktop-server.png", "06-desktop-gnome.png",
                     "06b-build-config.png", "07-partitions-erase.png",
                     "12-install-complete.png", "12-install-failed.png",
                     "12-install-timeout.png", "19-boot.png", "19-boot-timeout.png",
                     "20-lightdm-1.png", "21-desktop.png", "23-ping.png",
                     "23-ping-retry.png", "20-console-login.png",
                     "21-console-after-login.png"):
            for key in ("screenshots",):
                p = Path(r.get("artifacts", {}).get(key, "")) / name
                if p.is_file():
                    lines.append(f"![{name}]({_rel(p)})")
                    lines.append("")
        lines.append("")

    lines.append("## How to reproduce")
    lines.append("")
    lines.append("```bash")
    lines.append("cd /home/user/ember")
    lines.append(f"tests/ember-qa.py run --test-id bios-openbox-ext4 --firmware bios --desktop openbox --iso {info.get('snapshot', info['path'])}")
    lines.append(f"tests/ember-qa.py run --test-id uefi-openbox-ext4 --firmware uefi --desktop openbox --iso {info.get('snapshot', info['path'])}")
    lines.append(f"tests/ember-qa.py report --iso {info.get('snapshot', info['path'])}")
    lines.append("```")
    lines.append("")
    lines.append("See `tests/README.md` for the full matrix, filesystem/LUKS/LVM/")
    lines.append("Secure Boot and network-fault commands.")
    lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
