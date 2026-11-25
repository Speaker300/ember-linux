# Ember Linux 1.0 “Cinder” — branding pack manifest

**Pack version:** 2026-11-25  
**Target product:** Ember Linux 1.0 “Cinder” (Gentoo-based, OpenRC)  
**Install root used for tests:** disposable `/tmp/opencode/ember-root*`, never the main chroot  
**Licence:** artwork/documentation CC BY-SA 4.0; scripts MIT. See
`licenses/NOTICE.md`.

Ember is an independent distribution built on Gentoo. It is not affiliated
with, sponsored by, or endorsed by the Gentoo Foundation. The pack does not
use the Gentoo Violet theme; all artwork and configuration here is original.

---

## 1. What this pack is

A coherent set of files that turns a stock Calamares/Gentoo/Openbox
installation into something that reads as a finished distribution:

- a single mark and wordmark, warm ember accent on a cool near-black base;
- wallpapers for 1080p and 1440p, plus login, GRUB and Plymouth art;
- a real Calamares component with five slideshow slides, a stage3 guide and a
  conservative dark stylesheet;
- GRUB, Plymouth and LightDM themes;
- Openbox, tint2, rofi, GTK, icon and cursor defaults;
- offline Welcome/About pages and desktop entries;
- distribution-quality installer copy;
- an idempotent integration script with backups.

---

## 2. Identity

| File | What it is |
|---|---|
| `identity/ember-mark.svg` | Primary transparent mark, 512×512 |
| `identity/ember-logo.svg` | Badge/icon version with dark squircle, 512×512 |
| `identity/ember-logo.png`, `ember-logo-{1024,512,256,128,64,48,32}.png` | Raster badge |
| `identity/ember-mark.png`, `ember-mark-{512,256,128,64,48,32}.png` | Raster mark |
| `identity/ember-wordmark.svg`, `ember-wordmark.png` | “ember” + “LINUX” wordmark (paths, no font dependency) |
| `identity/ember-wordmark-dark.svg`, `ember-wordmark-dark.png` | Wordmark for light backgrounds |
| `identity/ember-lockup.svg`, `ember-lockup.png` | Horizontal badge + wordmark |
| `identity/ember-lockup-dark.svg`, `ember-lockup-dark.png` | Lockup for light backgrounds |
| `identity/ember-mark-mono-{light,dark}.svg` | One-colour marks |
| `identity/ember-avatar-{512,256}.png` | Circular login avatar |
| `identity/ember-banner.png` | 1600×500 README/social banner |
| `identity/palette.json`, `palette.md` | Tokens, roles and WCAG contrast notes |

**Palette:** ink `#14171C`, basalt `#1B2027`, graphite `#262C36`, ash
`#A6AEBB`, frost `#F4F6F8`, ember `#F26A3D`, ember-deep `#D8432A`, amber
`#FFB35C`, sand `#FFD9A0`, teal `#3FA796`, success `#4CAF6E`, warning
`#E0A526`, danger `#E5484D`.

**Type:** Inter (OFL 1.1) shipped in `desktop/fonts/inter/`. Regular, Medium,
SemiBold, Bold, Italic and InterDisplay Bold. Noto Sans is a documented
fallback (present on most systems).

**Rules:** one accent per surface; frost on ink for primary text; ash for body;
ember only for focus, selection and the primary installer action; monochrome
mark allowed where colour is limited.

---

## 3. Wallpapers and session backgrounds

All are PNG, generated from original vector work by `tools/gen_wallpapers.py`.

| File | Size | Use |
|---|---|---|
| `wallpapers/1920x1080/ember-ridge-1920x1080.png` | 1920×1080 | Default desktop wallpaper |
| `wallpapers/2560x1440/ember-ridge-2560x1440.png` | 2560×1440 | Default desktop wallpaper |
| `wallpapers/1920x1080/ember-halo-1920x1080.png` | 1920×1080 | Alternate desktop wallpaper (eclipse motif) |
| `wallpapers/2560x1440/ember-halo-2560x1440.png` | 2560×1440 | Alternate |
| `wallpapers/1920x1080/ember-login-1920x1080.png` | 1920×1080 | LightDM background |
| `wallpapers/2560x1440/ember-login-2560x1440.png` | 2560×1440 | LightDM background, HiDPI |
| `wallpapers/1920x1080/ember-grub-1920x1080.png` | 1920×1080 | GRUB theme background |
| `wallpapers/1920x1080/ember-plymouth-1920x1080.png` | 1920×1080 | Plymouth background |
| `wallpapers/1600x1040/ember-calamares-1600x1040.png` | 1600×1040 | Source for the Calamares wallpaper |

