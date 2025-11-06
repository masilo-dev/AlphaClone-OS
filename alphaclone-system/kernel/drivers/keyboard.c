/*
 * AlphaClone System OS - Keyboard Driver Scaffold
 * Purpose: Offer PS/2 keyboard initialization and non-blocking key read interface for the shell.
 * Author: AlphaClone Systems Core Team
 * License: MIT
 * TODO: Implement interrupt-driven key handling with scancode translation and layouts.
 */

#include <stdint.h>
#include <stdbool.h>

#define PS2_STATUS_PORT 0x64
#define PS2_DATA_PORT 0x60

static inline uint8_t io_in8(uint16_t port)
{
    uint8_t value;
    __asm__ volatile("inb %1, %0" : "=a"(value) : "Nd"(port));
    return value;
}

static inline void io_out8(uint16_t port, uint8_t value)
{
    __asm__ volatile("outb %0, %1" : : "a"(value), "Nd"(port));
}

void keyboard_initialize(void)
{
    io_out8(PS2_STATUS_PORT, 0xAE);
    (void)io_in8(PS2_DATA_PORT);
}

static bool scan_code_available(void)
{
    return (io_in8(PS2_STATUS_PORT) & 0x01) != 0;
}

bool keyboard_try_read_char(char *character)
{
    if (!character || !scan_code_available()) {
        return false;
    }

    const uint8_t scancode = io_in8(PS2_DATA_PORT);

    if (scancode == 0x1C) {
        *character = '\n';
        return true;
    }

    if (scancode >= 0x02 && scancode <= 0x0A) {
        static const char number_map[] = "1234567890";
        *character = number_map[scancode - 0x02];
        return true;
    }

    if (scancode >= 0x10 && scancode <= 0x32) {
        static const char letter_map[] = "qwertyuiopasdfghjklzxcvbnm";
        const uint8_t offset = scancode - 0x10;
        if (offset < sizeof(letter_map) - 1U) {
            *character = letter_map[offset];
            return true;
        }
    }

    return false;
}
