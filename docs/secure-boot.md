# Secure Boot

> **Status: experimental. Not supported. Not verified.**
>
> The current developer-preview ISO has not passed an end-to-end Secure Boot
> test. Disable Secure Boot in firmware before booting it. Do not enable the
> installer's Secure Boot option on a machine you need to boot.

## Why this page exists

Secure Boot is the most common way an installer silently fails on modern
laptops: the USB boots in BIOS mode, or GRUB starts and the kernel is rejected,
or the machine reboots into firmware setup with no explanation. Ember has the
components for a signed chain in the source tree, but components are not the
same as a verified chain.

This page records exactly what exists, what is missing, and what evidence is
required before the project may claim support.

## Current behavior

- The verified 2026-11-25 ISO was tested with Secure Boot **off**.
- The current source tree includes a Secure Boot checkbox on the build
  configuration page. **It is checked by default on UEFI systems.** Until the
  chain passes QA, uncheck it if your build shows the page.
- The installer's post-install report checks signatures only when
  `/etc/portage/secureboot.pem` exists. That check has not been exercised on a
  Secure Boot machine.
- Nothing in the project signs the ISO, shim, GRUB, or kernel with a
  project-wide key. The design uses a per-install machine key plus MOK.

## Intended chain

```text
firmware DB (Microsoft UEFI CA)
  └── shimx64.efi            Microsoft-signed, from sys-boot/shim
        └── grubx64.efi      signed with the Ember machine key
              └── vmlinuz-*  signed with the Ember machine key
```

The machine certificate is enrolled into the firmware's MOK list on first boot.
Shim trusts the MOK; GRUB's shim-lock verification trusts the same MOK for the
kernel. The private key never leaves the installed system and is not on the
ISO.

### What the source contains

| Piece | Location | State |
| --- | --- | --- |
| Key and certificate generation | `modules/secureboot_prepare/main.py` | Implemented, unverified |
| Portage signing environment | `/etc/portage/env/sys-kernel`, `/etc/portage/env/sys-boot` | Written at install, unverified |
| Source kernel and tools | `gentoo-kernel`, `shim`, `sbsigntools`, `mokutil` | Queued at install, unverified |
| GRUB and kernel signing | `modules/secureboot_finish/main.py` | Implemented, unverified |
| Shim and fallback path | `EFI/<id>/shimx64.efi`, `EFI/BOOT/BOOTX64.EFI` | Implemented, unverified |
| NVRAM entry | `efibootmgr` pointing at shim | Implemented, unverified |
| MOK enrollment | `mokutil --import` or first-boot helper | Implemented, unverified |
| Re-sign helper | `/usr/local/sbin/ember-secureboot` | Implemented, unverified |
| Kernel update hook | `/etc/kernel/install.d/99-ember-secureboot.install` | Implemented, unverified |
| Boot-time verification service | `/etc/init.d/ember-secureboot` | Implemented, unverified |
| Documentation in target | `/etc/ember/secureboot-info.txt` | Written at install |

"Implemented" means the code exists. It does **not** mean it has run correctly
on real firmware.

## What must pass before support is claimed

1. Build with `OVMF_CODE.secboot.4m.fd` and a VARS image that contains the
   Microsoft UEFI CA (or enroll the Microsoft certificate explicitly).
2. Install with Secure Boot enabled in the installer.
3. Confirm shim starts, GRUB's signature validates, and the kernel signature
   validates with `sbverify` and `mokutil --sb-state`.
4. Enroll the machine certificate in MokManager on first boot, including a
   wrong-password path and a cancel path.
5. Boot the installed disk with the ISO removed and Secure Boot still on.
6. Update the kernel and GRUB and confirm the automatic re-sign path keeps the
   system bootable.
7. Test recovery: boot the ISO, chroot, re-sign, and boot again.
8. Repeat on at least one physical UEFI machine, with the exact firmware and
   Secure Boot state recorded.
9. Add screenshots and logs to a QA report and update the matrices.

Until all of that is done, the matrix says **experimental**, and the README
tells users to disable Secure Boot.

## MOK enrollment (intended flow)

This is the flow the code is aiming for, not a verified procedure.

1. The installer generates a machine key and certificate, signs GRUB and every
   kernel in `/boot`, installs shim, and adds a NVRAM entry that points at
   shim.
2. On first boot, shim starts MokManager because the machine certificate is not
   yet enrolled.
3. Choose **Enroll MOK** → **Continue** → **Yes**, then enter the enrollment
   password if one was set.
4. The system reboots. Secure Boot remains enabled and the signed chain loads.

If the certificate is already on the ESP, it can be queued manually:

```sh
sudo ember-secureboot enroll
sudo reboot
```

Then complete enrollment in MokManager. The helper is part of the installer
source and has not been verified.

### If MokManager does not appear

- Confirm the firmware is in UEFI mode, not legacy/CSM.
- Confirm Secure Boot is enabled in firmware.
- Confirm the boot entry points at `shimx64.efi`, not `grubx64.efi`.
- Try the fallback `EFI/BOOT/BOOTX64.EFI` path.
- If the machine boots straight to firmware setup, the shim or GRUB signature
  was rejected. Do not keep rebooting; capture the firmware message and report
  it.

## Recovery

These commands are implemented in the helper but are not QA-verified.

### Re-sign from the installed system

```sh
sudo ember-secureboot status
sudo ember-secureboot resign
sudo reboot
```

### Re-sign from the live ISO

```sh
sudo mount /dev/nvme0n1p3 /mnt/ember     # use your root partition
sudo mount /dev/nvme0n1p1 /mnt/ember/boot/efi
sudo mount --bind /dev /mnt/ember/dev
sudo mount --bind /proc /mnt/ember/proc
sudo mount --bind /sys /mnt/ember/sys
sudo chroot /mnt/ember /usr/local/sbin/ember-secureboot resign
```

The private key must still be at `/etc/portage/secureboot.pem` inside the
installed root. If it is lost, the existing signatures cannot be renewed; the
practical recovery is to disable Secure Boot validation in firmware or
reinstall.

### Disable validation temporarily

From the installed system:

```sh
sudo ember-secureboot disable
sudo reboot
```

Confirm in MokManager. This lowers security. Use it to recover a machine, then
fix the signatures and re-enable Secure Boot in firmware. It is not a
permanent solution.

### Reset the MOK list

```sh
sudo ember-secureboot reset
sudo reboot
```

This removes enrolled machine keys. It may make the current installation
unbootable until the key is re-enrolled or validation is disabled.

## Security notes

- Secure Boot verifies the boot chain; it does **not** encrypt the disk. LUKS2
  is selectable but untested. Use full-disk encryption separately if your
  threat model needs it.
- MOK enrollment is trust-on-first-use. Verify the certificate fingerprint out
  of band if you are enrolling a key you did not generate.
- The machine private key is stored unencrypted at
  `/etc/portage/secureboot.pem` with mode `0600`. Anyone with root can sign
  boot components. Protect the disk and backups accordingly.
- The project does not yet have a hardware security module or a public
  reproducible signing story. Do not model Ember's preview signing as a
  distribution-wide trust root.

## How to help

The most useful contribution is a failed test with complete evidence: OVMF or
firmware version, VARS image, ISO checksum, `mokutil --sb-state`, `sbverify`
output, `efibootmgr -v`, and photographs of firmware/MokManager screens. Open
an **Install report** and mark Secure Boot as enabled.

Do not report "Secure Boot works" from a boot that had Secure Boot disabled.
That is the exact failure mode this page exists to prevent.
