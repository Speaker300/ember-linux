# Building Ember

> **The build is not yet reproducible from a clean clone.** It repacks a
> prepared Gentoo LiveGUI rootfs that lives outside Git. This page documents
> the current maintainer flow honestly, including its assumptions, so you can
> reproduce it if you have the same base or help replace it with a scripted
> bootstrap.

## What the build produces

```text
images/ember-live-amd64.iso
```

A hybrid BIOS/UEFI ISO with an El Torito BIOS image, a UEFI `efi.img`, a GPT +
protective MBR + APM layout, and a zstd-compressed squashfs containing the live
rootfs. The verified 2026-11-25 artifact was 4,260,958,208 bytes (3.97 GiB),
SHA-256 `934806c8e93766170a53dfff7aa650e90c391153283c1886720e2d9086d70eed`.

## Host requirements

- Gentoo Linux amd64 (the build scripts assume Gentoo paths and tools).
- Root access (loop devices, chroot, `mknod`, mounts).
- `sys-fs/squashfs-tools` (`mksquashfs`).
- `net-misc/xorriso` (ISO mastering).
- `sys-boot/grub` with both `pc` and `efi-64` platforms for the ISO's boot
  images.
- QEMU/KVM and OVMF for testing.
- At least 30 GB free: the rootfs, the extracted ISO tree, the squashfs, the
  new ISO, and the previous ISO backup all coexist during a rebuild.
- The package cache and Portage repository used by the prepared rootfs.

This is a large disk and time commitment. Do not build on a machine you cannot
leave alone for the duration.

## The prepared rootfs

The build expects:

```text
build/livegui-root/
```

This is a Gentoo LiveGUI rootfs with:

- Calamares 3.4.x (Gentoo-patched) installed;
- the Ember Calamares modules compiled into
  `/usr/lib64/calamares/modules/`;
- the live Openbox session and its packages;
- the Ember branding files available for the sync step;
- a populated `/var/db/repos/gentoo` (or the ability to sync).

`build/` is ignored by Git. There is no script in this repository that creates
this rootfs from scratch yet. That is the main gap between the current build and
a public reproducible build.

The original LiveGUI ISO is referenced inside `scripts/rebuild-iso2.sh` as
`/home/user/Downloads/livegui-amd64-20260913T163055Z.iso`. You will need that
file, or an equivalent source for the El Torito boot images, and you will need
to adjust the hard-coded paths.

## Build steps

From the repository root, as root:

```sh
# 1. Install the live branding pack into the rootfs (if it changed).
./scripts/install-branding.sh

# 2. Sync installer configs, modules, and Calamares branding.
./scripts/sync-installer.sh

# 3. Optionally enter the rootfs to inspect or adjust packages.
./scripts/chroot-run.sh 'emerge --info | head'

# 4. Repack the ISO.
./scripts/rebuild-iso2.sh
```

### What `sync-installer.sh` does

- Backs up the existing `/etc/calamares` to `/etc/calamares.prev`.
- Copies `configs/calamares/*.conf` and `settings.conf` into the rootfs.
- Replaces `/usr/share/calamares/branding/ember` with `branding/calamares/`.
- Copies the Python modules (`downloadstage3`, `gentoopkg`, `write_makeconf`,
  `secureboot_prepare`, `secureboot_finish`, `preflight`, `desktop_setup`,
  `desktop_overlay`, `branding`) into `/usr/lib64/calamares/modules/`.

It does **not** compile the C++ `makeconf` module. If you changed that module,
build and install it in the rootfs before repacking. It also does not install
the live desktop branding pack; `install-branding.sh` does that.

### What `rebuild-iso2.sh` does

1. Copies the current ISO to `images/ember-live-amd64-prev.iso`.
2. Unmounts `proc`, `sys`, `dev`, and `run` inside the rootfs if they are
   mounted. A squashfs must not contain live pseudo-filesystems.
3. Recreates `/dev/console` and `/dev/null` if missing.
4. Builds `build/image-final2.squashfs` with zstd level 22, 1 MiB blocks,
   excluding the Portage repository, binhost cache, distfiles, Portage temp,
   and user caches.
