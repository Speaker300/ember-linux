#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Write the make.conf chosen in the Ember build-configuration page."""
import os
import shutil

import libcalamares


def run():
    root = libcalamares.globalstorage.value("rootMountPoint")
    if not root:
        return ("Ember configuration error", "The target root is not mounted.")

    text = libcalamares.globalstorage.value("emberMakeConf")
    if not text:
        libcalamares.utils.warning("emberMakeConf is empty; leaving stage3 make.conf untouched")
        return None

    make_conf = os.path.join(root, "etc/portage/make.conf")
    os.makedirs(os.path.dirname(make_conf), exist_ok=True)
    if os.path.exists(make_conf):
        shutil.copy2(make_conf, make_conf + ".ember-stage3")
    with open(make_conf, "w", encoding="utf-8") as f:
        f.write(text)
        if not text.endswith("\n"):
            f.write("\n")
    os.chmod(make_conf, 0o644)

    # Keep a copy of the suggestion for troubleshooting.
    suggested = libcalamares.globalstorage.value("emberMakeConfSuggested")
    if suggested:
        with open(make_conf + ".ember-suggested", "w", encoding="utf-8") as f:
            f.write(suggested)

    world = bool(libcalamares.globalstorage.value("emberWorldUpdate"))
    libcalamares.globalstorage.insert("emberWorldUpdate", world)
    libcalamares.utils.debug("Wrote %s (world update=%s)" % (make_conf, world))
    return None
