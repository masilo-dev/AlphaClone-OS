/*
 * AlphaClone System OS - Interrupt Descriptor Table Setup
 * Purpose: Provide initialization scaffolding for the IDT and core interrupt gates.
 * Author: AlphaClone Systems Core Team
 * License: MIT
 * TODO: Populate full IDT entries and wire real interrupt handlers for hardware devices.
 */

#include <stdint.h>

#define IDT_ENTRY_COUNT 256

struct interrupt_gate {
    uint16_t offset_low;
    uint16_t selector;
    uint8_t zero;
    uint8_t type_attributes;
    uint16_t offset_high;
} __attribute__((packed));

struct idt_register {
    uint16_t limit;
    uint32_t base;
} __attribute__((packed));

static struct interrupt_gate interrupt_table[IDT_ENTRY_COUNT];

static void set_gate(uint8_t index, uint32_t handler, uint16_t selector, uint8_t type)
{
    interrupt_table[index].offset_low = handler & 0xFFFF;
    interrupt_table[index].selector = selector;
    interrupt_table[index].zero = 0;
    interrupt_table[index].type_attributes = type;
    interrupt_table[index].offset_high = (handler >> 16) & 0xFFFF;
}

void interrupts_initialize(void)
{
    struct idt_register idtr;
    idtr.limit = sizeof(interrupt_table) - 1;
    idtr.base = (uint32_t)&interrupt_table[0];

    for (uint16_t index = 0; index < IDT_ENTRY_COUNT; ++index) {
        set_gate(index, 0, 0x08, 0x8E);
    }

    __asm__ volatile("lidt %0" : : "m"(idtr));
    __asm__ volatile("sti");
}
