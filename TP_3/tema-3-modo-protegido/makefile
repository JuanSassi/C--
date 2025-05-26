all: protected_mode.bin

protected_mode.o: protected_mode.S
	as --32 -o protected_mode.o protected_mode.S

protected_mode.elf: protected_mode.o
	ld -m elf_i386 -Ttext 0x7c00 -nostdlib -static -o protected_mode.elf protected_mode.o

protected_mode.bin: protected_mode.elf
	objcopy -O binary protected_mode.elf protected_mode.bin
	# Aseguramos que tenga al menos 512 bytes para simular un sector de arranque
	truncate -s 512 protected_mode.bin

clean:
	rm -f *.o *.elf *.bin

run: protected_mode.bin
	qemu-system-i386 -drive format=raw,file=protected_mode.bin

debug: protected_mode.bin
	qemu-system-i386 -drive format=raw,file=protected_mode.bin -s -S &
	gdb -ex "target remote localhost:1234" \
	    -ex "set architecture i386" \
	    -ex "break *0x7c00" \
	    -ex "continue"
