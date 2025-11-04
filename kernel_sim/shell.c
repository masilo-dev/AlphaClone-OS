#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Include public headers for FS and process APIs */
#include "vfs.h"
#include "fs.h"
#include "process.h"

static void prompt(void) {
    printf("alpha> ");
    fflush(stdout);
}

int main_shell(void) {
    char line[1024];
    while (1) {
        prompt();
        if (!fgets(line, sizeof(line), stdin)) break;
        // Trim newline
        line[strcspn(line, "\n")] = '\0';
        if (strlen(line) == 0) continue;
        char *cmd = strtok(line, " ");
        if (!cmd) continue;
        if (strcmp(cmd, "help") == 0) {
            printf("commands: ls, cat <f>, write <f> <text>, rm <f>, touch <f>, run <name>, ps, kill <pid>, exit\n");
        } else if (strcmp(cmd, "ls") == 0) {
            vfs_list();
        } else if (strcmp(cmd, "cat") == 0) {
            char *name = strtok(NULL, " ");
            if (!name) { printf("usage: cat <file>\n"); continue; }
            char *data = vfs_read(name);
            if (!data) printf("cannot read '%s'\n", name);
            else { printf("%s\n", data); free(data); }
        } else if (strcmp(cmd, "write") == 0) {
            char *name = strtok(NULL, " ");
            char *text = strtok(NULL, "");
            if (!name || !text) { printf("usage: write <file> <text>\n"); continue; }
            if (vfs_write(name, text) == 0) printf("wrote %s\n", name); else printf("write failed\n");
        } else if (strcmp(cmd, "touch") == 0) {
            char *name = strtok(NULL, " ");
            if (!name) { printf("usage: touch <file>\n"); continue; }
            if (vfs_create(name, "") == 0) printf("created %s\n", name); else printf("create failed\n");
        } else if (strcmp(cmd, "rm") == 0) {
            char *name = strtok(NULL, " ");
            if (!name) { printf("usage: rm <file>\n"); continue; }
            if (vfs_delete(name) == 0) printf("deleted %s\n", name); else printf("delete failed\n");
        } else if (strcmp(cmd, "run") == 0) {
            char *name = strtok(NULL, " ");
            if (!name) { printf("usage: run <name>\n"); continue; }
            process_t *p = proc_create(name);
            if (!p) printf("failed to create process\n"); else printf("started %s pid=%d\n", p->name, p->pid);
        } else if (strcmp(cmd, "ps") == 0) {
            proc_list_print();
        } else if (strcmp(cmd, "kill") == 0) {
            char *pid_s = strtok(NULL, " ");
            if (!pid_s) { printf("usage: kill <pid>\n"); continue; }
            int pid = atoi(pid_s);
            if (proc_kill(pid) == 0) printf("killed %d\n", pid); else printf("no such pid\n");
        } else if (strcmp(cmd, "exit") == 0) {
            break;
        } else {
            printf("unknown: %s\n", cmd);
        }
    }
    return 0;
}
