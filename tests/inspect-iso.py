#!/usr/bin/env python3
"""Print the QA-relevant facts about an Ember ISO without booting it.

  tests/inspect-iso.py
  tests/inspect-iso.py images/ember-live-amd64.iso
  tests/inspect-iso.py qa/iso/ember-live-amd64-<sha12>.iso

Reads the Calamares configuration from the ISO's embedded squashfs through a
temporary loop device.  Creates/reuses the immutable qa/iso snapshot.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

LIB = Path(__file__).resolve().parent / "lib"
sys.path.insert(0, str(LIB))

from emberqa import ISO_DEFAULT, iso_capabilities, snapshot_iso  # noqa: E402


def main() -> int:
    iso = Path(sys.argv[1]) if len(sys.argv) > 1 else ISO_DEFAULT
    info = snapshot_iso(iso)
    caps = iso_capabilities(Path(info["snapshot"]))
    print(json.dumps({"iso": info, "capabilities": caps}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
