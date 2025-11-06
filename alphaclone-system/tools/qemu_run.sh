#!/usr/bin/env bash
# AlphaClone System OS - QEMU Runner
# Purpose: Launch the AlphaClone System OS ISO within QEMU for developer testing.
# Author: AlphaClone Systems Core Team
# License: MIT
# TODO: Add serial console capture and headless networking options.

set -euo pipefail

ISO_PATH="${1:-$(pwd)/build/alpha-system.iso}"
if [[ ! -f "${ISO_PATH}" ]]; then
  echo "AlphaClone System OS ISO not found at ${ISO_PATH}" >&2
  exit 1
fi

QEMU_ARGS=(
  -cdrom "${ISO_PATH}"
  -m 2048
  -smp 2
  -display none
  -serial stdio
)

if [[ -e /dev/kvm && -r /dev/kvm && -w /dev/kvm ]]; then
  QEMU_ARGS+=( -enable-kvm )
else
  echo "/dev/kvm unavailable or inaccessible, using TCG." >&2
  QEMU_ARGS+=( -accel tcg )
fi

if ! command -v qemu-system-x86_64 >/dev/null 2>&1; then
  echo "qemu-system-x86_64 is not installed. Install qemu-kvm." >&2
  exit 1
fi

if ! qemu-system-x86_64 "${QEMU_ARGS[@]}"; then
  echo "Falling back to software acceleration." >&2
  exec qemu-system-x86_64 "${QEMU_ARGS[@]}" -accel tcg
fi
