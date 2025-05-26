# Calculadora de Índices GINI: Interacción entre lenguajes de alto y bajo nivel
---

## Introducción
En el ámbito del desarrollo de sistemas informáticos, la arquitectura en capas constituye un paradigma fundamental que permite la construcción de aplicaciones complejas mediante la separación de responsabilidades. Esta estrategia facilita la interacción entre diferentes niveles de abstracción, desde las capas superiores que emplean lenguajes más cercanos al programador hasta las capas inferiores que se comunican directamente con el hardware. En este contexto, el presente informe aborda el desarrollo de una calculadora de índices GINI, un indicador económico ampliamente utilizado para medir la desigualdad en la distribución de ingresos dentro de un país.
Este proyecto representa un caso práctico de implementación de una arquitectura multicapa, donde se integran lenguajes de alto nivel como Python para la interfaz y la recuperación de datos mediante APIs REST, lenguajes de nivel intermedio como C para la lógica de procesamiento, y finalmente, lenguaje ensamblador para operaciones de bajo nivel como conversiones de tipos de datos. A través de este enfoque, se busca no solo crear una herramienta funcional para el cálculo de índices GINI, sino también profundizar en el conocimiento de las convenciones de llamada entre diferentes capas de abstracción, un aspecto crucial en el desarrollo de sistemas críticos y en la comprensión de la interacción entre software y hardware.

---

## Marco Teórico
- *Arquitectura de Capas en Sistemas Informáticos*
Los sistemas informáticos modernos están estructurados en capas de abstracción que permiten a los desarrolladores trabajar en diferentes niveles de complejidad. En la base de esta jerarquía se encuentra el hardware, seguido inmediatamente por los lenguajes de bajo nivel como el ensamblador, que ofrecen un control directo sobre los recursos del sistema. Los lenguajes de alto nivel, como Python y C, se sitúan en capas superiores y proporcionan abstracciones que facilitan el desarrollo de aplicaciones complejas.
La comunicación entre estas capas se realiza mediante convenciones de llamada (calling conventions), que son acuerdos sobre cómo se deben pasar parámetros, gestionar el stack y devolver resultados cuando una función de un nivel invoca a otra de un nivel inferior. Comprender estas convenciones es fundamental para desarrollar aplicaciones que interactúen eficientemente con el hardware subyacente.

- *Índice GINI y su Relevancia*
El índice GINI es una medida estadística que cuantifica la desigualdad en la distribución de ingresos o riqueza dentro de una población. Su valor oscila entre 0 (igualdad perfecta) y 1 (desigualdad máxima). Para realizar cálculos precisos con este índice, a menudo es necesario convertir entre diferentes representaciones numéricas, como números en punto flotante y enteros, lo que justifica la implementación de rutinas específicas en lenguaje ensamblador.

- *APIs REST y Consumo de Datos*
Las APIs REST (Representational State Transfer) constituyen un estilo arquitectónico para el desarrollo de servicios web que ha ganado popularidad por su simplicidad y escalabilidad. Estas interfaces permiten a las aplicaciones interactuar con servicios remotos mediante operaciones estándar HTTP. En el contexto de este proyecto, se utiliza una API del Banco Mundial para obtener datos actualizados sobre los índices GINI de diferentes países, lo que proporciona una fuente confiable para los cálculos posteriores.

---

## Desarrollo
- *Diseño de la Arquitectura*
La arquitectura de la calculadora de índices GINI se ha diseñado siguiendo un modelo de tres capas interconectadas:
1. Capa de Interfaz y Recuperación de Datos (Python): Encargada de interactuar con el usuario y consumir la API REST del Banco Mundial para obtener los datos sobre índices GINI. Python resulta ideal para esta tarea debido a su facilidad para manejar peticiones HTTP y procesar respuestas JSON.
2. Capa de Procesamiento Intermedio (C): Actúa como puente entre la capa superior y la inferior, recibiendo los datos obtenidos por Python y gestionando las llamadas a las rutinas en ensamblador. Esta capa se implementa en C por su eficiencia y capacidad para interactuar tanto con lenguajes de alto nivel como con el ensamblador.
3. Capa de Operaciones de Bajo Nivel (Ensamblador): Contiene las rutinas específicas para realizar conversiones entre números de punto flotante y enteros, así como para calcular el índice GINI ajustado (sumando 1 al valor original). Estas operaciones se implementan en ensamblador para maximizar el rendimiento y profundizar en la comprensión de la interacción directa con el hardware.

### *Primera Iteración: Comunicación Python y C*

En la primera etapa del trabajo, se desarrolló una interfaz entre un script en Python y un programa en C. El objetivo fue consultar el índice GINI de Argentina utilizando la API REST del Banco Mundial. Python se encargó de hacer el request a la API, obtener el valor y luego invocar al programa en C pasándole el dato como argumento.

El programa en C simplemente recibió el número en formato float, lo imprimió por pantalla y aplicó una operación básica, como sumar uno. En esta iteración no se utilizó código en ensamblador; el foco estuvo en lograr la interacción entre los lenguajes de alto nivel y garantizar que el traspaso de información fuera exitoso.
### *Segunda Iteración: Agregando Lógica en Ensamblador*

En la segunda fase se incorporó Assembler al proyecto. Esta vez, el valor del índice GINI obtenido en Python fue pasado al programa en C, y desde allí se llamó a una rutina asm para convertir el valor float a entero y sumarle uno.

Como parte de esta etapa, también se utilizó GDB para inspeccionar el contenido del stack antes, durante y después de la ejecución del asm. Esto permitió validar el uso correcto del stack.


![image](https://github.com/user-attachments/assets/17c79700-147f-463c-afac-bf3161add725)
![image](https://github.com/user-attachments/assets/1be2c908-72b6-4047-8c21-ed96c6f8fd3e)
![image](https://github.com/user-attachments/assets/a6836250-b691-4318-9376-a6a61f0913e8)
![image](https://github.com/user-attachments/assets/b114a1e5-eea6-4c51-a0ec-622c251c1ad0)
![image](https://github.com/user-attachments/assets/89ab780c-1ac3-4526-bb36-798156cb4fc0)

Viendo asi el cambio de contenido en los registros, especialmente con eax 

---

## Conclusión
El desarrollo de la calculadora de índices GINI ha proporcionado una valiosa oportunidad para profundizar en el conocimiento de la interacción entre lenguajes de diferentes niveles de abstracción. A través de la implementación de una arquitectura de tres capas, se ha logrado combinar la facilidad de uso de Python para la interfaz y la recuperación de datos, la eficiencia de C como capa intermedia, y la precisión del ensamblador para operaciones críticas de bajo nivel.
El proyecto ha permitido comprender en detalle cómo funcionan las convenciones de llamada entre diferentes lenguajes, un conocimiento fundamental para el desarrollo de sistemas críticos y para entender la interacción entre software y hardware. Además, la utilización de herramientas como GDB para la depuración ha proporcionado una visión directa de cómo se gestiona el stack durante las llamadas a funciones, lo que resulta esencial para identificar y resolver problemas en sistemas complejos.
Finalmente, la implementación de una solución funcional para el cálculo de índices GINI demuestra cómo los conceptos teóricos de arquitectura en capas pueden aplicarse en la práctica para desarrollar aplicaciones que integren diferentes tecnologías. Esta experiencia sienta las bases para futuros desarrollos en áreas como sistemas embebidos, seguridad informática y optimización de rendimiento, donde la comprensión profunda de la interacción entre software y hardware resulta crucial.