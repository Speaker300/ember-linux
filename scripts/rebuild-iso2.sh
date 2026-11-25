#!/bin/bash
set -euo pipefail
SRC=/home/user/ember/build/livegui-root
SQ=/home/user/ember/build/image-final2.squashfs
ISO=/home/user/ember/images/ember-live-amd64.iso
ORIG=/home/user/Downloads/livegui-amd64-20260913T163055Z.iso
cp -a "$ISO" /home/user/ember/images/ember-live-amd64-prev.iso
# Never squash a chroot with pseudo-filesystems mounted: proc/sys/dev/run must be plain dirs.
for m in run dev sys proc; do
  if mountpoint -q "$SRC/$m"; then umount -l "$SRC/$m" || umount "$SRC/$m"; fi
done
mkdir -p "$SRC/dev" "$SRC/proc" "$SRC/sys" "$SRC/run" "$SRC/tmp"
[ -c "$SRC/dev/console" ] || mknod -m 600 "$SRC/dev/console" c 5 1
[ -c "$SRC/dev/null" ] || mknod -m 666 "$SRC/dev/null" c 1 3
rm -f "$SQ"
mksquashfs "$SRC" "$SQ" -comp zstd -Xcompression-level 22 -b 1M -noappend \
  -e var/db/repos var/cache/binhost var/cache/distfiles var/tmp/portage root/.cache home/gentoo/.cache
ls -l "$SQ"
cp "$SQ" /home/user/ember/build/iso-root/image.squashfs
xorriso -as mkisofs -o "$ISO" \
 -V 'gentoo-amd64-livegui' --modification-date='2026112509000000' \
 --grub2-mbr "--interval:local_fs:0s-15s:zero_mbrpt,zero_gpt,zero_apm:$ORIG" \
 --protective-msdos-label -partition_cyl_align off -partition_offset 0 --mbr-force-bootable \
 -apm-block-size 2048 -hfsplus -efi-boot-part --efi-boot-image \
 -c '/boot.catalog' -b '/boot/grub/i386-pc/eltorito.img' -no-emul-boot -boot-load-size 4 \
 -boot-info-table --grub2-boot-info -eltorito-alt-boot -e '/efi.img' -no-emul-boot \
 /home/user/ember/build/iso-root
ls -l "$ISO"
