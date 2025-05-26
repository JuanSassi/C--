# Trabajo Práctico 1: Rendimiento 
## Introduccion 
El objetivo de este primer trabajo práctico es analizar el rendimiento de los sistemas informáticos y cuantificarlo. Para ello, se emplearán benchmarks y herramientas como GPROF y perf para medir la performance del código en una ESP32.

Evaluar el rendimiento de un sistema es fundamental para optimizar su desempeño y garantizar su eficiencia. Para ello, se utilizan métricas y herramientas que permiten medir su capacidad para ejecutar tareas en un tiempo determinado. Entre estas técnicas, los benchmarks se han consolidado como una de las más utilizadas, ya que ofrecen una manera objetiva y reproducible de comparar el rendimiento en distintos escenarios y cargas de trabajo.

El análisis de rendimiento no solo se centra en el hardware, sino también en el software, el sistema operativo y la arquitectura de los programas. Dependiendo de la aplicación, algunos benchmarks pueden ser más representativos que otros, lo que permite tomar decisiones informadas sobre optimización y adquisición de equipos.

---

## Marco Teorico
### **Benchmarks**
Una de las formas más precisas y confiables de medir el rendimiento de un sistema informático es evaluar el tiempo que tarda en ejecutar los programas que realmente serán utilizados por el usuario. Sin embargo, esta medición es subjetiva, ya que el rendimiento óptimo varía según la aplicación y las necesidades específicas de cada usuario.
El desempeño de una estación de trabajo se analiza considerando diversos factores físicos y lógicos que afectan su funcionamiento global. Para obtener una visión completa del rendimiento del sistema, es necesario evaluar no solo el hardware, sino también el sistema operativo, los dispositivos de red, los compiladores y las bibliotecas utilizadas en el software.

**Tipos de Benchmarks**

Existen diferentes tipos de benchmarks utilizados para evaluar el rendimiento de un sistema:
- Benchmarks sintéticos: Son pruebas diseñadas específicamente para medir el rendimiento de un sistema bajo condiciones controladas. Suelen ser programas pequeños que simulan cargas de trabajo específicas, proporcionando métricas comparativas entre diferentes configuraciones de hardware o software.
- Benchmarks reducidos: Son fragmentos de código extraídos de aplicaciones reales, que permiten medir el rendimiento de partes específicas del sistema sin necesidad de ejecutar el programa completo.
- Benchmarks kernel o de núcleo: Evaluan el rendimiento de componentes clave del sistema, como el procesamiento de instrucciones básicas o el acceso a memoria, con el objetivo de analizar el comportamiento del hardware ante ciertas tareas fundamentales.
- Programas reales: Se basan en la ejecución de software utilizado en entornos reales, proporcionando una medición más representativa del rendimiento en condiciones de uso cotidianas.

### **Rendimiento**
El rendimiento de un sistema se define como su capacidad para completar una tarea en un tiempo determinado. Se trata de una relación inversa entre tiempo y eficiencia: cuanto mayor sea el tiempo requerido para realizar una operación, menor será el rendimiento.
Dado que los sistemas informáticos ejecutan programas mediante instrucciones, su rendimiento está directamente relacionado con el tiempo de ejecución de dichos programas. En este sentido, el tiempo es la métrica fundamental para evaluar la eficiencia de un computador.

**Medidas de desempeño**

Para evaluar el rendimiento de un sistema se utilizan diversas métricas, entre ellas:
- Ciclos por instrucción (CPI): Indica el número promedio de ciclos de reloj requeridos para ejecutar una instrucción.
- Instrucciones por ciclo (IPC): Mide cuántas instrucciones se pueden ejecutar en un solo ciclo de reloj.
- Rendimiento (Throughput): Representa la cantidad de tareas o instrucciones completadas en un período de tiempo determinado.
- Latencia: Se refiere al tiempo total que tarda una tarea en completarse desde su inicio hasta su finalización.
- Speedup: Relaciona el rendimiento de dos sistemas distintos o de un mismo sistema antes y después de una mejora.
- Eficiencia: Evalúa el aprovechamiento de los recursos del sistema en función del rendimiento obtenido.

