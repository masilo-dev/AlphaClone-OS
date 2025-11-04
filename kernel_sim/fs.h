/* fs.h - simple host-backed filesystem API */

#ifndef FS_H
#define FS_H

int fs_create(const char *name, const char *data);
char *fs_read(const char *name);
int fs_write(const char *name, const char *data);
int fs_delete(const char *name);
int fs_list(void);

#endif /* FS_H */