5. Copies the squashfs into `build/iso-root/image.squashfs`.
6. Runs `xorriso` to create the hybrid ISO with the BIOS and UEFI boot images.

The volume ID is `gentoo-amd64-livegui`. Changing it is cosmetic; boot loaders
and tests do not depend on the string.

## Verify the artifact

```sh
sha256sum images/ember-live-amd64.iso
stat -c '%s bytes' images/ember-live-amd64.iso

# Inspect the El Torito boot images.
xorriso -indev images/ember-live-amd64.iso -report_el_torito as_mkisofs

# Confirm the squashfs is readable and does not contain mounted pseudo-fs.
unsquashfs -l build/image-final2.squashfs | head
```

Expected properties of a good build:

- ISO size under 4 GiB for the current target (the verified build is 3.97 GiB).
- Both BIOS (`/boot/grub/i386-pc/eltorito.img`) and UEFI (`/efi.img`) boot
  images present.
- Squashfs contains `dev/console` (char 5,1) and `dev/null` (char 1,3), and
  `proc`, `sys`, `run`, `tmp` are empty directories, not mount points.
- The Calamares branding directory contains `branding.desc`, `show.qml`,
  `stylesheet.qss`, and the logo/banner assets.

## Test in QEMU

Never flash a USB device during development. Use a fresh disk per test:

```sh
./scripts/vm-bios-v2.sh
./scripts/vm-uefi-v2.sh
```

Those scripts expect the ISO at `images/ember-live-amd64.iso` and create a
24 GiB qcow2 disk if one does not exist. They expose VNC on `localhost::5908`
(BIOS) and `localhost::5909` (UEFI), QMP sockets under `vm/`, and serial
consoles on ports 4448/4449.

The newer helper is more flexible:

```sh
./scripts/vm-launch.sh test-bios bios
./scripts/vm-launch.sh test-uefi uefi
./scripts/vm-launch.sh test-bios-disk bios "" disk
```

Read the script before using it; it chooses VNC/SSH ports from the name and
uses a larger default RAM allocation than the original QA run.

Inspect with any VNC client or `vncdo`. Record screenshots under `vm/shots/`
(ignored). The full test procedure and evidence rules are in
[Testing](testing.md).

## Common build failures

| Symptom | Cause | Fix |
| --- | --- | --- |
| Squashfs is huge or contains `/proc` entries | Pseudo-filesystems were mounted | Unmount them; `rebuild-iso2.sh` tries, but verify |
| Boot fails with "no /dev/console" | Device nodes missing from the squashfs | Recreate char 5,1 and char 1,3 before repacking |
| Installer shows old configs | Forgot `sync-installer.sh` | Sync and rebuild |
| Installer shows old branding | Branding not synced or wrong path | Check `/usr/share/calamares/branding/ember` |
| `makeconf` page missing | C++ module not compiled into the rootfs | Build/install the module, then sync |
| ISO does not boot in UEFI | Missing `efi.img` or OVMF boot order | Inspect El Torito; boot the UEFI entry explicitly |
| ISO does not boot in BIOS | Missing El Torito BIOS image or hybrid MBR | Inspect with `xorriso`; check the original boot images |
| Secure Boot rejects the ISO | Expected; the chain is unsigned/unverified | Disable Secure Boot for QA |

## Toward a reproducible build

The project needs a scripted, clean-clone path:

1. Bootstrap a Gentoo rootfs from a pinned stage3 and snapshot.
2. Install Calamares and the Ember modules with a documented package set.
3. Build the live session and branding from repository sources.
4. Produce the squashfs and ISO with pinned tool versions.
5. Run the BIOS/UEFI smoke tests in CI.
6. Publish the ISO, SHA-256, and build metadata together.

Until that exists, a build is a maintainer artifact, not a reproducible release.
Contributions toward this are welcome; open an issue before starting so the
approach can be reviewed.

## Licensing reminder

Do not add third-party binaries, firmware, fonts, or artwork to the build
without recording their license and source. The project has no top-level
license yet; see [Licensing](licensing.md). The build bundles Gentoo packages
under their own licenses, and the branding is CC-BY-SA-4.0.
