#include <stdio.h>

extern void sumo_uno(float value, int* resultado);

int main() {
    float gini = 42.7;

    printf("Antes de llamar a sumo_uno\n");

    int resultado = 0;
    sumo_uno(gini, &resultado);

    printf("Después de llamar a sumo_uno\n");

    printf("Resultado retornado: %d\n", resultado);

    return 0;
}