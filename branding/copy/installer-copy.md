# Ember Linux — installer and first-boot copy

This is the canonical wording for the installer and the installed system. It
is written to sound like a distribution, not like a generic wizard: concrete
actions, honest timing, no marketing claims we cannot test.

The Calamares pages that can be fully reworded through this branding pack are
the **Stage 3** page (`calamares/stage3guide.qml`) and the **slideshow**
(`calamares/show.qml`). The strings below are provided for `welcome.conf`,
`desktopchoose.conf`, the summary layout and any post-install page the lead
agent adds; they are already reflected in the QML where applicable.

---

## Welcome page

**Product name** (from `branding.desc`)
> Ember Linux

**Short name**
> Ember

**Heading** (rendered by Calamares as “Welcome to Ember Linux.”)
> Welcome to Ember Linux

**Body** — recommended if a custom welcome page is wired up; otherwise the
stock Calamares sentence with the Ember product name is acceptable.
> Ember is a careful desktop built on Gentoo. This installer sets up the
> partitions, a Gentoo stage3, your desktop and the bootloader. Most installs
> take 15–40 minutes and need an internet connection.

**Support buttons** — enable in `welcome.conf`:
> Support · Known issues · Release notes

**Requirements line** (if shown):
> At least 6 GB of free disk space and 1 GB of RAM. An online install also
> needs a working network connection.

---

## Stage 3 page — exact QML copy

Title:
> Choose your foundation

Intro:
> Ember installs a Gentoo stage3 before it adds a desktop. Pick the base that
> matches how you plan to use this machine. You can change it later, but
> starting with the right base avoids a long rebuild.

Card 1 — Desktop stage3 (recommended):
> **Desktop stage3**
> Best for Openbox, Xfce and KDE Plasma
> • The desktop profile is already enabled.
> • No large profile switch after installation.
> • Matches the desktop you select on the next page.

Card 2 — Minimal stage3:
> **Minimal stage3**
> Best for servers and custom builds
> • Smaller base system, no desktop profile.
> • The right choice for a headless server.
> • Switching to a desktop later triggers a large rebuild.

Footer:
> Next: choose the exact stage3 tarball, the init system and the desktop.

---

## Desktop page — recommended `desktopchoose.conf` item text

Keep the item order. These descriptions replace the shorter stock lines and
explain the trade-off without overselling any option.

### Openbox (recommended)
> **Openbox**
> A small, fast X11 desktop. Ember's panel, menu and application finder are
> already configured. The best choice for older machines and for a system that
> stays out of the way. Fully tested on the live image.

### Xfce
> **Xfce**
> A complete, familiar desktop with a traditional panel, Thunar and a settings
> centre. A good balance of speed and features if you want more than Openbox
> but do not need a full Qt desktop.

### KDE Plasma
> **KDE Plasma**
> A full-featured Qt desktop with Dolphin, Konsole and Kate. The largest
> download of the three desktops; best paired with the desktop stage3 and a
> reliable network connection.

### Server (no desktop)
> **Server**
> No X11 desktop and no display manager. A clean command line with the kernel,
> networking and the base tools. Choose this for a server, a VM you will
> administer over SSH, or a system you will build up by hand.

---

## Summary page

Calamares builds the summary from the module data, so the item labels come
from the modules above. Use these strings for the page intro and the
pre-install confirmation if the summary is wrapped in a custom page.

**Heading**
> Review your install

**Intro**
> Check the disk, the desktop and the user account below. When you choose
> Install, Ember will erase the selected disk and write the new system. This
> cannot be undone.

**What will happen**
> • The selected disk will be partitioned and formatted.
> • A Gentoo stage3 will be downloaded and unpacked.
> • The desktop and base packages will be installed with Portage.
> • Your user account, hostname and services will be configured.
> • GRUB will be installed for BIOS and UEFI boot.

**Warning**
> Back up anything you need from this disk first. Installing Ember erases the
> selected disk completely.

**Primary action**
> Install Ember

---

## Finish page

The finished page itself is compiled into Calamares. Use this copy in the
post-install Welcome app, a first-boot page, or a distribution-specific
finished page if one is added.

**Heading**
> Ember is installed

**Body**
> Remove the installation medium and restart. The machine will boot into
> Ember Linux and show the LightDM login screen. Log in with the account you
> just created; the first boot takes a little longer while services start.

**If the machine does not boot**
> Return to the live medium, open a terminal and check the bootloader and
> partition layout. The installer log is the first place to look; it is shown
> on the error page and also stored in the live session's cache.

**Buttons**
> Restart now · I'll restart later

---

## Error and help copy

Use this wording on the failure page, in the local help page and in the
installation guide. It must tell the user what state the disk is in and where
the log lives.

**Heading**
> The install could not finish

**Body**
> The disk may have been partially written, so do not boot it yet. The
> installer log contains the exact command that failed. Copy the log before
> closing the live session, or open a terminal with Ctrl+Alt+F2 and save it to
> a USB stick.

**Log locations**
> The installer shows the log path on the error page. In a live session it is
> usually under `~/.cache/calamares/`; the target system keeps package logs in
> `/var/log/emerge.log` after a successful install.

**What to include in a report**
> The Ember version, the chosen desktop, the disk layout, the last 100 lines
> of the installer log, and the output of `emerge --info`.

**Local help**
> The installed system includes **Welcome to Ember** in the application menu.
> It covers updates, software, network, shortcuts and recovery. The Gentoo
> Handbook remains the reference for Portage and USE flags.

**Support URL**
> https://emberlinux.org/help/

---

## Tone rules

- Say what will happen and how long it takes. Do not say “sit back and relax”.
- Say “Gentoo-based”, not “Gentoo”. Ember is independent.
- Never claim Secure Boot support unless the full signed chain is tested.
- Prefer “disk” and “machine” over “device” and “system” in user-facing text.
- Use the serial comma and sentence case for headings.
- Do not use the word “just”; it minimises real failures.
- Keep error text actionable: what happened, what state the disk is in, where
  the log is, what to do next.
