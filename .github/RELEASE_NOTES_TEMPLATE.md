# Ember Linux vX.Y.Z “Codename” — release notes

<!--
Copy this file to docs/releases/VERSION.md (or use it as the GitHub release
body). Do not publish a release with untested claims. Delete sections that do
not apply; never leave a placeholder in a published note.
-->

- **Release date:** YYYY-MM-DD
- **ISO:** `ember-live-amd64-vX.Y.Z.iso`
- **Size:** BYTES bytes (GIB)
- **SHA-256:** `SHA256`
- **Base:** Gentoo amd64, OpenRC, Calamares VERSION
- **Kernel (installed):** KERNEL_VERSION
- **Status:** developer preview / beta / stable

## Highlights

- USER_VISIBLE_CHANGE
- USER_VISIBLE_CHANGE
- USER_VISIBLE_CHANGE

## Tested matrix

Only list paths that completed the full QA cycle. Everything else belongs under
"Offered" or "Known issues".

| Path | BIOS | UEFI | Notes |
| --- | --- | --- | --- |
| DESKTOP, FILESYSTEM, SWAP | Pass | Pass | QA_REPORT_URL |
| DESKTOP, FILESYSTEM, SWAP | Not run | Not run | Offered, not supported |

**Hardware tested:** MACHINE_MODELS / FIRMWARE, or "VM only".

**Secure Boot:** NOT_SUPPORTED / TESTED_ON / KNOWN_ISSUE.

## What changed

### Installer

- CHANGE

### Desktops

- CHANGE

### Hardware and filesystems

- CHANGE

### Branding and desktop

- CHANGE

### Documentation and project

- CHANGE

## Known issues

- ISSUE, with workaround if one exists
- COSMETIC_ISSUE

## Upgrade notes

<!-- For an installed preview, how to update; for a reinstall-only release, say so. -->

```sh
sudo emerge --sync
sudo emerge --ask --update --deep --newuse @world
```

If the release requires a reinstall, state it plainly and explain why.

## Verification

```sh
sha256sum ember-live-amd64-vX.Y.Z.iso
# SHA256  ember-live-amd64-vX.Y.Z.iso
```

- [ ] Checksum published with the artifact.
- [ ] Release notes match the tested matrix.
- [ ] Secure Boot claim matches the evidence.
- [ ] No untested desktop, filesystem, or hardware is described as supported.
- [ ] Third-party licenses and notices are included.

## Contributors

Thanks to NAMES for testing, code, documentation, and design.

## Links

- Install guide: URL
- Troubleshooting: URL
- Testing and evidence: URL
- Issue tracker: URL
- Code of Conduct: URL
