# Ember Linux branding pack

A complete, original visual identity and desktop/boot integration for
**Ember Linux 1.0 “Cinder”**, a Gentoo-based installer distribution.

- **Identity:** mark, badge, wordmark, lockups, palette, Inter.
- **Wallpapers:** 1920×1080 and 2560×1440, plus login/GRUB/Plymouth art.
- **Installer:** Calamares `branding.desc`, `show.qml` (5 real slides),
  `SlideArt.qml`, `stage3guide.qml`, dark `stylesheet.qss`, welcome images.
- **Boot:** GRUB theme, Plymouth theme, LightDM GTK greeter theme and config.
- **Desktop:** Openbox theme/menu/autostart, tint2, rofi, GTK theme, original
  icon and cursor themes, Inter, wallpaper setter, Welcome/About apps.
- **Copy:** installer and first-boot wording in `copy/installer-copy.md`.
- **Integration:** idempotent `install-into-chroot.sh` with backups.

Start with `MANIFEST.md` for the file list, install instructions, package
recommendations and integration risks. Everything in `mockups/` is either a
real render of the shipped QML/themes or is explicitly named a mockup.

Licensed CC BY-SA 4.0 for artwork/documentation and MIT for scripts; see
`licenses/NOTICE.md`.
