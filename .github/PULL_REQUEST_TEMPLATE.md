# Pull request

## Summary

<!-- What changes, and why? Link the issue if there is one. -->

Closes #

## Type

- [ ] Installer behavior
- [ ] Partitioning / filesystems
- [ ] Desktop session / packages
- [ ] Secure Boot
- [ ] make.conf editor / hardware probing
- [ ] Branding / theme
- [ ] Documentation / website
- [ ] Build / test tooling
- [ ] Other

## Testing

Test the exact artifact. Do not check a box for a path you did not run.

- ISO: <!-- path -->
- SHA-256: <!-- checksum -->
- Build time: <!-- timestamp -->

| Check | BIOS | UEFI | Notes |
| --- | --- | --- | --- |
| Live boot | | | |
| Installer completes | | | |
| Disk-only boot | | | |
| Login / session | | | |
| Network | | | |
| Services | | | |

- Desktop: <!-- Openbox / Xfce / KDE Plasma / Server / N/A -->
- Filesystem / swap / LUKS / LVM: <!-- ... -->
- Hardware or VM: <!-- model / QEMU + OVMF version -->
- Secure Boot: <!-- off / on / not tested -->

### Commands and evidence

```text
<!-- Paste the relevant output, or link a QA report in vm/. -->
```

## Claims and documentation

- [ ] I updated the tested/offered/experimental matrix if this changes a claim.
- [ ] I linked evidence for any new support claim.
- [ ] I did not weaken, skip, or rewrite a test to make this pass.
- [ ] I updated `README.md` / `docs/` for behavior, requirements, or status changes.
- [ ] I recorded the exact ISO checksum if the ISO changed.
- [ ] Screenshots and logs contain no passwords, keys, MAC addresses, or serial numbers.

## Licensing

- [ ] New source files have an SPDX header consistent with the surrounding code.
- [ ] Any third-party code, asset, font, or firmware is identified with its source and license.
- [ ] No built ISO, VM disk, or large binary is committed.

If the project has no top-level license yet, do not state a new project-wide
license in this pull request. See [docs/licensing.md](../docs/licensing.md).

## Checklist

- [ ] The change is focused and does not include unrelated cleanup.
- [ ] Configuration changes live in `configs/calamares/` (the source of truth), not only in the build root.
- [ ] I ran `python3 .github/scripts/check_links.py` if I touched docs.
- [ ] I am willing to answer review questions and re-run the affected QA path.

## Screenshots

<!-- Before/after images, installer pages, or firmware errors. Remove personal data. -->
