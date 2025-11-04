# kernel_sim — AlphaClone-OS prototype

This is a userland simulator to exercise the kernel design: a small C program that implements
- a host-backed simple filesystem (CRUD) under `kernel_sim/fs_storage`
- a tiny process table simulation
- a basic interactive shell to run commands and create processes

Build

From the repository root:

```bash
make -C kernel_sim
```

Run

```bash
./kernel_sim/kernel_sim
```

Commands supported by the shell:
- ls
- cat <file>
- write <file> <text>
- touch <file>
- rm <file>
- run <name>     (create a simulated process)
- ps
- kill <pid>
- help
- exit

This is a prototype to validate interfaces. The real kernel will replace the simulator with proper
process scheduling, memory management, drivers, and a bootloader.
