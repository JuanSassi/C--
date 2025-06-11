#!/bin/bash

# Script de instalación para el proyecto de sensores
# Uso: ./install.sh

set -e  # Salir en caso de error

echo "=== Instalación del Sistema de Sensores ==="
echo

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Crear entorno virtual
print_status "Configurando entorno virtual de Python..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_status "Entorno virtual creado"
else
    print_status "Entorno virtual ya existe"
fi

# Activar entorno virtual
source venv/bin/activate

# Verificar que se ejecuta como usuario normal (no root)
if [ "$EUID" -eq 0 ]; then
    print_error "No ejecutes este script como root. Se pedirá sudo cuando sea necesario."
    exit 1
fi

# Verificar dependencias del sistema
print_status "Verificando dependencias del sistema..."

# Verificar herramientas de desarrollo del kernel
if ! dpkg -l | grep -q linux-headers-$(uname -r); then
    print_warning "Instalando linux-headers..."
    sudo apt-get update
    sudo apt-get install -y linux-headers-$(uname -r) build-essential
fi

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

# Verificar que tkinter esté instalado en el sistema
if ! python3 -c "import tkinter" &>/dev/null; then
    print_warning "tkinter no está instalado. Instalando con apt..."
    sudo apt-get install -y python3-tk
else
    print_status "tkinter ya está disponible"
fi

# Compilar el driver
print_status "Compilando el driver del kernel..."
make clean
make

if [ ! -f "sensor_driver.ko" ]; then
    print_error "Error compilando el driver"
    exit 1
fi

print_status "Driver compilado exitosamente"

# Crear script de inicio
print_status "Creando scripts de control..."

cat > load_driver.sh << 'EOF'
#!/bin/bash

# Script para cargar el driver
echo "Cargando driver de sensores..."

# Descargar driver anterior si existe
if lsmod | grep -q sensor_driver; then
    echo "Descargando driver anterior..."
    sudo rmmod sensor_driver
fi

# Cargar nuevo driver
sudo insmod sensor_driver.ko

# Verificar que se cargó correctamente
if lsmod | grep -q sensor_driver; then
    echo "Driver cargado exitosamente"
    
    # Mostrar información del dispositivo
    echo "Información del dispositivo:"
    ls -l /dev/sensor_drv 2>/dev/null || echo "Esperando creación del dispositivo..."
    
    # Esperar un momento para que udev cree el dispositivo
    sleep 2
    
    if [ -e /dev/sensor_drv ]; then
        ls -l /dev/sensor_drv
        echo "Dispositivo listo en /dev/sensor_drv"
    else
        echo "Advertencia: /dev/sensor_drv no se creó automáticamente"
        echo "Puede que necesites crear el dispositivo manualmente o verificar udev"
    fi
    
    # Mostrar mensajes del kernel
    echo "Últimos mensajes del kernel:"
    dmesg | tail -5
else
    echo "Error: No se pudo cargar el driver"
    exit 1
fi
EOF

cat > unload_driver.sh << 'EOF'
#!/bin/bash

# Script para descargar el driver
echo "Descargando driver de sensores..."

if lsmod | grep -q sensor_driver; then
    sudo rmmod sensor_driver
    echo "Driver descargado"
else
    echo "Driver no estaba cargado"
fi

# Mostrar mensajes del kernel
echo "Últimos mensajes del kernel:"
dmesg | tail -5
EOF

cat > run_app.sh << 'EOF'
#!/bin/bash

# Script para ejecutar la aplicación
echo "Ejecutando aplicación de monitoreo..."

# Activar entorno virtual
source venv/bin/activate

# Verificar que el driver esté cargado
if ! lsmod | grep -q sensor_driver; then
    echo "Error: Driver no está cargado"
    echo "Ejecuta primero: ./load_driver.sh"
    exit 1
fi

# Verificar que el dispositivo existe
if [ ! -e /dev/sensor_drv ]; then
    echo "Error: /dev/sensor_drv no existe"
    echo "Verifica que el driver esté correctamente cargado"
    exit 1
fi

# Ejecutar aplicación
python3 sensor_app.py
EOF

# Hacer scripts ejecutables
chmod +x load_driver.sh unload_driver.sh run_app.sh

# Crear archivo de configuración para QEMU
cat > qemu_setup.md << 'EOF'
# Configuración QEMU para Raspberry Pi

## Para usar con QEMU y qemu-rpi-gpio:

1. Instalar qemu-rpi-gpio:
   ```bash
   pip install qemu-rpi-gpio
   ```

2. Configurar GPIO virtuales en el código del driver si es necesario
   (el driver actual simula los sensores sin hardware real)

3. Para emular Raspberry Pi con QEMU:
   ```bash
   qemu-system-arm -M raspi3b -kernel kernel8.img -dtb bcm2710-rpi-3-b.dtb -append "console=ttyAMA0"
   ```

## Notas:
- El driver actual funciona en cualquier sistema Linux
- Simula lecturas de sensores sin hardware real
- Para hardware real, modifica las funciones de lectura GPIO
EOF

print_status "Instalación completada exitosamente"
echo
echo "=== Instrucciones de uso ==="
echo "1. Cargar el driver:     sudo ./load_driver.sh"
echo "2. Ejecutar aplicación:  sudo ./run_app.sh"
echo "3. Descargar driver:     sudo ./unload_driver.sh"
echo
echo "=== Comandos útiles ==="
echo "Ver driver cargado:      lsmod | grep sensor"
echo "Ver dispositivo:         ls -l /dev/sensor_drv"
echo "Ver mensajes kernel:     sudo dmesg | tail"
echo "Compilar driver:         make"
echo
echo "El entorno virtual está en: ./venv/"
echo "Para activarlo manualmente: source venv/bin/activate"
echo
print_status "¡Listo para usar!"