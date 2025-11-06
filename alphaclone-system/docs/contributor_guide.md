<!--
Purpose: Document contribution expectations for AlphaClone System OS.
Author: AlphaClone Systems Core Team
License: MIT
TODO: Add code review templates and automated checklists.
-->

# Contributor Guide

## Branch Strategy

- `main` remains stable and release-ready.
- Feature work lands on topic branches prefixed with domain (e.g., `kernel/`, `agents/`, `docs/`).
- Pull requests merge via squash unless otherwise agreed.

## Coding Standards

- C code follows `.clang-format` and compiles with `-Wall -Wextra -Werror` in CI.
- TypeScript uses `pnpm lint` for strict type checks.
- Every source file carries purpose, author, license, and TODO headers.

## CI Requirements

- `make all` (kernel + agents) must pass locally before submission.
- GitHub Actions run kernel build, ISO packaging, and agent compilation.
- Artifacts (kernel.bin, alpha-system.iso) upload on successful builds.

## Local Development

```bash
# Kernel toolchain
sudo apt-get install nasm gcc-multilib grub-pc-bin xorriso

# Agents
cd alphaclone-system
pnpm install
pnpm build
```

## Codespaces Workflow

- Use `make kernel` to validate kernel changes quickly.
- Run `make agents` to regenerate orchestrator builds.
- Verify QEMU boot via `make run`.

## Submitting Changes

1. Rebase on latest `main`.
2. Run full test suite (`make all`).
3. Open PR with clear summary, testing evidence, and risk callouts.
4. Request review from the core team via `CODEOWNERS` assignments.
