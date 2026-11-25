# Contributing to Ember Linux

Thanks for taking the time to help. Ember is a small project and independent
testing is the most valuable contribution you can make. This guide explains
what is useful, how to build and test, and the evidence rules that keep the
project honest.

By participating you agree to follow the
[Code of Conduct](CODE_OF_CONDUCT.md).

## Ways to contribute

| Contribution | Where to start |
| --- | --- |
| Install report on real hardware | [Install testing](../docs/testing.md), then open an **Install report** issue |
| Test an offered desktop (Xfce, KDE, GNOME, Cinnamon, MATE, LXQt, i3, Sway, Fluxbox, IceWM, Server) | [Desktop QA](../docs/desktops.md), then open an **Install report** |
| Reproduce a bug | [Troubleshooting](../docs/troubleshooting.md) and the bug template |
| Fix the installer or modules | `configs/calamares/`, `modules/` |
| Improve documentation | `docs/`, `README.md` |
| Branding and theme work | `branding/` |
| Translation | Not set up yet — open an issue first |

You do not need to be a Gentoo developer. A careful report with an exact ISO
checksum, firmware mode, and screenshots is more useful than a vague "it
didn't work".

## Before you start

- Search existing issues and pull requests.
- For a large change, open an issue first so we can agree on the approach.
- Do not include secrets, private keys, passwords, or personal data in issues,
  logs, or screenshots.
- Do not commit built ISOs, VM disks, screenshots, or logs. They are ignored on
  purpose; attach them to an issue or release instead.

## Project layout

| Path | What lives there |
| --- | --- |
| `configs/calamares/` | Installer configuration; source of truth for modules |
| `modules/` | Calamares C++ and Python modules |
| `branding/` | Identity, wallpapers, Calamares theme, desktop theme |
| `scripts/` | Build, chroot, VM, and VNC helpers |
| `docs/` | User docs and the GitHub Pages site |
| `vm/` | QA reports and VM helpers; disks and screenshots are ignored |

Build roots, extracted ISOs, and the package cache live outside Git.

## Development setup

Ember targets **Gentoo Linux amd64**. The installer itself is Calamares 3.4.x
with Gentoo patches; the custom modules are Python 3 and C++/Qt.

Useful host packages:

```sh
emerge --ask app-admin/calamares dev-qt/qtbase sys-fs/squashfs-tools \
  sys-boot/grub sys-firmware/edk2-ovmf app-emulation/qemu \
  net-misc/xorriso dev-vcs/git
```

The exact set depends on your host. The current ISO build is a maintainer
build that repacks a prepared LiveGUI rootfs — see
[docs/building.md](../docs/building.md). A clean-clone reproducible build is on
the [roadmap](../docs/roadmap.md).

### Editing installer configuration

`configs/calamares/` is the source of truth. Do not edit files inside
`build/livegui-root/etc/calamares/` directly; sync them:

```sh
./scripts/sync-installer.sh
./scripts/rebuild-iso2.sh
```

The rebuild script backs up the previous ISO. Never flash a USB device during
development unless the maintainer explicitly asks for it; test the ISO in QEMU.

### Running the VM tests

```sh
# BIOS, VNC on localhost::5908
./scripts/vm-bios-v2.sh

# UEFI (OVMF), VNC on localhost::5909
./scripts/vm-uefi-v2.sh
```

Inspect with `vncdo -s localhost::5908` or any VNC client. Take screenshots
into `vm/shots/` (ignored). The full QA procedure is in
[docs/testing.md](../docs/testing.md).

## Evidence rules

These are not optional. They are the reason the README can be trusted.

1. **Test the exact artifact.** Record the ISO path, size, SHA-256, and build
   time. Do not test ISO A and report on ISO B.
2. **Separate tested, offered, and experimental.** A desktop is "tested" only
   after a full install, a disk-only boot, a login, and a network check on both
   firmware modes claimed.
3. **VM results are not hardware results.** Say QEMU, and say which machine
   model and firmware.
4. **Do not weaken or skip a test to make it pass.** Fix the product or record
   the limitation.
5. **Attach evidence.** Screenshots and relevant log excerpts, with secrets
   removed. Link the QA report if you add one to `vm/`.
6. **No invented results.** If a check was not run, write "not run". If a
   behavior is unverified, call it unverified.

A change that adds or alters a support claim must update the relevant matrix
and link evidence.

## Making changes

- Keep changes focused. One logical change per pull request.
- Match the surrounding style. Configuration files are YAML; Python modules
  use the existing Calamares patterns; C++ follows the Qt style already present.
- Preserve SPDX headers and add one to new source files. The project's own
  license is not final yet; use the license already used by the file you are
  editing and note it in the pull request.
- Update documentation when behavior, requirements, or status changes.
- Add a QA note for anything that affects installation, boot, partitioning, or
  the desktop session.

### Commit messages

Use a short imperative subject, then explain the why:

```text
partition: create an 8 MiB BIOS boot partition on GPT

BIOS installs previously relied on blocklist embedding. A dedicated
bios_grub partition avoids fragile boot code placement.
```

## Pull requests

The pull request template asks for:

- what changed and why;
- how it was tested (firmware, desktop, filesystem, ISO checksum);
- which claims or docs were updated;
- known limitations.

A pull request that changes installer behavior without a test plan will be
asked for one. Documentation-only changes still need accurate claims.

Before opening a pull request:

```sh
# If you changed docs: check relative links.
python3 .github/scripts/check_links.py

# If you changed the ISO: record the new checksum.
sha256sum images/ember-live-amd64.iso
```

The GitHub Actions docs check runs on pull requests that touch documentation or
the `.github/` files.

## Reporting bugs and install failures

Use the issue templates:

- **Bug report** — something in the live session or installed system is wrong.
- **Install report** — a successful or failed install, especially on hardware.
- **Feature request** — a capability you want, with the problem it solves.

Include:

- Ember ISO checksum and build date;
- firmware mode (BIOS/UEFI), Secure Boot state, machine model or VM details;
- CPU, GPU, storage controller, network hardware;
- desktop and filesystem selected;
- the exact step where it failed;
- Calamares log excerpt: `/root/.cache/calamares/session.log` in the live
  session, or the terminal output on tty1;
- post-install report if the system booted:
  `/var/log/ember-install-report.txt`.

Redact passwords, usernames, MAC addresses, serial numbers, and keys.

## Security issues

Do not open a public issue for a vulnerability. See
[SECURITY.md](SECURITY.md) for the private reporting process and scope.

## Licensing

There is no top-level project license yet. By contributing, you agree that your
contribution may be distributed under the license the project adopts, and you
confirm you have the right to submit it. If your contribution includes
third-party code or assets, state their license and source in the pull request.
See [docs/licensing.md](../docs/licensing.md).

## Questions

Open a discussion or an issue with the **question** label. If the answer is
generally useful, we will fold it into the FAQ.
