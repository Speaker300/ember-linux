# Calamares integration

1. Put the whole branding pack at `/usr/share/ember/branding-pack` in the live
   root (or run `install-into-chroot.sh --root <live-root>` once, which copies
   it there).
2. Copy `calamares-emberbranding.conf` to
   `/etc/calamares/modules/emberbranding.conf`.
3. Add an instance and an exec step to `/etc/calamares/settings.conf`:

```yaml
instances:
- id: emberbranding
  module: shellprocess
  config: emberbranding.conf
...
exec:
...
- shellprocess@openrc
- shellprocess@emberbranding     # after openrc so its Openbox files do not win
- dracut_gentoo
- grubcfg
- bootloader
```

The current `openrc.conf` writes `/etc/xdg/openbox/autostart` and `menu.xml`.
Running Ember branding immediately after it is deliberate: the branded files
must be the last ones written before GRUB is generated.

Do not add `--default-session` here unless every desktop choice is Openbox.
Calamares/displaymanager should decide the LightDM session for Xfce/KDE.
