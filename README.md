# AlphaClone-OS
AlphaClone OS is a next-generation, cloud-powered operating system built entirely online — designed to merge traditional system architecture with modern AI capabilities. It’s not just an “OS” — it’s a unified environment for apps, automation, and intelligence.

AlphaClone OS is a next-generation, modular operating system project. The long-term goal is a full OS with a kernel, drivers, filesystems, and userland. This repository contains initial design docs and a small userland "kernel simulator" to prototype interfaces.

Quickstart — build the simulator

From the repository root:

```bash
make -C kernel_sim
./kernel_sim/kernel_sim
```

This will start a simple interactive shell which uses a host-backed directory (`kernel_sim/fs_storage`) as the storage backend.

What we added
- `docs/architecture.md` — high-level design and components
- `docs/CONTRIBUTING.md` — contribution guide
- `kernel_sim/` — prototype simulator with a small filesystem, process table, and interactive shell

Roadmap (short)
1. Design and iterate on kernel APIs (VFS, syscalls, device model).
2. Implement a real kernel (initially in C/Rust), add bootloader and image creation.
3. Add drivers (keyboard, display, storage) and a production filesystem (ext2/FAT32).

See `docs/architecture.md` for details and the top-level todo list tracked in the project.
