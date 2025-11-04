#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include "vfs.h"

/* Declarations for hostfs backend (from fs.c) */
int hostfs_create(const char *name, const char *data);
char *hostfs_read(const char *name);
int hostfs_write(const char *name, const char *data);
int hostfs_remove(const char *name);
int hostfs_list(void);
void *hostfs_open_flags(const char *name, int flags);
ssize_t hostfs_read_fd(void *handle, void *buf, size_t count);
ssize_t hostfs_write_fd(void *handle, const void *buf, size_t count);
off_t hostfs_seek_fd(void *handle, off_t offset, int whence);
int hostfs_close(void *handle);

int main(void) {
    /* Register hostfs as the backend for this example */
    vfs_register_backend("hostfs", hostfs_create, hostfs_read, hostfs_write, hostfs_remove, hostfs_list,
                         hostfs_open_flags, hostfs_read_fd, hostfs_write_fd, hostfs_seek_fd, hostfs_close);

    const char *fname = "vfs_example.txt";
    vfs_create(fname, "Initial content\n");
    int fd = vfs_open(fname, O_RDWR | O_CREAT);
    if (fd < 0) { perror("vfs_open"); return 1; }
    const char *more = "Appended by vfs_user\n";
    if (vfs_write_fd(fd, more, strlen(more)) < 0) { perror("vfs_write_fd"); return 1; }
    if (vfs_seek_fd(fd, 0, SEEK_SET) < 0) { perror("vfs_seek_fd"); return 1; }
    char buf[256];
    ssize_t n = vfs_read_fd(fd, buf, sizeof(buf)-1);
    if (n < 0) { perror("vfs_read_fd"); return 1; }
    buf[n] = '\0';
    printf("Read from %s:\n%s", fname, buf);
    vfs_close_fd(fd);
    return 0;
}
