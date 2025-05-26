#!/bin/bash

# Compilar y enlazar
as -g --32 -o protected_mode.o protected_mode.S

# Generar ELF primero (mejor para depuración)
ld -m elf_i386 -T link.ld -o protected_mode.elf protected_mode.o
objcopy -O binary protected_mode.elf protected_mode.img

# Verificar que el archivo binario tenga el tamaño adecuado y la firma correcta
ls -l protected_mode.img
hexdump -C -n 512 protected_mode.img | tail -2

# Iniciar QEMU con monitores separados para GDB y consola QEMU
echo "Iniciando QEMU con GDB..."
qemu-system-i386 -fda protected_mode.img -boot a -s -S -monitor stdio &

sleep 1  # Esperar a que QEMU inicie

# Iniciar GDB con configuración adecuada
echo "Iniciando GDB..."
gdb -ex "file protected_mode.elf" \
    -ex "target remote localhost:1234" \
    -ex "set architecture i386" \
    -ex "break *0x7c00" \
    -ex "continue"