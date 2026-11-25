# Ember Linux QA matrix — `dc8a064f87e1`

- Generated: `2026-11-25T22:46:40Z`
- ISO source path (at capture): `/home/user/ember/images/ember-live-amd64.iso`
- Tested immutable snapshot: `/home/user/ember/qa/iso/ember-live-amd64-dc8a064f87e1.iso`
- ISO size: `4,268,701,696` bytes (3.98 GiB)
- ISO mtime: `2026-11-25T16:04:27`
- ISO SHA-256: `dc8a064f87e15e05f95c77d9a810e6763d543f734b31376287906aa27b1f79b9`
- The build output may have been rebuilt after this snapshot was
  captured; QEMU booted the immutable snapshot, and its SHA above is
  the tested artifact.
- Harness: `tests/ember-qa.py` (QEMU/KVM, VNC, OCR-driven installer)
- Rules: one VM at a time; no test is weakened to pass. Product
  failures are recorded as FAIL. BLOCKED means the ISO does not expose
  the feature under test, not that it passed.

## Result summary

| Test | Firmware | Desktop | Filesystem | Install | Login | Terminal | Ping | Status | Time |
|---|---|---|---|---|---|---|---|---|---|
| bios-openbox-ext4 | bios | openbox | ext4 | FAIL | — | — | — | **FAIL** | 0.5m |
| uefi-openbox-ext4 | uefi | openbox | ext4 | FAIL | — | — | — | **FAIL** | 0.7m |
| bios-xfce-ext4 | bios | xfce | ext4 | FAIL | — | — | — | **FAIL** | 0.5m |
| bios-kde-ext4 | bios | kde | ext4 | FAIL | — | — | — | **FAIL** | 0.5m |
| bios-server-ext4 | bios | server | ext4 | FAIL | — | — | — | **FAIL** | 0.5m |
| uefi-xfce-ext4 | uefi | xfce | ext4 | FAIL | — | — | — | **FAIL** | 0.6m |
| uefi-kde-ext4 | uefi | kde | ext4 | FAIL | — | — | — | **FAIL** | 0.6m |
| uefi-server-ext4 | uefi | server | ext4 | FAIL | — | — | — | **FAIL** | 0.7m |
| bios-gnome-ext4 | bios | gnome | ext4 | FAIL | — | — | — | **FAIL** | 0.8m |
| bios-cinnamon-ext4 | bios | cinnamon | ext4 | FAIL | — | — | — | **FAIL** | 0.9m |
| bios-mate-ext4 | bios | mate | ext4 | FAIL | — | — | — | **FAIL** | 0.7m |
| bios-lxqt-ext4 | bios | lxqt | ext4 | FAIL | — | — | — | **FAIL** | 0.6m |
| bios-i3-ext4 | bios | i3 | ext4 | FAIL | — | — | — | **FAIL** | 0.5m |
| bios-sway-ext4 | bios | sway | ext4 | FAIL | — | — | — | **FAIL** | 0.5m |
| bios-hyprland-ext4 | bios | hyprland | ext4 | FAIL | — | — | — | **FAIL** | 0.5m |
| bios-fluxbox-ext4 | bios | fluxbox | ext4 | FAIL | — | — | — | **FAIL** | 0.5m |
| bios-icewm-ext4 | bios | icewm | ext4 | FAIL | — | — | — | **FAIL** | 0.5m |
| uefi-gnome-ext4 | uefi | gnome | ext4 | FAIL | — | — | — | **FAIL** | 0.7m |
| uefi-cinnamon-ext4 | uefi | cinnamon | ext4 | FAIL | — | — | — | **FAIL** | 0.7m |
| uefi-mate-ext4 | uefi | mate | ext4 | FAIL | — | — | — | **FAIL** | 0.7m |
| uefi-lxqt-ext4 | uefi | lxqt | ext4 | FAIL | — | — | — | **FAIL** | 0.7m |
| uefi-i3-ext4 | uefi | i3 | ext4 | FAIL | — | — | — | **FAIL** | 0.7m |
| uefi-sway-ext4 | uefi | sway | ext4 | — | — | — | — | NOT RUN | — |
| uefi-hyprland-ext4 | uefi | hyprland | ext4 | — | — | — | — | NOT RUN | — |
| uefi-fluxbox-ext4 | uefi | fluxbox | ext4 | — | — | — | — | NOT RUN | — |
| uefi-icewm-ext4 | uefi | icewm | ext4 | — | — | — | — | NOT RUN | — |
| bios-openbox-btrfs | bios | openbox | btrfs | — | — | — | — | NOT RUN | — |
| bios-openbox-xfs | bios | openbox | xfs | — | — | — | — | NOT RUN | — |
| bios-openbox-f2fs | bios | openbox | f2fs | — | — | — | — | NOT RUN | — |
| uefi-openbox-btrfs | uefi | openbox | btrfs | — | — | — | — | NOT RUN | — |
| uefi-openbox-xfs | uefi | openbox | xfs | — | — | — | — | NOT RUN | — |
| uefi-openbox-f2fs | uefi | openbox | f2fs | — | — | — | — | NOT RUN | — |
| bios-openbox-luks | bios | openbox | ext4+LUKS | — | — | — | — | NOT RUN | — |
| uefi-openbox-luks | uefi | openbox | ext4+LUKS | — | — | — | — | NOT RUN | — |
| bios-openbox-lvm | bios | openbox | ext4 | — | — | — | — | NOT RUN | — |
| uefi-openbox-lvm | uefi | openbox | ext4 | — | — | — | — | NOT RUN | — |
| uefi-openbox-secureboot | uefi | openbox | ext4 | — | — | — | — | NOT RUN | — |
| bios-openbox-netfault | bios | openbox | ext4 | — | — | — | — | NOT RUN | — |
| uefi-openbox-netfault | uefi | openbox | ext4 | — | — | — | — | NOT RUN | — |
| bios-openbox-worldupdate | bios | openbox | ext4 | — | — | — | — | NOT RUN | — |

