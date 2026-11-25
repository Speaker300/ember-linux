#!/usr/bin/env python3
"""Run the Ember QA matrix sequentially (one QEMU at a time).

Examples
--------
  # Everything currently defined for this ISO
  tests/run-matrix.py --group all

  # First pass: every desktop chooser entry on BIOS, Openbox on UEFI
  tests/run-matrix.py --tests bios-openbox-ext4,bios-xfce-ext4,bios-kde-ext4,bios-server-ext4,uefi-openbox-ext4

  # Filesystem and crypto rows
  tests/run-matrix.py --group storage

The script verifies the ISO SHA-256 before every row.  If a new ISO appears
while the matrix is running it stops instead of mixing artifacts.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

LIB = Path(__file__).resolve().parent / "lib"
sys.path.insert(0, str(LIB))

from emberqa import ISO_DEFAULT, QA, free_bytes, iso_info, qemu_processes, stamp, utcnow
from report import build_report
from runner import Spec, run_test

CASES: dict[str, dict] = {
    # Every desktop chooser entry, both firmwares.
    **{
        f"{fw}-{desktop}-ext4": dict(firmware=fw, desktop=desktop, filesystem="ext4")
        for fw in ("bios", "uefi")
        for desktop in (
            "openbox", "xfce", "kde", "gnome", "cinnamon", "mate", "lxqt",
            "i3", "sway", "hyprland", "fluxbox", "icewm", "server",
        )
    },
    # Filesystems.
    "bios-openbox-btrfs": dict(firmware="bios", desktop="openbox", filesystem="btrfs"),
    "bios-openbox-xfs": dict(firmware="bios", desktop="openbox", filesystem="xfs"),
    "bios-openbox-f2fs": dict(firmware="bios", desktop="openbox", filesystem="f2fs"),
    "uefi-openbox-btrfs": dict(firmware="uefi", desktop="openbox", filesystem="btrfs"),
    "uefi-openbox-xfs": dict(firmware="uefi", desktop="openbox", filesystem="xfs"),
    "uefi-openbox-f2fs": dict(firmware="uefi", desktop="openbox", filesystem="f2fs"),
    # Encryption / volume management.
    "bios-openbox-luks": dict(firmware="bios", desktop="openbox", filesystem="ext4", luks=True),
    "uefi-openbox-luks": dict(firmware="uefi", desktop="openbox", filesystem="ext4", luks=True),
    "bios-openbox-lvm": dict(firmware="bios", desktop="openbox", filesystem="ext4", lvm=True),
    "uefi-openbox-lvm": dict(firmware="uefi", desktop="openbox", filesystem="ext4", lvm=True),
    # Secure Boot, network failure/resume, optional @world.
    "uefi-openbox-secureboot": dict(firmware="uefi", desktop="openbox", filesystem="ext4", secure_boot=True),
    "bios-openbox-netfault": dict(firmware="bios", desktop="openbox", filesystem="ext4", network_fault=True),
    "uefi-openbox-netfault": dict(firmware="uefi", desktop="openbox", filesystem="ext4", network_fault=True),
    "bios-openbox-worldupdate": dict(firmware="bios", desktop="openbox", filesystem="ext4", world_update=True),
}

GROUPS = {
    "core": [
        "bios-openbox-ext4", "bios-xfce-ext4", "bios-kde-ext4", "bios-server-ext4",
        "uefi-openbox-ext4", "uefi-xfce-ext4", "uefi-kde-ext4", "uefi-server-ext4",
    ],
    "desktops-bios": ["bios-openbox-ext4", "bios-xfce-ext4", "bios-kde-ext4",
                      "bios-server-ext4"],
    "desktops-uefi": ["uefi-openbox-ext4", "uefi-xfce-ext4", "uefi-kde-ext4",
                      "uefi-server-ext4"],
    "storage": ["bios-openbox-btrfs", "bios-openbox-xfs", "bios-openbox-f2fs",
                "uefi-openbox-btrfs", "uefi-openbox-xfs", "uefi-openbox-f2fs"],
    "crypto": ["bios-openbox-luks", "uefi-openbox-luks", "bios-openbox-lvm",
               "uefi-openbox-lvm"],
    "secureboot": ["uefi-openbox-secureboot"],
    "network": ["bios-openbox-netfault", "uefi-openbox-netfault"],
    "all": list(CASES),
}


def wait_for_host(timeout: float) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        qs = qemu_processes()
        if not qs:
            return
        print(f"[{utcnow()}] waiting for another QEMU to finish: "
              + ", ".join(str(q["pid"]) for q in qs), flush=True)
        time.sleep(15)
    raise SystemExit("timed out waiting for the host to be free of QEMU processes")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--iso", default=str(ISO_DEFAULT))
    ap.add_argument("--group", choices=sorted(GROUPS), default="core")
    ap.add_argument("--tests", help="comma-separated case ids (overrides --group)")
    ap.add_argument("--timeout", type=float, default=3600,
                    help="per-install timeout seconds")
    ap.add_argument("--keep-disk", action="store_true")
    ap.add_argument("--wait-host", type=float, default=1800,
                    help="seconds to wait for another agent's QEMU to finish")
    ap.add_argument("--stop-on-fail", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    tests = ([t.strip() for t in args.tests.split(",") if t.strip()]
             if args.tests else GROUPS[args.group])
    unknown = [t for t in tests if t not in CASES]
    if unknown:
        raise SystemExit(f"unknown test ids: {', '.join(unknown)}")

    iso = Path(args.iso).resolve()
    start_info = iso_info(iso)
    print(f"matrix start {utcnow()}")
    print(f"ISO {iso} sha256={start_info['sha256']} size={start_info['size']}")
    print(f"rows: {', '.join(tests)}")
    if args.dry_run:
        for t in tests:
            print(json.dumps({"test_id": t, **CASES[t]}, sort_keys=True))
        return 0

    # One matrix log per invocation.
    logdir = QA / "matrix"
    logdir.mkdir(parents=True, exist_ok=True)
    log_path = logdir / f"matrix-{start_info['sha256'][:8]}-{stamp()}.log"
    results = []
    for idx, test_id in enumerate(tests, 1):
        info = iso_info(iso)
        if info["sha256"] != start_info["sha256"]:
            print("ISO CHANGED during the matrix; stopping to avoid mixed results",
                  flush=True)
            break
        wait_for_host(args.wait_host)
        if free_bytes(QA) < 18 * 1024**3:
            from emberqa import reclaim_qa_disks
            removed = reclaim_qa_disks()
            print(f"reclaimed {len(removed)} stale QA disks; free now "
                  f"{free_bytes(QA)/1024**3:.1f} GiB", flush=True)
        if free_bytes(QA) < 18 * 1024**3:
            print("not enough free space for another qcow2; stopping", flush=True)
            break
        case = CASES[test_id]
        spec = Spec(test_id=test_id, iso=str(iso), timeout=args.timeout,
                    keep_disk=args.keep_disk, **case)
        print(f"\n=== [{idx}/{len(tests)}] {test_id} {case} ===", flush=True)
        line = f"{utcnow()} START {test_id} {json.dumps(case, sort_keys=True)}"
        log_path.open("a", encoding="utf-8").write(line + "\n")
        try:
            result = run_test(spec)
        except Exception as exc:  # runner normally catches; belt and braces
            print(f"runner crashed on {test_id}: {exc}", flush=True)
            result = {"test_id": test_id, "status": "FAIL", "error": {"message": str(exc)}}
        results.append(result)
        line = f"{utcnow()} RESULT {test_id} {result.get('status')} {result.get('run_name','')}"
        print(line, flush=True)
        log_path.open("a", encoding="utf-8").write(line + "\n")
        try:
            report_iso = Path(result.get("iso", {}).get("snapshot", str(iso)))
            rp = build_report(iso=report_iso)
            print(f"report: {rp}", flush=True)
        except Exception as exc:
            print(f"report generation failed: {exc}", flush=True)
        if args.stop_on_fail and result.get("status") != "PASS":
            break

    print("\nmatrix summary")
    for r in results:
        print(f"  {r.get('test_id'):32s} {r.get('status')}")
    print(f"log: {log_path}")
    # Exit non-zero if anything failed; BLOCKED is not a pass either.
    return 0 if results and all(r.get("status") == "PASS" for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
