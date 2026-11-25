# Troubleshooting

Start with the exact ISO checksum and the firmware mode. Many "installer bugs"
are a stale ISO, a USB written in the wrong mode, or Secure Boot rejecting the
bootloader.

## Quick triage

| Symptom | First check |
| --- | --- |
| USB not in boot menu | Verify the write, try another port, enable USB boot, check BIOS/UEFI mode |
| Firmware rejects the USB | Disable Secure Boot; see [Secure Boot](secure-boot.md) |
| Black screen after boot menu | Try the other firmware mode; add `nomodeset` to the kernel command line |
| Installer does not appear | Start it manually with `sudo calamares`; check the log path below |
| No network in the live session | `nmcli device status`, then `ping -c1 9.9.9.9` |
| Stage3 list is empty | Network, DNS, clock, proxy, or mirror problem |
| Install fails partway | Read the Calamares log; note the exact job |
| Installed system does not boot | Firmware mode, boot order, ESP contents, GRUB |
| LightDM loops or shows a black screen | Switch to a TTY and check the session log |
| Openbox has no panel | Check the autostart file and run `tint2` manually |

## The USB does not appear in the boot menu

1. Re-run `lsblk` and confirm you wrote to the whole device (`/dev/sdX`), not a
   partition (`/dev/sdX1`).
2. Verify the ISO checksum on the host before writing.
3. Try a different USB port, preferably a rear USB 2 port on a desktop.
4. Enter firmware setup and enable USB boot, legacy/CSM if you need BIOS mode,
   or UEFI boot if the stick was written for UEFI.
5. Some firmware only shows the device under a one-time boot menu (F12, F11,
   Esc, or F8 depending on the vendor).
6. Re-write the stick with `dd` in DD mode, not a tool that extracts files.

The ISO is a hybrid image: it contains both BIOS and UEFI El Torito boot
images. The same stick can boot either way, but the firmware entry you choose
determines the install mode.

## Firmware rejects the USB or reports a security violation

Secure Boot is not supported yet. Disable it in firmware setup and boot again.
Do not enroll random keys to get past the message. See
[Secure Boot](secure-boot.md).

## Black screen after the boot menu

- Wait 30–60 seconds; the live environment may still be starting.
- Try the other firmware mode (BIOS vs UEFI).
- At the GRUB menu, edit the boot entry and add `nomodeset` after `linux`, then
  boot. This uses a basic framebuffer and can get a machine with an unsupported
  GPU to a desktop. It is a diagnostic workaround, not a fix.
- Try `video=1024x768` if the display mode is out of range.
- On a laptop with hybrid graphics, try disabling the discrete GPU in firmware
  if the option exists.

If the live session starts but the installer window is missing, open a terminal
and run `sudo calamares`.

## Finding the installer log

In the live session, Calamares writes:

```text
/root/.cache/calamares/session.log
```

If you launched it with `sudo`, that is the file to read:

```sh
sudo less /root/.cache/calamares/session.log
sudo tail -n 200 /root/.cache/calamares/session.log
```

The terminal on tty1 (Ctrl+Alt+F1) also shows installer output. Capture the
last 200 lines around the failure.

After a successful install, the target report is:

```text
/var/log/ember-install-report.txt
```

It records PASS/FAIL for the kernel, GRUB, fstab, machine-id, home directory,
display manager, Openbox autostart, `make.conf`, block devices, and EFI
entries. Attach it to an install report; it is designed for this.

## No network in the live session

NetworkManager is the network stack. Check the device and connection:

```sh
nmcli device status
nmcli connection show
ping -c1 9.9.9.9
```

- If the device is `unmanaged`, the live image may not have the driver or
  firmware. Check `lspci -nnk` for the kernel driver in use.
- If `ping 9.9.9.9` works but names do not resolve, check
  `/etc/resolv.conf` and try `ping -c1 distfiles.gentoo.org`.
- If the clock is far in the future or past, TLS downloads can fail. Set the
  time in the live session before retrying.
- On a corporate or campus network, a captive portal or proxy may block
  Gentoo mirrors. The installer has no proxy configuration page in this
  preview; configure the live session's environment before starting Calamares.
- Wi-Fi is untested. A wired connection is the reliable path for QA.

The normal path is online-only. There is no verified offline mode. Newer
builds add a Live CD (offline) stage option, but it is untested.

## The Stage 3 variant list is empty

The list is fetched from the network. Check:

```sh
ping -c1 distfiles.gentoo.org
date -u
```

Then go back and forward again to refresh. If the mirror is down, wait and
retry; the installer does not currently let you paste a custom mirror URL.

## The install fails partway

1. Do not close the installer before reading the error.
2. Note the job name and the last lines of
   `/root/.cache/calamares/session.log`.
3. Check free space on the target: the tested layout used a 24 GiB disk; a
   desktop with KDE Plasma needs substantially more than the 6 GB minimum.
4. Check that the network stayed up. A dropped connection during the package
   transaction is a common cause.
5. If the failure is a package build or fetch error, include the package name
   and the exact error text in the issue.