Executed: **FAIL** 22

> **Global blocker:** Calamares fails during initialization before the
> Welcome page (`Calamares Initialization Failed`, missing
> `shellprocess@postinstall`). No desktop package install, disk boot, login,
> terminal, or ping can start for any chooser entry. Rows below marked
> NOT RUN are blocked by this installer defect, not skipped to make a test pass.
>
> Desktop rows attempted: **22/26**; all 22 completed rows hit this same failure.
> The remaining desktop rows cannot reach the chooser either; they are NOT RUN rather than guessed.

**Root cause evidence:** the tested ISO's `etc/calamares/modules/postinstall.conf` does not parse as YAML, so Calamares cannot load `shellprocess@postinstall`:

```
while scanning a simple key   in "<unicode string>", line 62, column 1:     ssh-ed25519 AAAAC3NzaC1lZDI1NTE5 ...      ^
```

## Product failures / blockers

- **Global — Calamares initialization failure** in 22 executed row(s): `bios-openbox-ext4`, `uefi-openbox-ext4`, `bios-xfce-ext4`, `bios-kde-ext4`, `bios-server-ext4`, `uefi-xfce-ext4`, `uefi-kde-ext4`, `uefi-server-ext4`, `bios-gnome-ext4`, `bios-cinnamon-ext4`, `bios-mate-ext4`, `bios-lxqt-ext4`, `bios-i3-ext4`, `bios-sway-ext4`, `bios-hyprland-ext4`, `bios-fluxbox-ext4`, `bios-icewm-ext4`, `uefi-gnome-ext4`, `uefi-cinnamon-ext4`, `uefi-mate-ext4`, `uefi-lxqt-ext4`, `uefi-i3-ext4`
  - module `shellprocess@postinstall` could not be loaded; no installer page after startup was reachable

## Per-test evidence

### bios-openbox-ext4 — FAIL

- Run dir: `/home/user/ember/qa/runs/20261125-bios-openbox-ext4`
- Firmware: `bios`; desktop: `openbox`; filesystem: `ext4`; LUKS: `False`; LVM: `False`; Secure Boot: `False`
- Started/finished: `2026-11-25T22:21:32Z` → `2026-11-25T22:22:03Z`
- Error: **TestFailure** (install): Calamares Initialization Failed before the Welcome page; module `shellprocess@postinstall` could not be loaded