**Factores que afectan el rendimiento del procesador**

El desempeño de un procesador depende de múltiples factores, entre los cuales destacan:
- Frecuencia de la CPU (fCPU): Indica la cantidad de ciclos por segundo que ejecuta el procesador. Es importante diferenciar la frecuencia de la CPU de la del bus del sistema, ya que este último opera a una velocidad menor.
- Período de la CPU (TCPU): Se define como el tiempo de duración de un ciclo de reloj y es inversamente proporcional a la frecuencia de la CPU.
- Ciclos por instrucción (CPI): Cada instrucción puede descomponerse en múltiples microinstrucciones, que son ejecutadas en ciclos de reloj. El CPI mide el promedio de ciclos de reloj que una instrucción necesita para completarse.
- Número de instrucciones del programa: Un mayor número de instrucciones implica un mayor tiempo de ejecución y, por lo tanto, un menor rendimiento. La optimización del código y el uso de compiladores eficientes pueden reducir la cantidad de instrucciones ejecutadas.
- Multitarea: Hace referencia a la capacidad del sistema para gestionar múltiples procesos simultáneamente. Un buen manejo de la multitarea puede mejorar significativamente el rendimiento global del sistema.

---

## Desarrollo 

1) **Armar una lista de benchmarks, ¿cuales les serían más útiles a cada uno ? ¿Cuáles podrían llegar a medir mejor las tareas que ustedes realizan a diario ? Pensar en las tareas que cada uno realiza a diario y escribir en una tabla de dos entradas las tareas y que benchmark la representa mejor.**

Se realizo un a tabla con los benchmark que utilizamos durante la carrera y con que propositos:
| **Tarea**                                 | **Benchmark Ideal**            |
|-------------------------------------------|--------------------------------|
| Simulación de circuitos en LTspice        | LTspice Performance Test       |
| Compresión y descompresión de datos       | 7-Zip Benchmark                |
| Algoritmos de procesamiento de señales    | FFT Benchmark                  |
| Evaluación de código en C/C++             | Google Benchmark               |
| Compilación de firmware y código embebido | Google Benchmark               |

2) **¿Cual es el rendimiento de estos procesadores para compilar el kernel de linux?**

	Intel Core i5-13600K
	AMD Ryzen 9 5900X 12-Core

 De la página de [OpenBenchmarking](https://openbenchmarking.org/test/pts/build-linux-kernel-1.15.0) obtuviomos algunos datos de los procesadores Intel Core i5-13600K y AMD Ryzen 9 5900X 12-Core, visibles en la siguiente tabla: 
 
| **Procesador**            | **Ranking Percentil** | **Resultados Públicos Compatibles** | **Segundos (Promedio)** |
|---------------------------|-----------------------|----------------------------------|----------------------------|
| Intel Core i5 13600K      | 53                    | 8                                | 83 ± 3                     |
| AMD Ryzen 9 5900X         | 48                    | 36                               | 97 ± 6                     |

y tambien un gráfico donde se comparan ambos procesadores:

![image](https://github.com/user-attachments/assets/b9d83e25-9e8e-444b-9a6f-c74fe487144f)

Con esto podemos calcular el rendimiento de los procesadores relacionanodlos con el tiempo de ejecución:


$$\eta_{i5} = \frac{1}{T_{EX_1}} = \frac{1}{83} = 1.204\%,$$

$$\eta_{Ry9} = \frac{1}{T_{EX_2}} = \frac{1}{97} = 1.030\%$$

Donde:
- $$\ \eta_1 \$$ y $$\ \eta_2 \$$ son las eficiencias de los dos procesadores. 
- $$\ T_{EX_1} \$$ y $$\ T_{EX_2} \$$ son los tiempos de ejecución de cada procesador.


3) **¿Cual es la aceleración cuando usamos un AMD Ryzen 9 7950X 16-Core?**

   
   Para calcular la aceleracion(speedup) es la razón entre el rendimiento de un sistema mejorado y el rendimiento de su implementación original.
   Entonces al utilizar un AMD Ryzen 9 7950X 16-Core podemos calcularla usando el rendimiento original es decir al AMD Ryzen 9 5900X 12-Core y tambien al rendimiento mejorado que en este caso seria el Ryzen 9 7950X.
   Extrayendo informacion del sitio web https://openbenchmarking.org/test/pts/build-linux-kernel-1.15.0 encontramos que el  AMD Ryzen 9 7950X 16-Core tiene un tiempo promedio(s) de 46 +- 5. Utilizando la formula de Speed up recien mencionada: 76(s)/46(s) que nos da un n=1,65. El aumento de rendimiento es 1,65 veces al utilizar un procesador con 16 nucleos en comparacion al modelo de 12 nucleos. La aceleración (speedup) de 1.65x refleja un aumento del 65% en el rendimiento del Ryzen 9 7950X en comparación con el Ryzen 9 5900X para tareas específicas como la compilación del núcleo de Linux.
Es importante resaltar que el speedup depende de la naturaleza de la tarea. Para tareas de alto paralelismo, donde se puede aprovechar la mayor cantidad de núcleos, el aumento en el rendimiento será más notorio. Sin embargo, para tareas más ligeras o aquellas que no pueden paralelizarse bien, el incremento no será tan pronunciado.
El rendimiento no escala linealmente con el número de núcleos. Aunque el Ryzen 9 7950X tiene 4 núcleos más que el 5900X, el incremento de rendimiento será una fracción de la diferencia teórica, lo que explica el factor de aceleración de 1.65x. Por último, la optimización de software es clave para aprovechar multiples núcleos ya que algunos programas pueden no mostrar una mejora significativa a pesar de contar con más núcleos disponibles.
    

4) **Conseguir un esp32 o cualquier procesador al que se le pueda cambiar la frecuencia. Ejecutar un código que demore alrededor de 10 segundos. Puede ser un bucle for con sumas de enteros por un lado y otro con suma de floats por otro lado. ¿Qué sucede con el tiempo del programa al duplicar (variar) la frecuencia?**