The Calamares `wallpaper.png` is exactly **800×520** (the configured installer
window size) so it does not tile.

---

## 4. Calamares branding

Installed as `/usr/share/calamares/branding/ember/`. `componentName` is
`ember`, which must match the directory name — Calamares aborts if the two
differ. The install script therefore writes only the `ember` component and
patches `branding:` in `settings.conf`; do not copy this directory to
`.../branding/default` unless you also change `componentName` to `default`.

| File | Notes |
|---|---|
| `calamares/branding.desc` | Valid YAML; product name, version, URLs, palette, `slideshow: show.qml`, `slideshowAPI: 2` |
| `calamares/show.qml` | Five real Ember slides, timed at 11 s, dots, dark slide surface; API 2 `onActivate`/`onLeave` |
| `calamares/SlideArt.qml` | Reusable numbered art card used by the slides |
| `calamares/stage3guide.qml` | Two-card “Choose your foundation” page, loaded by `notesqml` via `qmlSearch: branding` |
| `calamares/stylesheet.qss` | Dark QSS: sidebar, buttons, form controls, tables, scrollbars, menus; next button ember |
| `calamares/ember-logo.png` | 256×256 product logo (sidebar, 80×80 display) |
| `calamares/ember-icon.png` | 256×256 window icon |
| `calamares/ember-mark.png` | 256×256 mark for slide art |
| `calamares/banner.png` | 460×64 welcome banner |
| `calamares/welcome.png` | 480×171 welcome lockup |
| `calamares/wallpaper.png` | 800×520 product wallpaper |
| `calamares/desktop-*.png` | Optional 640×400 desktop-chooser previews added during integration; not referenced by `branding.desc` |

Strings: `Ember Linux`, `Ember`, `1.0`, `1.0 "Cinder"`, `Ember 1.0`,
bootloader entry `Ember Linux`, URLs `https://emberlinux.org/…`.

Enable the matching welcome buttons by merging
`integration/welcome.conf.snippet` into the live `welcome.conf`; the current
file disables support/release/known-issue links, so the URLs exist in branding
but are not visible until that merge.

Slide headlines: “Setting up Ember Linux”, “Gentoo underneath. Ember on top.”,
“A desktop that gets out of the way”, “Boot with confidence”, “You’re almost
there”. No placeholder text; see `copy/installer-copy.md` for the full copy.

**QSS coverage:** the stylesheet deliberately avoids global
`QWidget { background-color }`. It styles `#mainApp`, buttons, inputs, tables,
tabs, group boxes, progress, scrollbars, menus and tooltips, and leaves the
content pages transparent so `productWallpaper` can show. This is the safest
dark palette for Calamares 3.4.

**Slideshow notes:** the QML sets `titleColor`, `textColor`, `fontFamily:
"Inter"` and a solid slide background, so it is readable even if the QSS or
wallpaper is missing. Art is QML geometry plus `ember-mark.png`; there are no
missing image references.

---

## 5. Boot experience

### GRUB

Installed as `/boot/grub/themes/ember/`; `/etc/default/grub` is set to:

```
GRUB_DISTRIBUTOR="Ember Linux"
GRUB_THEME="/boot/grub/themes/ember/theme.txt"
GRUB_TIMEOUT="5"
GRUB_TIMEOUT_STYLE="menu"
GRUB_GFXMODE="1920x1080,auto"
GRUB_GFXPAYLOAD_LINUX="keep"
```

Files: `boot/grub/theme.txt`, `background.png` (1920×1080), `logo.png`
(256×256), and the nine-slice sets `menu_*.png` / `select_*.png`. Menu labels
use GRUB’s built-in `Unifont Regular 16`, so no external `.pf2` is required.
The theme uses a left-hand menu panel, a badge on the right, an ember timeout
bar, and a one-line key hint.

### Plymouth

Installed as `/usr/share/plymouth/themes/ember/`; `ember.plymouth` uses
`ModuleName=script`. Assets: background 1920×1080, logo 220×220,
`progress_track.png`, 21 progress frames, 12 throbber frames.
`ember.script` uses only stable APIs: `Window.GetWidth/Height`, `Image`,
`Sprite`, `Image.Text`, `Plymouth.SetRefreshFunction`,
`Plymouth.SetBootProgressFunction`, `Plymouth.SetMessageFunction`. Layout is
proportional so it survives a firmware-to-KMS mode change.

