#!/usr/bin/env bash
set -euo pipefail

# qemu_boot.sh
# Boot a disk image in QEMU. For UEFI use OVMF; for BIOS this will work without UEFI.

IMG=${1:-alpha.img}
UEFI=${2:-0}

if [ ! -f "$IMG" ]; then
  echo "Image $IMG not found" >&2
  exit 1
fi

if [ "$UEFI" -eq 1 ]; then
  # Try to locate OVMF firmware
  OVMF_CODE=$(pkg-config --variable=libdir efi 2>/dev/null || true)
  echo "Starting QEMU with UEFI (OVMF)"
  qemu-system-x86_64 -drive file="$IMG",format=raw -machine q35 -m 1024 -bios /usr/share/ovmf/OVMF_CODE.fd -serial stdio
else
  echo "Starting QEMU with BIOS"
  qemu-system-x86_64 -drive file="$IMG",format=raw -m 1024 -serial stdio
fi
