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

### ¿Qué es coreboot ? ¿Qué productos lo incorporan ?¿Cuales son las ventajas de su utilización?

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

Para comparar la salida de objdump con hd y verificar dónde fue colocado el programa dentro de la imagen, realizamos los siguientes pasos:

```bash
# Examinar el archivo objeto con objdump
objdump -D protected_mode.o > objdump_output.txt
# Examinar la imagen binaria con hexdump
hd protected_mode.img > hexdump_output.txt
```
Al analizar ambos archivos, observamos que el código desensamblado por objdump aparece en la imagen hexadecimal, pero con un desplazamiento importante. En objdump_output.txt, el código comienza en la dirección 0x0000 y en hexdump_output.txt, las mismas instrucciones aparecen, pero con direcciones desplazadas. 
Comparación de secuencias específicas, como por ejemplo las primeras instrucciones del código:
En objdump:
```
00000000 <initial_dl-0x1c>:
   0:	fa                   	cli
   1:	ea 06 00 00 00 31 c0 	ljmp   $0xc031,$0x6
```
En hexdump:
```
00000000  fa ea 06 7c 00 00 31 c0  8e d8 8e c0 8e e0 8e e8  |...|..1.........|
```
La primera instrucción cli (fa) coincide, pero la segunda instrucción muestra una diferencia. En el objdump es ljmp $0xc031,$0x6, mientras que en hexdump aparece un valor diferente para la dirección de salto (7c en lugar de 00).

En cuanto al desplazamiento de memoria, el código fue colocado en la dirección 0x7c00 del disco, en hexdump_output.txt todas las referencias de memoria que en objdump se muestran como direcciones relativas a 0x00, aparecen modificadas para apuntar a direcciones relativas a 0x7c00. Por ejemplo, vemos que las referencias a memoria como 1c 00 en objdump aparecen como 1c 7c en hexdump. El mensaje "hello world" que en objdump aparece en la posición 0xd7, en hexdump aparece en 0xd7 + 0x7c00 (aunque hexdump solo muestra los últimos bytes de la dirección).
La imagen termina con los bytes 55 aa en la posición 0x1FE-0x1FF, que corresponde a la firma estándar del sector de arranque (boot sector). Esto confirma que el programa ha sido colocado en el primer sector de arranque del disco, que se carga en la dirección de memoria 0x7c00 al iniciar el sistema.
El programa fue colocado al comienzo del sector de arranque del disco (offset 0x0000 en hexdump), pero ha sido ensamblado para ejecutarse en la dirección de memoria 0x7c00, que es la dirección estándar donde el BIOS carga el sector de arranque al iniciar la computadora. Las referencias a memoria han sido ajustadas para reflejar esto, sustituyendo las direcciones relativas de objdump por direcciones absolutas en el archivo hexadecimal. La diferencia más notable está en todas las referencias que en objdump son relativas a 0x00, que en hexdump aparecen con el byte alto modificado a 0x7c, indicando el desplazamiento a la dirección 0x7c00.

### Grabar la imagen en un pendrive y probarla en una pc y subir una foto 

Para grabar la imagen en un pendrive y probarla en una PC real, primero conectamos el dispositivo USB y utilizamos el comando lsblk para identificar su nombre dentro del sistema, que en este caso resultó ser /dev/sdd. Es importante asegurarse de que esta ruta corresponde al pendrive y no a otro disco para evitar sobrescribir datos importantes. Luego, desde la carpeta donde se encontraba la imagen generada (~/Escritorio/C--/TP_3/protected-mode-sdc/x86-bare-metal-examples), ejecutamos el siguiente comando:

```bash
sudo dd if=protected_mode.img of=/dev/sdd bs=4M status=progress && sync
```
Este comando utiliza dd para copiar byte a byte el contenido de la imagen protected_mode.img directamente al dispositivo USB. El parámetro bs=4M mejora la velocidad al usar bloques de 4 megabytes, status=progress permite ver el avance del proceso, y sync asegura que todos los datos se escriban correctamente antes de finalizar. Una vez completado, retiramos el pendrive de forma segura, lo conectamos a una PC de pruebas y configuramos el arranque desde USB. Al encenderla, pudimos comprobar que el sistema booteó correctamente en modo protegido y mostró en pantalla el mensaje "Hello World":

![imagen en pendrive, prueba en computadora real](capturas/protected_mode%20en%20pendrive.jpeg)

### ¿Para que se utiliza la opción --oformat binary en el linker?

La opción --oformat binary se utiliza para indicar al linker (ld) que genere un archivo de salida en formato binario puro, sin ninguna cabecera o metadatos adicionales propios de formatos como ELF, COFF o PE.
Esta opción es crucial por las siguientes razones:
* Imagen de disco cruda: Para crear bootloaders o código que se ejecuta directamente en el hardware, necesitamos un archivo binario puro que contenga solo el código máquina y los datos, exactamente como deben estar en memoria.
* Sin cabeceras: Los formatos como ELF incluyen cabeceras y metadatos que el hardware desnudo no puede interpretar. La opción binary elimina toda esta información extra.
* Control total: Permite tener control absoluto sobre cada byte que va en la imagen final, lo cual es esencial para programación a bajo nivel donde cada byte importa.
* Compatibilidad con hardware: Formatos como MBR requieren una estructura binaria específica sin metadatos adicionales, donde los últimos dos bytes del sector deben ser 0x55 y 0xAA.

En el contexto del trabajo con modo protegido en x86, esta opción asegura que la imagen generada pueda ser cargada directamente por el BIOS o grabada en un dispositivo de arranque sin necesidad de ningún procesamiento adicional.

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
