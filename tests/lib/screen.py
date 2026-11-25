#!/usr/bin/env python3
"""VNC screen driver and OCR helpers for the Ember QA harness."""

from __future__ import annotations

import logging
import re
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageOps

from emberqa import VM, utcnow

log = logging.getLogger("emberqa.screen")

try:
    from vncdotool import api
except Exception as exc:  # pragma: no cover
    raise SystemExit("vncdotool is required (python-vncdotool)") from exc


class ScreenError(RuntimeError):
    pass


class WaitTimeout(ScreenError):
    pass


def _clean_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-") or "screen"


def preprocess(path: Path, *, crop: tuple[int, int, int, int] | None = None,
               scale: float = 1.0, invert: str = "auto") -> Image.Image:
    im = Image.open(path).convert("RGB")
    if crop:
        im = im.crop(crop)
    im = ImageOps.grayscale(im)
    if invert == "auto":
        hist = im.histogram()
        total = sum(hist)
        mean = sum(i * n for i, n in enumerate(hist)) / max(total, 1)
        if mean < 100:
            im = ImageOps.invert(im)
    elif invert == "yes":
        im = ImageOps.invert(im)
    if scale and scale != 1.0:
        im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
    return im


def ocr_image(path: Path, *, crop: tuple[int, int, int, int] | None = None,
              psm: int = 6, scale: float = 1.0, invert: str = "auto",
              tmpdir: Path | None = None) -> str:
    """Run tesseract on an image (or crop) and return plain text."""
    im = preprocess(path, crop=crop, scale=scale, invert=invert)
    if tmpdir is None:
        tmpdir = path.parent
    tmpdir.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        prefix="ocr-", suffix=".png", dir=tmpdir, delete=False
    ) as fh:
        tmp = Path(fh.name)
    try:
        im.save(tmp)
        proc = subprocess.run(
            ["tesseract", str(tmp), "stdout", "--psm", str(psm), "-l", "eng"],
            capture_output=True, text=True, timeout=60,
        )
        if proc.returncode != 0:
            raise ScreenError(f"tesseract failed: {proc.stderr.strip()}")
        return proc.stdout
    finally:
        tmp.unlink(missing_ok=True)


def ocr_tsv(path: Path, *, crop: tuple[int, int, int, int] | None = None,
            psm: int = 6, scale: float = 1.0, tmpdir: Path | None = None) -> list[dict]:
    im = preprocess(path, crop=crop, scale=scale)
    if tmpdir is None:
        tmpdir = path.parent
    tmpdir.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        prefix="ocr-", suffix=".png", dir=tmpdir, delete=False
    ) as fh:
        tmp = Path(fh.name)
    try:
        im.save(tmp)
        proc = subprocess.run(
            ["tesseract", str(tmp), "stdout", "--psm", str(psm), "-l", "eng", "tsv"],
            capture_output=True, text=True, timeout=60,
        )
        if proc.returncode != 0:
            raise ScreenError(f"tesseract tsv failed: {proc.stderr.strip()}")
        rows = []
        header = None
        for line in proc.stdout.splitlines():
            cols = line.split("\t")
            if header is None:
                header = cols
                continue
            if len(cols) != len(header):
                continue
            row = dict(zip(header, cols))
            try:
                if int(row.get("conf", "-1")) < 0:
                    continue
                row["left"] = int(row["left"]) / scale
                row["top"] = int(row["top"]) / scale
                row["width"] = int(row["width"]) / scale
                row["height"] = int(row["height"]) / scale
            except (ValueError, KeyError):
                continue
            rows.append(row)
        return rows
    finally:
        tmp.unlink(missing_ok=True)


