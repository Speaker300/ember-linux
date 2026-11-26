#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Configure the display manager and session for the chosen desktop."""
import os

import libcalamares
from libcalamares.utils import check_target_env_call


# desktop id -> (display manager, session id, executable for greetd)
DESKTOPS = {
    "openbox": ("lightdm", "openbox", "openbox-session"),
    "xfce": ("lightdm", "xfce", "xfce4-session"),
    "kde": ("sddm", "plasmax11", "startplasma-x11"),
    "gnome": ("gdm", "gnome", "gnome-session"),
    "cinnamon": ("lightdm", "cinnamon", "cinnamon-session"),
    "mate": ("lightdm", "mate", "mate-session"),
    "lxqt": ("lightdm", "lxqt", "lxqt-session"),
    "i3": ("lightdm", "i3", "i3"),
    "sway": ("greetd", "sway", "sway"),
    "hyprland": ("greetd", "hyprland", "start-hyprland"),
    "fluxbox": ("lightdm", "fluxbox", "fluxbox"),
    "icewm": ("lightdm", "icewm", "icewm-session"),
    "budgie": ("gdm", "budgie-desktop", "budgie-desktop"),
    "server": ("none", None, None),
}


def _write(path, text, mode=0o644):
    root = libcalamares.globalstorage.value("rootMountPoint")
    full = os.path.join(root, path.lstrip("/"))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(text)
    os.chmod(full, mode)


def _systemd():
    stage = (libcalamares.globalstorage.value("STAGE_NAME_TAR") or "").lower()
    return "systemd" in stage


def _enable_systemd(service):
    root = libcalamares.globalstorage.value("rootMountPoint")
    try:
        check_target_env_call(["systemctl", "enable", service])
        return
    except Exception as e:
        libcalamares.utils.warning("systemctl enable %s failed: %s" % (service, e))
    # Offline fallback: create the usual graphical.target wants symlink.
    unit = None
    for d in ("/usr/lib/systemd/system", "/lib/systemd/system"):
        p = os.path.join(root, d.lstrip("/"), service)
        if os.path.exists(p):
            unit = p
            break
    if unit:
        wants = os.path.join(root, "etc/systemd/system/graphical.target.wants")
        os.makedirs(wants, exist_ok=True)
        link = os.path.join(wants, service)
        if os.path.lexists(link):
            os.unlink(link)
        os.symlink(os.path.relpath(unit, wants), link)


def _configure_lightdm(session):
    _write("/etc/lightdm/lightdm.conf",
           "[Seat:*]\nuser-session=%s\ngreeter-session=lightdm-gtk-greeter\n" % session)


def _configure_sddm(session):
    _write("/etc/sddm.conf.d/00-ember.conf",
           "[Users]\nDefaultSession=%s.desktop\n" % session)


def _configure_gdm():
    _write("/etc/gdm/custom.conf",
           "[daemon]\nWaylandEnable=true\n")


def _configure_greetd(executable):
    # greetd needs a greeter user.  Calamares normally creates it, but the
    # desktop_setup job replaces that module, so do it here.
    for group in ("greeter", "video", "input", "seat"):
        try:
            if check_target_env_call(["getent", "group", group]) != 0:
                check_target_env_call(["groupadd", group])
        except Exception:
            pass
    try:
        if check_target_env_call(["getent", "passwd", "greeter"]) != 0:
            check_target_env_call(["useradd", "-c", "Greeter", "-g", "greeter",
                                   "-s", "/bin/bash", "greeter"])
    except Exception:
        pass
    _write("/etc/greetd/config.toml",
           "[terminal]\nvt = 1\n\n[default_session]\nuser = \"greeter\"\n"
           "command = \"tuigreet --remember --time --asterisk --cmd %s\"\n" % executable)
    _write("/etc/greetd/environments", executable + "\n")


def _openbox_theme():
    _write("/etc/xdg/openbox/autostart",
           "xsetroot -solid '#14171C' &\n"
           "feh --bg-fill /usr/share/backgrounds/ember/ember-ridge-1920x1080.png 2>/dev/null &\n"
           "tint2 &\n"
           "picom --backend xrender --xrender-sync-fence &\n")
    _write("/etc/xdg/openbox/menu.xml", """<?xml version="1.0" encoding="UTF-8"?>
<openbox_menu xmlns="http://openbox.org/3.4/menu">
  <menu id="root-menu" label="Ember">
    <item label="Terminal"><action name="Execute"><command>xterm</command></action></item>
    <item label="Files"><action name="Execute"><command>xdg-open /home</command></action></item>
    <item label="Run..."><action name="Execute"><command>rofi -show run</command></action></item>
    <separator />
    <item label="Reconfigure"><action name="Reconfigure" /></item>
    <item label="Exit"><action name="Exit" /></item>
  </menu>
</openbox_menu>
""")


