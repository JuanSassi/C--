# protected_mode.S - Ejemplo de cambio a modo protegido con dos segmentos diferentes
# (código y datos) con segmento de datos configurado como solo lectura

.code16
.global _start

_start:
    # Inicializar segmentos en modo real
    xorw    %ax, %ax
    movw    %ax, %ds
    movw    %ax, %es
    movw    %ax, %ss
    movw    $0x7C00, %sp      # Establecer el stack pointer

    # Mensaje de inicio en modo real (para verificar que el código se está ejecutando)
    movw    $msg_real_mode, %si
    call    print_string

    # Deshabilitar interrupciones
    cli

    # Cargar la GDT
    lgdt    gdt_descriptor

    # Habilitar bit de modo protegido (PE) en CR0
    movl    %cr0, %eax
    orl     $1, %eax
    movl    %eax, %cr0

    # Salto lejos para cargar CS con el selector de segmento de código
    ljmp    $0x08, $protected_mode

# Rutina para imprimir un string en modo real (usando BIOS)
print_string:
    lodsb                  # Cargar un byte de [SI] en AL e incrementar SI
    testb   %al, %al       # Verificar si es el carácter nulo (fin de string)
    jz      done_print     # Si es cero, terminar
    movb    $0x0E, %ah     # Función 0x0E de la int 0x10 (imprimir carácter)
    movw    $0x0007, %bx   # Página 0, atributo 7 (normal)
    int     $0x10          # Llamar a la interrupción de BIOS
    jmp     print_string   # Continuar con el siguiente carácter
done_print:
    ret

.code32
protected_mode:
    # Ya estamos en modo protegido, configurar los selectores de segmento
    # 0x10 es el selector del segmento de datos (índice 2, TI=0, RPL=0)
    movw    $0x10, %ax
    movw    %ax, %ds
    movw    %ax, %es
    movw    %ax, %ss
    movw    %ax, %fs
    movw    %ax, %gs

    # En modo protegido, mostrar algo en pantalla (directamente en memoria de video)
    # Memoria de video en 0xB8000
    movl    $0xB8000, %edi
    movl    $0x1F501F50, (%edi)    # 'P' en blanco sobre azul

    # Intentar escribir en el segmento de datos (generará excepción)
    movl    $0xDEADBEEF, data_test

    # Si llegamos aquí, la escritura no causó una excepción (algo está mal)
    # Mostrar alguna indicación visual
    movl    $0x1F451F45, 4(%edi)   # 'E' en blanco sobre azul

halt:
    # Bucle infinito
    hlt
    jmp     halt

# Mensajes
msg_real_mode:
    .asciz "Iniciando modo protegido...\r\n"

# Datos estáticos
.align 4
data_test:
    .long   0x12345678

# Alineación para la GDT
.align 8
gdt:
    # Descriptor nulo (índice 0)
    .quad   0

    # Descriptor de segmento de código (índice 1, selector 0x08)
    # Base 0x00000000, Límite 0xFFFFF (4GB)
    # P=1, DPL=00, S=1, Type=1010 (Code Execute/Read)
    # G=1, D=1, L=0, AVL=0
    .word   0xFFFF      # Límite [0:15]
    .word   0x0000      # Base [0:15]
    .byte   0x00        # Base [16:23]
    .byte   0x9A        # Acceso (P=1, DPL=00, S=1, Type=1010)
    .byte   0xCF        # Granularidad (G=1, D=1, L=0, AVL=0) + Límite [16:19]
    .byte   0x00        # Base [24:31]

    # Descriptor de segmento de datos de solo lectura (índice 2, selector 0x10)
    # Base 0x00000000, Límite 0xFFFFF (4GB)
    # P=1, DPL=00, S=1, Type=0010 (Data Read-Only)
    # G=1, D=1, L=0, AVL=0
    .word   0xFFFF      # Límite [0:15]
    .word   0x0000      # Base [0:15]
    .byte   0x00        # Base [16:23]
    .byte   0x92        # Acceso (P=1, DPL=00, S=1, Type=0010)
    #.byte   0x90        # Acceso (P=1, DPL=00, S=1, Type=0000) => Read-Only
    .byte   0xCF        # Granularidad (G=1, D=1, L=0, AVL=0) + Límite [16:19]
    .byte   0x00        # Base [24:31]

gdt_descriptor:
    .word   gdt_descriptor - gdt - 1    # Tamaño de la GDT
    .long   gdt                         # Dirección lineal de la GDT

# Asegurar que tenemos la firma de arranque
.org 510
.word 0xAA55