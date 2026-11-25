#!/usr/bin/env python3
"""Ember Linux QA harness: QEMU lifecycle, VNC driving, OCR assertions.

This module owns nothing outside ``qa/``.  It never edits product files, the
chroot, the ISO, or git history.  One QEMU guest may run at a time; callers are
expected to use :func:`start_vm` and :func:`stop_vm` in sequence.

Design notes
------------
* Ports are allocated dynamically from documented ranges:
    VNC display 30..99  -> TCP 5930..5999
    hostfwd   2300..2399 (guest :22)
* State lives in ``qa/runs/<run>/`` as JSON so a test can survive a reboot
  between the installer phase and the installed-system phase.
* Artifacts (screenshots, serial logs, OCR text) are kept.  qcow2 disks are
  deleted after a run unless ``keep_disk`` is set in the run metadata.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

try:
    from PIL import Image, ImageOps
except Exception as exc:  # pragma: no cover - dependency check
    raise SystemExit("Pillow is required (python-pillow)") from exc

REPO = Path(__file__).resolve().parents[2]
QA = REPO / "qa"
RUNS = QA / "runs"
ISO_DEFAULT = REPO / "images" / "ember-live-amd64.iso"
OVMF_DIR = Path("/usr/share/edk2-ovmf/x64")
OVMF_CODE = OVMF_DIR / "OVMF_CODE.4m.fd"
OVMF_CODE_SECBOOT = OVMF_DIR / "OVMF_CODE.secboot.4m.fd"
OVMF_VARS = OVMF_DIR / "OVMF_VARS.4m.fd"

VNC_FIRST = 30
VNC_LAST = 99
HOSTFWD_FIRST = 2300
HOSTFWD_LAST = 2399

ISO_CACHE = QA / "cache" / "iso-sha256.json"
ISO_SNAPSHOTS = QA / "iso"

log = logging.getLogger("emberqa")


# ---------------------------------------------------------------------------
# small utilities
# ---------------------------------------------------------------------------

def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def sanitize(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-")
    if not cleaned:
        raise ValueError("empty run name")
    return cleaned[:80]


def run_dir(name: str) -> Path:
    return RUNS / sanitize(name)


def ensure_run_dir(name: str) -> Path:
    d = run_dir(name)
    for sub in ("screenshots", "logs"):
        (d / sub).mkdir(parents=True, exist_ok=True)
    return d


def setup_logging(run: str | None = None) -> None:
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    if run:
        d = ensure_run_dir(run)
        handlers.append(logging.FileHandler(d / "driver.log", encoding="utf-8"))
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-7s %(message)s",
        handlers=handlers,
        force=True,
    )


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path, cache: bool = True) -> str:
    path = path.resolve()
    st = path.stat()
    key = f"{path}:{st.st_size}:{int(st.st_mtime)}"
    if cache and ISO_CACHE.exists():
        try:
            data = read_json(ISO_CACHE)
            if data.get("key") == key:
                return data["sha256"]
        except Exception:
            pass
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    digest = h.hexdigest()
    if cache:
        ISO_CACHE.parent.mkdir(parents=True, exist_ok=True)
        write_json(ISO_CACHE, {"key": key, "sha256": digest, "path": str(path)})
    return digest


def iso_info(path: Path) -> dict[str, Any]:
    path = path.resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    return {
        "path": str(path),
        "size": path.stat().st_size,
        "mtime": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
        "sha256": sha256_file(path),
    }


def snapshot_iso(path: Path, *, keep_old: bool = False) -> dict[str, Any]:
    """Copy the ISO to an immutable per-SHA snapshot and verify it.

    A rebuild writes ``ember-live-amd64.iso`` in place.  A QEMU guest reading
    that file while xorriso rewrites it sees corrupted blocks (observed:
    SQUASHFS zstd errors and the installer window disappearing mid-install).
    Tests must boot from a snapshot whose hash cannot change underneath them.
    """
    source = iso_info(path)
    ISO_SNAPSHOTS.mkdir(parents=True, exist_ok=True)
    snap = ISO_SNAPSHOTS / f"ember-live-amd64-{source['sha256'][:12]}.iso"
    meta_path = snap.with_suffix(".json")
    if snap.is_file():
        existing = sha256_file(snap)
        if existing == source["sha256"]:
            log.info("using verified ISO snapshot %s", snap)
            meta: dict[str, Any] = {}
            if meta_path.is_file():
                try:
                    meta = read_json(meta_path)
                except Exception:
                    meta = {}
            # Keep the original build-output identity (path/mtime) in reports.
            return {
                **{k: meta.get(k, source.get(k)) for k in ("path", "size", "mtime")},
                "sha256": existing,
                "snapshot": str(snap),
                "snapshot_sha256": existing,
            }
        log.warning("snapshot %s hash mismatch; recreating", snap)
        snap.unlink(missing_ok=True)

    if free_bytes(QA) < source["size"] + 8 * 1024**3:
        # Drop old snapshots other than the one we may be recreating.
        for old in ISO_SNAPSHOTS.glob("ember-live-amd64-*.iso"):
            if old != snap:
                log.warning("removing old ISO snapshot %s to make room", old)
                old.unlink(missing_ok=True)
                old.with_suffix(".json").unlink(missing_ok=True)
    if free_bytes(QA) < source["size"] + 2 * 1024**3:
        raise RuntimeError(
            f"not enough space for an ISO snapshot: need {source['size']/1024**3:.1f} "
            f"GiB, have {free_bytes(QA)/1024**3:.1f} GiB"
        )

    last_err: Exception | None = None
    for attempt in range(1, 4):
        tmp = ISO_SNAPSHOTS / f".copy-{source['sha256'][:12]}-{attempt}.iso"
        log.info("copying ISO to snapshot %s (attempt %s)", snap, attempt)
        try:
            subprocess.run(
                ["cp", "--sparse=always", str(path), str(tmp)],
                check=True, capture_output=True, text=True, timeout=600,
            )
            copied = sha256_file(tmp, cache=False)
            if copied != source["sha256"]:
                raise RuntimeError(
                    f"ISO changed or copy corrupt: source {source['sha256']}, copied {copied}"
                )
            tmp.replace(snap)
            write_json(meta_path, {**source, "snapshot": str(snap)})
            log.info("ISO snapshot verified: %s", snap)
            return {**source, "snapshot": str(snap), "snapshot_sha256": copied}
        except Exception as exc:
            last_err = exc
            tmp.unlink(missing_ok=True)
            time.sleep(1)
    raise RuntimeError(f"could not create a verified ISO snapshot: {last_err}")


def iso_calamares_file(iso_snapshot: Path, relpath: str) -> str:
    """Read a file from the ISO's embedded squashfs without extracting it.

    ``unsquashfs`` cannot read a squashfs inside an ISO directly.  Locate the
    image.squashfs extent with isoinfo, expose just that byte range through a
    loop device, and read the requested file.  No product file is modified.
    """
    iso_snapshot = Path(iso_snapshot).resolve()
    cache = QA / "cache" / f"iso-file-{iso_snapshot.stat().st_size}-{iso_snapshot.stat().st_mtime_ns}.json"
    try:
        data = read_json(cache)
        if data.get("snapshot") == str(iso_snapshot) and relpath in data.get("files", {}):
            return data["files"][relpath]
    except Exception:
        data = {"snapshot": str(iso_snapshot), "files": {}}

    listing = subprocess.run(
        ["isoinfo", "-R", "-l", "-i", str(iso_snapshot)],
        capture_output=True, text=True, timeout=120,
    )
    if listing.returncode != 0:
        raise RuntimeError(f"isoinfo failed: {listing.stderr.strip()}")
    m = re.search(
        r"^\S+\s+\d+\s+\d+\s+(\d+)\s+.*?\[\s*(\d+)\s+\d+\]\s+image\.squashfs\s*$",
        listing.stdout, re.M,
    )
    if not m:
        raise RuntimeError("could not locate image.squashfs in the ISO directory")
    size, extent = int(m.group(1)), int(m.group(2))
    offset = extent * 2048

    loop = subprocess.run(
        ["losetup", "--find", "--show", "--offset", str(offset),
         "--sizelimit", str(size), str(iso_snapshot)],
        capture_output=True, text=True, timeout=60,
    )
    if loop.returncode != 0:
        raise RuntimeError(f"losetup failed: {loop.stderr.strip()}")
    dev = loop.stdout.strip()
    try:
        proc = subprocess.run(
            ["unsquashfs", "-cat", dev, f"etc/calamares/{relpath}"],
            capture_output=True, text=True, timeout=180,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"cannot read etc/calamares/{relpath}: {proc.stderr.strip()}"
            )
        out = proc.stdout
    finally:
        subprocess.run(["losetup", "-d", dev], capture_output=True, text=True,
                       timeout=30)
    data.setdefault("files", {})[relpath] = out
    cache.parent.mkdir(parents=True, exist_ok=True)
    write_json(cache, data)
    return out


def iso_capabilities(iso_snapshot: Path) -> dict[str, Any]:
    """Inspect the ISO's Calamares config (read-only) to know what UI to expect."""
    caps: dict[str, Any] = {
        "filesystems": ["ext4"],
        "lvm": False,
        "luks": True,
        "makeconf": False,
        "desktops": [],
        "secureboot_ui": False,
    }
    try:
        part = iso_calamares_file(iso_snapshot, "modules/partition.conf")
        fs = re.findall(r"^\s*-\s*(ext4|btrfs|xfs|f2fs)\s*$", part, re.M)
        if fs:
            caps["filesystems"] = list(dict.fromkeys(fs))
        caps["lvm"] = bool(re.search(r"^lvm:\s*\n\s+enable:\s*true", part, re.M))
        caps["luks"] = "luksGeneration" in part
    except Exception as exc:
        log.warning("could not inspect partition.conf: %s", exc)
    try:
        settings = iso_calamares_file(iso_snapshot, "settings.conf")
        caps["makeconf"] = "module: makeconf" in settings
        caps["secureboot_ui"] = "secureboot_prepare" in settings
    except Exception as exc:
        log.warning("could not inspect settings.conf: %s", exc)
    try:
        desc = iso_calamares_file(iso_snapshot, "modules/desktopchoose.conf")
        caps["desktops"] = re.findall(r'^\s*-\s*id:\s*"([a-z0-9-]+)"', desc, re.M)
    except Exception as exc:
        log.warning("could not inspect desktopchoose.conf: %s", exc)
    return caps