`install-into-chroot.sh` writes `[Daemon] Theme=ember` to
`/etc/plymouth/plymouthd.conf` when Plymouth is present. Plymouth is **not in
the current package list**; see risks.

### LightDM

- `boot/lightdm/lightdm-gtk-greeter.conf` → `/etc/lightdm/`.
  Background `ember-login-1920x1080.png`, `theme-name=Ember-Greeter`,
  `icon-theme-name=Ember`, `cursor-theme-name=Ember`, Inter 11, bottom panel,
  clock, session and power indicators, default avatar.
- `boot/lightdm/99-ember.conf` → `/etc/lightdm/lightdm.conf.d/99-ember.conf`.
  Sets `greeter-session=lightdm-gtk-greeter` without touching the package’s
  `lightdm.conf`.
- `desktop/themes/Ember-Greeter/{index.theme,gtk-3.0/gtk.css}` →
  `/usr/share/themes/Ember-Greeter/`. Imports Adwaita dark, then styles
  `#login_window`, `#login_box`, `#user_image_border`, password/username
  entries, `#login_button`, `#message_label`, `#greeter_infobar`,
  `#panel_window` and `#power_window`.

SDDM is not shipped: all four desktop choices currently use LightDM. A
half-tested QML SDDM theme would be worse than no theme; add one only if the
display-manager choice changes.

**Live medium vs installed system.** The GRUB/Plymouth themes here are for the
installed system: the script installs them into the target and updates the
target's `/etc/default/grub`/`plymouthd.conf`. The live ISO's own GRUB menu and
initramfs are built separately by `scripts/rebuild-iso2.sh`/`iso-root`; this
pack does not edit those. If the live menu should be branded too, apply the
theme to the ISO's GRUB config as a separate build change.

---

## 6. Desktop defaults

| Area | Files | Installed to |
|---|---|---|
| Openbox theme | `desktop/themes/Ember/openbox-3/themerc` | `/usr/share/themes/Ember/openbox-3/` |
| Openbox config | `desktop/openbox/{rc.xml,menu.xml,autostart}` | `/etc/xdg/openbox/` and `/etc/skel/.config/openbox/` |
| tint2 | `desktop/tint2/tint2rc` | `/etc/xdg/tint2/` and `/etc/skel/.config/tint2/` |
| rofi | `desktop/rofi/{ember.rasi,config.rasi}` | `/usr/share/rofi/themes/ember.rasi`, `/etc/xdg/rofi/config.rasi`, `/etc/skel/.config/rofi/` |
| GTK theme | `desktop/themes/Ember/{index.theme,gtk-3.0/gtk.css}` | `/usr/share/themes/Ember/` |
| GTK settings | `desktop/gtk-3.0/settings.ini` | `/etc/gtk-3.0/` and `/etc/skel/.config/gtk-3.0/` |
| GTK2 fallback | `desktop/gtk-2.0/gtkrc` | `/etc/gtk-2.0/gtkrc` |
| Icons + cursors | `desktop/icons/Ember/` | `/usr/share/icons/Ember/` |
| Fonts | `desktop/fonts/inter/*.ttf` | `/usr/share/fonts/inter/` |
| Welcome app | `desktop/bin/ember-welcome`, `desktop/welcome/` | `/usr/local/bin/`, `/usr/share/ember/welcome/` |
| About app | `desktop/bin/ember-about` | `/usr/local/bin/` |
| Wallpaper setter | `desktop/bin/ember-wallpaper` | `/usr/local/bin/` |
| Desktop entries | `desktop/applications/ember-{welcome,about}.desktop` | `/usr/share/applications/` |
| Avatar | `desktop/pixmaps/ember-avatar.png` | `/usr/share/pixmaps/ember/ember-avatar.png` |

**Openbox:** 34 px tint2 bar, four named workspaces (Main/Web/Work/Media),
`Super+Enter` xterm, `Super+D` rofi drun, `Super+R` rofi run, `Super+E` Thunar,
`Super+B` Firefox, `Super+W` Welcome, arrow-key snapping, `Alt+Tab`, `Alt+F4`.
Right-click root opens the Ember menu. The theme uses built-in Openbox button
glyphs with ember hover/pressed states; close gets a red hover.

