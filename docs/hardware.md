# Hardware and platform support

This page separates what has been tested from what is merely present in the
installer. The short version: **Ember has passed install and boot QA in QEMU on
BIOS and UEFI; it has not been validated on physical hardware.**

## Requirements

| | Minimum | Recommended | QA baseline |
| --- | --- | --- | --- |
| CPU | amd64 (x86-64) | Any amd64 CPU | 4 virtual CPUs, `-cpu host` |
| RAM | 1 GB (installer check) | 4 GB for a desktop | 4 GB |
| Storage | 6 GB (installer check) | 20 GB+ | 24 GiB virtio disk |
| Firmware | BIOS or UEFI | UEFI, Secure Boot off | SeaBIOS and OVMF |
| Network | Internet required | Wired Ethernet | virtio-net, QEMU user network |
| Display | X11-capable GPU for desktops | Supported KMS driver | QEMU virtio-vga |
| Media | 4 GB USB | 8 GB USB | ISO booted as virtual CD-ROM |

The installer's welcome page enforces 1 GB RAM and 6 GB storage. Those are
floor values, not a comfortable configuration, and the 1 GB path has not been
tested end to end. A desktop install with KDE Plasma needs considerably more
space than a server install.

## Platform matrix

| Component | Status | What was tested | What is untested |
| --- | --- | --- | --- |
| BIOS firmware | **Tested** | QEMU q35 + SeaBIOS, GPT, 8 MiB BIOS boot | Real BIOS implementations, CSM quirks |
| UEFI firmware | **Tested** | QEMU q35 + OVMF 4m, GPT, 512 MiB ESP | Real UEFI implementations, NVRAM quirks |
| Secure Boot | **Experimental** | Code path exists; chain not verified | Shim, MOK, signed GRUB/kernel on `OVMF_CODE.secboot` |
| amd64 CPU | **Tested (VM)** | QEMU `-cpu host` | Old CPUs, exotic topologies, real thermal/power |
| Virtio disk | **Tested** | 24 GiB qcow2, GPT, ext4 root | — |
| SATA / AHCI | Untested | — | Real controllers, hotplug |
| NVMe | Untested | — | Namespaces, firmware, laptop RAID modes |
| USB storage boot | Untested | — | USB 2/3 controllers, removable-media BIOS entries |
| virtio-vga | **Tested (VM)** | 1280×800 VNC console | — |
| AMD GPU (amdgpu) | Untested | Driver package included | Real GPUs, firmware, multi-monitor |
| Intel GPU (i915) | Untested | Driver package included | Real GPUs, hybrid graphics |
| NVIDIA (nouveau) | Untested | Driver package included | Real GPUs, power management |
| NVIDIA proprietary | Not included | — | — |
| Wired Ethernet | **Tested (VM)** | virtio-net + NetworkManager + ping | Real NICs, Wake-on-LAN |
| Wi-Fi | Untested | `wpa_supplicant` and firmware included | Real chipsets, rfkill, roaming |
| Bluetooth | Untested | BlueZ is not part of the base install | — |
| Audio | Untested | ALSA/PulseAudio packages may be pulled by desktops | Real codecs, HDMI audio |
| Suspend / hibernate | Untested | — | Laptops, firmware S3/S0ix |
| Printers / scanners | Untested | — | — |
| Dual boot | Untested | Manual partitioning is offered | Existing ESPs, Windows BitLocker, os-prober |

## Firmware

### BIOS

The verified BIOS install used a GPT disk with a 512 MiB ESP, an 8 MiB BIOS
boot partition, and an ext4 root. GRUB is installed to the BIOS boot partition
rather than relying on blocklist embedding. The installed disk booted with the
ISO removed.

Real BIOS implementations vary. If the machine offers both "UEFI" and "Legacy"
entries for the same USB device, choose deliberately; the installer records the
firmware mode it booted in.

### UEFI

The verified UEFI install used OVMF with a 512 MiB FAT32 ESP mounted at
`/boot/efi`. `efibootmgr -v` showed an EFI boot entry pointing at the ESP GRUB
image; the reference build used the stock `FancyGL` label. The installed disk
booted without the ISO.

Some firmware ignores newly created NVRAM entries or requires the fallback
`EFI/BOOT/BOOTX64.EFI` path. The current installer writes a normal entry; a
fallback path is part of the Secure Boot work and is not verified for the
non-Secure-Boot path.

### Secure Boot

