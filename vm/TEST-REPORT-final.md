# Ember final ISO test report — new partition layout + Openbox autostart

Artifact: `/home/user/ember/images/ember-live-amd64.iso`
SHA-256: `934806c8e93766170a53dfff7aa650e90c391153283c1886720e2d9086d70eed`
Size: 4,260,958,208 bytes (3.97 GiB / 4.0G), mtime 2026-11-25 08:39:06 -0600
Built by: `scripts/rebuild-iso2.sh` (mksquashfs zstd-22, xorriso BIOS+UEFI)
Tested ISO is exactly this build; no rebuild was made after the tests below.
Calamares in the ISO: `app-admin/calamares-3.4.2-r1` (Gentoo patched).

## Result summary

| # | Test | BIOS | UEFI |
|---|------|------|------|
| 1 | New ISO boots installer | PASS | PASS |
| 2 | Stage 3 guide page renders | PASS | PASS |
| 3 | Select Stage: amd64 + `current-stage3-amd64-desktop-openrc` | PASS | PASS |
| 4 | Desktop chooser, Openbox default | PASS (preview pane still empty, cosmetic) | PASS (same) |
| 5 | Partitions: erase disk, no swap, ext4, new hybrid layout | PASS | PASS |
| 6 | Users: Gentoo User / gentoo / gentoo-test / admin same password | PASS | PASS |
| 7 | Install completes, no failure dialog | PASS ("All done.") | PASS ("All done.") |
| 8 | Disk-only boot to LightDM | PASS | PASS |
| 9 | Login to Openbox | PASS | PASS |
| 10 | Openbox autostart: tint2 + picom (+ xsetroot line) | PASS | PASS |
| 11 | Custom Openbox menu / rofi Run / xterm | PASS | PASS |
| 12 | Network `ping -c1 9.9.9.9` | PASS, 0% loss | PASS, 0% loss |
| 13 | `rc-status default` all services started | PASS | PASS |
| 14 | Bootloader: BIOS GRUB / UEFI GRUB entry | PASS | PASS |

No "Installation Failed" dialog appeared on either firmware. No fatal installer error text was produced.

## ISO verification (before boot tests)

- Squashfs: 4,118,663,168 bytes, zstd, 1 MiB blocks.
- `dev/console`: char 5,1; `dev/null`: char 1,3.
- `proc`, `sys`, `run`, `tmp`: 0 entries each (plain empty directories).
- El Torito: BIOS image `/boot/grub/i386-pc/eltorito.img` (LBA 1733, boot-info-table)
  and UEFI image `/efi.img` (LBA 107); protective MBR + GPT + APM.
- Volume ID: `gentoo-amd64-livegui`.
- ISO `/etc/calamares/modules/partition.conf` contains
  `createHybridBootloaderLayout: true` and the single root-only `partitionLayout`.
- ISO branding.desc contains `slideshowAPI: 2` and `slideshow: show.qml`.

## Partition layouts observed on the installed disks

BIOS (`sudo fdisk -l /dev/vda`, GPT, 24 GiB / 50,331,648 sectors):

```
Device      Start     End  Sectors  Size Type
/dev/vda1    2048 1050623  1048576  512M EFI System
/dev/vda2 1050624 1067007    16384    8M BIOS boot
/dev/vda3 1067008 50331575 49264568 23.5G Linux filesystem
```

UEFI (`sudo fdisk -l /dev/vda`, GPT, 24 GiB / 50,331,648 sectors):

```
Device      Start     End  Sectors  Size Type
/dev/vda1    4096 1052671  1048576  512M EFI System
/dev/vda2 1052672 1069055    16384    8M BIOS boot
/dev/vda3 1069056 50331575 49262520 23.5G Linux filesystem
```

`lsblk` on both confirmed `vda1 vfat` mounted at `/boot/efi`, `vda2` type
`BIOS boot`, and `vda3 ext4` mounted at `/`. The 8 MiB BIOS boot partition is
present on UEFI too because `createHybridBootloaderLayout` is global; UEFI does
not need it and boots from the 512 MiB ESP. BIOS uses the 8 MiB partition, so
GRUB is not blocklist-embedded; disk-only boot reached LightDM with no GRUB
embedding/blocklist error.

## Openbox autostart evidence