**tint2:** solid `#14171C` panel (transparency disabled so it stays readable
if picom is missing), 20 px launchers for Welcome/Firefox/Files/Terminal,
active-task pill, systray, Inter clock, tooltip. `nm-applet` and `picom` are
started from autostart when present.

**rofi:** 640 px rounded window, dark list with alternating rows, ember
selection, dark input bar, icon theme Ember, run/drun wording.

**Icons:** original 15-symbol line set at 16/24/32/48/64/128/256 plus
scalable SVGs, inheriting Papirus → Adwaita → hicolor. Covers Welcome, About,
browser, files, terminal, search, volume, network, settings, applications,
help, information, editor and shutdown.

**Cursors:** original Ember Xcursor theme, 15 shapes at 24/32/48 with 23
aliases (arrow, text, hand, resizes, move, not-allowed, progress), inheriting
Adwaita/breeze for anything else.

**Welcome page:** offline HTML at `/usr/share/ember/welcome/index.html`, with
real commands for updates, packages, NetworkManager, OpenRC, shortcuts,
workspace/desktop guidance, logs and the Gentoo Handbook link. `ember-welcome`
opens it in Firefox/Chromium/`xdg-open`, falls back to zenity/kdialog/xmessage,
then xterm, then stdout. `ember-about` shows live kernel/host/memory/disk
information in zenity/kdialog/HTML/xmessage.

---

## 7. Installer/first-boot copy

`copy/installer-copy.md` contains the canonical wording with exact strings for:

- welcome page, stage3 page, desktop chooser descriptions;
- summary heading/intro/checklist/warning/primary action;
- finish heading/body/next steps;
- error/help text and log locations;
- tone rules.

The stage3 and slideshow copy is already implemented in the QML. Calamares’
compiled-in “Finished” and error page strings cannot be replaced through
`branding.desc`; the finish copy is therefore used by the post-install Welcome
page and is ready for a distribution-specific finished page if the lead adds
one.

---

## 8. Integration script

`install-into-chroot.sh` (Bash, MIT) is idempotent and backs up every existing
file it replaces.

```bash
sudo ./install-into-chroot.sh --root /path/to/root [options]
```

Useful options:

```
--root DIR              target root (default /)
--dry-run               show changes, touch nothing
--quiet
--live-user NAME        also copy desktop defaults into /home/NAME
--os-release            write Ember /etc/os-release and /etc/issue
--default-session NAME  openbox|xfce|plasma|none for LightDM
--refresh-grub          run grub-mkconfig (root / only)
--refresh-initramfs     dracut/plymouth rebuild (root / only)
--no-grub --no-plymouth --no-lightdm --no-calamares
--no-fonts --no-icons --no-pack
```

**Idempotency:** files are compared with `cmp`, trees with `diff -qr`; if
identical, nothing is rewritten and no backup is made. A second run on a
branded root prints only “done”. Tested on a disposable root twice.

**Backups:** first differing version of each path goes to
`/var/backups/ember-branding/<timestamp>/<original path>`. One backup per path
per run. `--dry-run` writes nothing.

**Caches:** when `--root /`, the script runs `fc-cache`,
`gtk-update-icon-cache` and `update-desktop-database` if available. When
branding a mounted target from outside, run those inside the target chroot (or
let first boot build them).

### Live ISO integration (installer UI + live desktop)

The Calamares component must be in the live root before the ISO boots, not
only installed into the target. Two safe options:

```bash
# Minimal live branding: do not touch live GRUB/Plymouth/LightDM.
# --live-user gentoo also themes the live session while keeping the
# Calamares autostart (autostart-live).
./install-into-chroot.sh --root /home/user/ember/build/livegui-root \
  --no-grub --no-plymouth --no-lightdm --live-user gentoo --quiet

# Full live branding if you want the live session to match the target
./install-into-chroot.sh --root /home/user/ember/build/livegui-root \
  --live-user gentoo --quiet
```

The first form still installs Calamares branding, patches
`/etc/calamares/settings.conf` to `branding: ember`, installs the Openbox/GTK
defaults, themes the live `gentoo` home and copies the pack to
`<live-root>/usr/share/ember/branding-pack` for the target-side shellprocess.
When `/usr/bin/calamares` exists, the live user gets
`desktop/openbox/autostart-live`, which runs the Ember session then starts the
installer after three seconds; it does not silently drop the installer.

