# FAQ

## What is Ember Linux?

A Gentoo-based live ISO with a graphical installer. It boots a live
environment, asks which stage3 and desktop you want, partitions a disk, and
installs a normal Gentoo system. The project's focus is the installer and the
first-boot experience, not a new package manager or a fork of Gentoo.

## Is Ember a Gentoo fork?

No. The installed system is Gentoo. You use Portage, the Gentoo ebuild
repository, and a standard `make.conf`; the tested path also uses OpenRC.
Ember adds installer configuration, a branding pack, custom Calamares modules,
and a desktop setup. The project is independent and is not affiliated with or
endorsed by the Gentoo Foundation.

## Why not just install Gentoo the normal way?

The normal way is excellent if you want to learn the handbook and control every
step. Ember is for the case where you want a working Gentoo system without
hand-writing fstab, choosing a profile, and assembling a desktop from scratch.
If you want the handbook experience, use the handbook; Ember is not a
replacement for understanding your system.

## What is actually tested?

As of 25 November 2026, the full QA pass covers Openbox on the reference ISO:
BIOS and UEFI, hybrid GPT, ext4, no swap, disk-only boot to LightDM, Openbox
login, tint2/picom, NetworkManager ping, and OpenRC default services. See
[Testing](testing.md) and the
[final QA report](../vm/TEST-REPORT-final.md).

The current source tree adds 12 more desktop choices (Xfce, KDE Plasma, GNOME,
Cinnamon, MATE, LXQt, i3, Sway, Hyprland, Fluxbox, IceWM, Server), a make.conf
editor, branding, a Live CD stage option, and Secure Boot plumbing. **None of
those additions has completed end-to-end QA on the rebuilt ISO.** btrfs/XFS/
f2fs, LUKS2, LVM, Wi-Fi, Bluetooth, NVIDIA, NVMe, USB boot, and real hardware
are also outside the tested set.

## Is it systemd or OpenRC?

The tested path is **OpenRC**. The installer also offers a systemd stage3,
which GNOME requires; that path is not verified. There is no tested systemd
install yet, and other desktops are configured for OpenRC.

## Is it rolling?

The installed system is Gentoo, so it is rolling in the usual Gentoo sense: you
sync and update with Portage. The ISO itself is a snapshot of the installer and
live environment; it downloads a current stage3 at install time rather than
freezing packages at build date.

## Does it need internet?

For the normal path, yes: it downloads a stage3 and packages. Newer builds
expose a **Live CD (offline)** stage option that copies the live rootfs, but it
is untested and not part of the verified path. If the network is down, the
online path cannot proceed.

## Does it support Secure Boot?

Not yet. The source contains a shim/MOK/signed-kernel implementation, but the
chain has not passed end-to-end QA. Disable Secure Boot before booting the ISO,
and do not enable the installer's Secure Boot option on a machine you need to
boot. See [Secure Boot](secure-boot.md).

## Can I dual boot with Windows?

Manual partitioning is offered, but dual boot is untested. The installer's
tested path erases the whole disk. If you try manual partitioning, back up
first, keep the Windows ESP intact, and expect to repair the boot order. Do not
assume Ember will detect or preserve another OS.

## Does it work with NVIDIA?

The installer includes `xf86-video-nouveau`. The proprietary NVIDIA driver is
not part of the install, and nouveau is untested on real GPUs. Recent NVIDIA
cards may need additional firmware or the proprietary driver, which you would
install after boot.

## 32-bit, ARM, or RISC-V?

No. Ember targets amd64 (x86-64) only in this preview. There is no i686, ARM, or
RISC-V image.

## How big is the install?

The ISO is 3.97 GiB. The installer enforces a 6 GB minimum, but 20 GB+ is
sensible for a desktop and KDE Plasma needs more. The verified QA disk was
24 GiB. Actual installed size depends on the desktop and package set.

## Will it erase my disk?

If you choose **Erase disk**, yes — every partition on the selected device is
deleted. That is the tested path. Manual partitioning exists but is untested.
Back up your data before installing.

## How do I update the installed system?

Use Gentoo tooling:

```sh
sudo emerge --sync
sudo emerge --ask --update --deep --newuse @world
```

The verified build enables `FEATURES=getbinpkg` and a Gentoo binary package
host, so many updates can be fetched as binaries. Changing `USE` flags can
trigger source builds.

## Does Ember collect telemetry?

No. There is no telemetry or analytics code in the project. The installer uses
the network to fetch the stage3, packages, and a connectivity check; that is
ordinary installer traffic, not telemetry.

## What license is Ember under?

The project's own license is not finalized. That is a release blocker. Bundled
components retain their licenses: GPL-3.0-or-later for the Calamares modules,
CC-BY-SA-4.0 for the branding, OFL for the Inter font, and the licenses of the
Gentoo packages. See [Licensing](licensing.md).

## Is it ready for production?

No. This is a developer preview. Only one desktop path has passed QA, Secure
Boot is unverified, real hardware is untested, and the project license is not
final. Use it on a spare machine or VM.

## How can I help?

Test on hardware, test an offered desktop, report a failed install with logs,
improve the docs, or review the code. Start with
[Contributing](../.github/CONTRIBUTING.md). A careful failure report is as
valuable as a fix.

## Why "Ember"?

The name and visual identity are the project's brand: a warm mark on a cool,
near-black base. The palette and assets live in
[`branding/identity/`](../branding/identity/palette.md). It has no deeper
technical meaning.
