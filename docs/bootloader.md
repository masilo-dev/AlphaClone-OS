# Bootloader & Installation Plan

This document outlines a pragmatic, GRUB-based approach for creating bootable disk images for AlphaClone-OS.

Goals
- Produce a reproducible disk image that boots in QEMU and on real hardware via GRUB.
- Keep the initial kernel simple (ELF multiboot-compatible or a GRUB-compatible kernel stub).

Disk layout (suggested)
- MBR or GPT partition table (GPT recommended for modern systems).
- Partition 1: EFI System Partition (FAT32) — contains GRUB EFI binary.
- Partition 2: Root filesystem (ext2/ext4 or FAT32 for testing) — contains kernel image, initramfs, and /boot/grub.

Boot path (UEFI)
1. UEFI firmware loads GRUB EFI from the ESP.
2. GRUB config points to kernel (ELF/vmlinuz) and initramfs. GRUB passes control to the kernel.

Boot path (Legacy BIOS)
1. GRUB (in MBR) loads core.img and stage2, then loads kernel and initramfs.

Kernel format
- Start with a multiboot2-compliant ELF kernel or use GRUB's kexec support.
- Long-term: consider implementing a multiboot2 header for kernel entry and handing control to C/Rust entry point.

Installation process (prototype)
1. Build kernel binary (or use a simple bootable initrd for initial tests).
2. Create disk image: partition, format ESP as FAT32, format root partition as ext2.
3. Mount partitions and install files: GRUB EFI on ESP, kernel and grub config in /boot on root.
4. Install GRUB: use grub-install --target=x86_64-efi --boot-directory=/mnt/root/boot --efi-directory=/mnt/esp --removable for UEFI testing; for BIOS use grub-install to the image loop device.

Testing in QEMU
- Example (EFI): create EFI image and boot with OVMF for UEFI support.
- Example (BIOS): qemu-system-x86_64 -drive file=disk.img,format=raw -m 1G -serial stdio

Security and signing
- Initially skip kernel signing for fast prototyping.
- For production, create a secure boot plan: sign bootloader and kernel, provide keys in firmware.

Next steps
- Add `tools/` scripts to create disk images and automate GRUB installation.
- Choose kernel entry protocol (multiboot2) and implement a minimal kernel ELF with a multiboot header.
