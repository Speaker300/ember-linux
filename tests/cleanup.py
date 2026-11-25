#!/usr/bin/env python3
"""Deterministic cleanup of QA-only large files.

Only paths under qa/ are considered.  Never touches images/, vm/, the chroot,
product configs, or git.

  tests/cleanup.py --disks          # delete qa/runs/*/disk.qcow2 + NVRAM
  tests/cleanup.py --snapshots      # delete ISO snapshots except the current
  tests/cleanup.py --runs 7         # delete run dirs older than 7 days
  tests/cleanup.py --all
  tests/cleanup.py --dry-run --all
"""

from __future__ import annotations

import argparse
import shutil
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "qa"
RUNS = QA / "runs"
ISO_DIR = QA / "iso"
CURRENT_ISO = ROOT / "images" / "ember-live-amd64.iso"


def size(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return 0


def remove(path: Path, dry: bool) -> int:
    n = size(path)
    if path.is_dir():
        n = sum(p.stat().st_size for p in path.rglob("*") if p.is_file())
    if dry:
        print(f"would remove {path} ({n/1024**2:.1f} MiB)")
        return n
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink(missing_ok=True)
    print(f"removed {path} ({n/1024**2:.1f} MiB)")
    return n


def current_sha_prefix() -> str | None:
    # Deliberately do not hash a 4 GiB ISO here; compare size+mtime with the
    # snapshot JSON?  The snapshot JSON records the source hash, so identify
    # the snapshot newest by mtime and keep it plus any snapshot whose JSON
    # source path matches.
    if not CURRENT_ISO.exists():
        return None
    try:
        import json
        for meta in sorted(ISO_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime,
                           reverse=True):
            data = json.loads(meta.read_text())
            if data.get("path") == str(CURRENT_ISO):
                return meta.stem.split("-")[-1]
    except Exception:
        pass
    return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disks", action="store_true")
    ap.add_argument("--snapshots", action="store_true")
    ap.add_argument("--runs", type=float, default=None,
                    help="delete run dirs older than DAYS")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    if not any((args.disks, args.snapshots, args.runs is not None, args.all)):
        ap.print_help()
        return 1
    if args.all:
        args.disks = args.snapshots = True
        if args.runs is None:
            args.runs = 7

    total = 0
    if args.disks:
        for run in sorted(RUNS.iterdir()) if RUNS.exists() else []:
            if not run.is_dir():
                continue
            for name in ("disk.qcow2", "OVMF_VARS.fd", "OVMF_VARS.secboot.fd",
                         "qemu-install.pid", "qemu-disk.pid"):
                p = run / name
                if p.exists():
                    total += remove(p, args.dry_run)
            for p in run.glob("qmp-*.sock"):
                total += remove(p, args.dry_run)
    if args.snapshots:
        keep = current_sha_prefix()
        for p in sorted(ISO_DIR.glob("ember-live-amd64-*.iso")):
            if keep and keep in p.name:
                print(f"keeping current snapshot {p}")
                continue
            total += remove(p, args.dry_run)
            p.with_suffix(".json").unlink(missing_ok=True)
    if args.runs is not None:
        cutoff = time.time() - args.runs * 86400
        for run in sorted(RUNS.iterdir()) if RUNS.exists() else []:
            if not run.is_dir():
                continue
            if run.stat().st_mtime < cutoff:
                total += remove(run, args.dry_run)
    print(f"total {'would free' if args.dry_run else 'freed'}: {total/1024**2:.1f} MiB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
