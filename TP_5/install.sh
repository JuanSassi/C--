#!/bin/bash

# Script de instalación para el proyecto de sensores en QEMU
# Uso: ./install_qemu.sh

set -e  # Salir en caso de error

echo "=== Instalación del Sistema de Sensores para QEMU ==="
echo

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes con color
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_qemu() {
    echo -e "${BLUE}[QEMU]${NC} $1"
}

# Verificar que se ejecuta como usuario normal (no root)
if [ "$EUID" -eq 0 ]; then
    print_error "No ejecutes este script como root. Se pedirá sudo cuando sea necesario."
    exit 1
fi

# Verificar si estamos en QEMU
print_status "Verificando entorno QEMU..."
if [ -f /proc/cpuinfo ]; then
    if grep -q "QEMU" /proc/cpuinfo 2>/dev/null; then
        print_qemu "Detectado entorno QEMU"
    else
        print_warning "No se detectó QEMU en /proc/cpuinfo, continuando..."
    fi
fi

# Verificar herramientas QEMU necesarias
print_status "Verificando herramientas QEMU..."

# Instalar QEMU si no está disponible
if ! command -v qemu-system-arm &> /dev/null && ! command -v qemu-system-x86_64 &> /dev/null; then
    print_warning "QEMU no detectado, instalando..."
    sudo apt-get update
    sudo apt-get install -y qemu-system qemu-utils
fi

# Crear entorno virtual Python
print_status "Configurando entorno virtual de Python para QEMU..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_status "Entorno virtual creado"
else
    print_status "Entorno virtual ya existe"
fi

# Activar entorno virtual
source venv/bin/activate

# Verificar dependencias del sistema
print_status "Verificando dependencias del sistema..."

# Verificar herramientas de desarrollo del kernel
if ! dpkg -l | grep -q linux-headers-$(uname -r); then
    print_warning "Instalando linux-headers para desarrollo de drivers..."
    sudo apt-get update
    sudo apt-get install -y linux-headers-$(uname -r) build-essential
fi

# Instalar herramientas adicionales para QEMU
print_status "Instalando herramientas específicas para QEMU..."
sudo apt-get install -y bridge-utils uml-utilities

# Verificar Python3 y pip
if ! command -v python3 &> /dev/null; then
    print_error "Python3 no está instalado"
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    print_warning "Instalando pip3..."
    sudo apt-get install -y python3-pip
fi

# Instalar dependencias de Python
print_status "Instalando dependencias de Python..."
pip install --upgrade pip
pip install matplotlib numpy

# Instalar qemu-rpi-gpio para simulación GPIO
print_status "Instalando qemu-rpi-gpio para simulación GPIO..."
pip install qemu-rpi-gpio || print_warning "qemu-rpi-gpio no disponible, usando simulación integrada"

# Verificar que tkinter esté instalado en el sistema
if ! python3 -c "import tkinter" &>/dev/null; then
    print_warning "tkinter no está instalado. Instalando con apt..."
    sudo apt-get install -y python3-tk
else
    print_status "tkinter ya está disponible"
fi

# Compilar el driver adaptado para QEMU
print_status "Compilando el driver del kernel para QEMU..."
make clean
make QEMU=1  # Flag especial para compilación QEMU

if [ ! -f "sensor_driver.ko" ]; then
    print_error "Error compilando el driver"
    exit 1
fi

print_status "Driver compilado exitosamente para QEMU"

# Crear configuración QEMU
print_status "Creando configuración QEMU..."

cat > qemu_config.sh << 'EOF'
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
EOF

# Hacer el script ejecutable
chmod +x qemu_config.sh

# Crear script de carga del driver para QEMU
print_status "Creando scripts de control para QEMU..."

cat > load_driver.sh << 'EOF'
#!/bin/bash

# Script para cargar el driver en QEMU
echo "=== Cargando driver de sensores en QEMU ==="

# Cargar configuración QEMU
source ./qemu_config.sh

# Detectar arquitectura
ARCH=$(detect_qemu_arch)
echo "Arquitectura detectada: $ARCH"

