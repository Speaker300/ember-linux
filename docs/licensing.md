# Licensing audit

> **Release blocker:** the project has no top-level `LICENSE` file, and the
> GitHub repository reports no license. Until that is resolved, others cannot
> legally reuse Ember's original code. This page records the current state; it
> is not legal advice.

## Summary

| Item | Current state | Action needed |
| --- | --- | --- |
| Project source license | Not finalized; no root `LICENSE` | Maintainer decision, then add `LICENSE` and SPDX headers |
| Calamares modules | Mostly `GPL-3.0-or-later` headers | Keep consistent; add headers where missing |
| Branding and themes | `CC-BY-SA-4.0` headers | Confirm a top-level branding license statement |
| Inter font | SIL Open Font License 1.1, file included | Keep `Inter-LICENSE.txt` with the font |
| Gentoo packages / kernel / firmware | Their own licenses | Do not relicense; include notices in the image |
| Calamares itself | Upstream license | Preserve upstream notices and patches |
| shim / Microsoft signing | Upstream terms | Verify redistribution and signing story before claiming Secure Boot |

## What the tree currently says

The repository has SPDX identifiers in many project files, but not all, and
there is no single license text that ties them together.

| License | Used by | Notes |
| --- | --- | --- |
| `GPL-3.0-or-later` | Calamares Python/C++ modules, helper scripts | Dominant code license |
| `CC-BY-SA-4.0` | Branding, wallpapers, Calamares theme, Openbox/tint2/rofi themes | Attribution and share-alike |
| `CC0-1.0` | Some module descriptors / small files | Public-domain dedication |
| `MIT` | Some scripts and QML | Permissive |
| `OFL-1.1` | Inter font | Full text at `branding/desktop/fonts/inter/Inter-LICENSE.txt` |

The mixed headers are workable only if the project states how they combine.
Without that statement, a user cannot tell whether the project is
GPL-3.0-or-later, a collection of separately licensed parts, or something else.

## Recommended decision

This is the maintainer's call, not the docs agent's. A coherent default would
be:

- **Code:** GPL-3.0-or-later, matching the existing module headers and
  Calamares.
- **Branding and documentation:** CC-BY-SA-4.0 for the visual identity,
  wallpapers, and themes; a documentation license such as CC-BY-SA-4.0 for the
  prose.
- **Third-party components:** retain their upstream licenses; do not relicense.

If that is chosen:

1. Add a root `LICENSE` with the GPL-3.0-or-later text and a short statement
   that identifies the branding exception.
2. Add `LICENSE` or `NOTICE` files under `branding/` and `docs/` if they use a
   different license.
3. Add SPDX headers to every project source file that lacks one.
4. Update `README.md`, the GitHub repository license field, and the website
   footer.
5. Do not claim a license for third-party packages or the Gentoo stage3.

If a different license is chosen, the existing GPL-3.0-or-later headers must be
reconciled first. Do not silently relicense files whose authors have not
agreed.

## Bundled third-party components

The ISO includes, among other things:

- Gentoo stage3 and packages installed from Gentoo mirrors;
- the Linux kernel (`gentoo-kernel-bin` in the verified build);
- Calamares and its Qt/KF dependencies;
- Openbox, tint2, picom, rofi, xterm, LightDM, NetworkManager, OpenRC;
- `linux-firmware`, microcode, and hardware drivers;
- the Inter typeface;
- Microsoft-signed shim (in the Secure Boot path).

Each remains under its own license. The Ember license cannot override them.
Before publishing an ISO, include a machine-readable package manifest or a
`/usr/share/licenses` inventory, and preserve the notices the packages ship.

### Fonts

`branding/desktop/fonts/inter/Inter-LICENSE.txt` is the OFL text. Keep it next
to the font files and in the landing page assets. Do not subset or rename the
font in a way that violates the OFL.

### Firmware and microcode

`linux-firmware` and `intel-microcode` have their own redistribution terms.
They are installed as Gentoo packages. Do not extract and republish firmware
separately without checking those terms.

### Secure Boot / shim

`sys-boot/shim` is Microsoft-signed and distributed under its own license.
Ember's per-install machine key is generated locally. The project has not
verified redistribution, MOK behavior, or a public signing story. Until it
does, Secure Boot remains experimental and the license/notice requirements for
shim must be reviewed before a release ISO includes it.

## Release checklist

- [ ] Top-level `LICENSE` added and linked from `README.md`.
- [ ] GitHub repository license field set.
- [ ] SPDX header present on every project source file.
- [ ] Branding license statement added and consistent with the file headers.
- [ ] `Inter-LICENSE.txt` shipped with the font.
- [ ] Third-party notices / package manifest included in the ISO.
- [ ] No third-party asset added without source and license recorded.
- [ ] Secure Boot shim redistribution reviewed.
- [ ] Website footer states the project license accurately.
- [ ] `docs/licensing.md` updated from "not finalized" to the chosen license.

## What contributors should do now

- Do not copy code or assets from another project unless the license is
  compatible and you record the source.
- Keep existing SPDX headers; add one to new files using the license of the
  surrounding code.
- State the license of any third-party asset in the pull request.
- If you are the copyright holder of a file with no header, say so; that helps
  the maintainer make a clean decision.
- Ask before assuming the project is GPL-3.0-or-later as a whole. The module
  headers point that way, but the repository as a whole has not made the
  statement.

## References

- GPL-3.0-or-later: <https://www.gnu.org/licenses/gpl-3.0.html>
- CC-BY-SA-4.0: <https://creativecommons.org/licenses/by-sa/4.0/>
- OFL-1.1: <https://openfontlicense.org/>
- REUSE / SPDX: <https://reuse.software/>
- Calamares licensing: <https://github.com/calamares/calamares>
- Gentoo license policy: <https://www.gentoo.org/>
