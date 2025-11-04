#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>

// Simple host-backed filesystem adapter. Stores files under ./fs_storage

static const char *STORAGE_DIR = "fs_storage";

static int ensure_storage_dir(void) {
    struct stat st;
    if (stat(STORAGE_DIR, &st) == 0) return 0;
    if (mkdir(STORAGE_DIR, 0755) != 0) return -1;
    return 0;
}

int fs_create(const char *name, const char *data) {
    if (ensure_storage_dir() != 0) return -1;
    char path[1024];
    snprintf(path, sizeof(path), "%s/%s", STORAGE_DIR, name);
    FILE *f = fopen(path, "w");
    if (!f) return -1;
    if (data) fputs(data, f);
    fclose(f);
    return 0;
}

char *fs_read(const char *name) {
    char path[1024];
    snprintf(path, sizeof(path), "%s/%s", STORAGE_DIR, name);
    FILE *f = fopen(path, "r");
    if (!f) return NULL;
    fseek(f, 0, SEEK_END);
    long sz = ftell(f);
    fseek(f, 0, SEEK_SET);
    if (sz < 0) { fclose(f); return NULL; }
    /* handle empty files */
    if (sz == 0) {
        char *buf = malloc(1);
        if (!buf) { fclose(f); return NULL; }
        buf[0] = '\0';
        fclose(f);
        return buf;
    }
    char *buf = malloc((size_t)sz + 1);
    if (!buf) { fclose(f); return NULL; }
    size_t n = fread(buf, 1, (size_t)sz, f);
    if (n != (size_t)sz) {
        /* truncated read or error */
        free(buf);
        fclose(f);
        return NULL;
    }
    buf[sz] = '\0';
    fclose(f);
    return buf;
}

int fs_write(const char *name, const char *data) {
    return fs_create(name, data);
}

int fs_delete(const char *name) {
    char path[1024];
    snprintf(path, sizeof(path), "%s/%s", STORAGE_DIR, name);
    if (remove(path) != 0) return -1;
    return 0;
}

int fs_list(void) {
    if (ensure_storage_dir() != 0) return -1;
    DIR *d = opendir(STORAGE_DIR);
    if (!d) return -1;
    struct dirent *ent;
    while ((ent = readdir(d)) != NULL) {
        if (strcmp(ent->d_name, ".") == 0 || strcmp(ent->d_name, "..") == 0) continue;
        printf("%s\n", ent->d_name);
    }
    closedir(d);
    return 0;
}

/* Host backend wrappers for VFS registration */
int hostfs_create(const char *name, const char *data) { return fs_create(name, data); }
char *hostfs_read(const char *name) { return fs_read(name); }
int hostfs_write(const char *name, const char *data) { return fs_write(name, data); }
int hostfs_remove(const char *name) { return fs_delete(name); }
int hostfs_list(void) { return fs_list(); }

/* fd-style backend operations using FILE* handles */
void *hostfs_open(const char *name, const char *mode) {
    if (ensure_storage_dir() != 0) return NULL;
    char path[1024];
    snprintf(path, sizeof(path), "%s/%s", STORAGE_DIR, name);
    FILE *f = fopen(path, mode);
    return (void*)f;
}

ssize_t hostfs_read_fd(void *handle, void *buf, size_t count) {
    if (!handle) return -1;
    FILE *f = (FILE*)handle;
    size_t n = fread(buf, 1, count, f);
    if (n == 0 && ferror(f)) return -1;
    return (ssize_t)n;
}

ssize_t hostfs_write_fd(void *handle, const void *buf, size_t count) {
    if (!handle) return -1;
    FILE *f = (FILE*)handle;
    size_t n = fwrite(buf, 1, count, f);
    if (n != count) return -1;
    return (ssize_t)n;
}

off_t hostfs_seek(void *handle, off_t offset, int whence) {
    if (!handle) return -1;
    FILE *f = (FILE*)handle;
    if (fseek(f, (long)offset, whence) != 0) return -1;
    long pos = ftell(f);
    if (pos < 0) return -1;
    return (off_t)pos;
}

int hostfs_close(void *handle) {
    if (!handle) return -1;
    FILE *f = (FILE*)handle;
    return fclose(f);
}
/* Host backend wrappers for VFS registration */

/* flag-based open wrapper: convert POSIX flags to fopen mode string */
void *hostfs_open_flags(const char *name, int flags) {
    const char *mode = "r";
    if ((flags & O_RDWR) == O_RDWR) mode = "r+";
    else if (flags & O_WRONLY) mode = (flags & O_TRUNC) ? "w" : "a";
    else if (flags & O_RDONLY) mode = "r";
    /* fallback to write */
    if ((flags & O_CREAT) && !(flags & O_WRONLY)) mode = "w";
    return hostfs_open(name, mode);
}

/* alias to match vfs expected names */
ssize_t hostfs_seek_fd(void *handle, off_t offset, int whence) { return hostfs_seek(handle, offset, whence); }


