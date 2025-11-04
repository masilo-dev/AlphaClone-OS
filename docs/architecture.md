# AlphaClone-OS — Architecture Overview

This document describes the high-level architecture and design choices for AlphaClone-OS.

Goals
- Modularity: components (bootloader, kernel, drivers, vfs, userland) must be replaceable.
- Safety: prefer memory-safe languages where feasible; C is used for low-level prototype.
- Extensibility: clear driver/FS/IPC interfaces.

Languages
- Prototype / simulator: C (portable, easy to build).
- Long-term kernel: consider Rust for memory safety; C is acceptable for low-level parts.

Boot flow (target)
1. Bootloader (GRUB or custom multiboot) loads the kernel image.
2. Kernel init: CPU setup, paging, basic memory manager, device enumeration.
3. Mount root filesystem and spawn init process (PID 1).

Kernel components
- Process manager: create/terminate processes, context switch, simple scheduler (round-robin -> priority).
- Memory manager: physical memory allocator + virtual memory mappings (paging).
- I/O and drivers: device abstraction layer, driver registration, request queues.
- VFS: unified file API with filesystem drivers (ext2/FAT32) and device nodes.

Filesystem
- Provide VFS interface with CRUD and metadata operations.
- Prototype uses a host-backed simple FS; production will target ext2 or FAT32 for simplicity.

User interface
- Step 1: CLI shell with basic commands (ls, cat, write, rm, run, ps).
- Step 2: optional lightweight GUI using framebuffer + simple window manager.

Device drivers
- Keyboard: interrupt-driven input.
- Framebuffer/display: basic text console and graphical mode.
- Storage: block device driver that exposes a block API to the VFS.

Modularity & ABI
- Kernel exposes a minimal syscall ABI for user programs.
- Drivers register through a device manager and expose standardized ops.

Notes & Next Steps
- This repo contains a kernel_sim prototype (userland simulator) to exercise the VFS and basic scheduling design while we work on a real kernel and bootloader.
