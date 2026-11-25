# Mockup and screenshot notes

These files are documentation, not runtime assets.

**Captured from the shipped configuration**

- `desktop-openbox.png` — Openbox 3.6.1, tint2 17, xterm and the Ember
  wallpaper at 1920×1080 in a disposable Xvfb display. The panel, titlebar,
  menu colours and wallpaper are the real files in this pack. The menu is not
  visible in this frame; menu labels were verified separately.
- `rofi-theme.png` — rofi 2.0 with `desktop/rofi/ember.rasi` in run mode,
  over the same session.
- `welcome-page.png` — Firefox headless render of
  `desktop/welcome/index.html` at 1280 px wide.
- `calamares-slideshow.png` — actual `calamares/show.qml` rendered offscreen
  with Qt 6.11 at 800×520 (slide 1).
- `calamares-stage3.png` — actual `calamares/stage3guide.qml` rendered
  offscreen with Qt 6.11 at 800×520.

**Mockups**

- `lightdm-greeter.png` — GTK 3.24 window built with the LightDM greeter’s real
  widget names (`login_window`, `login_box`, `user_image_border`,
  `password_entry`, `login_button`, `panel_window`, `message_label`) and the
  shipped `Ember-Greeter` CSS. The real `lightdm-gtk-greeter` binary was not
  available in the test image.
- `calamares-welcome-mockup.png` — design layout for the Calamares welcome
  page using the shipped `welcome.png`, logo, palette and copy. The real
  Calamares wizard is an integration test.
- `grub-menu-mockup.png` — GRUB theme design using the shipped background,
  logo, nine-slice slices and palette. Not captured from a GRUB boot.
- `plymouth-boot-mockup.png` — Plymouth design using the shipped background,
  logo, progress frames and throbber. Not captured from a real boot.

No image in this folder is referenced by an installed config. You can delete
the folder when building a minimal live image.
