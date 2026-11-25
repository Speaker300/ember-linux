# Security policy

Ember is a developer preview. There is no supported release yet, so there are no
security-maintained versions. That will change with the first public release;
this page will be updated then.

## Reporting a vulnerability

Please **do not open a public issue** for a vulnerability.

Use the private contact method listed on the repository owner's GitHub profile
and ask for the report to be handled privately. Include:

- affected component (installer, a module, packaging, branding, website);
- Ember ISO/build or commit;
- steps to reproduce;
- impact and any known workaround;
- whether the issue is already public.

You will get an acknowledgement as soon as a maintainer can review it. Please
allow time for a fix before disclosure. If the issue is in a third-party package
(Gentoo, Calamares, the kernel, a desktop environment), it may need to go
upstream as well; we will help route it.

## Scope

In scope:

- custom Calamares modules in `modules/`;
- installer configuration in `configs/calamares/`;
- build and test scripts in `scripts/`;
- the GitHub Pages site and documentation;
- Ember-specific branding and desktop configuration.

Out of scope for this repository:

- vulnerabilities in Gentoo packages, the kernel, firmware, or upstream desktop
  software (report them upstream; tell us if Ember's defaults make them worse);
- issues that require physical access to an already-unlocked machine;
- the documented developer-preview limitations (for example, Secure Boot not
  being verified yet).

## Secure Boot

Secure Boot support is experimental and not verified. Do not treat it as a
security boundary for this preview. See [docs/secure-boot.md](../docs/secure-boot.md).

## Secrets in the repository

Do not commit passwords, private keys, tokens, or real user data. Test
credentials and test keys belong in ignored local files. If you find a secret
committed by mistake, report it privately; do not repeat it in a public issue.
