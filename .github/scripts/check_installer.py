#!/usr/bin/env python3
"""Validate the Ember Linux installer source tree.

This is intentionally dependency-light (PyYAML only) so it runs in GitHub
Actions and on a contributor's machine. It checks the things that have broken
real ISO builds before:

- settings.conf instances and sequence entries agree
- every referenced Calamares config exists and parses as YAML
- the desktop chooser has unique items and valid package lists
- Calamares branding has a real slideshow, not the stock placeholder
- QML image references exist next to the QML file

It does not validate Gentoo package atoms (that needs a synced Portage tree).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - CI installs PyYAML explicitly
    print("PyYAML is required: pip install pyyaml", file=sys.stderr)
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / "configs" / "calamares"
MODULE_DIR = ROOT / "modules"
BRAND_DIR = ROOT / "branding" / "calamares"

# Modules that ship with Calamares itself, or are provided by the Gentoo
# patch series. Every other sequence entry must have an instance.
BUILTIN_MODULES = {
    "bootloader", "contextualprocess", "displaymanager", "dracut",
    "dracutlukscfg", "finished", "fstab", "grubcfg", "hwclock", "keyboard",
    "locale", "localecfg", "luksbootkeyfile", "machineid", "mount",
    "netinstall", "openrcdmcryptcfg", "packagechooser", "packagechooserq",
    "packages", "partition", "preservefiles", "services-openrc",
    "shellprocess", "stagechoose", "summary", "umount", "unpackfs",
    "users", "welcome", "notesqml", "downloadstage3", "gentoopkg",
    "dracut_gentoo",
}

errors: list[str] = []
warnings: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def warn(message: str) -> None:
    warnings.append(message)


def load_yaml(path: Path) -> object:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - report the filename
        fail(f"{path.relative_to(ROOT)}: invalid YAML: {exc}")
        return None


def check_settings() -> dict:
    path = CONFIG_DIR / "settings.conf"
    data = load_yaml(path)
    if not isinstance(data, dict):
        fail("settings.conf: top level must be a mapping")
        return {}

    instances: dict[str, dict] = {}
    for item in data.get("instances", []) or []:
        if not isinstance(item, dict) or "id" not in item or "module" not in item:
            fail(f"settings.conf: bad instance entry: {item!r}")
            continue
        iid = str(item["id"])
        if iid in instances:
            fail(f"settings.conf: duplicate instance id {iid!r}")
        instances[iid] = item
        config = item.get("config")
        if config and not (CONFIG_DIR / str(config)).is_file():
            fail(f"settings.conf: instance {iid!r} references missing config {config!r}")

    sequence = data.get("sequence")
    if not isinstance(sequence, list) or not sequence:
        fail("settings.conf: sequence is missing or empty")
        return data

    for phase in sequence:
        if not isinstance(phase, dict):
            fail(f"settings.conf: bad sequence phase: {phase!r}")
            continue
        for mode in ("show", "exec"):
            entries = phase.get(mode)
            if entries is None:
                continue
            if not isinstance(entries, list):
                fail(f"settings.conf: {mode} must be a list")
                continue
            for entry in entries:
                if not isinstance(entry, str):
                    fail(f"settings.conf: bad {mode} entry: {entry!r}")
                    continue
                module = entry.split("@", 1)[0]
                if "@" in entry:
                    iid = entry.split("@", 1)[1]
                    instance = instances.get(iid)
                    if not instance:
                        fail(f"settings.conf: {mode} references unknown instance {iid!r}")
                    elif module and instance.get("module") != module:
                        fail(
                            f"settings.conf: {entry!r} module mismatch "
                            f"(instance uses {instance.get('module')!r})"
                        )
                elif module in instances:
                    instance = instances[module]
                    config = instance.get("config")
                    if config and not (CONFIG_DIR / str(config)).is_file():
                        fail(f"settings.conf: {module!r} references missing config {config!r}")
                elif module not in BUILTIN_MODULES:
                    fail(f"settings.conf: unknown module {module!r} in {mode}")

    branding = data.get("branding")
    if not branding:
        fail("settings.conf: branding key is missing")
    return data


def check_configs() -> None:
    for path in sorted(CONFIG_DIR.glob("*.conf")):
        data = load_yaml(path)
        if data is None and path.read_text(encoding="utf-8").strip() not in {"", "---"}:
            # load_yaml already reported invalid YAML
            continue
        if path.name == "desktopchoose.conf":
            check_desktop_chooser(data, path)
        if path.name == "stage3guide.conf":
            qml = data.get("qmlFilename") if isinstance(data, dict) else None
            if qml:
                candidates = (BRAND_DIR / f"{qml}.qml", CONFIG_DIR / f"{qml}.qml")
                if not any(candidate.is_file() for candidate in candidates):
                    fail(f"{path.name}: qmlFilename {qml!r} has no {qml}.qml")


def check_desktop_chooser(data: object, path: Path) -> None:
    if not isinstance(data, dict):
        fail(f"{path.name}: top level must be a mapping")
        return
    if data.get("method") not in {"packages", "legacy"}:
        fail(f"{path.name}: method must be 'packages' or 'legacy'")
    items = data.get("items")
    if not isinstance(items, list) or not items:
        fail(f"{path.name}: items must be a non-empty list")
        return
    seen: set[str] = set()
    for item in items:
        if not isinstance(item, dict):
            fail(f"{path.name}: bad item {item!r}")
            continue
        iid = str(item.get("id", ""))
        if not iid:
            fail(f"{path.name}: every item needs a non-empty id")
        if iid in seen:
            fail(f"{path.name}: duplicate item id {iid!r}")
        seen.add(iid)
        for key in ("name", "description"):
            if not item.get(key):
                fail(f"{path.name}: item {iid!r} is missing {key!r}")
        packages = item.get("packages")
        if data.get("method") == "packages" and not isinstance(packages, list):
            fail(f"{path.name}: item {iid!r} needs a packages list")
        screenshot = item.get("screenshot")
        if screenshot and not (BRAND_DIR / str(screenshot)).is_file():
            warn(f"{path.name}: preview {screenshot!r} is missing (empty preview)")
    default = data.get("default")
    if default and str(default) not in seen:
        fail(f"{path.name}: default {default!r} is not an item id")


def check_branding() -> None:
    desc = BRAND_DIR / "branding.desc"
    if not desc.is_file():
        if not BRAND_DIR.is_dir():
            warn("branding/calamares is not present in this checkout; skipping branding checks")
        else:
            fail("branding/calamares/branding.desc is missing")
        return
    data = load_yaml(desc)
    if not isinstance(data, dict):
        return
    strings = data.get("strings") if isinstance(data.get("strings"), dict) else {}
    product_name = data.get("name") or strings.get("productName")
    product_version = data.get("version") or strings.get("version")
    if not product_name:
        fail("branding.desc: product name is missing (name or strings.productName)")
    if not product_version:
        fail("branding.desc: version is missing (version or strings.version)")
    for key in ("slideshow", "slideshowAPI"):
        if key not in data:
            fail(f"branding.desc: required key {key!r} is missing")
    images = data.get("images") if isinstance(data.get("images"), dict) else {}
    for key, asset in images.items():
        if not (BRAND_DIR / str(asset)).is_file():
            fail(f"branding.desc: image {key} points to missing {asset!r}")
    slideshow = data.get("slideshow")
    if slideshow:
        qml = BRAND_DIR / str(slideshow)
        if not qml.is_file():
            fail(f"branding.desc: slideshow {slideshow!r} does not exist")
        else:
            check_qml_assets(qml)
    elif "slideshow" in data:
        fail("branding.desc: slideshow is empty; Calamares fatal at startup")
    if data.get("slideshowAPI") != 2:
        warn("branding.desc: slideshowAPI is not 2")

    check_qml_assets(BRAND_DIR / "SlideArt.qml")


def check_qml_assets(qml: Path) -> None:
    if not qml.is_file():
        return
    text = qml.read_text(encoding="utf-8", errors="replace")
    for match in re.finditer(r'source\s*:\s*"([^"]+)"', text):
        asset = match.group(1)
        if asset.startswith(("qrc:", ":/", "http:", "https:", "data:")):
            continue
        if not (qml.parent / asset).is_file():
            fail(f"{qml.relative_to(ROOT)}: missing image asset {asset!r}")


def check_modules() -> None:
    if not MODULE_DIR.is_dir():
        fail("modules/ directory is missing")
        return
    for module in sorted(p for p in MODULE_DIR.iterdir() if p.is_dir()):
        if not (module / "module.desc").is_file():
            warn(f"modules/{module.name}: module.desc is missing")
        if not any(module.glob("*.py")) and not any(module.glob("*.cpp")):
            warn(f"modules/{module.name}: no Python or C++ implementation found")


def main() -> int:
    if not CONFIG_DIR.is_dir():
        print("configs/calamares is missing", file=sys.stderr)
        return 2
    check_settings()
    check_configs()
    check_branding()
    check_modules()

    for message in warnings:
        print(f"warning: {message}")
    if errors:
        print()
        for message in errors:
            print(f"error: {message}")
        print(f"\n{len(errors)} installer validation error(s).")
        return 1
    print("Installer source validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
