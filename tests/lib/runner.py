#!/usr/bin/env python3
"""Orchestrate one Ember install -> disk boot -> login -> ping test."""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import shutil
import time
import traceback
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any

from emberqa import (
    QA, RUNS, ISO_DEFAULT, VM, ensure_run_dir, iso_info, snapshot_iso,
    iso_capabilities, free_bytes, reclaim_qa_disks, read_json, write_json,
    utcnow, stamp, sanitize, setup_logging, qemu_processes, port_free,
)
from screen import Screen, ScreenError
from installer import (
    Installer, TestFailure, TestBlocked, PASSWORD, FULLNAME, USERNAME, HOSTNAME,
)
from postboot import PostBoot

log = logging.getLogger("emberqa.runner")


@dataclass
class Spec:
    test_id: str
    desktop: str = "openbox"
    firmware: str = "bios"
    filesystem: str = "ext4"
    luks: bool = False
    lvm: bool = False
    secure_boot: bool = False
    network_fault: bool = False
    fault_install: bool = False
    world_update: bool = False
    timeout: float = 3600
    iso: str = str(ISO_DEFAULT)
    keep_disk: bool = False
    name: str | None = None

    def run_name(self) -> str:
        if self.name:
            return sanitize(self.name)
        return sanitize(f"{stamp()}-{self.test_id}")


def _phase_summary(checks: list[dict]) -> dict[str, int]:
    out: dict[str, int] = {}
    for c in checks:
        out[c.get("status", "INFO")] = out.get(c.get("status", "INFO"), 0) + 1
    return out


def _write_status(run: Path, status: str, detail: str = "") -> None:
    with (run / "status.log").open("a", encoding="utf-8") as fh:
        fh.write(f"{utcnow()} {status} {detail}\n")


def _serial_tail(run: Path, lines: int = 80) -> str:
    tails = []
    for p in sorted(run.glob("serial-*.log")):
        try:
            content = p.read_text(errors="replace").splitlines()
            tails.append(f"--- {p.name} (tail) ---\n" + "\n".join(content[-lines:]))
        except OSError:
            pass
    return "\n".join(tails)


def _capture_failure_screen(vm: VM, run: Path, label: str) -> str | None:
    try:
        s = Screen(vm, "failure")
        p = s.shot(label)
        return str(p)
    except Exception as exc:
        log.warning("could not capture failure screenshot: %s", exc)
        return None


