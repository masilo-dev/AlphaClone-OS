#!/usr/bin/env bash
# AlphaClone System OS - System Build Script
# Purpose: Orchestrate kernel and ISO build for production pipelines.
# Author: AlphaClone Systems Core Team
# License: MIT
# TODO: Integrate remote cache support and release signing steps.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="${ROOT_DIR}/build"
ISO_DIR="${BUILD_DIR}/iso"

mkdir -p "${ISO_DIR}/boot/grub"

make -C "${ROOT_DIR}" kernel
cp "${BUILD_DIR}/kernel.bin" "${ISO_DIR}/boot/kernel.bin"
cp "${ROOT_DIR}/system/grub.cfg" "${ISO_DIR}/boot/grub.cfg"

grub-mkrescue -o "${BUILD_DIR}/alpha-system.iso" "${ISO_DIR}" >/dev/null
