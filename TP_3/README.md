# Trabajo Practico 3: Modo Protegido 

## Tema 1- UEFI y coreboot
### ¿Qué es UEFI? ¿como puedo usarlo? Mencionar además una función a la que podría llamar usando esa dinámica. 
UEFI (Unified Extensible Firmware Interface) es como una evolución de la BIOS. Es un tipo de firmware que arranca la PC antes de que cargue el sistema operativo, lo que hace es definir una interfaz entre el sistema operativo y el firmware de la plataforma. Su propósito es actuar como un puente entre el hardware de tu computadora y el sistema operativo, permitiendo que el sistema arranque y funcione correctamente. A diferencia de la BIOS vieja, UEFI puede trabajar en modo protegido (32 o 64 bits) y no solo en modo real.

Para usar UEFI, generalmente accedes a su configuración al encender las computadoras y presionar una tecla específica (como F2 o DEL). Desde allí, se puede ajustar opciones como el orden de arranque, habilitar el arranque seguro, o configurar parámetros del hardware.

Una función que podrías llamar usando UEFI es el "Secure Boot" (Arranque Seguro). Esta función verifica que el sistema operativo y los controladores sean legítimos y estén firmados digitalmente antes de permitir que se carguen, ayudando a prevenir la ejecución de software malicioso durante el arranque

### ¿Menciona casos de bugs de UEFI que puedan ser explotados?

Un ejemplo reciente es la vulnerabilidad en Secure Boot conocida como LogoFAIL, que afecta tanto a dispositivos x86 como ARM. Este bug, cargar código no autorizado en el arranque, permitiendo a los atacantes explotar fallos en los analizadores de imágenes integrados en el firmware UEFI para inyectar payloads maliciosos, facilitando la instalación de malware persistente, incluso después de reinstalar el sistema operativo2.

También hubo problemas de overflow y corrupcion de memoriaen algunos servicios de UEFI. Estos bugs son peligrosos porque se explotan antes de que cargue el sistema operativo, o sea, son muy difíciles de detectar y corregir después

### ¿Qué es Converged Security and Management Engine (CSME), the Intel Management Engine BIOS Extension (Intel MEBx).?
Converged Security and Management Engine (CSME): El CSME es una tecnología de Intel que combina funciones de seguridad y gestión en un único motor integrado en el chipset. Es decir que es como un sistema operativo aparte que corre dentro del procesador Intel, independiente de tu sistema operativo real. Se usa para por ejemplo manejo remoto de PCs  y funciones de seguridad avanzadas, como cifrado y autenticación.

Intel Management Engine BIOS Extension (Intel MEBx): es la parte de la BIOS que te deja configurar las opciones de ese motor de seguridad. Es una extensión del firmware que permite configurar y gestionar las capacidades de Intel Management Engine (ME), como Intel Active Management Technology (AMT). Esto es útil para la administración remota de dispositivos, especialmente en entornos empresariales

###¿Qué es coreboot ? ¿Qué productos lo incorporan ?¿Cuales son las ventajas de su utilización?

coreboot es un proyecto de código abierto que reemplaza la BIOS/UEFI propietaria por una versión mucho más liviana y rápida.Lo usan productos como:

-Chromebooks
-Algunas motherboards de servidores
-Sistemas embebidos

Algunas de sus ventajas son:

-Arranca mucho más rápido que BIOS/UEFI tradicional.
-Es software libre: Permite a los usuarios examinar, modificar y adaptar el firmware según sus necesidades.
-Tiene menos vulnerabilidades porque es más simple.
-Se puede customizar para el hardware disponible.
-Compatibilidad: Funciona con una amplia gama de hardware y sistemas operativos.


## Tema 2 - Linker
### ¿Que es un linker? ¿que hace ? 
Un linker (o enlazador) es una herramienta que toma los archivos de código (que compila el assembler o el C)  generados por el compilador y los combina en un único archivo ejecutable o biblioteca. Sus funciones principales son las de resolución de símbolos(Asocia referencias a funciones o variables con sus definiciones) y la reubicación, resolviendo las direcciones de memoria.

### ¿Que es la dirección que aparece en el script del linker?¿Porqué es necesaria ?

La dirección en el script del linker define dónde se colocarán las diferentes secciones del programa (como código, datos y variables) en la memoria del sistema. 
Permite que el programa se ejecute correctamente en el hardware específico, porque asegura que las referencias a las variables y funciones sean válidas y accesibles, ya que el gestor de arranque espera que el código esté en una dirección especifica para ejecutarlo.

### Compare la salida de objdump con hd, verifique donde fue colocado el programa dentro de la imagen.


** Pendiente **


### Grabar la imagen en un pendrive y probarla en una pc y subir una foto 

** Pendiente **

### ¿Para que se utiliza la opción --oformat binary en el linker?

** Pendiente **

## Tema 3 - Modo Protegido
El modo protegido es un modo de operación de los procesadores x86 introducido con el Intel 80286. Su principal objetivo es mejorar la estabilidad y seguridad del sistema al permitir características como la protección de memoria, segmentación avanzada y paginación. En este modo, el sistema operativo puede evitar que un programa acceda a áreas de memoria no autorizadas, lo que protege tanto al núcleo del sistema como a otros procesos en ejecución.

### Crear un código assembler que pueda pasar a modo protegido (sin macros).

** Pendiente ** 

### ¿Cómo sería un programa que tenga dos descriptores de memoria diferentes, uno para cada segmento (código y datos) en espacios de memoria diferenciados? 

En modo protegido, se puede crear un programa que defina dos descriptores en la Global Descriptor Table (GDT), uno de segmento de código (Configurado con permisos de ejecución y lectura), y otro de segmento de datos (Configurado inicialmente con permisos de lectura y escritura).

Cada descriptor especifica la base, el límite y los permisos del segmento. El programa debe cargar los registros de segmento (CS para código y DS para datos) con los selectores correspondientes a estos descriptores.

** Pendiente intentarlo y capturar resultados **

### Cambiar los bits de acceso del segmento de datos para que sea de solo lectura,  intentar escribir, ¿Que sucede? ¿Que debería suceder a continuación? (revisar el teórico) Verificarlo con gdb. 

** Pendiente **


### En modo protegido, ¿Con qué valor se cargan los registros de segmento ? ¿Porque? 
En modo protegido, los registros de segmento (CS, DS, SS, etc.) se cargan con selectores de segmento, en lugar de cargar direcciones directas como en modo real. Un selector es un valor de 16 bits que apunta a un descriptor en la GDT o LDT (Local Descriptor Table). Este valor es necesario porque:
-Define la base, el límite y los permisos del segmento.
-Permite la segmentación avanzada y la protección de memoria.
Esto es así porque  en modo protegido los segmentos son más que sólo una dirección, en relaidad estos dan permisos de acceso, limites, bases variablesy reglas de seguridad de nuvel de anillo . Entonces el valor que se carga no es una direccion fisica si no un selectopr que el procesador usa para buscar en la GDT la info del segmento 