| Check | Result | Detail |
|---|---|---|
| live_boot_installer | FAIL | Calamares initialization failed before the Welcome page |

Screenshots: `/home/user/ember/qa/runs/20261125-bios-openbox-ext4/screenshots`

Logs: [serial_install](qa/runs/20261125-bios-openbox-ext4/serial-install.log), [qmp_install](qa/runs/20261125-bios-openbox-ext4/qmp-install.log)

![installer-init-failed.png](qa/runs/20261125-bios-openbox-ext4/screenshots/installer-init-failed.png)


### uefi-openbox-ext4 — FAIL

- Run dir: `/home/user/ember/qa/runs/20261125-uefi-openbox-ext4`
- Firmware: `uefi`; desktop: `openbox`; filesystem: `ext4`; LUKS: `False`; LVM: `False`; Secure Boot: `False`
- Started/finished: `2026-11-25T22:22:12Z` → `2026-11-25T22:22:53Z`
- Error: **TestFailure** (install): Calamares Initialization Failed before the Welcome page; module `shellprocess@postinstall` could not be loaded

| Check | Result | Detail |
|---|---|---|
| live_boot_installer | FAIL | Calamares initialization failed before the Welcome page |

Screenshots: `/home/user/ember/qa/runs/20261125-uefi-openbox-ext4/screenshots`

Logs: [serial_install](qa/runs/20261125-uefi-openbox-ext4/serial-install.log), [qmp_install](qa/runs/20261125-uefi-openbox-ext4/qmp-install.log)

![installer-init-failed.png](qa/runs/20261125-uefi-openbox-ext4/screenshots/installer-init-failed.png)


### bios-xfce-ext4 — FAIL

- Run dir: `/home/user/ember/qa/runs/20261125-bios-xfce-ext4`
- Firmware: `bios`; desktop: `xfce`; filesystem: `ext4`; LUKS: `False`; LVM: `False`; Secure Boot: `False`
- Started/finished: `2026-11-25T22:24:14Z` → `2026-11-25T22:24:41Z`
- Error: **TestFailure** (install): Calamares Initialization Failed before the Welcome page; module `shellprocess@postinstall` could not be loaded

| Check | Result | Detail |
|---|---|---|
| live_boot_installer | FAIL | Calamares initialization failed before Welcome; could not load shellprocess@postinstall |

Screenshots: `/home/user/ember/qa/runs/20261125-bios-xfce-ext4/screenshots`

Logs: [serial_install](qa/runs/20261125-bios-xfce-ext4/serial-install.log), [qmp_install](qa/runs/20261125-bios-xfce-ext4/qmp-install.log)

![installer-init-failed.png](qa/runs/20261125-bios-xfce-ext4/screenshots/installer-init-failed.png)


### bios-kde-ext4 — FAIL

- Run dir: `/home/user/ember/qa/runs/20261125-bios-kde-ext4`
- Firmware: `bios`; desktop: `kde`; filesystem: `ext4`; LUKS: `False`; LVM: `False`; Secure Boot: `False`
- Started/finished: `2026-11-25T22:24:41Z` → `2026-11-25T22:25:08Z`
- Error: **TestFailure** (install): Calamares Initialization Failed before the Welcome page; module `shellprocess@postinstall` could not be loaded

| Check | Result | Detail |
|---|---|---|
| live_boot_installer | FAIL | Calamares initialization failed before Welcome; could not load shellprocess@postinstall |

Screenshots: `/home/user/ember/qa/runs/20261125-bios-kde-ext4/screenshots`

Logs: [serial_install](qa/runs/20261125-bios-kde-ext4/serial-install.log), [qmp_install](qa/runs/20261125-bios-kde-ext4/qmp-install.log)

![installer-init-failed.png](qa/runs/20261125-bios-kde-ext4/screenshots/installer-init-failed.png)


### bios-server-ext4 — FAIL

