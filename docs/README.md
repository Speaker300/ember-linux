# Ember Linux documentation

Ember is a Gentoo-based live ISO with a graphical installer. These documents
cover installation, the supported and untested matrix, development, and the
project's evidence rules.

> **Developer preview.** Only the Openbox path has completed a full BIOS and
> UEFI install plus disk-boot QA, and that was on the reference build below.
> The current source tree offers 13 desktop choices and a rebuilt ISO; those
> changes are still in QA. Secure Boot is not verified. See
> [Testing](testing.md) for the evidence.

## Start here

| If you want to… | Read |
| --- | --- |
| Install Ember on a machine | [Install guide](install.md) |
| Know what is actually tested | [Testing](testing.md) |
| Choose a desktop | [Desktop matrix](desktops.md) |
| Check your hardware | [Hardware matrix](hardware.md) |
| Understand the Secure Boot state | [Secure Boot](secure-boot.md) |
| Fix a failed boot or install | [Troubleshooting](troubleshooting.md) |
| Build the ISO | [Building](building.md) |
| Contribute or run QA | [Contributing](../.github/CONTRIBUTING.md) |
| See what is planned | [Roadmap](roadmap.md) |
| Ask a general question | [FAQ](faq.md) |
| Check licensing | [Licensing audit](licensing.md) |

## Status vocabulary

Ember uses three words deliberately:

- **Tested** — a complete install from an exact ISO, followed by a disk-only
  boot, login, and network check on the firmware modes claimed. For a desktop,
  the session and panel must start.
- **Offered** — selectable in the installer with a defined package set, but not
  yet through the full QA cycle. It may work; the project has not proven it.
- **Experimental** — present in the source tree, may be incomplete, and is not
  ready for a system you depend on.

"Supported" is only used when the tested definition is met and the evidence is
linked. VM coverage is not hardware coverage.

## Current QA snapshot

Reference artifact (the file at `images/ember-live-amd64.iso` has since been
rebuilt and is **not** this checksum):

```text
images/ember-live-amd64.iso
4,260,958,208 bytes (3.97 GiB)
sha256 934806c8e93766170a53dfff7aa650e90c391153283c1886720e2d9086d70eed
built 2026-11-25 08:39 -0600
```

The newer intermediate rebuild is untested. Its presence in `images/` does not
promote any row below.

| Check | BIOS | UEFI |
| --- | --- | --- |
| Live boot and installer | Pass | Pass |
| Stage3 selection and download | Pass | Pass |
| Desktop chooser | Pass (preview pane empty) | Pass (preview pane empty) |
| Erase disk, GPT, ext4, no swap | Pass | Pass |
| Openbox install | Pass | Pass |
| Disk-only boot to LightDM | Pass | Pass |
| Openbox session, tint2, picom | Pass | Pass |
| NetworkManager ping | Pass | Pass |
| OpenRC default services | Pass | Pass |

Reports: [final](../vm/TEST-REPORT-final.md) and
[v2](../vm/TEST-REPORT-v2.md). Known non-blocking cosmetic issues are listed
there: empty desktop previews, stock slideshow copy, a summary page that does
not recap Stage 3/desktop choices, and a root color masked by picom.

## Documentation map

```text
README.md                  project overview and quick start
docs/
  install.md               end-to-end install walkthrough
  desktops.md              Openbox / Xfce / KDE / Server status
  hardware.md              firmware, CPU, GPU, storage, network matrix
  secure-boot.md           shim/MOK state, recovery, test plan
  troubleshooting.md       symptoms, logs, reporting
  faq.md                   common questions
  roadmap.md               now / next / later with exit criteria
  building.md              maintainer build and reproducible-build plan
  testing.md               QA policy, levels, VM helpers
  licensing.md             license audit and release blockers
  assets/                  landing-page and screenshot assets
  index.html               GitHub Pages landing page
.github/
  CONTRIBUTING.md          contribution guide
  CODE_OF_CONDUCT.md       community standards
  ISSUE_TEMPLATE/          bug, install report, feature request
  PULL_REQUEST_TEMPLATE.md review checklist
  RELEASE_NOTES_TEMPLATE.md
  RELEASE_CHECKLIST.md
  SECURITY.md              private vulnerability reporting
  workflows/               Pages deploy and docs link check
  scripts/check_links.py   local and CI link checker
```

## Documentation rules

1. Every support claim needs a test or a clearly labeled plan.
2. Prefer "not tested" over an optimistic guess.
3. Link the exact report, ISO checksum, or command output.
4. Keep the tested/offered/experimental distinction visible.
5. Update the matrices when a QA run changes the answer.

See [Contributing](../.github/CONTRIBUTING.md#evidence-rules) for the full
evidence policy.
