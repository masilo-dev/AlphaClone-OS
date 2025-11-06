/*
 * AlphaClone System OS - VGA Text Driver
 * Purpose: Provide minimal console output services for early boot diagnostics.
 * Author: AlphaClone Systems Core Team
 * License: MIT
 * TODO: Extend with color management, scrolling, and multi-console abstractions.
 */

#include <stdint.h>

#define VGA_WIDTH 80
#define VGA_HEIGHT 25
#define VGA_COLOR 0x0F

static volatile uint16_t *const vga_buffer = (uint16_t *)0xB8000;
static uint8_t cursor_row = 0;
static uint8_t cursor_column = 0;

static uint16_t vga_entry(char character)
{
    return (uint16_t)character | ((uint16_t)VGA_COLOR << 8);
}

void vga_console_initialize(void)
{
    cursor_row = 0;
    cursor_column = 0;
}

void vga_console_clear(void)
{
    for (uint32_t index = 0; index < VGA_WIDTH * VGA_HEIGHT; ++index) {
        vga_buffer[index] = vga_entry(' ');
    }
    cursor_row = 0;
    cursor_column = 0;
}

static void vga_put_character(char character)
{
    if (character == '\n') {
        cursor_column = 0;
        if (++cursor_row >= VGA_HEIGHT) {
            cursor_row = VGA_HEIGHT - 1;
        }
        return;
    }

    const uint32_t position = cursor_row * VGA_WIDTH + cursor_column;
    vga_buffer[position] = vga_entry(character);

    if (++cursor_column >= VGA_WIDTH) {
        cursor_column = 0;
        if (++cursor_row >= VGA_HEIGHT) {
            cursor_row = VGA_HEIGHT - 1;
        }
    }
}

void vga_console_write(const char *message)
{
    if (!message) {
        return;
    }

    while (*message) {
        vga_put_character(*message++);
    }
}

void vga_console_write_char(char character)
{
    vga_put_character(character);
}

void vga_console_write_line(const char *message)
{
    if (!message) {
        return;
    }

    vga_console_write(message);
    vga_put_character('\n');
}
