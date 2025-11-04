#!/usr/bin/env bash
set -euo pipefail

# create_disk_image.sh
# Create a simple disk image with EFI and root partitions and install GRUB.
# Requires: parted, mkfs.vfat, mkfs.ext4, grub-install, losetup, mount, qemu (optional)

IMG=${1:-alpha.img}
SIZE=${2:-512M}
MOUNT_DIR=$(mktemp -d)
ESP_MOUNT=$(mktemp -d)

echo "Creating disk image $IMG size $SIZE"
fallocate -l "$SIZE" "$IMG"

echo "Partitioning image (GPT with ESP + root)..."
parted --script "$IMG" mklabel gpt
parted --script "$IMG" mkpart ESP fat32 1MiB 261MiB
parted --script "$IMG" mkpart primary ext4 261MiB 100%
parted --script "$IMG" set 1 boot on

LOOP=$(losetup --show -f -P "$IMG")
echo "Loop device: $LOOP"
ESP_DEV=${LOOP}p1
ROOT_DEV=${LOOP}p2

echo "Formatting partitions"
mkfs.vfat -F32 "$ESP_DEV"
mkfs.ext4 -F "$ROOT_DEV"

echo "Mounting root partition"
mount "$ROOT_DEV" "$MOUNT_DIR"
mkdir -p "$MOUNT_DIR/boot/grub"

echo "Mounting ESP"
mount "$ESP_DEV" "$ESP_MOUNT"
mkdir -p "$ESP_MOUNT/EFI/BOOT"

echo "Place your kernel and grub config into $MOUNT_DIR/boot and install GRUB"
echo "Example: cp path/to/vmlinuz $MOUNT_DIR/boot/vmlinuz; create grub.cfg in $MOUNT_DIR/boot/grub"

echo "Installing GRUB (BIOS+UEFI support may require additional packages). Run as root." 
if command -v grub-install >/dev/null 2>&1; then
  grub-install --boot-directory="$MOUNT_DIR/boot" --target=i386-pc --recheck --removable "$LOOP"
  # For EFI, user should copy grubx64.efi into ESP/EFI/BOOT/BOOTX64.EFI or use grub-install with --target=x86_64-efi
else
  echo "grub-install not found; please install grub and run it manually to install a bootloader into the image." >&2
fi

echo "Syncing and cleaning up"
sync
umount "$ESP_MOUNT" || true
umount "$MOUNT_DIR" || true
losetup -d "$LOOP"
rm -rf "$MOUNT_DIR" "$ESP_MOUNT"

echo "Disk image $IMG created. Use qemu to boot for testing (see tools/qemu_boot.sh)."
