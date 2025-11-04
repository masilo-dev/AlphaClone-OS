/* process.h - process table and API */

#ifndef PROCESS_H
#define PROCESS_H

typedef enum { PROC_RUNNING, PROC_SLEEPING, PROC_ZOMBIE } proc_state_t;

typedef struct process {
    int pid;
    proc_state_t state;
    char name[64];
    struct process *next;
} process_t;

process_t *proc_create(const char *name);
void proc_list_print(void);
int proc_kill(int pid);

#endif /* PROCESS_H */
