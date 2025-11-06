<!--
Purpose: Document vulnerability disclosure process for AlphaClone System OS.
Author: AlphaClone Systems Core Team
License: MIT
TODO: Publish PGP key for encrypted submissions.
-->

# Security Policy

## Supported Releases

The `main` branch and active feature branches receive security attention. Forks and forks-of-forks should merge upstream patches promptly.

## Reporting a Vulnerability

Email `security@alphaclone.systems` with detailed reproduction steps. Include `ALPHACLONE-SECURITY` in the subject.

- We respond within **48 hours**.
- We provide a remediation plan or mitigation within **10 business days**.
- Coordinated disclosure timelines are handled case-by-case.

## Handling Sensitive Information

- Do not commit secrets to this repository. Use GitHub Secrets or external vaults.
- Never share exploit details publicly until fixes ship.
- Encrypt attachments with a mutually agreed key when sending sensitive diagnostics.

## Hardening Checklist

- Enable compiler hardening flags (`-fstack-protector-strong`, ASLR) during release builds.
- Enforce capability tokens for every agent before enabling network access.
- Run CI security scans (future integration) before promoting builds.
