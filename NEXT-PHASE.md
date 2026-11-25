# Ember Gentoo Installer — Full-Scope Phase

## User request (verbatim, current priority)

"Finish secure boot make sure all the installs actually work make sure the editor and the suggestion button work as well as do all the options as well as choosing anything else that is marked as optional. Make sure all types of file systems work try to make the ISO smaller you could do that by making it more onlineas well as don’t try to flush it to anything cause I don’t have a USB plugged in."

No USB flashing. Final artifact must be an ISO. Never weaken or alter a test to make it pass; fix the product.

## Verified current state

- Final ISO: `/home/user/ember/images/ember-live-amd64.iso`
  - Size 4,260,958,208 bytes; SHA-256 `934806c8e93766170a53dfff7aa650e90c391153283c1886720e2d9086d70eed`.
  - Built 2026-11-25 08:39 -0600 by `scripts/rebuild-iso2.sh`.
- Passed on both BIOS and UEFI: live boot, Stage 3 guide, desktop chooser, Openbox install, disk-only boot, LightDM login, Openbox session, tint2/picom autostart, custom menu/rofi/xterm, NetworkManager, ping, GRUB.
- Partition layout on 24 GiB GPT: 512 MiB ESP + 8 MiB BIOS boot + 23.5 GiB ext4 root, both firmwares. `createHybridBootloaderLayout: true`.
- Openbox install autostart:
  `tint2 &`, `picom --backend xrender &`, `xsetroot -solid '#2e3440' &`.
- Installed credentials used in tests: full name `Gentoo User`, login `gentoo`, host `gentoo-test`, password `[test-password]` (same for admin).
- Reports: `/home/user/ember/vm/TEST-REPORT-final.md`, `/home/user/ember/vm/TEST-REPORT-v2.md`.

## Key paths

- Source configs: `/home/user/ember/configs/calamares/`
- Live rootfs/chroot: `/home/user/ember/build/livegui-root`
- Extracted ISO tree: `/home/user/ember/build/iso-root`
- Calamares 3.4.2 + Gentoo patch source: `/home/user/ember/build/calamares-src`
- Build script: `/home/user/ember/scripts/rebuild-iso2.sh`
- Chroot helper: `/home/user/ember/scripts/chroot-run.sh`
- VM scripts: `scripts/vm-bios-v2.sh` (VNC :8/5908, QMP `vm/v2-bios.qmp`, serial 4448, hostfwd 2227), `scripts/vm-uefi-v2.sh` (VNC :9/5909, QMP `vm/v2-uefi.qmp`, serial 4449, hostfwd 2226).
- OVMF: `/usr/share/edk2-ovmf/x64/OVMF_CODE.4m.fd`, `OVMF_CODE.secboot.4m.fd`, `OVMF_VARS.4m.fd`.
- Pkg cache: `/home/user/ember-cache/`.
- Portage repo in chroot: `/home/user/ember/build/livegui-root/var/db/repos/gentoo`.

## Pending work (priority order)

1. **Desktop installs actually work**: test Xfce, KDE Plasma, and Server choices from `desktopchoose.conf` in VMs; fix package lists, display manager/session defaults, and any install failures. Openbox already passes.
2. **Secure Boot**: UEFI shim -> signed GRUB -> signed kernel; MOK enrollment; sign `gentoo-kernel-bin` and a source-built kernel/modules; automatic re-sign after kernel/GRUB updates; recovery path; test with OVMF `OVMF_CODE.secboot.4m.fd`. Do not claim support until the full chain passes.
3. **make.conf editor + Suggest**: a real editable screen/tab; probe CPU/RAM/GPU/firmware/init/desktop; generate validated make.conf values (CFLAGS/CXXFLAGS, MAKEOPTS, USE, VIDEO_CARDS, INPUT_DEVICES, ACCEPT_LICENSE, GENTOO_MIRRORS, FEATURES, BINPKG_COMPRESS, EMERGE_DEFAULT_OPTS, GRUB_PLATFORMS, CPU_FLAGS_X86, LINGUAS); validate and show diff/reset.
4. **Optional @world**: installer checkbox (default off) that runs `emerge --update --deep --newuse @world` in target.
5. **Filesystems**: ext4, btrfs, xfs, f2fs; LUKS2 root; LVM; swap none/file/partition. Test installs and disk boot for each.
6. **Smaller ISO**: strip KDE Plasma/Plasma apps from the live rootfs, keep Calamares Qt/KF deps and Openbox live; remove docs/locales/uneeded firmware; target well under 4 GiB. Stay online-first.
7. **Cosmetic**: slideshow placeholder text, desktop chooser preview images, Summary recap of Stage 3/Desktop choices, xsetroot color masked by picom.

## Engineering rules

- Back up before overwriting; the rebuild script already backs up the ISO.
- Keep `/home/user/ember/configs/calamares/` as source of truth; copy into chroot before rebuild.
- Test from the exact final ISO; no USB writes.
- VNC control: `vncdo -s localhost::5908` / `::5909`; screenshots under `/home/user/ember/vm/shots/`.
- Wizard coordinates: Next (1148,784), Install (1148,784), Install Now (353,78), arch combo (620,400), amd64 (618,422), erase radio (185,62), user fields (275,47 / 100 / 156 / 213), repeat (482,213), admin checkbox (184,249).
- VNC can drop characters; verify field text and green checks before proceeding.
- Report pass/fail with exact screenshots and logs.
