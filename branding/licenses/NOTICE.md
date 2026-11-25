# Ember Linux branding — licensing notice

Copyright © 2026 Ember Linux contributors.

## Original artwork and documentation

The Ember mark, wordmark, lockups, wallpapers, boot backgrounds, slideshow
art, icon theme, cursor theme, Openbox/tint2/rofi/LightDM themes, HTML guide
and the copy in `copy/` are original work by the Ember Linux contributors and
are licensed under **Creative Commons Attribution-ShareAlike 4.0
International** (`licenses/CC-BY-SA-4.0.txt`).

You may share and adapt the artwork, including commercially, as long as you
give appropriate credit, link to the licence, indicate changes, and license
derivative artwork under the same terms. The Ember name and logo are not
trademarks of the Gentoo Foundation.

## Code

The shell and Python integration/build scripts, desktop entries and
configuration snippets are licensed under the **MIT License**
(`licenses/MIT.txt`), unless a file says otherwise.

## Fonts

Inter is © 2016–2026 The Inter Project Authors, licensed under the **SIL Open
Font License 1.1** (`licenses/OFL-1.1-Inter.txt`). The font files are
unmodified copies from the official Inter 4.1 release.

## Upstream components referenced, not redistributed

- Adwaita and Adwaita-dark are part of GTK 3 (LGPL-2.1+). The Ember GTK and
  greeter themes import Adwaita's dark stylesheet at runtime; no Adwaita files
  are copied into this pack.
- Openbox is GPL-2.0-or-later. The Ember `themerc`, `rc.xml` and `menu.xml`
  are original configuration written for Openbox, not derived from the Gentoo
  Violet theme.
- Calamares is GPL-3.0-or-later. `show.qml` follows the public Calamares
  slideshow API; the stock `Presentation.qml`/`Slide.qml` are not copied.
- Plymouth is GPL-2.0-or-later. The Ember script uses the documented Plymouth
  script API.
- Gentoo is a trademark of the Gentoo Foundation. Ember Linux is an
  independent project and is not affiliated with or endorsed by the Gentoo
  Foundation.

## Palette and contrast

The palette was checked against WCAG 2.1 contrast ratios; see
`identity/palette.md`.