def _i3_config():
    _write("/etc/i3/config", """# Ember i3 defaults
set $mod Mod4
font pango:DejaVu Sans 10
bindsym $mod+Return exec xterm
bindsym $mod+d exec dmenu_run
bindsym $mod+Shift+q kill
bindsym $mod+Shift+r restart
bindsym $mod+Shift+e exec i3-msg exit
bar {
    status_command i3status
}
exec --no-startup-id xsetroot -solid '#14171C'
exec --no-startup-id picom --backend xrender --xrender-sync-fence
""")
    _write("/etc/i3status.conf", """general {
    colors = true
    interval = 5
}
order += "ipv6"
order += "disk /"
order += "load"
order += "memory"
order += "tztime local"
tztime local {
    format = "%Y-%m-%d %H:%M"
}
""")


def _sway_config():
    _write("/etc/sway/config", """# Ember Sway defaults
set $mod Mod4
font pango:DejaVu Sans 10
bindsym $mod+Return exec foot
bindsym $mod+d exec wofi --show drun
bindsym $mod+Shift+q kill
output * bg #14171C solid_color
exec waybar
exec swaybg -i /usr/share/backgrounds/ember/ember-ridge-1920x1080.png -m fill
""")
    _write("/etc/xdg/waybar/config", """{
  "layer": "top",
  "modules-left": ["sway/workspaces", "sway/mode"],
  "modules-center": ["clock"],
  "modules-right": ["network", "battery", "tray"],
  "clock": {"format": "{:%Y-%m-%d %H:%M}"},
  "network": {"format-wifi": "wifi {essid}", "format-ethernet": "eth", "format-disconnected": "offline"},
  "battery": {"format": "{capacity}% {icon}"},
  "tray": {"spacing": 8}
}
""")
    _write("/etc/xdg/waybar/style.css", """* { font-family: "DejaVu Sans"; font-size: 11px; }
window#waybar { background: #14171C; color: #F4F6F8; }
#workspaces button.focused { background: #F26A3D; color: #14171C; }
""")


def _hyprland_config():
    _write("/etc/hypr/hyprland.conf", """# Ember Hyprland defaults (experimental)
monitor=,preferred,auto,1
exec-once = waybar
exec-once = hyprpaper
$mod = SUPER
bind = $mod, Return, exec, kitty
bind = $mod, D, exec, wofi --show drun
bind = $mod, Q, killactive
bind = $mod SHIFT, E, exit
general { gaps_in = 4; gaps_out = 8; border_size = 2; col.active_border = rgba(f26a3dff) }
decoration { rounding = 6 }
""")


def run():
    desktop = libcalamares.globalstorage.value("packagechooser_desktopchoose") or "openbox"
    if desktop not in DESKTOPS:
        return ("Unknown desktop", "The desktop selection '%s' is not supported." % desktop)
    dm, session, executable = DESKTOPS[desktop]
    systemd = _systemd()

    if not systemd and desktop != "server":
        # elogind conflicts with systemd, so it cannot live in the shared
        # package list. display-manager-init provides OpenRC's
        # /etc/init.d/display-manager for LightDM and greetd.
        try:
            check_target_env_call(
                ["emerge", "--ask=n", "--verbose=y",
                 "sys-auth/elogind", "gui-libs/display-manager-init"])
        except Exception as e:
            return ("OpenRC desktop helpers failed", str(e))

    if desktop in ("gnome", "budgie") and not systemd:
        return ("This desktop needs systemd",
                "%s requires a systemd stage3. Go back to Select Stage and choose a systemd stage3." % desktop)

    if desktop == "openbox":
        _openbox_theme()
    elif desktop == "i3":
        _i3_config()
    elif desktop == "sway":
        _sway_config()
    elif desktop == "hyprland":
        _hyprland_config()

    if dm == "none":
        root = libcalamares.globalstorage.value("rootMountPoint")
        if not systemd:
            try:
                check_target_env_call(["rc-update", "del", "display-manager", "default"])
            except Exception:
                pass
        for name in ("lightdm", "sddm", "gdm", "greetd"):
            p = os.path.join(root, "etc/runlevels/default", name)
            if os.path.lexists(p):
                os.unlink(p)
        libcalamares.globalstorage.insert("emberDisplayManager", "none")
        return None

    if systemd:
        _enable_systemd(dm + ".service")
    else:
        _write("/etc/conf.d/display-manager", 'DISPLAYMANAGER="%s"\n' % dm)
        check_target_env_call(["rc-update", "add", "display-manager", "default"])

    if dm == "lightdm":
        _configure_lightdm(session)
    elif dm == "sddm":
        _configure_sddm(session)
    elif dm == "gdm":
        _configure_gdm()
    elif dm == "greetd":
        _configure_greetd(executable)

    # Common desktop services (not forced on Server installs).
    if desktop != "server":
        for svc in ("bluetooth", "cupsd", "acpid"):
            if systemd:
                _enable_systemd(svc + ".service")
            else:
                try:
                    check_target_env_call(["rc-update", "add", svc, "default"])
                except Exception:
                    pass

    libcalamares.globalstorage.insert("emberDisplayManager", dm)
    libcalamares.globalstorage.insert("emberSession", session)
    libcalamares.utils.debug("Desktop %s -> %s (%s)" % (desktop, dm, session))
    return None
