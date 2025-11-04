#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/*
 * simple_user.c
 * A tiny example "user" program that demonstrates file operations
 * by writing directly into the simulator storage directory.
 * This simulates a user program performing file I/O that the OS would
 * eventually mediate via syscalls/VFS.
 */

int main(int argc, char **argv) {
    (void)argc; (void)argv;
    const char *path = "fs_storage/example_from_user.txt";
    FILE *f = fopen(path, "w");
    if (!f) {
        perror("fopen");
        return 1;
    }
    if (fprintf(f, "Hello from simple_user!\n") < 0) {
        perror("fprintf");
        fclose(f);
        return 1;
    }
    if (fclose(f) != 0) {
        perror("fclose");
        return 1;
    }
    printf("Wrote %s\n", path);
    return 0;
}