- Run dir: `/home/user/ember/qa/runs/20261125-bios-server-ext4`
- Firmware: `bios`; desktop: `server`; filesystem: `ext4`; LUKS: `False`; LVM: `False`; Secure Boot: `False`
- Started/finished: `2026-11-25T22:25:08Z` → `2026-11-25T22:25:35Z`
- Error: **TestFailure** (install): Calamares Initialization Failed before the Welcome page; module `shellprocess@postinstall` could not be loaded

| Check | Result | Detail |
|---|---|---|
| live_boot_installer | FAIL | Calamares initialization failed before Welcome; could not load shellprocess@postinstall |

Screenshots: `/home/user/ember/qa/runs/20261125-bios-server-ext4/screenshots`

Logs: [serial_install](qa/runs/20261125-bios-server-ext4/serial-install.log), [qmp_install](qa/runs/20261125-bios-server-ext4/qmp-install.log)

![installer-init-failed.png](qa/runs/20261125-bios-server-ext4/screenshots/installer-init-failed.png)


### uefi-xfce-ext4 — FAIL

- Run dir: `/home/user/ember/qa/runs/20261125-uefi-xfce-ext4`
- Firmware: `uefi`; desktop: `xfce`; filesystem: `ext4`; LUKS: `False`; LVM: `False`; Secure Boot: `False`
- Started/finished: `2026-11-25T22:25:36Z` → `2026-11-25T22:26:13Z`
- Error: **TestFailure** (install): Calamares Initialization Failed before the Welcome page; module `shellprocess@postinstall` could not be loaded

| Check | Result | Detail |
|---|---|---|
| live_boot_installer | FAIL | Calamares initialization failed before Welcome; could not load shellprocess@postinstall |

Screenshots: `/home/user/ember/qa/runs/20261125-uefi-xfce-ext4/screenshots`

Logs: [serial_install](qa/runs/20261125-uefi-xfce-ext4/serial-install.log), [qmp_install](qa/runs/20261125-uefi-xfce-ext4/qmp-install.log)

![installer-init-failed.png](qa/runs/20261125-uefi-xfce-ext4/screenshots/installer-init-failed.png)


### uefi-kde-ext4 — FAIL

- Run dir: `/home/user/ember/qa/runs/20261125-uefi-kde-ext4`
- Firmware: `uefi`; desktop: `kde`; filesystem: `ext4`; LUKS: `False`; LVM: `False`; Secure Boot: `False`
- Started/finished: `2026-11-25T22:26:13Z` → `2026-11-25T22:26:50Z`
- Error: **TestFailure** (install): Calamares Initialization Failed before the Welcome page; module `shellprocess@postinstall` could not be loaded

| Check | Result | Detail |
|---|---|---|
| live_boot_installer | FAIL | Calamares initialization failed before Welcome; could not load shellprocess@postinstall |

Screenshots: `/home/user/ember/qa/runs/20261125-uefi-kde-ext4/screenshots`

Logs: [serial_install](qa/runs/20261125-uefi-kde-ext4/serial-install.log), [qmp_install](qa/runs/20261125-uefi-kde-ext4/qmp-install.log)

![installer-init-failed.png](qa/runs/20261125-uefi-kde-ext4/screenshots/installer-init-failed.png)


### uefi-server-ext4 — FAIL

- Run dir: `/home/user/ember/qa/runs/20261125-uefi-server-ext4`
- Firmware: `uefi`; desktop: `server`; filesystem: `ext4`; LUKS: `False`; LVM: `False`; Secure Boot: `False`
- Started/finished: `2026-11-25T22:26:50Z` → `2026-11-25T22:27:31Z`
- Error: **TestFailure** (install): Calamares Initialization Failed before the Welcome page; module `shellprocess@postinstall` could not be loaded

| Check | Result | Detail |
|---|---|---|
| live_boot_installer | FAIL | Calamares initialization failed before Welcome; could not load shellprocess@postinstall |

Screenshots: `/home/user/ember/qa/runs/20261125-uefi-server-ext4/screenshots`

Logs: [serial_install](qa/runs/20261125-uefi-server-ext4/serial-install.log), [qmp_install](qa/runs/20261125-uefi-server-ext4/qmp-install.log)