# Configurar GPIO virtual
setup_virtual_gpio || echo "Usando simulación GPIO completa"

# Descargar driver anterior si existe
if lsmod | grep -q sensor_driver; then
    echo "Descargando driver anterior..."
    sudo rmmod sensor_driver
fi

# Cargar nuevo driver
echo "Cargando driver sensor_driver.ko..."
sudo insmod sensor_driver.ko

# Verificar que se cargó correctamente
if lsmod | grep -q sensor_driver; then
    echo "✓ Driver cargado exitosamente en QEMU"
    
    # Mostrar información del dispositivo
    echo "Información del dispositivo:"
    
    # Esperar a que el dispositivo se cree
    for i in {1..10}; do
        if [ -e /dev/sensor_drv ]; then
            break
        fi
        echo "Esperando creación del dispositivo... ($i/10)"
        sleep 1
    done
    
    if [ -e /dev/sensor_drv ]; then
        ls -l /dev/sensor_drv
        echo "✓ Dispositivo listo en /dev/sensor_drv"
        
        # Configurar permisos para QEMU
        sudo chmod 666 /dev/sensor_drv
        echo "✓ Permisos configurados para acceso de usuario"
    else
        echo "⚠ /dev/sensor_drv no se creó automáticamente"
        echo "Creando dispositivo manualmente..."
        
        # Obtener número mayor del driver
        MAJOR=$(grep sensor_drv /proc/devices | awk '{print $1}')
        if [ ! -z "$MAJOR" ]; then
            sudo mknod /dev/sensor_drv c $MAJOR 0
            sudo chmod 666 /dev/sensor_drv
            echo "✓ Dispositivo creado manualmente: /dev/sensor_drv"
        else
            echo "✗ Error: No se pudo determinar el número mayor del dispositivo"
            exit 1
        fi
    fi
    
    # Mostrar información del sistema QEMU
    echo ""
    echo "=== Información del sistema QEMU ==="
    echo "Kernel: $(uname -r)"
    echo "Arquitectura: $(uname -m)"
    
    # Mostrar mensajes del kernel
    echo ""
    echo "=== Últimos mensajes del kernel ==="
    dmesg | tail -10 | grep -E "(sensor_drv|QEMU)" || dmesg | tail -5
    
    echo ""
    echo "✓ Driver listo para usar en QEMU"
    
else
    echo "✗ Error: No se pudo cargar el driver"
    echo "Verificando mensajes de error..."
    dmesg | tail -10
    exit 1
fi
EOF

cat > unload_driver.sh << 'EOF'
#!/bin/bash

# Script para descargar el driver en QEMU
echo "=== Descargando driver de sensores en QEMU ==="

if lsmod | grep -q sensor_driver; then
    sudo rmmod sensor_driver
    echo "✓ Driver descargado"
else
    echo "⚠ Driver no estaba cargado"
fi

# Limpiar dispositivo si existe
if [ -e /dev/sensor_drv ]; then
    sudo rm /dev/sensor_drv
    echo "✓ Dispositivo removido"
fi

# Mostrar mensajes del kernel
echo ""
echo "=== Últimos mensajes del kernel ==="
dmesg | tail -5

echo "✓ Limpieza completada"
EOF

cat > run_app.sh << 'EOF'
#!/bin/bash

# Script para ejecutar la aplicación en QEMU
echo "=== Ejecutando aplicación de monitoreo en QEMU ==="

# Activar entorno virtual
source venv/bin/activate

# Cargar configuración QEMU
source ./qemu_config.sh

# Verificar que el driver esté cargado
if ! lsmod | grep -q sensor_driver; then
    echo "✗ Error: Driver no está cargado"
    echo "Ejecuta primero: ./load_driver.sh"
    exit 1
fi

# Verificar que el dispositivo existe
if [ ! -e /dev/sensor_drv ]; then
    echo "✗ Error: /dev/sensor_drv no existe"
    echo "Verifica que el driver esté correctamente cargado"
    exit 1
fi

# Configurar display para QEMU si es necesario
if [ -z "$DISPLAY" ]; then
    export DISPLAY=:0.0
    echo "⚠ DISPLAY configurado a :0.0 para QEMU"
