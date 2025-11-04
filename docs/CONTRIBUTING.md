# Contributing to AlphaClone-OS

Thanks for your interest! This guide explains how to contribute and the repo structure.

Getting started
- Read `docs/architecture.md`.
- Build and run the `kernel_sim` prototype to understand subsystem interactions.

Development workflow
- Fork -> feature branch -> open PR against `main`.
- Include tests where applicable and keep changes small and focused.

Coding guidelines
- Keep C code in the `kernel_sim/` folder minimal and portable.
- Follow simple style: 4-space indent, clear comments, and small functions.

Testing
- The repo includes a basic Makefile for the simulator. CI should build the simulator and run smoke tests.
