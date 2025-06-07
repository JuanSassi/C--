# TP4 – Módulos del Kernel en Linux

**Materia:** Sistemas de Computación  
**Año:** 2025  
**Carreras:** Ingeniería en Computación / Electrónica  
**Grupo:** C--  
**Profesores:** Miguel Ángel Solinas y Javier Alejandro Jorge  
**Integrantes:**
- Oro Castro, Magdalena  
- Ludueña, Elio Nicolás  
- Sassi, Juan Ignacio  

---

## Introducción

Este trabajo práctico explora el funcionamiento interno del kernel de Linux mediante la creación, carga, prueba y análisis de módulos del kernel. Se busca:

- Aprender a compilar, cargar y descargar módulos del kernel.
- Interactuar con el sistema de archivos virtual `/proc`.
- Comprender las diferencias entre el espacio de usuario y el espacio del kernel.
- Investigar Secure Boot y la firma de módulos para mejorar la seguridad.
- Documentar pruebas, errores y soluciones con capturas y comandos utilizados.

Este informe representa una introducción práctica a la programación de bajo nivel y temas de ciberseguridad.

## Desafío #1 – Checkinstall

### ¿Qué es `checkinstall` y para qué sirve?

Es una herramienta que reemplaza `make install` y genera paquetes `.deb` o `.rpm`. Esto facilita la instalación, desinstalación y seguimiento de software compilado manualmente.

Ejemplo práctico: empaquetar un módulo `bienvenida.ko` con checkinstall.

---

## Instalación del entorno de desarrollo
sudo apt update
sudo apt install build-essential linux-headers-$(uname -r)

Desafío #2 – Análisis de programas vs. módulos
Diferencias clave
| Concepto            | Módulo del Kernel            | Programa de Usuario              |
| ------------------- | ---------------------------- | -------------------------------- |
| Contexto            | Espacio del kernel           | Espacio del usuario              |
| Inicio              | `module_init()`              | `main()`                         |
| Finalización        | `module_exit()`              | Retorno desde `main()`           |
| Riesgos             | Kernel panic                 | Fallo de proceso                 |
| Interfaz con kernel | Acceso directo a estructuras | Syscalls (`write`, `open`, etc.) |

## Acceso a memoria
Los módulos acceden directamente a memoria usando funciones del kernel como kmalloc, ioremap, etc.
Los programas de usuario acceden solo a través de llamadas al sistema protegidas.
## Drivers y /dev
/dev contiene archivos que representan dispositivos.
Los drivers del kernel (que pueden ser módulos) manejan la interacción con estos dispositivos.
Cuando un módulo (driver) es cargado, se crean las entradas correspondientes en /dev.
Números mayor y menor
En /dev, el número mayor identifica al driver (controlador).
El número menor distingue cada dispositivo particular controlado por ese driver.

Ejemplo: /dev/sda puede tener mayor 8 (SCSI disk) y menor 0.

## Comparación de modinfo
modinfo mimodulo.ko: muestra que es un módulo creado por el usuario, sin firma y sin parámetros.
modinfo des_generic.ko: muestra un módulo oficial del sistema, con parámetros, dependencias y firma.

Esto resalta la diferencia entre módulos externos ("out-of-tree") y módulos internos del sistema ("in-tree").

## Namespace en el Kernel
Los namespaces permiten aislar recursos entre procesos. Son la base de la virtualización y los contenedores.

## Tipos comunes de namespaces:

PID Namespace (aislar procesos)
Mount Namespace (sistemas de archivos)
Network Namespace (interfaces de red)
Importancia: permite que varios entornos convivan en un mismo kernel sin interferirse.

## ¿Qué es un segmentation fault?
Es un error que ocurre cuando un programa intenta acceder a una zona de memoria no permitida. El kernel detecta esto y termina el proceso con una señal SIGSEGV.

En espacio de usuario: el proceso muere.

En el kernel: un fallo puede generar un kernel panic.

## ¿Qué pasa si un companero intenta cargar mi modulo firmado?
Si tiene Secure Boot activado, no podra cargar un modulo firmado por vos (con tu clave personal), a menos que:
Le compartas tu certificado .der.
Lo importe con:
sudo mokutil --import cert.der
En el reinicio, acepte la clave en el menu MOK Manager.

## Analisis del parche de Microsoft sobre GRUB
# a. ¿Cual fue la consecuencia principal del parche?
Impidio el arranque de Linux en sistemas dual boot con Secure Boot activo, mostrando errores como:
SBAT self-check failed: Security Policy Violation.

# b. ¿Que implica desactivar Secure Boot?
Permite que el sistema arranque normalmente, pero compromete la seguridad.

# c. ¿Cual es el propósito principal de Secure Boot?
Evitar que se cargue software malicioso en el proceso de arranque, asegurando que todo esté firmado por entidades confiables.

Propósito del Secure Boot y firma de módulos
Secure Boot verifica la firma de cada componente del arranque: GRUB, kernel, módulos, etc.

Mi entorno no tiene Secure Boot (modo BIOS/legacy):
EFI variables are not supported on this system
Sin embargo, el proceso de firma investigado sería:
# Crear clave
openssl req -new -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -nodes -days 36500 -subj "/CN=MiFirma/"

# Convertir a DER
openssl x509 -in cert.pem -outform DER -out cert.der

# Importar
sudo mokutil --import cert.der

# Firmar módulo
/usr/src/linux-headers-$(uname -r)/scripts/sign-file sha256 key.pem cert.pem mi_modulo.ko

# Cargar
sudo insmod mi_modulo.ko
¿Qué es /proc?
Sistema de archivos virtual creado por el kernel.

No reside en disco, está en memoria.

Expone información del sistema en tiempo real.

Modulos como proc_modulo.ko:
Crean archivos como /proc/info_modulo.

Permiten leer datos directamente del kernel.
cat /proc/modules      # Ver módulos cargados
cat /proc/cpuinfo      # Info del procesador
cat /proc/kallsyms     # Simbolos del kernel (opcional)
Módulo mimodulo.ko
Módulo simple que muestra mensajes en dmesg.

Pasos realizados:
make
sudo insmod mimodulo.ko
sudo dmesg | tail
sudo rmmod mimodulo

Modulo proc_modulo.ko
Modulo más avanzado que crea /proc/info_modulo y permite leer un mensaje.

Código relevante:
Prueba:
sudo insmod proc_modulo.ko
cat /proc/info_modulo
# => Hola desde /proc!
sudo rmmod proc_modulo
Modulos cargados y disponibles
Cargados: lsmod, cat /proc/modules.

Disponibles: ls /lib/modules/$(uname -r)/kernel

Si un driver no esta cargado, el dispositivo puede no funcionar correctamente.
Escaneo de hardware real
Se ejecuto en una máquina real el siguiente comando:
sudo -E hw-probe -all -upload
 Resultado:
https://linux-hardware.org/?probe=7688f095eb

strace y llamadas al sistema
Se compila el programa:
#include <stdio.h>
int main() {
    printf("Hola Mundo\n");
    return 0;
}

gcc -Wall main.c -o hello
strace -tt ./hello
Salida clave:

write(1, "Hola Mundo\n", 11) = 11
exit_group(0)
Se observa que incluso un simple printf realiza llamadas al sistema (syscall) como write() y exit_group().