![installer-init-failed.png](qa/runs/20261125-uefi-server-ext4/screenshots/installer-init-failed.png)


### bios-gnome-ext4 — FAIL

- Run dir: `/home/user/ember/qa/runs/20261125-bios-gnome-ext4`
- Firmware: `bios`; desktop: `gnome`; filesystem: `ext4`; LUKS: `False`; LVM: `False`; Secure Boot: `False`
- Started/finished: `2026-11-25T22:29:46Z` → `2026-11-25T22:30:33Z`
- Error: **TestFailure** (install): Calamares Initialization Failed before the Welcome page; module `shellprocess@postinstall` could not be loaded

| Check | Result | Detail |
|---|---|---|
| live_boot_installer | FAIL | Calamares initialization failed before Welcome; could not load shellprocess@postinstall |

Screenshots: `/home/user/ember/qa/runs/20261125-bios-gnome-ext4/screenshots`

Logs: [serial_install](qa/runs/20261125-bios-gnome-ext4/serial-install.log), [qmp_install](qa/runs/20261125-bios-gnome-ext4/qmp-install.log)

![installer-init-failed.png](qa/runs/20261125-bios-gnome-ext4/screenshots/installer-init-failed.png)


### bios-cinnamon-ext4 — FAIL

- Run dir: `/home/user/ember/qa/runs/20261125-bios-cinnamon-ext4`
- Firmware: `bios`; desktop: `cinnamon`; filesystem: `ext4`; LUKS: `False`; LVM: `False`; Secure Boot: `False`
- Started/finished: `2026-11-25T22:30:34Z` → `2026-11-25T22:31:26Z`
- Error: **TestFailure** (install): Calamares Initialization Failed before the Welcome page; module `shellprocess@postinstall` could not be loaded

| Check | Result | Detail |
|---|---|---|
| live_boot_installer | FAIL | Calamares initialization failed before Welcome; could not load shellprocess@postinstall |

Screenshots: `/home/user/ember/qa/runs/20261125-bios-cinnamon-ext4/screenshots`

Logs: [serial_install](qa/runs/20261125-bios-cinnamon-ext4/serial-install.log), [qmp_install](qa/runs/20261125-bios-cinnamon-ext4/qmp-install.log)

![installer-init-failed.png](qa/runs/20261125-bios-cinnamon-ext4/screenshots/installer-init-failed.png)


### bios-mate-ext4 — FAIL

- Run dir: `/home/user/ember/qa/runs/20261125-bios-mate-ext4`
- Firmware: `bios`; desktop: `mate`; filesystem: `ext4`; LUKS: `False`; LVM: `False`; Secure Boot: `False`
- Started/finished: `2026-11-25T22:31:27Z` → `2026-11-25T22:32:10Z`
- Error: **TestFailure** (install): Calamares Initialization Failed before the Welcome page; module `shellprocess@postinstall` could not be loaded

| Check | Result | Detail |
|---|---|---|
| live_boot_installer | FAIL | Calamares initialization failed before Welcome; could not load shellprocess@postinstall |

Screenshots: `/home/user/ember/qa/runs/20261125-bios-mate-ext4/screenshots`

Logs: [serial_install](qa/runs/20261125-bios-mate-ext4/serial-install.log), [qmp_install](qa/runs/20261125-bios-mate-ext4/qmp-install.log)

![installer-init-failed.png](qa/runs/20261125-bios-mate-ext4/screenshots/installer-init-failed.png)


### bios-lxqt-ext4 — FAIL

- Run dir: `/home/user/ember/qa/runs/20261125-bios-lxqt-ext4`
- Firmware: `bios`; desktop: `lxqt`; filesystem: `ext4`; LUKS: `False`; LVM: `False`; Secure Boot: `False`
- Started/finished: `2026-11-25T22:32:11Z` → `2026-11-25T22:32:47Z`
- Error: **TestFailure** (install): Calamares Initialization Failed before the Welcome page; module `shellprocess@postinstall` could not be loaded

| Check | Result | Detail |
|---|---|---|
| live_boot_installer | FAIL | Calamares initialization failed before Welcome; could not load shellprocess@postinstall |