def free_bytes(path: Path = QA) -> int:
    return shutil.disk_usage(path).free


def pid_alive(pid: int | None) -> bool:
    if not pid:
        return False
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def qemu_processes() -> list[dict[str, Any]]:
    """Return live qemu-system processes (name/pid/cmdline)."""
    found = []
    for proc in Path("/proc").glob("[0-9]*"):
        try:
            cmd = (proc / "cmdline").read_bytes().replace(b"\0", b" ").decode(
                "utf-8", "replace"
            )
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue
        if "qemu-system-x86_64" in cmd or "qemu-system-" in cmd:
            try:
                pid = int(proc.name)
            except ValueError:
                continue
            found.append({"pid": pid, "cmdline": cmd.strip()})
    return found


def ensure_host_idle() -> None:
    """Refuse to start a second VM, including one owned by another agent."""
    qs = qemu_processes()
    if qs:
        if os.environ.get("EMBERQA_ALLOW_CONCURRENT") == "1":
            log.warning(
                "EMBERQA_ALLOW_CONCURRENT=1: starting while %s other QEMU "
                "process(es) are running; this is an operator override, not "
                "the default matrix behavior", len(qs),
            )
            return
        lines = "\n".join(f"  pid {q['pid']}: {q['cmdline'][:180]}" for q in qs)
        raise RuntimeError(
            "another QEMU is already running; this harness allows one VM at a "
            "time:\n" + lines
        )


