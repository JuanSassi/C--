SECTIONS
{
    /* The BIOS loads the code from the disk to this location */
    . = 0x7c00;
    
    .text : {
        __start = .;
        *(.text)
        *(.rodata)
        *(.data)
        *(.bss)
        /* Si queremos que el linker coloque la firma automáticamente */
        /* Descomenta estas líneas si no usas .org 510 en el código */
        /* . = 510; */
        /* SHORT(0xAA55) */
    }
}
