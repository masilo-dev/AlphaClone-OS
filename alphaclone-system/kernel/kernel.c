/*
 * AlphaClone System OS - Kernel Entry
 * Purpose: Bootstrap core subsystems and start the scheduler loop after bootloader handoff.
 * Author: AlphaClone Systems Core Team
 * License: MIT
 * TODO: Integrate real interrupt controller, memory manager, and multi-core scheduler.
 */

#include <stdint.h>
#include <stddef.h>

void vga_console_initialize(void);
void vga_console_clear(void);
void vga_console_write_line(const char *message);
void interrupts_initialize(void);
void memory_initialize(const void *multiboot_info);
void keyboard_initialize(void);
void scheduler_initialize(void);
void scheduler_enter(void);
void shell_run(void);

void kernel_main(uint32_t multiboot_magic, uint32_t multiboot_info_address)
{
    (void)multiboot_magic;          /* Multiboot validations handled in future revisions. */

    vga_console_initialize();
    vga_console_clear();

    interrupts_initialize();
    memory_initialize((const void *)(uintptr_t)multiboot_info_address);
    keyboard_initialize();
    scheduler_initialize();

    vga_console_write_line("AlphaClone System OS — Kernel boot successful");

    shell_run();
    scheduler_enter();

    for (;;) {
        __asm__ volatile("hlt");
    }
}