Screenshots: `/home/user/ember/qa/runs/20261125-bios-lxqt-ext4/screenshots`

Logs: [serial_install](qa/runs/20261125-bios-lxqt-ext4/serial-install.log), [qmp_install](qa/runs/20261125-bios-lxqt-ext4/qmp-install.log)

![installer-init-failed.png](qa/runs/20261125-bios-lxqt-ext4/screenshots/installer-init-failed.png)


### bios-i3-ext4 — FAIL

- Run dir: `/home/user/ember/qa/runs/20261125-bios-i3-ext4`
- Firmware: `bios`; desktop: `i3`; filesystem: `ext4`; LUKS: `False`; LVM: `False`; Secure Boot: `False`
- Started/finished: `2026-11-25T22:32:47Z` → `2026-11-25T22:33:14Z`
- Error: **TestFailure** (install): Calamares Initialization Failed before the Welcome page; module `shellprocess@postinstall` could not be loaded

| Check | Result | Detail |
|---|---|---|
| live_boot_installer | FAIL | Calamares initialization failed before Welcome; could not load shellprocess@postinstall |

Screenshots: `/home/user/ember/qa/runs/20261125-bios-i3-ext4/screenshots`

Logs: [serial_install](qa/runs/20261125-bios-i3-ext4/serial-install.log), [qmp_install](qa/runs/20261125-bios-i3-ext4/qmp-install.log)

![installer-init-failed.png](qa/runs/20261125-bios-i3-ext4/screenshots/installer-init-failed.png)


### bios-sway-ext4 — FAIL

- Run dir: `/home/user/ember/qa/runs/20261125-bios-sway-ext4`
- Firmware: `bios`; desktop: `sway`; filesystem: `ext4`; LUKS: `False`; LVM: `False`; Secure Boot: `False`
- Started/finished: `2026-11-25T22:33:14Z` → `2026-11-25T22:33:41Z`
- Error: **TestFailure** (install): Calamares Initialization Failed before the Welcome page; module `shellprocess@postinstall` could not be loaded

| Check | Result | Detail |
|---|---|---|
| live_boot_installer | FAIL | Calamares initialization failed before Welcome; could not load shellprocess@postinstall |

Screenshots: `/home/user/ember/qa/runs/20261125-bios-sway-ext4/screenshots`

Logs: [serial_install](qa/runs/20261125-bios-sway-ext4/serial-install.log), [qmp_install](qa/runs/20261125-bios-sway-ext4/qmp-install.log)

![installer-init-failed.png](qa/runs/20261125-bios-sway-ext4/screenshots/installer-init-failed.png)


### bios-hyprland-ext4 — FAIL

- Run dir: `/home/user/ember/qa/runs/20261125-bios-hyprland-ext4`
- Firmware: `bios`; desktop: `hyprland`; filesystem: `ext4`; LUKS: `False`; LVM: `False`; Secure Boot: `False`
- Started/finished: `2026-11-25T22:33:42Z` → `2026-11-25T22:34:09Z`
- Error: **TestFailure** (install): Calamares Initialization Failed before the Welcome page; module `shellprocess@postinstall` could not be loaded

| Check | Result | Detail |
|---|---|---|
| live_boot_installer | FAIL | Calamares initialization failed before Welcome; could not load shellprocess@postinstall |

Screenshots: `/home/user/ember/qa/runs/20261125-bios-hyprland-ext4/screenshots`

Logs: [serial_install](qa/runs/20261125-bios-hyprland-ext4/serial-install.log), [qmp_install](qa/runs/20261125-bios-hyprland-ext4/qmp-install.log)

![installer-init-failed.png](qa/runs/20261125-bios-hyprland-ext4/screenshots/installer-init-failed.png)


### bios-fluxbox-ext4 — FAIL

- Run dir: `/home/user/ember/qa/runs/20261125-bios-fluxbox-ext4`
- Firmware: `bios`; desktop: `fluxbox`; filesystem: `ext4`; LUKS: `False`; LVM: `False`; Secure Boot: `False`
- Started/finished: `2026-11-25T22:34:09Z` → `2026-11-25T22:34:36Z`
- Error: **TestFailure** (install): Calamares Initialization Failed before the Welcome page; module `shellprocess@postinstall` could not be loaded