### Target integration with Calamares

`integration/calamares-emberbranding.conf` is a ready shellprocess config.
Add an instance to `settings.conf` and run it **after** the existing
`shellprocess@openrc` (that config writes stock Openbox files) and **before**
`dracut_gentoo`, `grubcfg` and `bootloader`:

```yaml
instances:
- id: emberbranding
  module: shellprocess
  config: emberbranding.conf

sequence:
- exec:
  ...
  - shellprocess@openrc
  - shellprocess@emberbranding
  - dracut_gentoo
  - grubcfg
  - bootloader
  ...
```

The sample runs with `dontChroot: true`, `--root ${ROOT}` and
`--live-user ${USER}`. Calamares expands `${USER}` from the users module; the
home copy is required because Calamares creates the user from the target's
stock `/etc/skel` before this shellprocess runs. It does not force a LightDM
session; add `--default-session openbox` only if every desktop choice is
Openbox.

### Manual target build (without Calamares)

```bash
sudo mount /dev/nvme0n1p2 /mnt/gentoo
sudo mount /dev/nvme0n1p1 /mnt/gentoo/boot/efi   # or /boot as appropriate
sudo ./install-into-chroot.sh --root /mnt/gentoo --live-user youruser
sudo arch-chroot /mnt/gentoo grub-mkconfig -o /boot/grub/grub.cfg
sudo arch-chroot /mnt/gentoo dracut -f
```

(Replace `arch-chroot` with the project’s `chroot-run.sh`; `/boot` must be
mounted where the target expects it.)

---

## 9. Packages needed for the full experience

The current Openbox package list already has Openbox, tint2, rofi, picom,
xterm, LightDM and the greeter. To make every menu entry, launcher and
fallback work, add:

| Package | Why |
|---|---|
| `www-client/firefox` (or `firefox-bin`) | Web Browser menu, Welcome page primary viewer |
| `xfce-base/thunar` | File Manager menu/launcher |
| `media-sound/pavucontrol` | Volume Control menu |
| `gnome-extra/nm-applet` | Network tray icon and menu entry |
| `media-gfx/feh` | Wallpaper setter (`ember-wallpaper` falls back to solid ink without it) |
| `x11-misc/zenity` | Welcome/About dialog fallback when no browser is installed |
| `x11-misc/lxappearance` | Settings menu entry (GTK theme/fonts) |
| `x11-themes/papirus-icon-theme` (optional) | Preferred fallback for app icons; Ember inherits it first |
| `sys-boot/plymouth` + dracut `plymouth` USE | Enables the Plymouth theme; not currently installed |
| `media-gfx/scrot` (optional) | A screenshot key could be added later |

If `feh` is not added, the desktop still starts with the Ember ink colour and
a clear panel; it is not broken, just not photographic.

---

## 10. Verification performed

- `bash -n` on `install-into-chroot.sh`, `ember-welcome`, `ember-about`,
  `ember-wallpaper`, `autostart`.
- `xmllint --noout` on `rc.xml` and `menu.xml`.
- YAML parse of `branding.desc`; every referenced image and `show.qml`
  confirmed present.
- `qmllint` 6.11: no errors in `show.qml`, `SlideArt.qml` or
  `stage3guide.qml` (only a Qt plugin-types import warning from the test
  toolchain).
- QML rendered offscreen at 800×520 and 600×460; all five slides checked for
  overflow, plus the stage3 page.
- GTK theme loaded in GTK 3.24 under Xvfb; suggested/selection colours
  verified in a real GTK window.
- LightDM theme CSS tested with a GTK mock that uses the greeter’s real widget
  names (`login_window`, `login_box`, `password_entry`, `login_button`,
  `panel_window`, …). The actual `lightdm-gtk-greeter` binary was not available
  in the test image.
- Openbox 3.6.1 + tint2 17 + rofi 2.0 run in Xvfb with the shipped configs;
  desktop, panel, menu and rofi theme captured.
- Installer script: `--dry-run` on a clean fake root made no changes; real run
  on a fresh fake root; second run was a no-op; backups checked; GRUB,
  Plymouth, LightDM, Calamares and `os-release` output inspected.
- Font files are valid TTFs; `fc-match Inter` resolves Regular and Bold.

**Not verified here:** a real GRUB/Plymouth boot from the ISO, the actual
Calamares wizard with this component loaded, real LightDM/SDDM sessions,
KDE/Xfce theming, and Secure Boot. Those remain integration tests for the lead
agent.

