# AlphaClone System OS - Build Orchestration
# Purpose: Provide reproducible build targets for kernel, ISO, agents, and runtime validation.
# Author: AlphaClone Systems Core Team
# License: MIT
# TODO: Integrate toolchain autodetection and remote cache optimizations.

NASM := nasm
CC := gcc
LD := ld
PNPM := pnpm

BUILD_DIR := build
OBJ_DIR := $(BUILD_DIR)/obj
ISO_DIR := $(BUILD_DIR)/iso

CFLAGS := -ffreestanding -O2 -nostdlib -fno-pic -fno-builtin -fno-stack-protector -Wall -Wextra
LDFLAGS := -m elf_i386 -T boot/linker.ld -nostdlib
ASFLAGS := -f elf32

KERNEL_SOURCES := \
    kernel/kernel.c \
    kernel/interrupts.c \
    kernel/memory.c \
    kernel/scheduler/scheduler.c \
    kernel/drivers/vga.c \
    kernel/drivers/keyboard.c \
    kernel/drivers/disk.c \
    kernel/shell/shell.c

KERNEL_OBJECTS := $(patsubst %.c,$(OBJ_DIR)/%.o,$(KERNEL_SOURCES))
BOOT_OBJECT := $(OBJ_DIR)/boot.o

.PHONY: all kernel iso agents run clean fmt

all: kernel agents

kernel: $(BUILD_DIR)/kernel.bin

iso: kernel
	@mkdir -p $(ISO_DIR)/boot/grub
	cp $(BUILD_DIR)/kernel.bin $(ISO_DIR)/boot/kernel.bin
	cp system/grub.cfg $(ISO_DIR)/boot/grub.cfg
	grub-mkrescue -o $(BUILD_DIR)/alpha-system.iso $(ISO_DIR)

agents:
	$(PNPM) install
	$(PNPM) build

run: iso agents
	@echo "Starting AlphaClone System OS orchestrator..."
	$(PNPM) exec node build/agents/orchestrator/src/index.js & \
	ORCH_PID=$$!; \
	sleep 2; \
	./tools/qemu_run.sh $(BUILD_DIR)/alpha-system.iso; \
	kill $$ORCH_PID || true

fmt:
	clang-format -i $(KERNEL_SOURCES)

clean:
	rm -rf $(BUILD_DIR)

$(BUILD_DIR)/kernel.bin: $(BOOT_OBJECT) $(KERNEL_OBJECTS) boot/linker.ld
	@mkdir -p $(BUILD_DIR)
	$(LD) $(LDFLAGS) -o $@ $(BOOT_OBJECT) $(KERNEL_OBJECTS)

$(OBJ_DIR)/boot.o: boot/boot.asm
	@mkdir -p $(dir $@)
	$(NASM) $(ASFLAGS) $< -o $@

$(OBJ_DIR)/%.o: %.c
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) -m32 -c $< -o $@