Installed `/etc/xdg/openbox/autostart` on both systems (read in xterm):

```
tint2 &
picom --backend xrender &
xsetroot -solid '#2e3440' &
```

Running processes after login:

- BIOS: `openbox` PID 2330, `tint2` PID 2355, `picom --backend xrender` PID 2366.
- UEFI: `openbox` PID 2356, `tint2` PID 2341, `picom --backend xrender` PID 2332.

The custom `/etc/xdg/openbox/menu.xml` is active on both: right-click shows
`Terminal`, `Run...`, `Reconfigure`, `Exit`. `Terminal` launches xterm; `Run...`
launches rofi and successfully launched `xsetroot`/`picom` during verification.

`xsetroot` is a one-shot, so it does not remain in `ps`. `/usr/bin/xsetroot`
exists, the autostart line runs without error (`~/.xsession-errors` contains
only harmless tint2 icon-theme warnings), and a manual
`xsetroot -solid red` immediately changed the root window to red while picom
was stopped. Visual caveat: with picom running, its xrender backend keeps
showing the LightDM `_XROOTPMAP_ID` wallpaper, so the `#2e3440` solid colour is
not visible. This is cosmetic; the panel, compositor and menu work.

## Sign-in / services / network

- LightDM greeted with hostname `gentoo-test` and user `Gentoo User` on both.
- Password `[test-password]` logged into Openbox on both.
- BIOS `rc-status default`: dbus, elogind, NetworkManager, netmount,
  display-manager, local — all `[started]`.
- UEFI identical: all six `[started]`.
- `ping -c1 9.9.9.9`: 64 bytes, ttl 63, 0% packet loss on both.
- Installed kernel: `6.18.4-gentoo-dist-bin`.
- UEFI `efibootmgr -v` shows a `FancyGL` entry pointing at the ESP GRUB image.

## Screenshots

BIOS (`/home/user/ember/vm/shots/`):
`final-bios-09-partitions.png` (new 512M ESP + 8M BIOS boot + root layout),
`final-bios-18-summary.png`, `final-bios-20-installstart.png`,
`final-bios-27-progress.png` ("All done."), `final-bios-31-openbox.png`,
`final-bios-32-menu.png`, `final-bios-34-procs.png`,
`final-bios-37-services.png` (rc-status + ping), `final-bios-52-lsblk.png`,
`final-bios-54-sgdisk.png`/`final-bios-55-fdisk.png`,
`final-bios-59-psver.png` (ps showing openbox/tint2/picom).

UEFI:
`final-uefi-07-partitions.png`, `final-uefi-14-summary.png`,
`final-uefi-20-progress.png` ("All done."), `final-uefi-31-openbox.png`,
`final-uefi-32-menu.png`, `final-uefi-34-procs.png`,
`final-uefi-35-rcstatus.png`, `final-uefi-36-ping.png`,
`final-uefi-37-lsblk.png`, `final-uefi-38-fdisk.png`,
`final-uefi-39-autostart.png`, `final-uefi-40-efibootmgr.png`.

## Remaining issues (non-blocking, all cosmetic)

1. Install slideshow still uses stock Calamares placeholder text
   (`This is a second Slide element.`, `This is a third Slide element.`,
   `This is a customizable QML slideshow...`). `slideshowAPI: 2` and
   `show.qml` are correctly configured; only the QML text is stock.
2. Desktop chooser preview pane is still an empty framed box for every entry.
3. Summary page recaps Location/Keyboard/Partitions only; Stage 3 and Desktop
   choices are not shown.
4. `xsetroot -solid '#2e3440'` is masked by picom's cached LightDM wallpaper
   (details above). Autostart commands and processes are correct.
5. `sgdisk` is not installed in the target (gdisk package); `fdisk`/`lsblk`
   work and were used for the partition evidence.

## Readiness

The final ISO is **ready**: it was built with the new partition layout and
Openbox autostart, installed successfully on both BIOS and UEFI, and both
installed systems boot disk-only with LightDM/Openbox, panel, compositor,
custom menu, working network and all default services started. Remaining
issues are cosmetic only.

VMs left running for inspection: BIOS VNC `localhost::5908` (disk
`vm/disk-v2-bios.qcow2`), UEFI VNC `localhost::5909` (disk
`vm/disk-v2-uefi.qcow2`).
