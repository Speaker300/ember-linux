# Screenshot provenance

These images are derived from the verified 2026-11-25 QA ISO, not from a stock
Calamares installation.

| File | Source | Shows |
| --- | --- | --- |
| `desktop-chooser.jpg` | `vm/shots/v2-desktop-page.png` | Desktop selection page, Openbox default |
| `partitioning.jpg` | `vm/shots/final-bios-09-partitions.png` | Erase-disk page, 24 GiB virtio disk |
| `summary.jpg` | `vm/shots/final-bios-18-summary.png` | Summary before install, hybrid GPT layout |

Source artifact:

```text
images/ember-live-amd64.iso
4,260,958,208 bytes (3.97 GiB)
sha256 934806c8e93766170a53dfff7aa650e90c391153283c1886720e2d9086d70eed
built 2026-11-25 08:39 -0600
```

The captures are JPEG conversions of 1280×800 VNC screenshots. They predate the
final Ember branding pass: the page chrome and the version string are still
stock Calamares ("FancyGL 2023.3"), while the sidebar uses the Ember accent.
The next ISO will carry the complete Ember theme. Do not use these as evidence
of the final visual design.

The empty preview pane in the desktop chooser is a known cosmetic defect, not a
missing screenshot in this directory.

If you replace these images, keep the same naming and update this table with the
new ISO checksum and build date. Do not use screenshots from an unrelated
distribution or a stock Calamares demo.