def run_test(spec: Spec) -> dict[str, Any]:
    name = spec.run_name()
    run = ensure_run_dir(name)
    setup_logging(name)
    iso = Path(spec.iso).resolve()

    # Refuse to mix results from two ISOs in one run directory, and record the
    # exact artifact identity up front.  Boot from the verified snapshot, not
    # the mutable build output.
    info = snapshot_iso(iso)
    boot_iso = Path(info["snapshot"])
    caps = iso_capabilities(boot_iso)
    meta = {
        "test_id": spec.test_id,
        "run_name": name,
        "spec": asdict(spec),
        "iso": info,
        "capabilities": caps,
        "started": utcnow(),
        "status": "RUNNING",
        "password": PASSWORD,
        "credentials": {
            "full_name": FULLNAME, "login": USERNAME, "host": HOSTNAME,
        },
        "runner": "tests/ember-qa.py",
    }
    write_json(run / "meta.json", meta)
    _write_status(run, "START", f"{spec.firmware}/{spec.desktop}/{spec.filesystem}")

    all_checks: list[dict] = []
    install_checks: list[dict] = []
    postboot_checks: list[dict] = []
    evidence: list[str] = []
    phases: list[dict] = []
    error: dict[str, Any] | None = None
    result_status = "FAIL"
    vm = VM(name)
    install_done = False
    postboot_done = False

    try:
        if spec.secure_boot and spec.firmware != "uefi":
            raise TestBlocked("Secure Boot requires UEFI firmware")
        if caps.get("desktops") and spec.desktop not in caps["desktops"]:
            raise TestBlocked(
                f"desktop {spec.desktop!r} is not in this ISO's chooser: "
                + ", ".join(caps["desktops"])
            )
        if spec.filesystem not in caps.get("filesystems", ["ext4"]):
            raise TestBlocked(
                f"filesystem {spec.filesystem!r} is not exposed by this ISO "
                f"(available: {', '.join(caps.get('filesystems', []))})"
            )
        if spec.luks and not caps.get("luks", False):
            raise TestBlocked("this ISO has no LUKS support configured")
        if spec.world_update and not caps.get("makeconf", False):
            raise TestBlocked("this ISO has no make.conf / @world option")
        if spec.secure_boot and not caps.get("secureboot_ui", False):
            raise TestBlocked("this ISO has no Secure Boot configuration module")
        if free_bytes(run) < 18 * 1024**3:
            removed = reclaim_qa_disks(keep={name})
            if removed:
                log.warning("reclaimed stale qa disks: %s", ", ".join(removed))
        if free_bytes(run) < 18 * 1024**3:
            raise TestBlocked(
                f"only {free_bytes(run)/1024**3:.1f} GiB free; cannot create a 24 GiB qcow2"
            )
        leftovers = qemu_processes()
        if leftovers and os.environ.get("EMBERQA_ALLOW_CONCURRENT") != "1":
            raise TestBlocked(
                "another QEMU is running; QA is serialized to one VM. "
                + "; ".join(f"pid {q['pid']}" for q in leftovers)
            )

        # ---- phase 1: live installer ---------------------------------
        _write_status(run, "PHASE", "install")
        t0 = time.time()
        vm.start(firmware=spec.firmware, boot="install", iso=boot_iso,
                 secure_boot=spec.secure_boot, phase="install")
        if spec.fault_install:
            # Drop the link briefly after installation starts.  The driver's
            # monitor loop calls this from a timer-like check below.
            pass
        screen = Screen(vm, "install")
        installer = Installer(
            screen, desktop=spec.desktop, filesystem=spec.filesystem,
            luks=spec.luks, lvm=spec.lvm, timeout=spec.timeout,
            fault_during_install=spec.fault_install,
            world_update=spec.world_update, secure_boot=spec.secure_boot,
        )
        try:
            out = installer.run()
            install_checks = out["checks"]
            evidence += out["evidence"]
            all_checks += install_checks
            install_done = True
        except TestBlocked as exc:
            install_checks = [c.__dict__ for c in installer.checks]
            all_checks += install_checks
            error = {"phase": "install", "kind": "BLOCKED", "message": str(exc)}
            result_status = "BLOCKED"
            _capture_failure_screen(vm, run, "blocked-install")
            raise
        except Exception as exc:
            install_checks = [c.__dict__ for c in installer.checks]
            all_checks += install_checks
            error = {
                "phase": "install", "kind": type(exc).__name__,
                "message": str(exc),
                "traceback": traceback.format_exc(),
            }
            result_status = "FAIL"
            _capture_failure_screen(vm, run, "failed-install")
            raise
        finally:
            phases.append({
                "phase": "install", "seconds": round(time.time() - t0, 1),
                "status": "PASS" if install_done else result_status,
                "checks": _phase_summary(install_checks),
            })
            try:
                (run / "serial-install-tail.txt").write_text(
                    _serial_tail(run), encoding="utf-8")
            except OSError:
                pass
            vm.stop(clean_disk=False)

        # ---- phase 2: installed disk boot -----------------------------
        _write_status(run, "PHASE", "disk")
        t1 = time.time()
        vm.start(firmware=spec.firmware, boot="disk", iso=None,
                 secure_boot=spec.secure_boot, phase="disk")
        screen2 = Screen(vm, "disk")
        post = PostBoot(screen2, vm, desktop=spec.desktop,
                        network_fault=spec.network_fault, luks=spec.luks)
        try:
            out = post.run()
            postboot_checks = out["checks"]
            evidence += out["evidence"]
            all_checks += postboot_checks
            postboot_done = True
            result_status = "PASS"
        except TestBlocked as exc:
            postboot_checks = [c.__dict__ for c in post.checks]
            all_checks += postboot_checks
            error = {"phase": "postboot", "kind": "BLOCKED", "message": str(exc)}
            result_status = "BLOCKED"
            _capture_failure_screen(vm, run, "blocked-postboot")
            raise
        except Exception as exc:
            postboot_checks = [c.__dict__ for c in post.checks]
            all_checks += postboot_checks
            error = {
                "phase": "postboot", "kind": type(exc).__name__,
                "message": str(exc),
                "traceback": traceback.format_exc(),
            }
            result_status = "FAIL"
            _capture_failure_screen(vm, run, "failed-postboot")
            raise
        finally:
            phases.append({
                "phase": "disk", "seconds": round(time.time() - t1, 1),
                "status": "PASS" if postboot_done else result_status,
                "checks": _phase_summary(postboot_checks),
            })
            try:
                (run / "serial-disk-tail.txt").write_text(
                    _serial_tail(run), encoding="utf-8")
            except OSError:
                pass
            # Keep disk only if requested; default is deterministic cleanup.
            vm.stop(clean_disk=not spec.keep_disk)

    except TestBlocked as exc:
        if not error:
            error = {"phase": "harness", "kind": "BLOCKED", "message": str(exc)}
        result_status = "BLOCKED"
        log.error("BLOCKED: %s", exc)
    except Exception as exc:
        if not error:
            error = {
                "phase": "harness", "kind": type(exc).__name__,
                "message": str(exc), "traceback": traceback.format_exc(),
            }
        result_status = "FAIL"
        log.error("FAIL: %s", exc)
    finally:
        # Never leave a QEMU behind, even after an unexpected exception.
        try:
            if vm.running:
                vm.stop(clean_disk=not spec.keep_disk)
        except Exception as exc:
            log.error("cleanup stop failed: %s", exc)
        # Record disk usage before it is deleted (helpful for sizing reports).
        disk = run / "disk.qcow2"
        if disk.exists():
            try:
                import subprocess
                info_out = subprocess.run(
                    ["qemu-img", "info", "--output=json", str(disk)],
                    capture_output=True, text=True, timeout=30,
                ).stdout
                (run / "disk-info.json").write_text(info_out, encoding="utf-8")
            except Exception:
                pass
            if not spec.keep_disk:
                disk.unlink(missing_ok=True)
        for p in (run / "OVMF_VARS.fd", run / "OVMF_VARS.secboot.fd"):
            if p.exists() and not spec.keep_disk:
                p.unlink(missing_ok=True)

    finished = utcnow()
    # Derive the final status from the checks, never only from control flow.
    statuses = [c.get("status") for c in all_checks]
    if error:
        result_status = error.get("kind") if error.get("kind") in ("BLOCKED",) else result_status
    elif "FAIL" in statuses:
        result_status = "FAIL"
        if not error:
            first = next(c for c in all_checks if c.get("status") == "FAIL")
            error = {
                "phase": "check", "kind": "CheckFailed",
                "message": f"{first.get('name')}: {first.get('detail')}",
            }
    elif "BLOCKED" in statuses:
        result_status = "BLOCKED"
        if not error:
            first = next(c for c in all_checks if c.get("status") == "BLOCKED")
            error = {
                "phase": "check", "kind": "BLOCKED",
                "message": f"{first.get('name')}: {first.get('detail')}",
            }
    elif install_done and postboot_done:
        result_status = "PASS"
    else:
        result_status = "FAIL"
        if not error:
            error = {"phase": "harness", "kind": "Incomplete",
                     "message": "install or post-boot phase did not complete"}

    summary = {
        "run_name": name,
        "test_id": spec.test_id,
        "status": result_status,
        "started": meta["started"],
        "finished": finished,
        "iso": info,
        "spec": asdict(spec),
        "credentials": meta["credentials"],
        "checks": all_checks,
        "install_checks": install_checks,
        "postboot_checks": postboot_checks,
        "phases": phases,
        "error": error,
        "evidence": sorted(set(evidence)),
        "artifacts": {
            "dir": str(run),
            "screenshots": str(run / "screenshots"),
            "serial_install": str(run / "serial-install.log"),
            "serial_disk": str(run / "serial-disk.log"),
            "qmp_install": str(run / "qmp-install.log"),
            "qmp_disk": str(run / "qmp-disk.log"),
        },
    }
    write_json(run / "result.json", summary)
    _write_status(run, "RESULT", result_status)
    log.info("RESULT %s: %s", name, result_status)
    return summary


def make_spec(args: argparse.Namespace) -> Spec:
    return Spec(
        test_id=args.test_id,
        desktop=args.desktop,
        firmware=args.firmware,
        filesystem=args.filesystem,
        luks=args.luks,
        lvm=args.lvm,
        secure_boot=args.secure_boot,
        network_fault=args.network_fault,
        fault_install=args.fault_install,
        world_update=args.world_update,
        timeout=args.timeout,
        iso=args.iso,
        keep_disk=args.keep_disk,
        name=args.name,
    )