---

## 11. Screenshots and mockups

| File | Type | Notes |
|---|---|---|
| `mockups/desktop-openbox.png` | Captured | Real Openbox + tint2 + xterm session under Xvfb using the shipped themes; 1920×1080 |
| `mockups/lightdm-greeter.png` | Mocked | GTK 3.24 mock using the LightDM greeter’s widget names and the shipped greeter CSS; 1920×1080 |
| `mockups/welcome-page.png` | Captured | Firefox headless render of the shipped offline Welcome page |
| `mockups/calamares-slideshow.png` | Captured | Actual `show.qml` render (slide 1) at 800×520 |
| `mockups/calamares-stage3.png` | Captured | Actual `stage3guide.qml` render at 800×520 |
| `mockups/calamares-welcome-mockup.png` | Mockup | Calamares welcome layout with the shipped images/QSS palette; 800×520 |
| `mockups/grub-menu-mockup.png` | Mockup | GRUB theme design with the shipped background/slices; 1920×1080 |
| `mockups/plymouth-boot-mockup.png` | Mockup | Plymouth design with the shipped frames; 1920×1080 |
| `mockups/rofi-theme.png` | Captured | Real rofi 2.0 window with the shipped theme (run mode) under Xvfb |

Screenshots are documentation-only. They are not generated at install time
and are not referenced by any runtime config.

---

## 12. Licences and sources

- **Original artwork, HTML and copy:** CC BY-SA 4.0,
  `licenses/CC-BY-SA-4.0.txt`.
- **Shell/Python integration and build scripts:** MIT, `licenses/MIT.txt`.
- **Inter:** SIL OFL 1.1, `licenses/OFL-1.1-Inter.txt`; unmodified official
  Inter 4.1 TTFs.
- **Adwaita/Adwaita-dark:** part of GTK 3 (LGPL-2.1+); imported at runtime,
  not redistributed.
- **Openbox, Calamares, Plymouth:** upstream projects; only original
  configuration/QML/scripts are included. The stock Calamares
  `Presentation.qml`/`Slide.qml` are used from the installed Calamares, not
  copied into this pack.
- **Gentoo:** trademark of the Gentoo Foundation. Ember is independent.
- Generators: `tools/gen_identity.py`, `gen_wallpapers.py`, `gen_icons.py`,
  `gen_cursors.py`, `gen_boot.py`, `gen_mockups.py`. They are optional build
  helpers, ship with the pack, and require `rsvg-convert`, Pillow and (for the
  wordmark paths) fontTools.

---

## 13. Integration risks and preflight checks

1. **Plymouth is not installed in the current package list.** Theme files are
   staged and `plymouthd.conf` is set only if Plymouth exists. Add
   `sys-boot/plymouth`, enable dracut’s `plymouth` USE flag, rebuild the
   initramfs, and boot-test. Without it, the kernel messages/`quiet` splash is
   whatever the ISO already uses.
2. **Missing desktop apps.** Firefox, Thunar, pavucontrol, nm-applet, feh and
   zenity are referenced. Menus skip missing launchers; the wallpaper falls
   back to solid ink; Welcome falls back to xterm/stdout. Add the packages.
   The live `gentoo` home is only updated with `--live-user gentoo`; without
   it the live session keeps its stock autostart (including Calamares).
3. **Calamares component name.** `branding.desc` says `componentName: ember`;
   Calamares refuses to load a component whose directory name differs. Keep it
   at `/usr/share/calamares/branding/ember` and set `branding: ember` (the
   script does both). If manual copying to `default` is unavoidable, change
   `componentName` to `default` in the copied `branding.desc`.
4. **Live ISO GRUB/Plymouth are separate.** The target themes do not change
   the already-built `iso-root` GRUB menu or the live initramfs. Brand the live
   GRUB/Plymouth as a separate ISO-build step if required.
5. **Calamares ordering.** `openrc.conf` currently overwrites
   `/etc/xdg/openbox/autostart` and `menu.xml`. Run `emberbranding` after
   `shellprocess@openrc`, not before. Run it before `grubcfg`/`bootloader` so
   `/etc/default/grub` and the GRUB theme are present when GRUB is generated.
6. **`/boot` must be mounted** at the target’s `/boot` when the script runs;
   otherwise the GRUB theme is skipped with a warning. `GRUB_THEME` is still
   written if `/boot` exists as a directory on the root filesystem.