| Check | Result | Detail |
|---|---|---|
| live_boot_installer | FAIL | Calamares initialization failed before Welcome; could not load shellprocess@postinstall |

Screenshots: `/home/user/ember/qa/runs/20261125-bios-fluxbox-ext4/screenshots`

Logs: [serial_install](qa/runs/20261125-bios-fluxbox-ext4/serial-install.log), [qmp_install](qa/runs/20261125-bios-fluxbox-ext4/qmp-install.log)

![installer-init-failed.png](qa/runs/20261125-bios-fluxbox-ext4/screenshots/installer-init-failed.png)


### bios-icewm-ext4 — FAIL

- Run dir: `/home/user/ember/qa/runs/20261125-bios-icewm-ext4`
- Firmware: `bios`; desktop: `icewm`; filesystem: `ext4`; LUKS: `False`; LVM: `False`; Secure Boot: `False`
- Started/finished: `2026-11-25T22:34:36Z` → `2026-11-25T22:35:03Z`
- Error: **TestFailure** (install): Calamares Initialization Failed before the Welcome page; module `shellprocess@postinstall` could not be loaded

| Check | Result | Detail |
|---|---|---|
| live_boot_installer | FAIL | Calamares initialization failed before Welcome; could not load shellprocess@postinstall |

Screenshots: `/home/user/ember/qa/runs/20261125-bios-icewm-ext4/screenshots`

Logs: [serial_install](qa/runs/20261125-bios-icewm-ext4/serial-install.log), [qmp_install](qa/runs/20261125-bios-icewm-ext4/qmp-install.log)

![installer-init-failed.png](qa/runs/20261125-bios-icewm-ext4/screenshots/installer-init-failed.png)


### uefi-gnome-ext4 — FAIL

- Run dir: `/home/user/ember/qa/runs/20261125-uefi-gnome-ext4`
- Firmware: `uefi`; desktop: `gnome`; filesystem: `ext4`; LUKS: `False`; LVM: `False`; Secure Boot: `False`
- Started/finished: `2026-11-25T22:36:13Z` → `2026-11-25T22:36:54Z`
- Error: **TestFailure** (install): Calamares Initialization Failed before the Welcome page; module `shellprocess@postinstall` could not be loaded

| Check | Result | Detail |
|---|---|---|
| live_boot_installer | FAIL | Calamares initialization failed before Welcome; could not load shellprocess@postinstall |

Screenshots: `/home/user/ember/qa/runs/20261125-uefi-gnome-ext4/screenshots`

Logs: [serial_install](qa/runs/20261125-uefi-gnome-ext4/serial-install.log), [qmp_install](qa/runs/20261125-uefi-gnome-ext4/qmp-install.log)

![installer-init-failed.png](qa/runs/20261125-uefi-gnome-ext4/screenshots/installer-init-failed.png)


### uefi-cinnamon-ext4 — FAIL

- Run dir: `/home/user/ember/qa/runs/20261125-uefi-cinnamon-ext4`
- Firmware: `uefi`; desktop: `cinnamon`; filesystem: `ext4`; LUKS: `False`; LVM: `False`; Secure Boot: `False`
- Started/finished: `2026-11-25T22:36:54Z` → `2026-11-25T22:37:37Z`
- Error: **TestFailure** (install): Calamares Initialization Failed before the Welcome page; module `shellprocess@postinstall` could not be loaded

| Check | Result | Detail |
|---|---|---|
| live_boot_installer | FAIL | Calamares initialization failed before Welcome; could not load shellprocess@postinstall |

Screenshots: `/home/user/ember/qa/runs/20261125-uefi-cinnamon-ext4/screenshots`

Logs: [serial_install](qa/runs/20261125-uefi-cinnamon-ext4/serial-install.log), [qmp_install](qa/runs/20261125-uefi-cinnamon-ext4/qmp-install.log)

