/*
 * AlphaClone System OS - Kernel Shell Loop
 * Purpose: Offer a minimal interactive loop for diagnostics through the kernel console.
 * Author: AlphaClone Systems Core Team
 * License: MIT
 * TODO: Integrate command routing, security policies, and IPC-backed agent interactions.
 */

#include <stdint.h>
#include <stdbool.h>

void vga_console_write(const char *message);
void vga_console_write_char(char character);
void vga_console_write_line(const char *message);
bool keyboard_try_read_char(char *character);

#define SHELL_BUFFER_LENGTH 128

void shell_run(void)
{
    char buffer[SHELL_BUFFER_LENGTH];
    uint32_t length = 0;

    vga_console_write_line("Kernel shell online.");
    vga_console_write("shell> ");

    for (;;) {
        char key;
        if (!keyboard_try_read_char(&key)) {
            continue;
        }

        if (key == '\n') {
            buffer[length] = '\0';
            vga_console_write_char('\n');
            vga_console_write("ack: ");
            vga_console_write_line(buffer);
            length = 0;
            vga_console_write("shell> ");
            continue;
        }

        if (length < SHELL_BUFFER_LENGTH - 1) {
            buffer[length++] = key;
            vga_console_write_char(key);
        }
    }
}
