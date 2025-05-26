#include <stdio.h>
#include <stdlib.h>

extern int float_to_int_plus_one(float);

int main() {
    float gini;
    FILE *fp = popen("python3 python/main.py", "r");
    if (fp == NULL) {
        perror("Error ejecutando script Python");
        return 1;
    }

    fscanf(fp, "%f", &gini);
    pclose(fp);

    printf("GINI recibido: %.2f\n", gini);
    int result = float_to_int_plus_one(gini);
    printf("Resultado final (int +1): %d\n", result);

    return 0;
}