def port_free(port: int, host: str = "127.0.0.1") -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        return True
    except OSError:
        return False
    finally:
        s.close()


def allocate_ports() -> dict[str, int]:
    for display in range(VNC_FIRST, VNC_LAST + 1):
        if port_free(5900 + display):
            for hostfwd in range(HOSTFWD_FIRST, HOSTFWD_LAST + 1):
                if port_free(hostfwd):
                    return {
                        "vnc_display": display,
                        "vnc_port": 5900 + display,
                        "hostfwd": hostfwd,
                    }
    raise RuntimeError("no free VNC/hostfwd port in the documented ranges")


def reclaim_qa_disks(keep: set[str] | None = None) -> list[str]:
    """Delete qcow2 files from finished QA runs when disk space is tight."""
    keep = keep or set()
    removed = []
    if not RUNS.exists():
        return removed
    for d in sorted(RUNS.iterdir(), key=lambda p: p.stat().st_mtime):
        if not d.is_dir() or d.name in keep:
            continue
        state_path = d / "vm-disk.json"
        if not state_path.exists():
            state_path = d / "vm-install.json"
        disk = d / "disk.qcow2"
        if not disk.exists():
            continue
        running = False
        if state_path.exists():
            try:
                running = pid_alive(read_json(state_path).get("pid"))
            except Exception:
                pass
        if running:
            continue
        try:
            disk.unlink()
            removed.append(str(disk))
        except OSError as exc:
            log.warning("could not remove %s: %s", disk, exc)
    return removed


