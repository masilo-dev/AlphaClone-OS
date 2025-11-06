<!--
Purpose: Outline phased milestones for AlphaClone System OS.
Author: AlphaClone Systems Core Team
License: MIT
TODO: Revisit milestone timelines quarterly and map to release trains.
-->

# AlphaClone System OS Roadmap

## Phase 0 – Alpha Boot (Q4 2025)
- ✅ Establish repository structure, licensing, and CI foundations.
- Implement Multiboot bootstrap, VGA console, and kernel shell.
- Provide sample agent orchestrator and logging agent.

## Phase 1 – Kernel Feature Expansion (Q1 2026)
- Add physical memory allocator and paging support.
- Wire interrupt handlers for keyboard, timer, and storage devices.
- Introduce preemptive scheduling with per-core run queues.

## Phase 2 – Agent Platform Hardening (Q2 2026)
- Extend orchestrator with authentication providers and RBAC.
- Launch robust agent sandbox leveraging containers or WASM.
- Deliver comprehensive agent SDKs (TypeScript, Rust, Python).

## Phase 3 – Secure Agent Sandbox (Q3 2026)
- Implement capability tokens enforced via kernel hooks and runtime policies.
- Add audit logging pipeline feeding security agents.
- Certify agent distribution channel with signed bundles.

## Phase 4 – UI Runtime Evolution (Q4 2026)
- Ship Electron-based management console and lightweight TUI fallback.
- Integrate live kernel telemetry dashboards.
- Provide remote update workflow for orchestrator and agents.

## Phase 5 – Device Integration (2027)
- Build storage, network, and GPU driver support.
- Enable virtual disk management and snapshotting.
- Achieve hardware bring-up on bare-metal x86_64 reference boards.