Se ejecutó el siguiente código en una ESP32 
```
#include "Arduino.h"
#include "esp_system.h" 
#include "esp32/clk.h" 

void benchmark(int freq) {
    Serial.println("\n---------------------\n");

    // Cambiar la frecuencia de la CPU
    setCpuFrequencyMhz(freq);  
    delay(500);  

    Serial.flush(); 
    delay(100);

    uint32_t startTime, elapsedTime;
    int repeticiones = 10000;  
    volatile int suma = 0; 

    startTime = micros();  // Inicio de medición de tiempo
    for (int j = 0; j < repeticiones; j++) {
        suma = 0;
        for (int i = 1; i <= 30; i++) {
            suma += i;
        }
    }
    elapsedTime = micros() - startTime; 
    float tiempoPromedio = elapsedTime / (float)repeticiones;  
    float rendimiento = tiempoPromedio > 0 ? (1.0 / tiempoPromedio) : 0;

    //Resultados
    Serial.print("Frecuencia CPU: ");
    Serial.print(getCpuFrequencyMhz());  
    Serial.print(" MHz -> Tiempo: ");
    Serial.print(tiempoPromedio, 6);
    Serial.print(" us -> Rendimiento: ");
    Serial.print(rendimiento, 6);
    Serial.println(" ops/us");
}

void setup() {
    Serial.begin(115200);
    delay(2000);  // Esperar inicio de Serial

    // Ejecutando para diferentes frecuencias
    benchmark(40);   // Baja frecuencia
    benchmark(80);   // Media
    benchmark(160);  // Alta
    benchmark(240);  // Máxima para ESP32
}

void loop() {}
```
obteniendo los siguientes resultados:
![image](https://github.com/user-attachments/assets/30f3e1f4-10ff-40e3-8b9a-a9fde96578d7)
 Por lo que se ve que al aumentar la frecuencia, se reduce el tiempo de ejecuciónaproximadamente a la mitad, y con la frecuencia maxima de 240Mhz obtenemos que el tiempo de ejecución minimo para este script seria de 1,4 us aproximadamente. Con esto, aumenta el rendimiento, ya que es inversamente proporcional al tiempo de ejecución.
