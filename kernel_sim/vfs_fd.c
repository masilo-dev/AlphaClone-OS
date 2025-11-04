#include "vfs.h"
#include <string.h>
#include <stdlib.h>
#include <errno.h>

/* Single backend for prototype */
static struct vfs_backend {
    const char *name;
    int (*create)(const char*, const char*);
    char *(*read)(const char*);
    int (*write)(const char*, const char*);
    int (*remove)(const char*);
    int (*list)(void);
    /* fd-style ops */
    void *(*open)(const char*, int);
    ssize_t (*read_fd)(void*, void*, size_t);
    ssize_t (*write_fd)(void*, const void*, size_t);
    off_t (*seek_fd)(void*, off_t, int);
    int (*close_fd)(void*);
} backend = {0};

/* Simple fd table: map small ints to backend handles */
#define VFS_MAX_FDS 256
static void *fd_table[VFS_MAX_FDS];

static int alloc_fd(void *handle) {
    for (int i = 3; i < VFS_MAX_FDS; ++i) {
        if (fd_table[i] == NULL) { fd_table[i] = handle; return i; }
    }
    errno = EMFILE;
    return -1;
}

static void *get_handle(int fd) {
    if (fd < 0 || fd >= VFS_MAX_FDS) return NULL;
    return fd_table[fd];
}

static void free_fd(int fd) {
    if (fd >= 0 && fd < VFS_MAX_FDS) fd_table[fd] = NULL;
}

int vfs_register_backend(const char *name,
                         int (*create)(const char*, const char*),
                         char *(*read)(const char*),
                         int (*write)(const char*, const char*),
                         int (*remove)(const char*),
                         int (*list)(void),
                         void *(*open)(const char*, int),
                         ssize_t (*read_fd)(void*, void*, size_t),
                         ssize_t (*write_fd)(void*, const void*, size_t),
                         off_t (*seek_fd)(void*, off_t, int),
                         int (*close_fd)(void*)) {
    if (!name) return -1;
    backend.name = name;
    backend.create = create;
    backend.read = read;
    backend.write = write;
    backend.remove = remove;
    backend.list = list;
    backend.open = open;
    backend.read_fd = read_fd;
    backend.write_fd = write_fd;
    backend.seek_fd = seek_fd;
    backend.close_fd = close_fd;
    /* clear fd table */
    for (int i = 0; i < VFS_MAX_FDS; ++i) fd_table[i] = NULL;
    return 0;
}

int vfs_create(const char *name, const char *data) {
    if (!backend.create) return -1;
    return backend.create(name, data);
}

char *vfs_read(const char *name) {
    if (!backend.read) return NULL;
    return backend.read(name);
}

int vfs_write(const char *name, const char *data) {
    if (!backend.write) return -1;
    return backend.write(name, data);
}

int vfs_delete(const char *name) {
    if (!backend.remove) return -1;
    return backend.remove(name);
}

int vfs_list(void) {
    if (!backend.list) return -1;
    return backend.list();
}

/* FD-style operations: allocate fd mapped to backend handle */
int vfs_open(const char *name, int flags) {
    if (!backend.open) { errno = ENOSYS; return -1; }
    void *h = backend.open(name, flags);
    if (!h) return -1;
    return alloc_fd(h);
}

ssize_t vfs_read_fd(int fd, void *buf, size_t count) {
    void *h = get_handle(fd);
    if (!h || !backend.read_fd) { errno = EBADF; return -1; }
    return backend.read_fd(h, buf, count);
}

ssize_t vfs_write_fd(int fd, const void *buf, size_t count) {
    void *h = get_handle(fd);
    if (!h || !backend.write_fd) { errno = EBADF; return -1; }
    return backend.write_fd(h, buf, count);
}

off_t vfs_seek_fd(int fd, off_t offset, int whence) {
    void *h = get_handle(fd);
    if (!h || !backend.seek_fd) { errno = EBADF; return -1; }
    return backend.seek_fd(h, offset, whence);
}

int vfs_close_fd(int fd) {
    void *h = get_handle(fd);
    if (!h || !backend.close_fd) { errno = EBADF; return -1; }
    int r = backend.close_fd(h);
    free_fd(fd);
    return r;
}
