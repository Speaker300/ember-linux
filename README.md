# Ember Linux

A Gentoo-based amd64 live ISO with a graphical Calamares installer. The live
session is a minimal Openbox desktop; the installer can install a selected
desktop, supports legacy BIOS and UEFI, and is intended to feel like a normal
distribution installer rather than a stock Calamares wizard.

## Status

- **Verified:** BIOS and UEFI Openbox installs, disk-only boot, LightDM login,
  networking, and the Openbox live session.
- **In progress:** Xfce/KDE/Server install verification, Secure Boot,
  make.conf editor and hardware-probing Suggest button, optional `@world`,
  additional filesystems (btrfs, xfs, f2fs, LUKS2, LVM), branding, and ISO
  size reduction.
- **Testing boundary:** VM coverage is not real-hardware coverage. The user's
  Intel UEFI machine is the final hardware check. Some firmware, GPU, Wi-Fi,
  and Bluetooth behavior cannot be proven in QEMU.

## Repository layout

| Path | Purpose |
| --- | --- |
| `configs/calamares/` | Calamares settings, module configs, and branding source of truth |
| `scripts/` | ISO build, chroot, and QEMU test helpers |
| `branding/` | Ember Linux visual identity and desktop/boot themes |
| `vm/` | Test reports and VM metadata (disks and screenshots are ignored) |
| `NEXT-PHASE.md` | Current full-scope work plan and live status |
| `images/` | Built ISOs (ignored by Git; publish via Releases) |

## Building

The build root is a prepared Gentoo LiveGUI rootfs at
`build/livegui-root`, with Calamares and the live Openbox session installed.
The ISO is repacked with:

```sh
./scripts/rebuild-iso2.sh
```

The script unmounts any chroot pseudo-filesystems, recreates the static
`/dev/console` and `/dev/null` nodes, builds `image-final2.squashfs`, and
writes `images/ember-live-amd64.iso` with the hybrid BIOS/UEFI El Torito
layout.

## Testing

VM helpers are in `scripts/` (`vm-bios-v2.sh`, `vm-uefi-v2.sh`). They use
QEMU/KVM, OVMF for UEFI, VNC for inspection, QMP for control, and a serial
console for recovery. Do not flash a USB device during development; test the
ISO in QEMU and only write it to removable media when explicitly requested.

## License

Ember Linux bundles third-party components under their own licenses. The
project's own source licensing will be finalized before a public release.
