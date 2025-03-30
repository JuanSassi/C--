# Trabajo Práctico 1: Rendimiento 
## Introduccion 
El objetivo de este primer trabajo práctico de la materia es el de analizar el rendimiento de las computadores, para poder cuantificarlo. Con este proposito se utilizarán benchmarks y se utilizarán herramientas como GPROF y perf para medir performance de codigo, haciendo uso de una ESP32.


## Marco Teorico?
**Benchmarks**

**Rendimiento**


## Desarrollo 


1)Armar una lista de benchmarks, ¿cuales les serían más útiles a cada uno ? ¿Cuáles podrían llegar a medir mejor las tareas que ustedes realizan a diario ?
Pensar en las tareas que cada uno realiza a diario y escribir en una tabla de dos entradas las tareas y que benchmark la representa mejor.

Se realizo un a tabla con los benchmark que iutilizamos duante la carrera y con que propositos:
| **Tarea**                                 | **Benchmark Ideal**            |
|-------------------------------------------|--------------------------------|
| Simulación de circuitos en LTspice        | LTspice Performance Test       |
| Compresión y descompresión de datos       | 7-Zip Benchmark                |
| Algoritmos de procesamiento de señales    | FFT Benchmark                  |
| Evaluación de código en C/C++             | Google Benchmark               |
| Compilación de firmware y código embebido | Google Benchmark               |

2)Cual es el rendimiento de estos procesadores para compilar el kernel de linux ?
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


3)Cual es la aceleración cuando usamos un AMD Ryzen 9 7950X 16-Core

4)Conseguir un esp32 o cualquier procesador al que se le pueda cambiar la frecuencia.
Ejecutar un código que demore alrededor de 10 segundos. Puede ser un bucle for con sumas de enteros por un lado y otro con suma de floats por otro lado.
¿Qué sucede con el tiempo del programa al duplicar (variar) la frecuencia ? 