# ---------------------------------------------------------------------------
# QMP
# ---------------------------------------------------------------------------

class QMP:
    def __init__(self, path: Path, log_path: Path | None = None):
        self.path = Path(path)
        self.log_path = log_path
        self.sock: socket.socket | None = None
        self.fh = None

    def connect(self, timeout: float = 10.0) -> "QMP":
        deadline = time.time() + timeout
        last: Exception | None = None
        while time.time() < deadline:
            try:
                self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                self.sock.settimeout(10)
                self.sock.connect(str(self.path))
                self.fh = self.sock.makefile("rwb", buffering=0)
                self._recv()  # greeting
                self.execute("qmp_capabilities")
                return self
            except Exception as exc:  # retry while QEMU starts
                last = exc
                self.close()
                time.sleep(0.25)
        raise RuntimeError(f"cannot connect to QMP {self.path}: {last}")

    def _recv(self) -> dict[str, Any]:
        assert self.fh is not None
        line = self.fh.readline()
        if not line:
            raise RuntimeError("QMP closed unexpectedly")
        return json.loads(line)

    def execute(self, command: str, arguments: dict[str, Any] | None = None) -> Any:
        assert self.fh is not None
        msg: dict[str, Any] = {"execute": command}
        if arguments:
            msg["arguments"] = arguments
        self.fh.write((json.dumps(msg) + "\n").encode())
        if self.log_path:
            with self.log_path.open("a", encoding="utf-8") as fh:
                fh.write(f"{utcnow()} >>> {json.dumps(msg)}\n")
        reply = self._recv()
        if self.log_path:
            with self.log_path.open("a", encoding="utf-8") as fh:
                fh.write(f"{utcnow()} <<< {json.dumps(reply)}\n")
        if "error" in reply:
            raise RuntimeError(f"QMP {command} failed: {reply['error']}")
        return reply.get("return")

    def close(self) -> None:
        try:
            if self.fh:
                self.fh.close()
        except Exception:
            pass
        try:
            if self.sock:
                self.sock.close()
        except Exception:
            pass
        self.fh = None
        self.sock = None

    def __enter__(self) -> "QMP":
        return self.connect()

    def __exit__(self, *exc: object) -> None:
        self.close()


# ---------------------------------------------------------------------------
# QEMU lifecycle
# ---------------------------------------------------------------------------

