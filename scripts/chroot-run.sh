#!/bin/bash
set -euo pipefail
R=/home/user/ember/build/livegui-root
mkdir -p "$R/proc" "$R/sys" "$R/dev" "$R/run" "$R/var/tmp/portage"
mountpoint -q "$R/proc" || mount -t proc proc "$R/proc"
mountpoint -q "$R/sys" || mount --rbind /sys "$R/sys"
mountpoint -q "$R/dev" || mount --rbind /dev "$R/dev"
mountpoint -q "$R/run" || mount -t tmpfs tmpfs "$R/run"
cp -L /etc/resolv.conf "$R/etc/resolv.conf"
exec chroot "$R" /bin/bash -lc "$*"
