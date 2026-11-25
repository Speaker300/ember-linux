# Roadmap

No dates. Work is ordered by what blocks a trustworthy release, not by what is
fun to build. The live engineering plan is [`NEXT-PHASE.md`](../NEXT-PHASE.md);
this page is the public view.

## Done and evidenced

| Item | Evidence |
| --- | --- |
| Hybrid BIOS/UEFI GPT layout: 512 MiB ESP + 8 MiB BIOS boot + ext4 root | [Final QA](../vm/TEST-REPORT-final.md) |
| Openbox install on BIOS and UEFI | [Final QA](../vm/TEST-REPORT-final.md) |
| Disk-only boot, LightDM, Openbox, tint2, picom | [Final QA](../vm/TEST-REPORT-final.md) |
| NetworkManager, ping, OpenRC default services | [Final QA](../vm/TEST-REPORT-final.md) |
| Stage3 guide, desktop chooser, package transaction | [v2 QA](../vm/TEST-REPORT-v2.md) |
| Post-install verification report | `configs/calamares/postinstall.conf` |
| Ember identity, wallpapers, Calamares theme, Openbox/tint2 theme | `branding/` |
| Public documentation, issue/PR templates, Code of Conduct | `docs/`, `.github/` |

"Done" means the code exists and the behavior is verified in the linked report.
Branding assets exist but are not yet in a verified ISO; the next build carries
them.

## Now: release blockers

### 1. Desktop QA: every offered choice except Openbox

The source tree now offers 13 choices: Openbox, Xfce, KDE Plasma, GNOME,
Cinnamon, MATE, LXQt, i3, Sway, Hyprland, Fluxbox, IceWM, and Server. Only
Openbox has completed a full install and disk-boot cycle, and that was on the
reference ISO. The rebuilt ISO must re-run Openbox as a regression gate first.

**Priority order:** Openbox regression, then Xfce, KDE Plasma, Server, GNOME on
a systemd stage3, i3, Sway, Cinnamon/MATE/LXQt, Fluxbox/IceWM, and finally
Hyprland.

**Exit criteria for each:** install on BIOS and UEFI, boot without the ISO,
verify the correct LightDM/SDDM/GDM/greetd session or console, log in, run a
terminal, check `rc-status default` (or `systemctl --failed`), check networking,
attach screenshots and logs, and update the matrix. Fix package lists, session
detection, and display-manager enablement before calling it tested.

**Known risks:** GNOME is refused on OpenRC by design; Sway and Hyprland use
greetd and Wayland; Hyprland depends on the external hyproverlay overlay;
Cinnamon and MATE add GNOME-adjacent dependencies on OpenRC.

### 2. Secure Boot

The shim/MOK/signed-kernel code exists but has not passed an end-to-end test.

**Exit criteria:** the full chain on `OVMF_CODE.secboot.4m.fd` with Microsoft
certs, MOK enrollment including cancel/wrong-password paths, automatic re-sign
after a kernel update, recovery from the live ISO, and one physical UEFI
machine. See [Secure Boot](secure-boot.md).

**Known risk:** the build-configuration page currently defaults the Secure Boot
checkbox to on for UEFI. Until the chain is verified, this should default off or
be clearly marked experimental.

### 3. Build configuration and Suggest

The editable make.conf page and hardware probing are in the tree but are not in
the verified ISO and not part of a completed install.

**Exit criteria:** the page probes CPU, RAM, GPU, firmware, init, and desktop;
generates validated `CFLAGS`/`CXXFLAGS`, `MAKEOPTS`, `USE`, `VIDEO_CARDS`,
`INPUT_DEVICES`, `ACCEPT_LICENSE`, `GENTOO_MIRRORS`, `FEATURES`,
`BINPKG_COMPRESS`, `EMERGE_DEFAULT_OPTS`, `GRUB_PLATFORMS`, `CPU_FLAGS_X86`,
and `LINGUAS`; shows a diff and a reset; writes a `make.conf` that survives an
`@world` update; tested on BIOS and UEFI with at least Openbox.

### 4. Filesystem QA

ext4 is tested. btrfs, XFS, f2fs, LUKS2, LVM, and swap variants are selectable
but not verified.

**Exit criteria:** install and disk boot for each supported combination, with
the exact initramfs/GRUB configuration recorded. If a combination cannot be
supported, remove it from the installer rather than shipping an untested
option. Ext4 remains the default until then.

### 5. Optional `@world`

An opt-in `emerge --update --deep --newuse @world` in the target is described
in the configuration but not verified.

**Exit criteria:** off by default; clear time/space warning; runs after the base
install; failure is reported without claiming a successful install; tested with
Openbox and at least one large desktop.

### 6. Smaller ISO

The verified ISO is 3.97 GiB. The live rootfs still carries more than the live
session needs.

**Exit criteria:** remove live KDE/Plasma applications that the installer does
not need, prune unneeded firmware/locales/docs, keep Calamares Qt/KF
dependencies and the Openbox live session, and land well under 4 GiB without
breaking BIOS/UEFI boot, the installer, or the live session. Re-run the full QA
matrix after any squashfs change.

### 7. Offline Live CD and branding integration

The tree adds a Live CD (offline) stage option and an exec job that installs
wallpapers, fonts, icons, Openbox/tint2/rofi configs, the greeter theme, and
`/etc/os-release`.

**Exit criteria:** the Live CD install completes and boots without network (or
is removed if it cannot be supported); the branding job runs on a clean install
without breaking session startup; the installed system shows the Ember identity;
and the result is tested on BIOS and UEFI with at least Openbox.

### 8. Cosmetic fixes

- Desktop chooser preview images (or hide the empty frame).
- Replace stock slideshow placeholder text.
- Summary recap of Stage 3 and desktop choices.
- `xsetroot` color visible under picom.
- Prune Openbox menu entries for applications that are not installed.

These are not release blockers, but the first two make the installer look
unfinished.

## Next: release readiness

| Item | Why it matters |
| --- | --- |
| Top-level project license | Without it, others cannot legally reuse the code |
| Real-hardware QA on at least one UEFI and one BIOS machine | VM coverage is not hardware coverage |
| Reproducible build from a clean clone | The current build depends on a prepared rootfs |
| Published ISO with SHA-256 and release notes | Users need a verifiable artifact |
| Pages workflow enabled on the repository | Documentation and download entry point |
| Signed release checksums / provenance | Supply-chain trust |
| Hardware and desktop matrices updated from QA | Keeps claims honest |

## Later

- Wi-Fi, Bluetooth, audio, suspend, and hybrid-GPU QA on real laptops.
- NVMe, SATA, USB boot, and dual-boot validation.
- Installer translation and locale coverage.
- Accessibility review of the installer and Openbox session.
- Package cache for repeat installs, if it can be done without weakening the
  online-first design.
- Public reproducible-build tooling and CI that builds the ISO, not just docs.

## How priorities are decided

1. A claim that is not true is worse than a feature that is missing.
2. Anything that can destroy data or prevent boot comes before cosmetics.
3. A desktop or filesystem is not "supported" until its QA matrix is complete.
4. Documentation follows evidence, not the other way around.

If you want to take one of the "Now" items, open an issue first. The QA exit
criteria are the acceptance test.
