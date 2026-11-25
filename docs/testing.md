# Testing and QA

Ember's documentation is only as good as its test evidence. This page defines
the evidence levels, the current result, how to run the tests, and what a useful
report contains.

> **Rule zero:** never weaken, skip, or rewrite a test to make a build pass.
> Fix the product, or record the limitation and mark the claim as untested.

## Evidence levels

| Level | Meaning | What it proves |
| --- | --- | --- |
| **L0 — present** | Code/config exists in the tree | Nothing about runtime behavior |
| **L1 — live boot** | ISO boots to the live environment | Boot media and live userspace |
| **L2 — install completes** | Calamares reaches the finish page | Installer flow and package transaction |
| **L3 — disk boot** | Installed disk boots without the ISO | Bootloader, kernel, initramfs, rootfs |
| **L4 — usable session** | Login, desktop/console, network, services | A usable install |
| **L5 — hardware** | L4 on physical hardware, with the model recorded | Real firmware/driver behavior |

A desktop is **tested** only at L4 on both firmware modes claimed. "Offered"
means L0–L2 at best. VM results never become L5.

## Current result

Reference artifact (the file now at `images/ember-live-amd64.iso` is a newer,
untested rebuild):

```text
images/ember-live-amd64.iso
4,260,958,208 bytes (3.97 GiB)
sha256 934806c8e93766170a53dfff7aa650e90c391153283c1886720e2d9086d70eed
built 2026-11-25 08:39 -0600
```

Environment: QEMU/KVM, q35 machine, 4 vCPU, 4 GiB RAM, 24 GiB virtio disk,
1280×800 virtio-vga. BIOS used SeaBIOS; UEFI used OVMF 4m. Network was
virtio-net with QEMU user networking.

| Test | BIOS | UEFI | Level |
| --- | --- | --- | --- |
| Live boot and installer | Pass | Pass | L1 |
| Stage3 guide and selection | Pass | Pass | L2 |
| Desktop chooser, Openbox default | Pass (empty preview) | Pass (empty preview) | L2 |
| Erase disk, GPT, hybrid layout, ext4, no swap | Pass | Pass | L2 |
| Openbox install completes | Pass | Pass | L2 |
| Disk-only boot to LightDM | Pass | Pass | L3 |
| Openbox login, tint2, picom | Pass | Pass | L4 |
| Custom menu, rofi, xterm | Pass | Pass | L4 |
| NetworkManager ping | Pass | Pass | L4 |
| OpenRC default services | Pass | Pass | L4 |
| Real hardware | Not run | Not run | — |

Reports: [final](../vm/TEST-REPORT-final.md),
[v2](../vm/TEST-REPORT-v2.md). The exact partition tables, process IDs, service
list, and screenshot names are in the final report.

### Not tested

- Xfce, KDE Plasma, GNOME, Cinnamon, MATE, LXQt, i3, Sway, Hyprland, Fluxbox,
  IceWM, and Server installs (only Openbox has a completed pass, on the
  reference ISO).
- The rebuilt ISO itself; its checksum differs from the reference artifact.
- The make.conf editor and Suggest, offline Live CD, and branding install jobs.
- btrfs, XFS, f2fs, LUKS2, LVM, and swap variants.
- Secure Boot, MOK enrollment, and automatic re-signing.
- Real hardware, USB boot, NVMe, SATA, Wi-Fi, Bluetooth, audio, suspend.
- NVIDIA proprietary drivers and hybrid graphics.
- Dual boot and manual partitioning.
- The optional `@world` update.

## Running the VM tests

The helpers are in `scripts/`. They expect the ISO at
`images/ember-live-amd64.iso`, KVM available, and OVMF installed at
`/usr/share/edk2-ovmf/x64/`.

```sh
# BIOS: VNC localhost::5908, serial 4448, QMP vm/v2-bios.qmp
./scripts/vm-bios-v2.sh

# UEFI: VNC localhost::5909, serial 4449, QMP vm/v2-uefi.qmp
./scripts/vm-uefi-v2.sh
```

The scripts create a 24 GiB disk only if one does not exist. For a clean test,
use a new disk path or delete the old qcow2 after confirming it is not needed.

Inspect with a VNC client or `vncdo -s localhost::5908`. Take screenshots into
`vm/shots/` (ignored by Git). Use QMP or the serial console for recovery.

### Test sequence

1. Record the ISO SHA-256 and size.
2. Boot the live ISO in the firmware mode under test.
3. Confirm the live session and start the installer.
4. Complete the flow with the exact choices recorded:
   - stage3 variant and filename;
   - desktop;
   - filesystem, swap, encryption/LVM;
   - bootloader target;
   - user/host values (redact before publishing).
5. Let the install finish; do not skip the post-install report.
6. Shut down, detach the ISO, boot the disk only.
7. Log in, open a terminal, and run:

```sh
cat /var/log/ember-install-report.txt
rc-status default
ping -c1 9.9.9.9
lsblk -f
sudo efibootmgr -v        # UEFI only
```

8. For a desktop, confirm the session, panel, compositor, menu, terminal, and
   display manager.
9. Capture screenshots of the choice pages, progress, finish, login, desktop,
   and verification commands.
10. Write a QA report with the result and attach it to a pull request or issue.

## Hardware testing

Physical hardware is the missing L5. Use a spare machine or a VM with a
passthrough device if you can. Record:

- vendor/model and firmware version;
- CPU and GPU;
- storage controller and disk model;
- Wi-Fi/Bluetooth/Ethernet chipsets (`lspci -nnk`, `lsusb`);
- firmware mode and Secure Boot state;
- RAM and disk size;
- every result from live boot through suspend.

If a machine fails before the installer, that is still a valid report. Photograph
the firmware screen if it is the only evidence.

## What counts as a regression

A regression is a previously passing check that now fails, or a newly offered
option that cannot complete the flow it promises. Cosmetic defects are tracked,
but they do not turn an untested desktop into a tested one.

When a test fails:

1. Reproduce once from the same ISO.
2. Capture the log and screenshot.
3. Determine whether the failure is the ISO, the environment, or the test.
4. Fix the product or document the limitation.
5. Re-run the full affected matrix, not just the failing step.

## Report template

```markdown
# Ember QA — <desktop> — <BIOS|UEFI> — <date>

- ISO: <path>
- SHA-256: <checksum>
- Size: <bytes>
- Build time: <timestamp>
- Firmware: <SeaBIOS/OVMF version, or machine model + firmware version>
- VM/hardware: <machine type, CPU, RAM, disk, network, GPU>
- Secure Boot: <off/on, MOK state>
- Desktop: <Openbox/Xfce/KDE/Server>
- Filesystem: <ext4/btrfs/xfs/f2fs/LUKS2/LVM>
- Swap: <none/partition/file>

## Results

| Step | Result | Evidence |
| --- | --- | --- |
| Live boot | | |
| Stage3 selection/download | | |
| Desktop chooser | | |
| Partitioning | | |
| Package install | | |
| Bootloader | | |
| Disk-only boot | | |
| Login/session | | |
| Network | | |
| Services | | |

## Logs

<Calamares session.log excerpt, post-install report, dmesg/Xorg excerpts>

## Screenshots

<paths or attachments>

## Defects

<exact reproduction, expected vs actual, severity>

## Verdict

Tested / offered / failed — and which matrix rows this changes.
```

## Reporting a CI or docs failure

The docs workflow checks relative links on push and pull request. Run it
locally before opening a PR:

```sh
python3 .github/scripts/check_links.py
```

If the check is wrong, fix the checker cautiously and add a test case for the
link pattern you are changing. Do not disable the check to make a PR green.
