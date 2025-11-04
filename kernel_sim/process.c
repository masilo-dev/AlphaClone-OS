#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef enum { PROC_RUNNING, PROC_SLEEPING, PROC_ZOMBIE } proc_state_t;

typedef struct process {
    int pid;
    proc_state_t state;
    char name[64];
    struct process *next;
} process_t;

static process_t *proc_list = NULL;
static int next_pid = 1;

process_t *proc_create(const char *name) {
    process_t *p = malloc(sizeof(process_t));
    if (!p) return NULL;
    p->pid = next_pid++;
    p->state = PROC_RUNNING;
    strncpy(p->name, name, sizeof(p->name)-1);
    p->name[sizeof(p->name)-1] = '\0';
    p->next = proc_list;
    proc_list = p;
    return p;
}

void proc_list_print(void) {
    process_t *it = proc_list;
    printf("PID\tSTATE\tNAME\n");
    while (it) {
        const char *s = it->state==PROC_RUNNING?"RUN":(it->state==PROC_SLEEPING?"SLEEP":"ZOMBIE");
        printf("%d\t%s\t%s\n", it->pid, s, it->name);
        it = it->next;
    }
}

int proc_kill(int pid) {
    process_t *it = proc_list;
    while (it) {
        if (it->pid == pid) { it->state = PROC_ZOMBIE; return 0; }
        it = it->next;
    }
    return -1;
}