class Screen:
    """A reconnecting VNC session with screenshot/OCR helpers."""

    def __init__(self, vm: VM, prefix: str = "screen"):
        self.vm = vm
        self.prefix = _clean_name(prefix)
        self.shots = vm.screenshots
        self.shots.mkdir(parents=True, exist_ok=True)
        self.client = None
        self.last_text = ""
        self._n = 0

    # -- connection ------------------------------------------------------
    def connect(self, timeout: float = 30.0) -> "Screen":
        if self.client is not None:
            return self
        last: Exception | None = None
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                self.client = api.connect(self.vm.vnc, timeout=15)
                # Force a full update so the first screenshot is current.
                try:
                    self.client.refreshScreen()
                except Exception:
                    pass
                return self
            except Exception as exc:
                last = exc
                self.client = None
                time.sleep(1)
        raise ScreenError(f"cannot connect to VNC {self.vm.vnc}: {last}")

    def reconnect(self) -> None:
        self.close()
        self.connect()

    def close(self) -> None:
        if self.client is not None:
            try:
                self.client.disconnect()
            except Exception:
                pass
            self.client = None

    def _ensure(self) -> None:
        if self.client is None:
            self.connect()

    # -- primitives ------------------------------------------------------
    def shot(self, name: str | None = None) -> Path:
        self._ensure()
        if name is None:
            self._n += 1
            name = f"{self._n:02d}"
        name = _clean_name(name)
        if not name.endswith(".png"):
            name += ".png"
        path = self.shots / name
        last: Exception | None = None
        for attempt in range(3):
            try:
                self.client.captureScreen(str(path))
                if path.exists() and path.stat().st_size > 100:
                    return path
            except Exception as exc:
                last = exc
                self.reconnect()
                time.sleep(0.5)
        raise ScreenError(f"could not capture screenshot {path}: {last}")

    def click(self, x: int, y: int, *, button: int = 1, settle: float = 0.35) -> None:
        self._ensure()
        for attempt in range(3):
            try:
                self.client.mouseMove(x, y)
                time.sleep(0.05)
                self.client.mousePress(button)
                time.sleep(settle)
                return
            except Exception:
                self.reconnect()

    def move(self, x: int, y: int) -> None:
        self._ensure()
        self.client.mouseMove(x, y)

    def key(self, key: str, *, settle: float = 0.15) -> None:
        self._ensure()
        for attempt in range(3):
            try:
                self.client.keyPress(key)
                time.sleep(settle)
                return
            except Exception:
                self.reconnect()

    def type_text(self, text: str, *, delay: float = 0.055) -> None:
        self._ensure()
        for ch in text:
            if ch == " ":
                k = "spacebar"
            elif ch == "\n":
                k = "return"
            elif ch == "\t":
                k = "tab"
            else:
                k = ch
            self.key(k, settle=0)
            time.sleep(delay)

    def ctrl_a(self) -> None:
        self.key("ctrl-a", settle=0.1)

    # -- OCR -------------------------------------------------------------
    def ocr(self, path: Path, *, crop=None, psm: int = 6, scale: float = 1.0,
            invert: str = "auto", save_text: bool = True) -> str:
        text = ocr_image(path, crop=crop, psm=psm, scale=scale, invert=invert,
                         tmpdir=self.shots)
        if save_text:
            path.with_suffix(".txt").write_text(text, encoding="utf-8")
        self.last_text = text
        return text

    def text_now(self, name: str = "now", *, crop=None, psm: int = 6,
                 scale: float = 1.0) -> str:
        p = self.shot(name)
        return self.ocr(p, crop=crop, psm=psm, scale=scale)

    def wait_text(self, needles: Iterable[str], *, timeout: float = 60,
                  crop=None, psm: int = 6, scale: float = 1.0,
                  label: str = "text", every: float = 1.5) -> str:
        """Wait until any needle appears in OCR text (case-insensitive)."""
        needles = [n.lower() for n in needles]
        deadline = time.time() + timeout
        last = ""
        while time.time() < deadline:
            p = self.shot(f"wait-{label}")
            try:
                text = self.ocr(p, crop=crop, psm=psm, scale=scale, save_text=False)
            except Exception as exc:
                log.debug("ocr during wait failed: %s", exc)
                text = ""
            last = text
            low = text.lower()
            if any(n in low for n in needles):
                log.info("wait %s: matched %r", label,
                         next(n for n in needles if n in low))
                return text
            time.sleep(every)
        self.shot(f"timeout-{label}")
        raise WaitTimeout(
            f"timed out after {timeout:.0f}s waiting for {needles!r} ({label}); "
            f"last OCR: {last[-1200:]!r}"
        )

    def wait_gone(self, needles: Iterable[str], *, timeout: float = 60,
                  crop=None, psm: int = 6, label: str = "gone",
                  every: float = 1.5) -> str:
        needles = [n.lower() for n in needles]
        deadline = time.time() + timeout
        last = ""
        while time.time() < deadline:
            p = self.shot(f"wait-{label}")
            text = self.ocr(p, crop=crop, psm=psm, save_text=False)
            last = text
            low = text.lower()
            if not any(n in low for n in needles):
                return text
            time.sleep(every)
        raise WaitTimeout(f"timed out waiting for {needles!r} to disappear ({label})")

    def find_word(self, word: str, path: Path, *, crop=None) -> tuple[int, int] | None:
        rows = ocr_tsv(path, crop=crop, tmpdir=self.shots)
        target = word.lower()
        for r in rows:
            if r.get("text", "").strip().lower().strip(":.") == target:
                x = int(r["left"] + r["width"] / 2)
                y = int(r["top"] + r["height"] / 2)
                return x, y
        return None

    def click_word(self, word: str, path: Path | None = None, *, crop=None,
                   offset_x: int = 0, offset_y: int = 0,
                   label: str | None = None) -> tuple[int, int]:
        label = label or _clean_name(word)
        p = path if path is not None else self.shot(f"find-{label}")
        pos = self.find_word(word, p, crop=crop)
        if not pos:
            raise ScreenError(f"word {word!r} not found on screen")
        x, y = pos[0] + offset_x, pos[1] + offset_y
        self.click(x, y)
        return x, y

    def save_text(self, name: str, text: str) -> Path:
        p = self.shots / (name + ".txt")
        p.write_text(text, encoding="utf-8")
        return p
