# Release checklist

A release is not ready because the ISO builds. It is ready when the claims,
artifacts, and licenses are all in order.

## 1. Code and configuration

- [ ] `configs/calamares/` is the source of truth; no fix lives only in the build root.
- [ ] `sync-installer.sh` and `rebuild-iso2.sh` completed without errors.
- [ ] The C++ `makeconf` module is compiled into the rootfs if its source changed.
- [ ] No mounted pseudo-filesystems inside the squashfs.
- [ ] ISO fits the target size budget.
- [ ] No test was weakened, skipped, or rewritten to pass.

## 2. QA evidence

- [ ] Exact ISO checksum recorded before testing and unchanged after.
- [ ] BIOS and UEFI installs pass on the release artifact.
- [ ] Disk-only boot, login, network, and services pass.
- [ ] Every desktop listed as "tested" has its own QA report.
- [ ] Every filesystem/encryption option listed as "supported" has a boot test.
- [ ] Secure Boot is either fully tested or clearly marked experimental.
- [ ] Real-hardware result recorded (or the release is explicitly VM-only).
- [ ] Matrices in `README.md`, `docs/desktops.md`, and `docs/hardware.md` match the evidence.
- [ ] Known issues are listed with workarounds where possible.

## 3. Licensing

- [ ] Top-level `LICENSE` exists and matches the intended project license.
- [ ] GitHub repository license field is set.
- [ ] SPDX headers are present on project source files.
- [ ] Branding license is stated and consistent.
- [ ] `Inter-LICENSE.txt` ships with the font.
- [ ] Third-party notices / package manifest included.
- [ ] Secure Boot shim redistribution terms reviewed.
- [ ] `docs/licensing.md` no longer says "not finalized".

## 4. Artifact and release notes

- [ ] ISO size and SHA-256 recorded.
- [ ] Release notes use `.github/RELEASE_NOTES_TEMPLATE.md`.
- [ ] Release notes tested matrix matches reality.
- [ ] Secure Boot status is accurate.
- [ ] Upgrade/reinstall guidance is explicit.
- [ ] Download link and checksum published together.
- [ ] Release tagged after the artifact is final.
- [ ] GitHub Release body does not contain placeholders.

## 5. Documentation and site

- [ ] `python3 .github/scripts/check_links.py` passes.
- [ ] Install guide matches the actual installer pages and labels.
- [ ] Screenshots are current, or labeled with the build they came from.
- [ ] The landing page has no stock Calamares screenshots.
- [ ] Pages workflow succeeds and the site loads with assets.
- [ ] No secrets, personal data, or test credentials in docs or screenshots.
- [ ] Release notes linked from README and docs index.

## 6. Post-release

- [ ] Announcement links to the exact release and checksum.
- [ ] Issue templates still point to valid docs.
- [ ] A follow-up issue exists for every deferred limitation.
- [ ] The next roadmap item is unblocked.

## Rollback plan

If a release is found to be unbootable or destructive:

1. Mark the GitHub Release as a pre-release or remove the artifact.
2. Publish a short notice with the affected checksum and symptoms.
3. Keep the previous ISO available.
4. Open a blocking issue and do not re-release until the failing matrix passes.
5. Never silently replace an artifact under the same version.
