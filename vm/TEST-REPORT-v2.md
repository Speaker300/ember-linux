# Ember ISO v2 test report — new Stage 3 guide, Desktop chooser, packages step

Artifact: `/home/user/ember/images/ember-live-amd64.iso` (4.0G, Fancy GNU/Linux 2023.3 LTS "Venomous Vole" installer, Calamares)
Date: 2026-11-25
VMs: BIOS (VNC :8 / 5908, disk-v2-bios.qcow2), UEFI (VNC :9 / 5909, disk-v2-uefi.qcow2)

## Result summary

| # | Step | Result |
|---|------|--------|
| 1 | BIOS Select Stage: amd64 + current-stage3-amd64-desktop-openrc | PASS |
| 2 | BIOS Desktop chooser renders 4 options | PASS (cosmetic gap: no preview images) |
| 3 | BIOS Partitions: erase disk, no swap, ext4, MBR /dev/vda | PASS |
| 4 | BIOS Users fields | PASS |
| 5 | BIOS Summary -> Install -> new `packages` step | PASS (no failure) |
| 6 | BIOS disk-only boot: GRUB/LightDM/Openbox login, ping, rc-status | PASS |
| 7 | UEFI Stage 3 guide + Desktop page; full install + disk boot | PASS |

No "Installation Failed" dialog occurred on either firmware. No installer error text was produced.

## Step detail

1. **Select Stage (BIOS)** — PASS
   - Arch `64-bit Intel/AMD (amd64)` selected; variant list fetched and `current-stage3-amd64-desktop-openrc` selected.
   - Selected tarball: `stage3-amd64-desktop-openrc-20261122T164601Z.tar.xz`.
   - Shots: `shots/v2-stagechoose-arch.png`, `shots/v2-arch-selected.png`, `shots/v2-variant-combo.png`, `shots/v2-stage3-final.png`.

1b. **Stage 3 guidance page** — PASS
   - Heading "Choose the right stage3", full guidance text rendered (desktop vs minimal, recommendation, pointer to next page).
   - Shots: `shots/v2-stage3-guide2.png` (BIOS), `shots/v2-uefi-stage3guide.png` (UEFI).

2. **Desktop chooser (BIOS)** — PASS, with cosmetic defect
   - Four entries present with correct titles/descriptions:
     - Openbox (recommended) — "Minimal, fast X11 desktop. The live session uses Openbox. Fully tested."
     - Xfce — "Lightweight full desktop. Good balance of speed and features."
     - KDE Plasma — "Full-featured Qt desktop. Large download; best with the desktop stage3."
     - Server (no desktop) — "No X11 desktop or display manager. Kernel, networking and CLI tools only."
   - Default selection is Openbox.
   - DEFECT: the preview pane is an empty framed box with a generic blue image icon for every entry; no per-desktop screenshots/icons are shipped.
   - Shots: `shots/v2-desktop-page.png`, `shots/v2-desktop-xfce.png`, `shots/v2-desktop-kde.png`, `shots/v2-desktop-server.png`.
   - UEFI identical: `shots/v2-uefi-desktop.png`.

3. **Partitions (BIOS)** — PASS
   - Erase disk, No swap, ext4, bootloader "Master Boot Record of vda (/dev/vda)".
   - Shots: `shots/v2-partitions-erase.png`, `shots/v2-bootloader-combo.png`.
   - NOTE: Calamares actually created a **GPT** table with a single 24574MiB ext4 root (no bios_grub partition). GRUB nonetheless installed and the disk booted. This BIOS+GPT blocklist-style setup is fragile; consider an explicit bios_grub partition or msdos table for BIOS installs.

4. **Users (BIOS)** — PASS
   - `Gentoo User` / `gentoo` / `gentoo-test` / password `[test-password]` + repeat, "Use the same password for the administrator account" checked.
   - Shots: `shots/v2-users-empty.png`, `shots/v2-users-name.png`, `shots/v2-users-comp.png`, `shots/v2-users-pass.png`, `shots/v2-users-final-check.png`.