You can retry an erase-disk install; it will recreate the partitions. Back up
anything you care about first.

## The target disk is not detected

```sh
lsblk -o NAME,SIZE,TYPE,FSTYPE,MODEL
sudo lspci -nnk | grep -A3 -i 'sata\|raid\|nvme'
```

- Some laptops ship with Intel RST / VMD / RAID mode enabled. Linux may not see
  the disk until the firmware is switched to AHCI. Changing that mode can break
  an existing Windows install; understand the risk before changing it.
- NVMe, RAID, and exotic controllers are untested. If `lsblk` does not show the
  disk, the installer cannot install to it.
- A USB-attached target disk may appear and disappear; use an internal disk for
  QA.

## The installed system does not boot

### Check the firmware mode and boot order

- If you installed in UEFI mode, boot the disk in UEFI mode. A BIOS boot of a
  UEFI install will not find GRUB.
- If you installed in BIOS mode, enable legacy/CSM boot for the disk.
- In UEFI firmware, check that an **Ember Linux** entry exists. If it does not,
  the NVRAM write failed or the firmware ignored it.

From the live ISO, with the installed root mounted:

```sh
sudo efibootmgr -v
sudo lsblk -f
sudo find /mnt/ember/boot/efi -maxdepth 3 -type f
```

### Reinstall GRUB (advanced)

Only do this if you know which disk and partition hold the installed system.
Boot the live ISO, mount the target, and chroot:

```sh
sudo mount /dev/nvme0n1p3 /mnt/ember       # root partition
sudo mount /dev/nvme0n1p1 /mnt/ember/boot/efi
for d in dev proc sys; do sudo mount --bind /$d /mnt/ember/$d; done
sudo chroot /mnt/ember
```

Inside the chroot, for UEFI:

```sh
grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=ember
grub-mkconfig -o /boot/grub/grub.cfg
```

For BIOS, replace the target with the whole disk:

```sh
grub-install --target=i386-pc /dev/sdX
grub-mkconfig -o /boot/grub/grub.cfg
```

Exit, unmount, and reboot. This is standard Gentoo recovery, not a tested Ember
feature; capture the output if it fails.

## The installed system boots to a black screen or a console

Switch to a text console with Ctrl+Alt+F2 (or F3/F4). Log in as your user.

```sh
rc-status default
rc-service display-manager status
cat ~/.xsession-errors
sudo less /var/log/Xorg.0.log
```

If LightDM is not running:

```sh
sudo rc-service display-manager start
```

If X starts but the session exits immediately, check the session configuration:

```sh
cat /etc/lightdm/lightdm.conf
ls /usr/share/xsessions/
```

The installer configures `user-session=` for Plasma, Xfce, or Openbox based on
what it finds. A missing session file or a failed driver load will send you
back to the greeter. The Xorg log names the driver and the failure.

If you only need a shell, Ctrl+Alt+F2 is enough to inspect and repair. You can
also boot the live ISO and chroot into the install.

## Openbox has no panel or menu

```sh
pgrep -a tint2
pgrep -a picom
cat /etc/xdg/openbox/autostart
```

If the processes are missing, start them manually:

```sh
tint2 &
picom --backend xrender &
```

The installed autostart is written by `configs/calamares/openrc.conf`. The
known cosmetic issue is that picom can mask the `xsetroot` solid color with the
LightDM wallpaper; the panel itself should still appear.

## Wi-Fi does not work

Wi-Fi is untested. Check whether the kernel has a driver and firmware:

```sh
lspci -nnk | grep -A3 -i network
dmesg | grep -i -E 'firmware|wifi|iwlwifi|rtw|mt76'
nmcli device status
```

If the device is present but unmanaged, the driver or firmware is missing.
`linux-firmware` is installed, but very new or unusual chipsets may need a
newer kernel or a vendor driver. A USB Ethernet adapter is the pragmatic
workaround for an install.

## The clock or TLS downloads fail

If the system clock is wrong, package downloads can fail certificate checks.
Check and set the time in the live session before installing. On the installed
system, enable a time service or set the clock manually. This is a common cause
of "mirror unreachable" errors that are not actually network failures.

## Known cosmetic issues in this preview

These do not block an install:

- desktop chooser previews are empty frames;
- the install slideshow still contains placeholder copy;
- the summary does not recap Stage 3 or desktop choices;
- the `xsetroot` color is masked by picom's cached wallpaper;
- the Openbox menu may reference applications that are not installed.

See the [roadmap](roadmap.md) and the
[final QA report](../vm/TEST-REPORT-final.md#remaining-issues-non-blocking-all-cosmetic).

## Reporting a problem

Open an issue with the **bug report** or **install report** template. Include:

- ISO filename, size, SHA-256, and build date;
- firmware mode and Secure Boot state;
- machine or VM model, CPU, GPU, storage controller, network device;
- desktop and filesystem selected;
- the exact step and the exact error text;
- the relevant log excerpt (last 100–200 lines);
- screenshots without personal data.

Do not paste passwords, private keys, MAC addresses, or serial numbers. If a
log contains them, redact before attaching.