class VM:
    def __init__(self, name: str):
        self.name = sanitize(name)
        self.dir = ensure_run_dir(self.name)
        self.state_path = self.dir / "vm.json"
        self.state: dict[str, Any] = {}

    @property
    def running(self) -> bool:
        return pid_alive(self.state.get("pid"))

    @property
    def vnc(self) -> str:
        return f"127.0.0.1::{self.state['vnc_port']}"

    @property
    def screenshots(self) -> Path:
        return self.dir / "screenshots"

    def _qemu_cmd(
        self,
        phase: str,
        firmware: str,
        boot: str,
        iso: Path | None,
        secure_boot: bool,
    ) -> list[str]:
        disk = self.dir / "disk.qcow2"
        vars_path = Path(self.state.get("vars", self.dir / "OVMF_VARS.fd"))
        qmp = self.dir / f"qmp-{phase}.sock"
        serial = self.dir / f"serial-{phase}.log"
        pidfile = self.dir / f"qemu-{phase}.pid"
        netdev = "net0"

        common = [
            "qemu-system-x86_64",
            "-name", f"emberqa-{self.name}",
            "-enable-kvm",
            "-machine", "q35",
            "-cpu", "host",
            "-m", "4096",
            "-smp", "4",
            "-device", "virtio-vga,xres=1280,yres=800",
            "-device", "qemu-xhci",
            "-device", "usb-tablet",
            "-display", "none",
            "-vnc", f"127.0.0.1:{self.state['vnc_display']}",
            "-qmp", f"unix:{qmp},server=on,wait=off",
            "-serial", f"file:{serial}",
            "-monitor", "none",
            "-netdev", f"user,id={netdev},hostfwd=tcp:127.0.0.1:{self.state['hostfwd']}-:22",
            "-device", f"virtio-net-pci,netdev={netdev},id={netdev}",
            "-daemonize",
            "-pidfile", str(pidfile),
        ]

        if firmware == "bios":
            cmd = common + [
                "-drive", f"file={disk},if=virtio,format=qcow2,cache=writeback",
            ]
            if boot == "install":
                cmd += [
                    "-drive", f"file={iso},media=cdrom,readonly=on",
                    "-boot", "once=d,menu=off",
                ]
            else:
                cmd += ["-boot", "c"]
        else:
            code = OVMF_CODE_SECBOOT if secure_boot else OVMF_CODE
            if secure_boot:
                # OVMF Secure Boot requires SMM and a secure pflash.
                for i, item in enumerate(common):
                    if item == "-machine":
                        common[i + 1] = "q35,smm=on"
                        break
                cmd = common + [
                    "-global", "driver=cfi.pflash01,property=secure,value=on",
                    "-drive", f"if=pflash,format=raw,readonly=on,file={code}",
                    "-drive", f"if=pflash,format=raw,file={vars_path}",
                    "-drive", f"file={disk},if=virtio,format=qcow2,cache=writeback",
                ]
            else:
                cmd = common + [
                    "-drive", f"if=pflash,format=raw,readonly=on,file={code}",
                    "-drive", f"if=pflash,format=raw,file={vars_path}",
                    "-drive", f"file={disk},if=virtio,format=qcow2,cache=writeback",
                ]
            if boot == "install":
                cmd += [
                    "-drive", f"file={iso},media=cdrom,readonly=on",
                    "-boot", "once=d,menu=off",
                ]
            else:
                cmd += ["-boot", "c"]
        return cmd

    def start(
        self,
        *,
        firmware: str = "bios",
        boot: str = "install",
        iso: Path | None = None,
        secure_boot: bool = False,
        phase: str | None = None,
    ) -> dict[str, Any]:
        if firmware not in ("bios", "uefi"):
            raise ValueError("firmware must be bios or uefi")
        if boot not in ("install", "disk"):
            raise ValueError("boot must be install or disk")
        if self.running:
            raise RuntimeError(f"VM {self.name} is already running")
        ensure_host_idle()
        phase = phase or boot

        disk = self.dir / "disk.qcow2"
        if boot == "install":
            if disk.exists():
                disk.unlink()
            if free_bytes() < 18 * 1024**3:
                removed = reclaim_qa_disks()
                if removed:
                    log.warning("removed stale qa disks: %s", ", ".join(removed))
            if free_bytes() < 18 * 1024**3:
                raise RuntimeError(
                    f"only {free_bytes() / 1024**3:.1f} GiB free; need 18 GiB "
                    "for a 24 GiB sparse install disk"
                )
            subprocess.run(
                ["qemu-img", "create", "-f", "qcow2", "-o", "lazy_refcounts=on",
                 str(disk), "24G"],
                check=True, capture_output=True, text=True,
            )
        elif not disk.exists():
            raise FileNotFoundError(f"disk for disk boot not found: {disk}")

        vars_path = self.dir / "OVMF_VARS.fd"
        if firmware == "uefi" and secure_boot:
            # A secure-boot run must not reuse normal-boot NVRAM.
            vars_path = self.dir / "OVMF_VARS.secboot.fd"
            if not vars_path.exists():
                shutil.copy2(OVMF_VARS, vars_path)
        elif firmware == "uefi" and not vars_path.exists():
            shutil.copy2(OVMF_VARS, vars_path)

        ports = allocate_ports()
        self.state = {
            "name": self.name,
            "phase": phase,
            "firmware": firmware,
            "boot": boot,
            "secure_boot": secure_boot,
            "iso": str(iso) if iso else None,
            **ports,
            "qmp": str(self.dir / f"qmp-{phase}.sock"),
            "serial": str(self.dir / f"serial-{phase}.log"),
            "qmp_log": str(self.dir / f"qmp-{phase}.log"),
            "disk": str(disk),
            "vars": str(vars_path),
            "pidfile": str(self.dir / f"qemu-{phase}.pid"),
            "started": utcnow(),
        }
        # The command builder reads ports and the NVRAM path from state.
        cmd = self._qemu_cmd(phase, firmware, boot, iso, secure_boot)
        log.info("starting QEMU: %s", " ".join(cmd))
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(
                f"QEMU failed to start (rc={proc.returncode}):\n{proc.stderr}\n{proc.stdout}"
            )
        pid = None
        for _ in range(60):
            try:
                pid = int(Path(self.state["pidfile"]).read_text().strip())
                break
            except (FileNotFoundError, ValueError):
                time.sleep(0.1)
        if not pid:
            raise RuntimeError("QEMU started but pidfile was not written")
        self.state["pid"] = pid
        write_json(self.state_path, self.state)
        with (self.dir / "phases.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(self.state) + "\n")

        # Wait for the VNC listener.
        deadline = time.time() + 20
        while time.time() < deadline:
            if not port_free(self.state["vnc_port"]):
                break
            if not pid_alive(pid):
                raise RuntimeError("QEMU exited before VNC became available")
            time.sleep(0.2)
        else:
            raise RuntimeError("VNC did not start listening")
        log.info(
            "VM %s up: VNC 127.0.0.1:%s (display :%s), hostfwd %s, pid %s",
            self.name, self.state["vnc_port"], self.state["vnc_display"],
            self.state["hostfwd"], pid,
        )
        return self.state

    def qmp(self) -> QMP:
        return QMP(Path(self.state["qmp"]), Path(self.state["qmp_log"]))

    def set_link(self, up: bool) -> None:
        with self.qmp() as q:
            q.execute("set_link", {"name": "net0", "up": up})
        log.info("network link %s", "up" if up else "down")

    def stop(self, *, clean_disk: bool = False) -> None:
        pid = self.state.get("pid")
        if pid_alive(pid):
            try:
                with self.qmp() as q:
                    try:
                        q.execute("quit")
                    except Exception:
                        pass
            except Exception as exc:
                log.warning("QMP quit failed: %s", exc)
            deadline = time.time() + 12
            while time.time() < deadline and pid_alive(pid):
                time.sleep(0.25)
            if pid_alive(pid):
                log.warning("QEMU %s did not quit; sending TERM", pid)
                try:
                    os.kill(pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                deadline = time.time() + 5
                while time.time() < deadline and pid_alive(pid):
                    time.sleep(0.2)
            if pid_alive(pid):
                log.warning("QEMU %s still alive; sending KILL", pid)
                try:
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        for name in ("pidfile", "qmp"):
            try:
                Path(self.state[name]).unlink(missing_ok=True)
            except OSError:
                pass
        # Socket files can be left behind by QEMU.
        for p in self.dir.glob("qmp-*.sock"):
            try:
                p.unlink()
            except OSError:
                pass
        if clean_disk:
            for name in ("disk", "vars"):
                path = self.state.get(name)
                if path:
                    try:
                        Path(path).unlink(missing_ok=True)
                    except OSError as exc:
                        log.warning("could not remove %s: %s", path, exc)
            # Also remove the secure-boot NVRAM copy if it exists.
            for p in (self.dir / "OVMF_VARS.secboot.fd", self.dir / "OVMF_VARS.fd"):
                if p.exists() and clean_disk:
                    try:
                        p.unlink()
                    except OSError:
                        pass
        log.info("VM %s stopped%s", self.name, " (disk removed)" if clean_disk else "")


def load_vm(name: str) -> VM:
    vm = VM(name)
    if not vm.state_path.exists():
        raise FileNotFoundError(f"no VM state at {vm.state_path}")
    vm.state = read_json(vm.state_path)
    return vm
