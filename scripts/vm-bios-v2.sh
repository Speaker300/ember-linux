#!/bin/bash
# Boot the rebuilt Ember ISO in a fresh BIOS VM.
set -euo pipefail
D=/home/user/ember/vm
I=/home/user/ember/images/ember-live-amd64.iso
mkdir -p "$D/shots"
[ -f "$D/disk-v2-bios.qcow2" ] || qemu-img create -f qcow2 "$D/disk-v2-bios.qcow2" 24G
rm -f "$D/v2-bios.qmp" "$D/v2-bios.pid"
qemu-system-x86_64 -name ember-v2-bios -enable-kvm -machine q35 -cpu host -m 4096 -smp 4 \
  -drive file="$D/disk-v2-bios.qcow2",if=virtio,format=qcow2 \
  -cdrom "$I" -boot d \
  -nic user,model=virtio-net-pci,hostfwd=tcp::2227-:22 \
  -device virtio-vga,xres=1280,yres=800 -device qemu-xhci -device usb-tablet \
  -display none -vnc :8 \
  -qmp unix:"$D/v2-bios.qmp",server=on,wait=off \
  -serial tcp:127.0.0.1:4448,server=on,wait=off \
  -daemonize -pidfile "$D/v2-bios.pid"
echo "BIOS VM: VNC localhost::5908 QMP $D/v2-bios.qmp serial 4448 hostfwd 2225"
