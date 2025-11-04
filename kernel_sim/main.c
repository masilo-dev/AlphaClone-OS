#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <stddef.h>

int main_shell(void);

int vfs_register_backend(const char *name,
                         int (*create)(const char*, const char*),
                         char *(*read)(const char*),
                         int (*write)(const char*, const char*),
                         int (*remove)(const char*),
                         int (*list)(void),
                         void *(*open)(const char*, const char*),
                         ssize_t (*read_fd)(void*, void*, size_t),
                         ssize_t (*write_fd)(void*, const void*, size_t),
                         off_t (*seek)(void*, off_t, int),
                         int (*close)(void*));

/* hostfs backend wrappers (defined in fs.c) */
int hostfs_create(const char *name, const char *data);
char *hostfs_read(const char *name);
int hostfs_write(const char *name, const char *data);
int hostfs_remove(const char *name);
int hostfs_list(void);
void *hostfs_open(const char *name, const char *mode);
ssize_t hostfs_read_fd(void *handle, void *buf, size_t count);
ssize_t hostfs_write_fd(void *handle, const void *buf, size_t count);
off_t hostfs_seek(void *handle, off_t offset, int whence);
int hostfs_close(void *handle);

int main(int argc, char **argv) {
    (void)argc; (void)argv;
    printf("AlphaClone-OS kernel_sim prototype\n");
    printf("Storage directory: ./kernel_sim/fs_storage\n");

    /* Register the host-backed filesystem as the default VFS backend */
    vfs_register_backend("hostfs", hostfs_create, hostfs_read, hostfs_write, hostfs_remove, hostfs_list,
                         hostfs_open, hostfs_read_fd, hostfs_write_fd, hostfs_seek, hostfs_close);

    return main_shell();
}
