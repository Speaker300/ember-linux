# Ember Linux QA harness

Reusable, serialized QEMU/KVM test harness for Ember installer ISOs. It boots
the real ISO, drives Calamares over VNC exactly as a user would, boots the
installed disk, logs in, opens a terminal, and runs `ping`. It never edits the
ISO, the chroot, product configuration, or git history.

## Quick start

```bash
cd /home/user/ember
tests/inspect-iso.py                 # SHA, capabilities, desktop list
tests/ember-qa.py run --test-id bios-openbox-ext4 --firmware bios --desktop openbox
tests/ember-qa.py report
```

The full matrix (sequential, one VM at a time):

```bash
tests/run-matrix.py --group core          # 8 desktop/firmware rows
tests/run-matrix.py --group storage       # ext4/btrfs/xfs/f2fs rows
tests/run-matrix.py --group crypto        # LUKS/LVM rows
tests/run-matrix.py --group secureboot    # UEFI Secure Boot row
tests/run-matrix.py --group network       # link down/up rows
tests/run-matrix.py --group all
```

Every run prints its result and writes `qa/runs/<run>/result.json`. The
report is written to `qa/REPORT-<iso-sha8>.md`.

## Requirements

- `qemu-system-x86_64`, `qemu-img` (KVM enabled)
- `vncdotool` Python package (`python-vncdotool`)
- Pillow (`python-pillow`)
- `tesseract` plus the English data (`tesseract-data-eng` on Artix/Arch;
  `tesseract-ocr-eng` on Debian/Ubuntu)
- OVMF 4 MiB images at `/usr/share/edk2-ovmf/x64/`

Install the OCR data if reports show empty OCR:

```bash
sudo pacman -S --needed tesseract-data-eng
```

## Safety and ownership

- **One VM at a time.** `start` refuses if any `qemu-system-*` process exists,
  including one owned by another agent. `run-matrix.py` waits for the host to
  become idle (`--wait-host`, default 30 min). An explicit operator override,
  `EMBERQA_ALLOW_CONCURRENT=1`, exists for a single manual run when the host
  has spare capacity; it is never set by the matrix.
- **Only `tests/` and `qa/` are written.** Product files, the chroot, the ISO,
  and git are never touched.
- **Immutable ISO snapshot.** QEMU boots a verified copy at
  `qa/iso/ember-live-amd64-<sha12>.iso`. If the ISO is rebuilt while a test is
  running, the running test is unaffected and cannot see corrupted squashfs
  blocks. Without this, rewriting `images/ember-live-amd64.iso` underneath a
  guest causes `SQUASHFS error: zstd decompression failed` and the installer
  disappears mid-install (observed 2026-11-25).
- **Deterministic cleanup.** qcow2 disks are deleted at the end of every run
  unless `--keep-disk` is passed. Screenshots, serial logs, QMP logs, and
  `result.json` are kept. Old QA disks are also reclaimed automatically when
  free space is low.

## Ports

Allocated dynamically, checked for collisions:

| Resource | Range |
|---|---|
| VNC display | `:30` … `:99` (TCP 5930–5999), bound to `127.0.0.1` |
| hostfwd | TCP 2300–2399 (`guest :22`, reserved for future SSH checks) |

The actual ports are recorded in `qa/runs/<run>/vm.json`. Only one VM runs, so
there is no port churn during a test.

## What a run does

1. Verify ISO SHA-256 and create/reuse a verified snapshot.
2. Create a 24 GiB sparse qcow2 disk.
3. Boot the live ISO (BIOS or UEFI; optional Secure Boot OVMF).
4. Drive Calamares:
   - Welcome → Location → Keyboard → Stage 3 guide
   - Select Stage: `current-stage3-amd64-desktop-openrc` (or `-systemd` for GNOME)
   - Desktop chooser (13 entries in the current ISO)
   - Build configuration (make.conf editor): verify generated values, click
     **Suggest from hardware**, click **Validate**
   - Partitions: erase disk, select filesystem/swap/LUKS as requested
   - Users: `Gentoo User` / `gentoo` / host `gentoo-test` / password `embertest`
   - Summary → Install → confirmation
   - Wait for Calamares **All done.**; fail on a failure dialog, timeout, or
     QEMU death.
5. Stop the live VM (disk kept), boot the disk only.
6. Wait for the installed display manager / console, log in.
7. Open a terminal for the chosen desktop, run `ping -c 1 9.9.9.9`, and record
   the terminal output as a screenshot plus OCR text.
8. Check the desktop process and, for OpenRC desktops, `rc-status default`.
9. Optional post-login network fault: QMP link down → ping must fail → link up
   → ping must succeed.
10. Stop QEMU, delete the disk (unless `--keep-disk`), write `result.json` and
    update the report.

The password is intentionally simple (`embertest`) so VNC key delivery is
reliable. Credentials are recorded in each `result.json`.

## Manual debugging

Start a VM without running a test:

```bash
tests/ember-qa.py start debug-bios --firmware bios --boot install
tests/ember-qa.py shot debug-bios /tmp/boot.png
tests/ember-qa.py click debug-bios 1148 784
tests/ember-qa.py type debug-bios hello
tests/ember-qa.py key debug-bios return
tests/ember-qa.py net debug-bios down
tests/ember-qa.py net debug-bios up
tests/ember-qa.py stop debug-bios --clean-disk
```

`start` also accepts `--secure-boot` and `--iso PATH`. For a disk-only boot of a
kept disk, use `--boot disk`. The disk lives at
`qa/runs/<name>/disk.qcow2`.

If a test fails, keep the disk for inspection:

```bash
tests/ember-qa.py run --test-id debug-row --firmware bios --desktop openbox --keep-disk --name debug-keep
# inspect, then:
tests/ember-qa.py stop debug-keep --clean-disk
```

## Matrix rows

Desktop entries (current ISO): Openbox, Xfce, KDE Plasma, GNOME (systemd),
Cinnamon, MATE, LXQt, i3, Sway, Hyprland, Fluxbox, IceWM, Server.

`run-matrix.py --group core` covers the four original desktops on both
firmwares. `--group all` includes the storage, crypto, Secure Boot and network
rows defined in `tests/run-matrix.py`. Add a row there when the product adds a
new desktop; the report's intended-matrix table is in
`tests/lib/report.py`.

## Result semantics

- **PASS** — every assertion in the row passed.
- **FAIL** — a product or boot behavior failed; the error, phase, screenshot,
  serial log, and QMP log are in the run directory. Never converted to PASS.
- **BLOCKED** — the ISO does not expose the feature under test (for example a
  filesystem selector or LVM control that is not present). This is not a pass.
- **NOT RUN** — the report lists intended rows that were not executed.

The harness does not retry a failing install or login. The only retry is a
single `ping` retry for a transient QEMU slirp hiccup; the first failure is
preserved and the check detail says a retry was needed.

## Artifacts

```
qa/
  iso/ember-live-amd64-<sha12>.iso   verified immutable snapshot
  runs/<run>/
    meta.json          ISO identity, spec, credentials, start time
    result.json        final status, checks, phases, error, artifact paths
    status.log         timestamped phase/status lines
    driver.log         driver log
    screenshots/       every page, timeout, login, terminal, ping
    serial-install.log kernel/live serial output
    serial-disk.log    installed-system serial output
    qmp-install.log    QMP commands and replies
    qmp-disk.log
  REPORT-<sha8>.md     current matrix report
  matrix/              per-invocation matrix logs
```

Screenshots are real VNC captures; OCR text is saved beside each screenshot
(`*.txt`) when the driver read it.

## Filesystem / LUKS / LVM / Secure Boot / network notes

- **Filesystems**: the runner reads the ISO's `partition.conf` (read-only,
  through a loop-mounted squashfs) and refuses to run a non-ext4 row if the ISO
  does not list that filesystem. The driver uses the filesystem combo attached
  to “Erase disk”. A missing feature becomes BLOCKED, never a silent ext4 pass.
- **LUKS**: enables “Encrypt system”, enters the passphrase twice, and verifies
  the page state. On disk boot the driver handles GRUB/initramfs passphrase
  prompts before the login screen.
- **LVM**: Calamares exposes LVM only through **Manual partitioning**. The
  current automated driver does not fake an LVM install; the row is BLOCKED
  until a manual-partition driver is added. Do not mark it PASS from an ext4
  install.
- **Secure Boot**: boots `OVMF_CODE.secboot.4m.fd` with SMM and secure pflash.
  It records whether the ISO/installed chain boots. MOK enrollment at first
  boot is a product/user interaction and is not bypassed.
- **Network fault**: post-login QMP `set_link net0 off/on`; the check requires a
  failed ping while down and a successful ping after resume. Installer-phase
  link fault injection is reserved (`--fault-install`) but not enabled in the
  default matrix.

## Re-running after a new ISO

```bash
cd /home/user/ember
tests/run-matrix.py --group core
tests/ember-qa.py report
```

The new ISO gets a new SHA-256 and a separate snapshot/report. Results from the
old SHA are never mixed into the new report. To generate a report for an older
snapshot explicitly:

```bash
tests/ember-qa.py report --iso qa/iso/ember-live-amd64-<oldsha12>.iso
```

## Troubleshooting

- **“another QEMU is already running”** — another agent/test is using the
  host. Wait, then rerun; do not kill their VM.
- **Installer did not appear** — inspect `screenshots/installer-not-found.png`
  and `serial-install.log`; often the ISO is corrupt or the host is out of
  memory.
- **Empty OCR** — install `tesseract-data-eng`; verify with
  `tesseract tests/.../shot.png stdout --psm 6`.
- **Report missing a run** — reports are per ISO SHA. Pass the snapshot with
  `--iso` if the build output has been replaced since the run.
- **Disk space** — `qa/iso` and `qa/runs/*/disk.qcow2` are the only large QA
  files. `tests/cleanup.py` removes old QA disks/snapshots; it never touches
  `images/`, `vm/`, product files, or git.
