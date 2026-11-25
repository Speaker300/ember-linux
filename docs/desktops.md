# Desktops

The current source tree offers **13 install choices**. That is a menu, not a
support matrix. As of this documentation pass, only **Openbox on the reference
2026-11-25 build** has completed a full install and disk-boot QA cycle. The
newer ISO in `images/` is an intermediate rebuild and has not completed the
matrix.

| Desktop | Session / display manager | Base | Status |
| --- | --- | --- | --- |
| **Openbox** | X11 · LightDM | OpenRC | **Tested on the reference ISO** |
| Xfce | X11 · LightDM | OpenRC | Offered — QA pending |
| KDE Plasma | X11 · SDDM | OpenRC | Offered — QA pending |
| GNOME | X11/Wayland · GDM | **systemd stage3** | Offered — conditional, QA pending |
| Cinnamon | X11 · LightDM | OpenRC | Offered — QA pending |
| MATE | X11 · LightDM | OpenRC | Offered — QA pending |
| LXQt | X11 · LightDM | OpenRC | Offered — QA pending |
| i3 | X11 · LightDM | OpenRC | Offered — QA pending |
| Sway | Wayland · greetd | OpenRC | Offered — QA pending |
| Hyprland | Wayland · greetd | OpenRC | **Experimental** |
| Fluxbox | X11 · LightDM | OpenRC | Offered — QA pending |
| IceWM | X11 · LightDM | OpenRC | Offered — QA pending |
| Server | none | OpenRC | Offered — QA pending |

> **Reference vs. current build.** The verified evidence is for
> `images/ember-live-amd64.iso` at SHA-256
> `934806c8e93766170a53dfff7aa650e90c391153283c1886720e2d9086d70eed`
> (2026-11-25 08:39). The file currently at that path is a newer rebuild with a
> different checksum. Openbox must be re-run as a regression gate before the
> newer build can be called tested. See [Testing](testing.md).

## Status definitions

- **Tested** — full install from an exact ISO, disk-only boot, correct session,
  login, terminal, network, and services, on the firmware modes claimed.
- **Offered** — selectable with a defined package set and session
  configuration. Not yet proven end to end.
- **Experimental** — may require a third-party overlay, an unusual session
  stack, or has known integration risk. Not ready for a system you depend on.

Do not describe an offered desktop as supported.

## Openbox (tested on the reference build)

The default and the only desktop with completed QA. It is a small X11 session
with a curated Ember menu, not a bare window manager.

**Packages:** Xorg, libinput, VESA/QXL/amdgpu/Intel/nouveau drivers, Openbox,
xterm, tint2, rofi, picom, PCManFM, feh, xsetroot, xrandr, xdg utilities,
LightDM and the GTK greeter.

**Session:** LightDM starts `openbox-session`. The installed autostart sets a
solid root color, the Ember Ridge wallpaper via feh, tint2, and picom.

**Verified on the reference ISO:** install, disk-only boot, LightDM login,
tint2 and picom running, custom menu, rofi Run, xterm, NetworkManager ping, and
all OpenRC default services on BIOS and UEFI.

**Not verified:** audio, suspend, multi-monitor, screen tearing, real GPUs,
and the newer branding/desktop overlay. The root color is still masked by
picom's cached LightDM wallpaper in some captures — cosmetic.

## Offered X11 desktops

| Desktop | What it installs | Display manager | Main risk before QA |
| --- | --- | --- | --- |
| Xfce | `xfce4-meta`, notifyd, power manager, terminal | LightDM | Session detection; panel starts |
| KDE Plasma | `plasma-meta`, Plasma NM/PA, Dolphin, Konsole, Kate | **SDDM** | Large download; SDDM session |
| Cinnamon | `cinnamon`, Nemo, GNOME Terminal | LightDM | GNOME-adjacent deps on OpenRC |
| MATE | `mate`, Caja, MATE Terminal | LightDM | Session detection |
| LXQt | `lxqt-meta`, QTerminal, PCManFM-Qt | LightDM | Qt/OpenRC integration |
| i3 | i3, i3status, i3lock, dmenu, rofi, picom | LightDM | Default config and bar |
| Fluxbox | Fluxbox, xterm, rofi, picom, feh | LightDM | Menu and wallpaper setup |
| IceWM | IceWM, xterm, rofi, picom, feh | LightDM | Task bar and session |

