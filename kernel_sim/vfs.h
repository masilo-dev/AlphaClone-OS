/* vfs.h - virtual filesystem interface */

/* vfs.h - virtual filesystem interface */

#ifndef VFS_H
#define VFS_H

#include <sys/types.h>
#include <stddef.h>
#include <unistd.h>
#include <fcntl.h>

/* Simple VFS API for the simulator. Backends implement the operations below. */

/* Backend registration: path ops + fd-style ops. The fd-style open returns an
 * opaque pointer (backend handle) which is stored in the VFS FD table. */
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
                         int (*close_fd)(void*));

/* Path-based convenience API */
int vfs_create(const char *name, const char *data);
char *vfs_read(const char *name);
int vfs_write(const char *name, const char *data);
int vfs_delete(const char *name);
int vfs_list(void);

/* File-descriptor-like API (simulated) */
int vfs_open(const char *name, int flags);
ssize_t vfs_read_fd(int fd, void *buf, size_t count);
ssize_t vfs_write_fd(int fd, const void *buf, size_t count);
off_t vfs_seek_fd(int fd, off_t offset, int whence);
int vfs_close_fd(int fd);

#endif /* VFS_H */