7. **LightDM config precedence.** The greeter is set through a `99-ember.conf`
   drop-in, so package/Calamares updates to `lightdm.conf` are preserved. If
   another file sets `greeter-session` later (e.g. `99-zz-*`), it wins. Check
   `/etc/lightdm/lightdm.conf.d/` order.
8. **User session is not forced.** Calamares/displaymanager must set
   `user-session` for the chosen desktop. Use `--default-session` only for
   Openbox-only images.
9. **Font cache.** When installing into a mounted target, run `fc-cache -f`
   inside the target (or reboot); the script skips host-side caches for
   non-`/` roots.
10. **Icon/cursor fallback.** The Ember icon set is intentionally small. It
   inherits Papirus → Adwaita → hicolor. Add Papirus if complete app coverage
   matters. The cursor theme has 15 real shapes and relies on
   Adwaita/breeze for the rest; install one of them.
11. **Rofi version.** Tested with rofi 2.0. The `.rasi` syntax used here is the
   common 1.7+ syntax; older rofi may ignore some properties but should still
   launch. `config.rasi` points at the absolute installed theme path.
12. **Openbox menu icons.** Openbox loads menu PNGs through Imlib2. The test
    host lacked the chroot’s Imlib2 loader path, so menu screenshots show no
    icons; the installed target has working loaders. If icons do not appear,
    check `imlib2` loaders and file permissions.
13. **GTK theme dependency.** `Ember` and `Ember-Greeter` import Adwaita’s
    dark stylesheet from GTK’s resource bundle. This is present with GTK 3;
    if a stripped GTK lacks it, the theme is minimally styled but apps still
    run. Test on the final ISO.
14. **Calamares wallpaper and QSS.** The 800×520 product wallpaper is exactly
    the window size. The QSS keeps content pages transparent for it; if a
    future Calamares version makes a page opaque, the wallpaper simply hides
    on that page. Do not add a global `QWidget { background-color }` to the
    QSS.
15. **URLs.** `https://emberlinux.org/…` is the intended project domain and
    must be registered/owned before release. Until then, support/release
    buttons should stay disabled (`welcome.conf` currently disables them).
16. **Finished/error strings.** Calamares’ built-in finished/error page text is
    compiled in. The Ember wording is in `copy/installer-copy.md` and the
    Welcome page; wiring a custom finished page requires a Calamares module
    change outside this pack.
17. **KDE/Xfce.** This pack brands LightDM, fonts, GTK, icons and the Openbox
    session. Xfce will use its own window manager/panel defaults; KDE Plasma
    will use Breeze unless a Plasma colour scheme/theme is added. The current
    installer defaults and requirement target Openbox; do not claim the other
    desktops are fully themed.
18. **Secure Boot.** No Secure Boot claim is made anywhere in this pack. The
    GRUB theme is independent of signing; secure boot remains a separate
    integration task.
19. **Pack self-copy.** The script copies the whole pack (~8 MB) to
    `/usr/share/ember/branding-pack` in the target so it can be reapplied.
    Exclude it if ISO size becomes critical with `--no-pack`; then keep a copy
    on the live medium only.
20. **Version/codename.** The pack says 1.0 “Cinder”. Change `branding.desc`,
    `os-release` snippet, Welcome page, About page, GRUB theme labels and
    slideshow if the release version changes.

---

## 14. Quick checklist for the lead

- [ ] Copy/install the Calamares component into the live root and set
      `branding: ember` (or run the script with `--root <live-root>`).
- [ ] Add `emberbranding` shellprocess after `shellprocess@openrc`, before
      `grubcfg`/`bootloader`.
- [ ] Add Firefox, Thunar, pavucontrol, nm-applet, feh, zenity (and Plymouth
      if the splash is required).
- [ ] Ensure `/boot` is mounted in the target before the script runs.
- [ ] Run `fc-cache`/`gtk-update-icon-cache` in the target or on first boot.
- [ ] Rebuild the ISO, then boot BIOS and UEFI and verify GRUB, Plymouth,
      LightDM, Openbox, wallpaper, menu, panel and Welcome.
- [ ] Re-run the installer and verify the target has the same theme; check
      `/var/backups/ember-branding/` after an upgrade.
- [ ] Test Xfce/KDE/Server paths separately; this pack only claims the Openbox
      desktop defaults.