Xfce, KDE, Cinnamon, MATE, LXQt, i3, Fluxbox, and IceWM all install Xorg and
the same video driver set as Openbox. The installer configures the display
manager and session, not a full per-desktop theme.

## GNOME (systemd only)

GNOME is offered with GDM, but it **requires a systemd stage3**. The preflight
and desktop setup jobs refuse it on an OpenRC stage3 with a clear error. This is
intentional: forcing GNOME onto OpenRC is not a supported configuration.

To test GNOME, select a systemd stage3 such as
`current-stage3-amd64-desktop-systemd` on the Select Stage page. The verified
reference build used an OpenRC stage3, so GNOME has no end-to-end evidence in
this project yet. The systemd install path, GDM enablement, and the resulting
boot must all be tested independently. Do not assume the OpenRC QA result
transfers.

## Wayland desktops

### Sway (offered)

Sway is a Wayland tiling compositor. The installer provides greetd + tuigreet,
foot, wofi, waybar, swaybg, and a basic Ember Sway config. There is no Xorg
server in this package set.

Wayland sessions are a different display-manager and session path from the
tested X11 stack. Sway is untested; expect config and input issues on real
hardware.

### Hyprland (experimental)

Hyprland is explicitly experimental. The installer adds the third-party
`hyproverlay` overlay, accepts `~amd64` packages from it, and configures
greetd, waybar, hyprpaper, and kitty. This depends on an external overlay, a
compositor that changes quickly, and a Wayland session path with no QA.

Do not use Hyprland on a machine you need to boot. It is in the menu so it can
be tested, not because it is ready.

## Server (offered)

No X11, no Wayland, no display manager. The install provides the kernel, OpenRC,
NetworkManager, OpenSSH, and command-line tools. The desktop setup job removes
display-manager services from the default runlevel.

The server path shares the base install with Openbox but has not completed a
full install and reboot test. Treat it as offered.

## How the choice is applied

1. The **Desktop** page is a Calamares `packagechooser` in `packages` mode.
2. `preflight` validates the stage3/desktop pairing (notably GNOME and the
   systemd requirement) and checks mirror reachability.
3. `desktop_overlay` adds `hyproverlay` for Hyprland and nothing for the others.
4. The selected package list is added to `packageOperations`.
5. `gentoopkg` installs the base set and desktop set in one Portage transaction.
6. `desktop_setup` writes the display manager and session configuration:
   LightDM, SDDM, GDM, or greetd; Server gets none.
7. `branding` installs the Ember theme, wallpapers, fonts, icons, Openbox/tint2/
   rofi configs, and `/etc/os-release`.

The source of truth is `configs/calamares/desktopchoose.conf` plus
`modules/desktop_setup/main.py` and `modules/preflight/main.py`. A package-set
change without a matching QA run is not a supported desktop.

## QA required for every offered desktop

- Install on BIOS and UEFI from an exact ISO.
- Boot the installed disk without the ISO.
- Confirm the correct display manager and session start.
- Log in and open a terminal.
- Check `rc-status default` (or `systemctl --failed` on a systemd stage3).
- Check `ping -c1 9.9.9.9`.
- Capture screenshots and the ISO checksum.
- Record the result in a QA report and update this table.

GNOME additionally needs a systemd stage3 install test. Sway and Hyprland need
a Wayland session test, greetd login, and input/clipboard checks. Hyprland also
needs the overlay sync and package keyword path verified.

## Desktop support policy

A desktop moves to **tested** only when the full list above passes and the
evidence is linked. Until then it stays **offered**, and Hyprland stays
**experimental**. The reference Openbox result does not automatically promote
the newer build; regressions are possible and must be re-tested.
