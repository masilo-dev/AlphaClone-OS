# Examples for kernel_sim

This folder contains small example programs that demonstrate user-like file operations.

- `simple_user.c` — writes `fs_storage/example_from_user.txt` using standard C I/O. This simulates a user program performing file operations while the simulator is running.
- `demo.sh` — runs a short scripted sequence against `kernel_sim` (write, list, cat) to demonstrate the shell and VFS.
