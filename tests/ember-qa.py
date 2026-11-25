#!/usr/bin/env python3
"""Ember Linux QA command line.

Examples
--------
  tests/ember-qa.py run --test-id bios-openbox --firmware bios --desktop openbox
  tests/ember-qa.py run --test-id uefi-xfce --firmware uefi --desktop xfce
  tests/ember-qa.py start --name manual --firmware bios --boot install
  tests/ember-qa.py shot manual qa/manual.png
  tests/ember-qa.py stop --name manual --clean-disk
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

LIB = Path(__file__).resolve().parent / "lib"
sys.path.insert(0, str(LIB))

from emberqa import (  # noqa: E402
    ISO_DEFAULT, QA, RUNS, VM, load_vm, read_json, setup_logging, utcnow,
)
from screen import Screen  # noqa: E402
from runner import Spec, make_spec, run_test  # noqa: E402


def cmd_run(args: argparse.Namespace) -> int:
    spec = make_spec(args)
    result = run_test(spec)
    print(json.dumps({
        "run_name": result["run_name"],
        "status": result["status"],
        "result": str(Path(result["artifacts"]["dir"]) / "result.json"),
        "error": result.get("error"),
    }, indent=2))
    return 0 if result["status"] == "PASS" else (2 if result["status"] == "BLOCKED" else 1)


def cmd_start(args: argparse.Namespace) -> int:
    setup_logging(args.name)
    vm = VM(args.name)
    state = vm.start(
        firmware=args.firmware, boot=args.boot, iso=Path(args.iso),
        secure_boot=args.secure_boot,
        phase=args.phase,
    )
    print(json.dumps(state, indent=2))
    return 0


def cmd_stop(args: argparse.Namespace) -> int:
    setup_logging(args.name)
    vm = load_vm(args.name)
    vm.stop(clean_disk=args.clean_disk)
    print(json.dumps({"name": args.name, "stopped": True,
                      "clean_disk": args.clean_disk}, indent=2))
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    d = RUNS / args.name
    out = {"name": args.name, "dir": str(d)}
    for f in ("meta.json", "result.json", "vm.json", "status.log"):
        p = d / f
        if p.exists():
            if f.endswith(".json"):
                out[f] = read_json(p)
            else:
                out[f] = p.read_text(errors="replace")[-4000:]
    print(json.dumps(out, indent=2))
    return 0


def _screen(name: str) -> Screen:
    return Screen(load_vm(name), "manual")


def cmd_shot(args: argparse.Namespace) -> int:
    s = _screen(args.name)
    try:
        p = s.shot(args.out)
    finally:
        s.close()
    print(p)
    return 0


def cmd_click(args: argparse.Namespace) -> int:
    s = _screen(args.name)
    try:
        s.click(args.x, args.y, button=args.button)
    finally:
        s.close()
    return 0


def cmd_key(args: argparse.Namespace) -> int:
    s = _screen(args.name)
    try:
        s.key(args.key)
    finally:
        s.close()
    return 0


def cmd_type(args: argparse.Namespace) -> int:
    s = _screen(args.name)
    try:
        s.type_text(" ".join(args.text))
    finally:
        s.close()
    return 0


def cmd_net(args: argparse.Namespace) -> int:
    setup_logging(args.name)
    vm = load_vm(args.name)
    vm.set_link(args.state == "up")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    rows = []
    if RUNS.exists():
        for d in sorted(RUNS.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
            if not d.is_dir():
                continue
            row = {"name": d.name}
            try:
                r = read_json(d / "result.json")
                row.update(status=r.get("status"), test_id=r.get("test_id"),
                           iso=r.get("iso", {}).get("sha256", "")[:12])
            except Exception:
                pass
            if (d / "disk.qcow2").exists():
                row["disk"] = str(d / "disk.qcow2")
            rows.append(row)
    print(json.dumps(rows, indent=2))
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    from report import build_report
    path = build_report(iso=Path(args.iso), run_filter=args.run,
                        title=args.title)
    print(path)
    return 0


def add_run_parser(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("run", help="run a full install -> boot -> login -> ping test")
    p.add_argument("--test-id", required=True, help="matrix row id, e.g. bios-openbox")
    p.add_argument("--desktop", default="openbox",
                   choices=["openbox", "xfce", "kde", "gnome", "cinnamon", "mate",
                            "lxqt", "i3", "sway", "hyprland", "fluxbox", "icewm",
                            "server"])
    p.add_argument("--firmware", default="bios", choices=["bios", "uefi"])
    p.add_argument("--filesystem", default="ext4",
                   choices=["ext4", "btrfs", "xfs", "f2fs"])
    p.add_argument("--iso", default=str(ISO_DEFAULT))
    p.add_argument("--luks", action="store_true")
    p.add_argument("--lvm", action="store_true")
    p.add_argument("--secure-boot", action="store_true")
    p.add_argument("--network-fault", action="store_true",
                   help="post-login link down/up test")
    p.add_argument("--fault-install", action="store_true",
                   help="reserved: inject link loss during install")
    p.add_argument("--world-update", action="store_true",
                   help="check the optional Update @world box")
    p.add_argument("--timeout", type=float, default=3600,
                   help="installer timeout seconds (default 3600)")
    p.add_argument("--keep-disk", action="store_true")
    p.add_argument("--name", help="optional deterministic run directory name")
    p.set_defaults(func=cmd_run)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    add_run_parser(sub)

    p = sub.add_parser("start", help="start a VM without running a test")
    p.add_argument("name")
    p.add_argument("--firmware", default="bios", choices=["bios", "uefi"])
    p.add_argument("--boot", default="install", choices=["install", "disk"])
    p.add_argument("--iso", default=str(ISO_DEFAULT))
    p.add_argument("--secure-boot", action="store_true")
    p.add_argument("--phase")
    p.set_defaults(func=cmd_start)

    p = sub.add_parser("stop", help="stop a VM")
    p.add_argument("name")
    p.add_argument("--clean-disk", action="store_true")
    p.set_defaults(func=cmd_stop)

    p = sub.add_parser("status", help="show run metadata/status")
    p.add_argument("name")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("shot", help="capture a screenshot from a running VM")
    p.add_argument("name")
    p.add_argument("out")
    p.set_defaults(func=cmd_shot)

    p = sub.add_parser("click", help="click in a running VM")
    p.add_argument("name")
    p.add_argument("x", type=int)
    p.add_argument("y", type=int)
    p.add_argument("--button", type=int, default=1)
    p.set_defaults(func=cmd_click)

    p = sub.add_parser("key", help="send one key/combination")
    p.add_argument("name")
    p.add_argument("key")
    p.set_defaults(func=cmd_key)

    p = sub.add_parser("type", help="type text into a running VM")
    p.add_argument("name")
    p.add_argument("text", nargs="+")
    p.set_defaults(func=cmd_type)

    p = sub.add_parser("net", help="QMP link up/down")
    p.add_argument("name")
    p.add_argument("state", choices=["up", "down"])
    p.set_defaults(func=cmd_net)

    p = sub.add_parser("list", help="list QA runs")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("report", help="build qa/REPORT-*.md from results")
    p.add_argument("--iso", default=str(ISO_DEFAULT))
    p.add_argument("--run", action="append", help="restrict to run name(s)")
    p.add_argument("--title")
    p.set_defaults(func=cmd_report)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
