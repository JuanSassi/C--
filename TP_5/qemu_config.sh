#!/bin/bash

# Configuración QEMU para el proyecto de sensores
# Este archivo contiene la configuración específica para QEMU

QEMU_ARCH="x86_64"  # Cambiar a arm si usas emulación ARM
QEMU_MEMORY="1G"
QEMU_CPU="2"

# Función para detectar arquitectura QEMU
detect_qemu_arch() {
    if grep -q "ARM" /proc/cpuinfo 2>/dev/null; then
        echo "arm"
    elif grep -q "QEMU" /proc/cpuinfo 2>/dev/null; then
        echo "x86_64"
    else
        echo "unknown"
    fi
}

# Función para configurar GPIO virtual
setup_virtual_gpio() {
    echo "Configurando GPIO virtual para QEMU..."
    
    # Crear directorio de GPIO virtual si no existe
    if [ ! -d "/sys/class/gpio" ]; then
        echo "Sistema GPIO no disponible, usando simulación completa"
        return 1
    fi
    
    # Configurar pines GPIO virtuales (si están disponibles)
    for pin in 18 19; do
        if [ ! -d "/sys/class/gpio/gpio${pin}" ]; then
            echo ${pin} > /sys/class/gpio/export 2>/dev/null || true
            echo "in" > /sys/class/gpio/gpio${pin}/direction 2>/dev/null || true
        fi
    done
    
    return 0
}

# Exportar funciones para uso en otros scripts
export -f detect_qemu_arch
export -f setup_virtual_gpio
export QEMU_ARCH QEMU_MEMORY QEMU_CPU
