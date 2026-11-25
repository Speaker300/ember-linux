#!/bin/bash
# Boot the rebuilt Ember ISO in a fresh UEFI VM (OVMF 4m).
set -euo pipefail
D=/home/user/ember/vm
I=/home/user/ember/images/ember-live-amd64.iso
OVMF=/usr/share/edk2-ovmf/x64
mkdir -p "$D/shots"
[ -f "$D/disk-v2-uefi.qcow2" ] || qemu-img create -f qcow2 "$D/disk-v2-uefi.qcow2" 24G
cp -f "$OVMF/OVMF_VARS.4m.fd" "$D/OVMF_VARS-v2.fd"
rm -f "$D/v2-uefi.qmp" "$D/v2-uefi.pid"
qemu-system-x86_64 -name ember-v2-uefi -enable-kvm -machine q35 -cpu host -m 4096 -smp 4 \
  -drive if=pflash,format=raw,readonly=on,file="$OVMF/OVMF_CODE.4m.fd" \
  -drive if=pflash,format=raw,file="$D/OVMF_VARS-v2.fd" \
  -drive file="$D/disk-v2-uefi.qcow2",if=virtio,format=qcow2 \
  -cdrom "$I" -boot d \
  -nic user,model=virtio-net-pci,hostfwd=tcp::2226-:22 \
  -device virtio-vga,xres=1280,yres=800 -device qemu-xhci -device usb-tablet \
  -display none -vnc :9 \
  -qmp unix:"$D/v2-uefi.qmp",server=on,wait=off \
  -serial tcp:127.0.0.1:4449,server=on,wait=off \
  -daemonize -pidfile "$D/v2-uefi.pid"
echo "UEFI VM: VNC localhost::5909 QMP $D/v2-uefi.qmp serial 4449 hostfwd 2226"
