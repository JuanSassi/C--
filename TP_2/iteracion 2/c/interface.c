//interface.c
#include <stdio.h>
#include <stdlib.h>

//Leo el gini en el lugar 0 de argv[], convierto a float y llamo la funcion de Assembler

extern void sumo_uno(float value, int* resultado);

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Uso: %s <valor_float>\n", argv[0]);
        return 1;
    }

    float value = atof(argv[1]);
    int resultado;

    printf("GINI recibido: %.2f\n", value);

    // Pasás el float y un puntero donde guardar el resultado
    sumo_uno(value, &resultado);

    printf("Resultado adicionando 1: %d\n", resultado);

    return 0;
}