5. **Install + packages step (BIOS)** — PASS
   - Summary -> Install -> Install Now at 13:46:53; Finish "All done." at ~14:05.
   - Desktop chooser queued 15 packages: xorg-server, xf86-input-libinput, xf86-video-vesa/qxl/amdgpu/intel/nouveau, openbox, xterm, tint2, rofi, picom, xsetroot, lightdm, lightdm-gtk-greeter.
   - `packages` job (18/31) ran 13:59:52 -> 14:01:13 and completed; later jobs (bootloader, services, etc.) ran and the Finish page appeared.
   - Verified in target /var/db/pkg: `x11-base/xorg-server-21.1.26`, `x11-wm/openbox-3.6.1-r11`, `x11-misc/lightdm-1.32.0-r5`, `x11-misc/lightdm-gtk-greeter-2.0.9-r1`, `x11-terms/xterm-411`.
   - Only log noise: `[PYTHON JOB]: "[Errno 2] No such file or directory: 'chcon'"` x5 during mount (harmless; no SELinux tools in live env).
   - Shots: `shots/v2-summary.png`, `shots/v2-install-confirm.png`, `shots/v2-bios-wake2.png`, `shots/v2-bios-10m.png`.

6. **BIOS disk-only boot** — PASS
   - QMP quit, relaunched same machine minus ISO with `-boot c`.
   - GRUB -> kernel 6.18.4-gentoo-dist-bin -> LightDM greeter (`gentoo-test`, user `Gentoo User`), Openbox login with `[test-password]`.
   - `ping -c1 9.9.9.9` -> 64 bytes, 0% loss.
   - `rc-status default`: dbus, elogind, NetworkManager, netmount, display-manager, local all `[started]`.
   - Shots: `shots/v2-bios-reboot2.png` (greeter), `shots/v2-bios-openbox-menu.png`, `shots/v2-bios-xterm.png`, `shots/v2-bios-ping.png`, `shots/v2-bios-rcstatus.png`.

7. **UEFI** — PASS
   - Welcome -> Location (America/Toronto) -> Keyboard (us) -> Stage 3 guide -> Select Stage (same tarball) -> Desktop chooser all render identically.
   - Full Openbox install completed ("All done."), then disk-only OVMF boot: GRUB 3.15, LightDM greeter, Openbox login, `ping -c1 9.9.9.9` 0% loss, `rc-status default` all started.
   - Shots: `shots/v2-uefi-location.png`, `shots/v2-uefi-keyboard.png`, `shots/v2-uefi-stage3guide.png`, `shots/v2-uefi-desktop.png`, `shots/v2-uefi-prog3.png`, `shots/v2-uefi-lightdm.png`, `shots/v2-uefi-checks.png`.

## Defects / next required fixes

1. **Openbox session is bare (highest priority UX bug).** tint2, picom, rofi, xsetroot are installed but never launched. `/etc/xdg/openbox/autostart` is stock and only probes gnome-settings-daemon/xfce-mcs-manager. Result: recommended desktop logs in to a flat gray screen with no panel, wallpaper, or compositor. Fix: ship a desktop-openbox autostart/config (tint2rc, picom.conf, wallpaper + `xsetroot`/`feh`) via the desktopchoose package list or a Calamares `shellprocess`/branding file.
2. **Slideshow placeholders.** Install slideshow shows literal "This is a second Slide element." / "This is a third Slide element." and then the stock Calamares "This is a customizable QML slideshow..." text. The custom presentation has empty/placeholder slides. Fix the `branding.desc` presentation/slides list.
3. **Desktop chooser preview pane empty.** All four entries show only a generic image icon; supply screenshots/icons or hide the frame.
4. **BIOS + GPT without bios_grub.** Boot works today via blocklist embedding but is fragile; create a 1-2MiB bios_grub partition on BIOS/GPT installs.
5. Minor: stock Openbox menu advertises Gnome Terminal / Xfce Terminal / Konsole, which are not installed (clicking them fails); prune the menu or add the packages.
6. Minor: Summary page shows only Location/Keyboard/Partitions (no Stage 3 or Desktop selection recap), so the two new choices cannot be reviewed before Install.

## VM state left behind

- BIOS VM: running disk-only install, logged in as `gentoo` in Openbox with xterm open (VNC 5908).
- UEFI VM: running disk-only install, logged in as `gentoo` in Openbox with xterm open (VNC 5909).
- Both QMP sockets and serial consoles are live; disks untouched after verification.