![installer-init-failed.png](qa/runs/20261125-uefi-cinnamon-ext4/screenshots/installer-init-failed.png)


### uefi-mate-ext4 — FAIL

- Run dir: `/home/user/ember/qa/runs/20261125-uefi-mate-ext4`
- Firmware: `uefi`; desktop: `mate`; filesystem: `ext4`; LUKS: `False`; LVM: `False`; Secure Boot: `False`
- Started/finished: `2026-11-25T22:37:37Z` → `2026-11-25T22:38:17Z`
- Error: **TestFailure** (install): Calamares Initialization Failed before the Welcome page; module `shellprocess@postinstall` could not be loaded

| Check | Result | Detail |
|---|---|---|
| live_boot_installer | FAIL | Calamares initialization failed before Welcome; could not load shellprocess@postinstall |

Screenshots: `/home/user/ember/qa/runs/20261125-uefi-mate-ext4/screenshots`

Logs: [serial_install](qa/runs/20261125-uefi-mate-ext4/serial-install.log), [qmp_install](qa/runs/20261125-uefi-mate-ext4/qmp-install.log)

![installer-init-failed.png](qa/runs/20261125-uefi-mate-ext4/screenshots/installer-init-failed.png)


### uefi-lxqt-ext4 — FAIL

- Run dir: `/home/user/ember/qa/runs/20261125-uefi-lxqt-ext4`
- Firmware: `uefi`; desktop: `lxqt`; filesystem: `ext4`; LUKS: `False`; LVM: `False`; Secure Boot: `False`
- Started/finished: `2026-11-25T22:38:18Z` → `2026-11-25T22:39:00Z`
- Error: **TestFailure** (install): Calamares Initialization Failed before the Welcome page; module `shellprocess@postinstall` could not be loaded

| Check | Result | Detail |
|---|---|---|
| live_boot_installer | FAIL | Calamares initialization failed before Welcome; could not load shellprocess@postinstall |

Screenshots: `/home/user/ember/qa/runs/20261125-uefi-lxqt-ext4/screenshots`

Logs: [serial_install](qa/runs/20261125-uefi-lxqt-ext4/serial-install.log), [qmp_install](qa/runs/20261125-uefi-lxqt-ext4/qmp-install.log)

![installer-init-failed.png](qa/runs/20261125-uefi-lxqt-ext4/screenshots/installer-init-failed.png)


### uefi-i3-ext4 — FAIL

- Run dir: `/home/user/ember/qa/runs/20261125-uefi-i3-ext4`
- Firmware: `uefi`; desktop: `i3`; filesystem: `ext4`; LUKS: `False`; LVM: `False`; Secure Boot: `False`
- Started/finished: `2026-11-25T22:39:00Z` → `2026-11-25T22:39:41Z`
- Error: **TestFailure** (install): Calamares Initialization Failed before the Welcome page; module `shellprocess@postinstall` could not be loaded

| Check | Result | Detail |
|---|---|---|
| live_boot_installer | FAIL | Calamares initialization failed before Welcome; could not load shellprocess@postinstall |

Screenshots: `/home/user/ember/qa/runs/20261125-uefi-i3-ext4/screenshots`

Logs: [serial_install](qa/runs/20261125-uefi-i3-ext4/serial-install.log), [qmp_install](qa/runs/20261125-uefi-i3-ext4/qmp-install.log)

![installer-init-failed.png](qa/runs/20261125-uefi-i3-ext4/screenshots/installer-init-failed.png)


## How to reproduce

```bash
cd /home/user/ember
tests/ember-qa.py run --test-id bios-openbox-ext4 --firmware bios --desktop openbox --iso /home/user/ember/qa/iso/ember-live-amd64-dc8a064f87e1.iso
tests/ember-qa.py run --test-id uefi-openbox-ext4 --firmware uefi --desktop openbox --iso /home/user/ember/qa/iso/ember-live-amd64-dc8a064f87e1.iso
tests/ember-qa.py report --iso /home/user/ember/qa/iso/ember-live-amd64-dc8a064f87e1.iso
```

See `tests/README.md` for the full matrix, filesystem/LUKS/LVM/
Secure Boot and network-fault commands.