**Not supported yet.** Disable Secure Boot before booting the current ISO.
Enabling it may prevent the unsigned GRUB from starting. See
[Secure Boot](secure-boot.md).

## Storage and filesystems

| Filesystem / layout | Installer | Status |
| --- | --- | --- |
| ext4 root | Yes | **Tested** |
| btrfs root | Yes | Selectable, untested |
| XFS root | Yes | Selectable, untested |
| f2fs root | Yes | Selectable, untested |
| LUKS2 root | Yes | Selectable, untested |
| LVM | Yes | Selectable, untested |
| No swap | Yes | **Tested** |
| Swap partition / file / suspend | Yes | Selectable, untested |
| Manual partitioning | Yes | Offered, untested |
| Dual boot | Via manual partitioning | Untested |

The tested layout is intentionally simple. Nothing about btrfs subvolumes,
snapshots, LUKS unlock in GRUB, LVM activation in the initramfs, or f2fs boot
has been verified. Do not use them on a system you need to boot.

The installer includes `btrfs-progs`, `xfsprogs`, `f2fs-tools`, `lvm2`,
`cryptsetup`, and `gptfdisk`, so the tools are present in the target even when
the tested path does not exercise them.

## Graphics

The X11 desktop choices install Xorg and the VESA, QXL, amdgpu, Intel, and
nouveau drivers. Sway and Hyprland are Wayland sessions and do not install
Xorg; GNOME uses GDM and may choose Wayland. The QA VM used QEMU `virtio-vga`,
which is not one of those named drivers, so the VM result proves the X11 session
and installer UI, not a specific real GPU driver.

- **AMD:** `xf86-video-amdgpu` is installed. Modern AMD GPUs normally use the
  kernel modesetting driver through Xorg; untested.
- **Intel:** `xf86-video-intel` is installed. Untested; some newer Intel GPUs
  are better served by modesetting.
- **NVIDIA:** `xf86-video-nouveau` is installed; the proprietary driver is not.
  Expect limitations on recent GPUs. Untested.
- **Multi-GPU / hybrid laptops:** untested.
- **Wayland:** Sway and Hyprland are Wayland-only choices; GNOME may use
  Wayland under GDM. None is verified.
- **X11:** Openbox is X11; Xfce, KDE Plasma, Cinnamon, MATE, LXQt, i3,
  Fluxbox, and IceWM are configured as X11 sessions. Only Openbox is tested.

If X fails to start, see
[Troubleshooting](troubleshooting.md#the-installed-system-boots-to-a-black-screen-or-a-console).

## Networking

The base install includes NetworkManager, `wpa_supplicant`, `linux-firmware`,
`dhcpcd`, and `openssh`. Wired networking through NetworkManager was verified
in QEMU with a ping to `9.9.9.9`.

Wi-Fi is installed but untested. Laptops with MediaTek, Realtek, Broadcom, or
very new Intel chipsets are the most likely to need extra firmware or a
different driver. Bluetooth is not part of the base install.

## Laptops and real hardware

The first physical-machine QA run is a release blocker. Laptops add firmware,
power-management, hybrid-graphics, and Wi-Fi variables that QEMU cannot
reproduce. If you test on a laptop, record the model, firmware version, GPU,
Wi-Fi chipset, and whether suspend works.

## Virtual machines

The QA scripts use:

```sh
qemu-system-x86_64 -enable-kvm -machine q35 -cpu host -m 4096 -smp 4 \
  -device virtio-vga -nic user,model=virtio-net-pci
```

UEFI uses OVMF `OVMF_CODE.4m.fd` and a writable `OVMF_VARS.4m.fd` copy. BIOS
uses SeaBIOS. The disk is a 24 GiB qcow2 attached with `if=virtio`.

VirtualBox, VMware, Hyper-V, and Proxmox are untested. Nested virtualization,
ballooning, snapshots, and virtio-fs are out of scope for the current QA.

## Reporting a hardware result

Open an **Install report** with:

- machine model and firmware version;
- CPU, GPU, storage controller, and network chipset;
- firmware mode and Secure Boot state;
- ISO checksum;
- desktop/filesystem selected;
- result at each stage: live boot, install, disk boot, login, network, audio,
  suspend;
- `lspci -nnk`, `lsusb`, `lsblk -f`, `dmesg` excerpts for failures;
- screenshots where useful.

A clean failure on unusual hardware is valuable. It tells the next person what
to expect.
