/*
 * AlphaClone System OS - Linker Script
 * Purpose: Define kernel memory layout with entry point at 1 MiB for Multiboot.
 * Author: AlphaClone Systems Core Team
 * License: MIT
 * TODO: Harden memory regions and add per-section protections.
 */

ENTRY(start)

SECTIONS
{
    . = 0x00100000;

    .text ALIGN(4K) :
    {
        *(.multiboot)
        *(.text*)
    }

    .rodata ALIGN(4K) :
    {
        *(.rodata*)
    }

    .data ALIGN(4K) :
    {
        *(.data*)
    }

    .bss ALIGN(4K) :
    {
        *(COMMON)
        *(.bss*)
    }
}
