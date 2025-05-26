; calculator.asm
global sumo_uno
section .text

sumo_uno:
    push ebp  ;Extended Base Pointer, guarda el marco de la pila anterior
    mov ebp, esp  ;crea un nuevo marco de pila

    ; obtener el parámetro (float)
    fld dword [ebp+8]     ; carga el float (4 bytes)en la FPU stack (Floating point unit, para operaciones con coma)
    fistp dword [esp-4]   ; convierte float a int, guarda en la memoria (esp-4) y lo elimina de FPU
    mov eax, [esp-4]      ; copia ese valor a eax (Extended Accumulator Register - de uso general) para usarlo en c
    add eax, 1            ; le suma 1

    mov edx, [ebp+12]       ; edx = puntero a resultado
    mov [edx], eax          ; guarda eax en *resultado

    pop ebp     ;restaura el marco de la pila anterior 
    ret