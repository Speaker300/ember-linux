#!/bin/bash
# Launch an Ember test VM.
#   vm-launch.sh NAME bios|uefi [iso] [bootmode]
# bootmode: install (default, boot CD once then disk) or disk
set -euo pipefail
NAME=${1:?name}
FW=${2:?bios|uefi}
ISO=${3:-/home/user/ember/images/ember-live-amd64.iso}
BOOTMODE=${4:-install}
D=/home/user/ember/vm
OVMF=/usr/share/edk2-ovmf/x64
mkdir -p "$D/shots" "$D/logs"

# VNC display number from name hash (stable): 20..79
N=$(python3 -c "import hashlib,sys; print(20+int(hashlib.md5(sys.argv[1].encode()).hexdigest(),16)%60)" "$NAME")
QMP="$D/$NAME.qmp"
PID="$D/$NAME.pid"
DISK="$D/disk-$NAME.qcow2"
SERIAL="$D/logs/$NAME-serial.log"
[ -f "$DISK" ] || qemu-img create -f qcow2 "$DISK" 24G
rm -f "$QMP" "$PID" "$SERIAL"

COMMON=(-name "ember-$NAME" -enable-kvm -machine q35 -cpu host -m 4096 -smp 4
  -device virtio-vga,xres=1280,yres=800 -device qemu-xhci -device usb-tablet
  -display none -vnc ":$N"
  -qmp unix:"$QMP",server=on,wait=off
  -serial "file:$SERIAL"
  -daemonize -pidfile "$PID")

if [ "$FW" = bios ]; then
  if [ "$BOOTMODE" = install ]; then
    qemu-system-x86_64 "${COMMON[@]}" \
      -drive file="$DISK",if=virtio,format=qcow2 \
      -drive file="$ISO",media=cdrom,readonly=on \
      -boot "once=d,menu=off" \
      -nic user,model=virtio-net-pci,hostfwd=tcp::2228-:22
  else
    qemu-system-x86_64 "${COMMON[@]}" \
      -drive file="$DISK",if=virtio,format=qcow2 -boot c \
      -nic user,model=virtio-net-pci,hostfwd=tcp::2228-:22
  fi
else
  # fresh NVRAM copy per test run (preserve across disk boots)
  VARS="$D/OVMF_VARS-$NAME.fd"
  if [ ! -f "$VARS" ]; then cp -f "$OVMF/OVMF_VARS.4m.fd" "$VARS"; fi
  if [ "$BOOTMODE" = install ]; then
    qemu-system-x86_64 "${COMMON[@]}" \
      -drive if=pflash,format=raw,readonly=on,file="$OVMF/OVMF_CODE.4m.fd" \
      -drive if=pflash,format=raw,file="$VARS" \
      -drive file="$DISK",if=virtio,format=qcow2 \
      -drive file="$ISO",media=cdrom,readonly=on \
      -boot "once=d,menu=off" \
      -nic user,model=virtio-net-pci,hostfwd=tcp::2228-:22
  else
    qemu-system-x86_64 "${COMMON[@]}" \
      -drive if=pflash,format=raw,readonly=on,file="$OVMF/OVMF_CODE.4m.fd" \
      -drive if=pflash,format=raw,file="$VARS" \
      -drive file="$DISK",if=virtio,format=qcow2 -boot c \
      -nic user,model=virtio-net-pci,hostfwd=tcp::2228-:22
  fi
fi
echo "$NAME: VNC localhost::$N QMP $QMP serial $SERIAL disk $DISK"