fi

# Verificar que X11 forwarding funciona
if ! xset q &>/dev/null; then
    echo "⚠ Advertencia: X11 no disponible, la GUI podría no funcionar"
    echo "  Asegúrate de tener X11 forwarding habilitado o ejecutar en entorno gráfico"
fi

# Ejecutar aplicación
echo "Iniciando aplicación..."
python3 sensor_app.py
EOF

# Hacer scripts ejecutables
chmod +x load_driver.sh unload_driver.sh run_app.sh

# Crear archivo README específico para QEMU
cat > README.md << 'EOF'
# Sistema de Sensores para QEMU

Este proyecto está configurado específicamente para funcionar en QEMU con simulación GPIO.

## Requisitos QEMU

- QEMU instalado (qemu-system-x86_64 o qemu-system-arm)
- Kernel headers para desarrollo de drivers
- Python 3 con matplotlib y tkinter
- X11 forwarding para GUI (si usas SSH)

## Instalación

```bash
./install.sh
```

## Uso

1. **Cargar el driver:**
   ```bash
   ./load_driver.sh
   ```

2. **Ejecutar la aplicación:**
   ```bash
   ./run_app.sh
   ```

3. **Descargar el driver:**
   ```bash
   ./unload_driver.sh
   ```

## Características específicas de QEMU

- **GPIO Simulado**: Los sensores son completamente simulados
- **Valores realistas**: Temperatura (15-45°C) y Humedad (20-90%)
- **Sin hardware real**: No requiere GPIO físico
- **Compatible con x86_64 y ARM**: Funciona en ambas arquitecturas

## Arquitecturas soportadas

- **x86_64**: Emulación estándar de PC
- **ARM**: Emulación de Raspberry Pi (raspi3b)

## Comandos útiles QEMU

```bash
# Ver si estás en QEMU
cat /proc/cpuinfo | grep QEMU

# Ver driver cargado
lsmod | grep sensor

# Ver dispositivo
ls -l /dev/sensor_drv

# Ver mensajes del driver
dmesg | grep sensor_drv

# Información del sistema
uname -a
```

## Troubleshooting

### GUI no aparece
- Verifica X11 forwarding: `ssh -X usuario@host`
- Configura DISPLAY: `export DISPLAY=:0.0`

### Driver no carga
- Verifica kernel headers: `dpkg -l | grep linux-headers`
- Recompila: `make clean && make QEMU=1`

### Dispositivo no se crea
- El script lo creará automáticamente
- Verifica permisos: `ls -l /dev/sensor_drv`

## Configuración avanzada

Edita `qemu_config.sh` para ajustar:
- Memoria QEMU
- Número de CPUs
- Configuración GPIO virtual
EOF

print_status "Instalación para QEMU completada exitosamente"
echo
echo "=== Instrucciones de uso para QEMU ==="
echo "1. Cargar el driver:     sudo ./load_driver.sh"
echo "2. Ejecutar aplicación:  sudo ./run_app.sh"
echo "3. Descargar driver:     sudo ./unload_driver.sh"
echo
echo "=== Comandos útiles para QEMU ==="
echo "Ver si estás en QEMU:    cat /proc/cpuinfo | grep QEMU"
echo "Ver driver cargado:      lsmod | grep sensor"
echo "Ver dispositivo:         ls -l /dev/sensor_drv"
echo "Ver mensajes kernel:     dmesg | grep sensor_drv"
echo "Configuración QEMU:      cat qemu_config.sh"
echo
echo "=== Archivos específicos QEMU creados ==="
echo "- qemu_config.sh         (configuración QEMU)"
echo "- load_driver.sh    (cargar driver en QEMU)"
echo "- unload_driver.sh  (descargar driver)"
echo "- run_app.sh        (ejecutar aplicación QEMU)"
echo "- README.md         (documentación QEMU)"
echo
echo "El entorno virtual está en: ./venv/"
echo "Para activarlo manualmente: source venv/bin/activate"
echo
print_qemu "¡Sistema listo para QEMU!"