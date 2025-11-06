; AlphaClone System OS - Bootloader Entry
; Purpose: Provide GRUB-compliant Multiboot header and bootstrap into kernel_main.
; Author: AlphaClone Systems Core Team
; License: MIT
; TODO: Replace stub stack setup with architecture abstraction and SMP bring-up.

BITS 32

ALIGN 4
MULTIBOOT_MAGIC      equ 0x1BADB002
MULTIBOOT_FLAGS      equ 0x00000003
MULTIBOOT_CHECKSUM   equ -(MULTIBOOT_MAGIC + MULTIBOOT_FLAGS)

section .multiboot
align 4
multiboot_header:
    dd MULTIBOOT_MAGIC
    dd MULTIBOOT_FLAGS
    dd MULTIBOOT_CHECKSUM
    dd multiboot_header
    dd 0
    dd 0
    dd 0
    dd 0

section .text
global start
extern kernel_main

start:
    cli
    mov esp, stack_top
    push eax                 ; Multiboot magic
    push ebx                 ; Multiboot info pointer
    call kernel_main

.hang:
    cli
    hlt
    jmp .hang

section .bss
align 16
stack_bottom:
    resb 4096
stack_top:

section .note.GNU-stack noalloc noexec nowrite progbits
