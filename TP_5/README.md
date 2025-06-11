# TP5 – Device drivers

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

# Character Device Driver para Sensores Duales

Este proyecto implementa un Character Device Driver (CDD) para Linux que simula la lectura de dos señales de sensores con un período de muestreo de 1 segundo, junto con una aplicación de usuario que permite seleccionar y graficar las señales en tiempo real.

## 📋 Características

- **Driver del Kernel**: CDD que simula dos sensores (temperatura y humedad)
- **Muestreo Periódico**: Lectura automática cada 1 segundo usando kernel timers
- **Selección de Señal**: La aplicación puede seleccionar cuál de las dos señales leer
- **Graficación en Tiempo Real**: Visualización de datos con matplotlib
- **Buffer Circular**: Almacenamiento eficiente de datos en el kernel
- **Thread Safety**: Protección con mutex para acceso concurrente
- **Compatibilidad QEMU**: Funciona en entornos virtualizados

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Aplicación    │    │      Driver      │    │   Simulación    │
│   de Usuario    │    │    del Kernel    │    │   de Sensores   │
│                 │    │                  │    │                 │
│  - GUI tkinter  │◄──►│  - Timer (1s)    │◄──►│  - Temperatura  │
│  - Matplotlib   │    │  - Buffer Circ.  │    │  - Humedad      │
│  - Threading    │    │  - Mutex         │    │  - Ruido        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
    /dev/sensor_drv         Kernel Space
```

## 🚀 Instalación Rápida

1. **Clonar y preparar el entorno**:
```bash
git clone <este-repositorio>
cd TP_5
chmod +x install.sh
./install.sh
```

2. **Cargar el driver**:
```bash
./load_driver.sh
```

3. **Ejecutar la aplicación**:
```bash
sudo ./run_app.sh
```

## 📁 Estructura del Proyecto

```
driver-sensores/
├── sensor_driver.c      # Código fuente del driver
├── Makefile            # Compilación del driver
├── sensor_app.py       # Aplicación de usuario
├── install.sh          # Script de instalación
├── test_driver.py      # Suite de pruebas
├── load_driver.sh      # Cargar driver
├── unload_driver.sh    # Descargar driver
├── run_app.sh          # Ejecutar aplicación
├── qemu_setup.md       # Configuración QEMU
└── README.md           # Este archivo
```

## 🔧 Compilación Manual

### Prerrequisitos

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install build-essential linux-headers-$(uname -r) python3-dev python3-pip

# Python dependencies
pip3 install matplotlib numpy tkinter
```

### Compilar el Driver

```bash
make clean
make
```

### Cargar el Driver

```bash
sudo insmod sensor_driver.ko
```

### Verificar la Carga

```bash
lsmod | grep sensor_driver
ls -l /dev/sensor_drv
dmesg | tail
```

## 🎮 Uso del Sistema

### 1. Interfaz de la Aplicación

La aplicación proporciona:
- **Selector de Señal**: Radio buttons para elegir entre Señal 1 (Temperatura) y Señal 2 (Humedad)
- **Controles**: Botones Iniciar/Detener monitoreo
- **Gráfico en Tiempo Real**: Visualización con matplotlib

### 2. Protocolo de Comunicación

**Escritura al dispositivo** (seleccionar señal):
```bash
echo "0" > /dev/sensor_drv  # Seleccionar señal 1 (temperatura)
echo "1" > /dev/sensor_drv  # Seleccionar señal 2 (humedad)
```

**Lectura del dispositivo** (obtener datos):
```bash
cat /dev/sensor_drv
# Output: signal_type,value,timestamp
# Ejemplo: 0,25,1234567890
```

### 3. Formato de Datos

Los datos se devuelven en formato CSV:
- `signal_type`: 0 (temperatura) o 1 (humedad)
- `value`: Valor del sensor (entero)
- `timestamp`: Timestamp del kernel (jiffies)

## 🧪 Pruebas del Sistema

Ejecutar la suite completa de pruebas:

```bash
python3 test_driver.py
```

Las pruebas verifican:
1. ✅ Compilación del driver
2. ✅ Carga en el kernel
3. ✅ Creación del dispositivo
4. ✅ Comunicación bidireccional
5. ✅ Mensajes del kernel
6. ✅ Dependencias de Python

### Pruebas Manuales

```bash
# Verificar driver cargado
lsmod | grep sensor_driver

# Probar comunicación básica
echo "0" > /dev/sensor_drv
cat /dev/sensor_drv

# Ver mensajes del kernel
dmesg | grep sensor_drv
```

## 🐛 Solución de Problemas

### Error: Dispositivo no encontrado

```bash
# Verificar que el driver esté cargado
lsmod | grep sensor_driver

# Si no está cargado
sudo insmod sensor_driver.ko

# Verificar permisos
ls -l /dev/sensor_drv
sudo chmod 666 /dev/sensor_drv  # Si es necesario
```

### Error: Permisos denegados

```bash
# Agregar usuario al grupo correcto
sudo usermod -a -G dialout $USER
# Logout y login nuevamente

# O cambiar permisos temporalmente
sudo chmod 666 /dev/sensor_drv
```

### Error: Módulo no compila

```bash
# Instalar headers del kernel
sudo apt-get install linux-headers-$(uname -r)

# Verificar versión del kernel
uname -r
ls /usr/src/linux-headers-$(uname -r)
```

### Error: Python matplotlib

```bash
# Instalar dependencias del sistema
sudo apt-get install python3-tk python3-dev

# Instalar en entorno virtual
python3 -m venv venv
source venv/bin/activate
pip install matplotlib numpy
```

## 🖥️ Configuración QEMU

Para usar con QEMU y Raspberry Pi:

### 1. Instalar qemu-rpi-gpio

```bash
pip install qemu-rpi-gpio
```

### 2. Ejecutar QEMU con Raspberry Pi

```bash
# Descargar imagen de Raspberry Pi OS
# Ejecutar QEMU
qemu-system-arm -M raspi3b -kernel kernel8.img \
    -dtb bcm2710-rpi-3-b.dtb \
    -append "console=ttyAMA0" \
    -netdev user,id=net0 -device usb-net,netdev=net0
```

### 3. Configurar GPIO Virtual

El driver actual simula sensores sin hardware real. Para usar GPIO real en Raspberry Pi, modifica las funciones de lectura en `sensor_driver.c`.

## 📊 Detalles Técnicos

### Arquitectura del Driver

```c
// Estructura principal
struct sensor_data {
    int signal_type;        // 0 o 1
    int current_value;      // Valor medido
    unsigned long timestamp; // jiffies
};

// Buffer circular thread-safe
static struct sensor_data sensor_buffer[BUFFER_SIZE];
static DEFINE_MUTEX(sensor_mutex);
```

### Timer del Kernel

```c
// Timer para muestreo periódico (1 segundo)
static struct timer_list sensor_timer;
static void sensor_timer_callback(struct timer_list *timer);

// Reprogramación automática
mod_timer(&sensor_timer, jiffies + msecs_to_jiffies(1000));
```

### Simulación de Sensores

```c
// Señal 1: Temperatura (20-40°C con ruido)
// Señal 2: Humedad (30-80% con ruido)
static int read_sensor_value(int signal_type);
```

## 🔍 Monitoreo y Debug

### Ver actividad del driver

```bash
# Mensajes en tiempo real
sudo dmesg -w | grep sensor_drv

# Estado del buffer
cat /proc/devices | grep sensor

# Información del módulo
modinfo sensor_driver.ko
```

### Debugging avanzado

```bash
# Habilitar debug en el kernel (si está compilado con debug)
echo 8 > /proc/sys/kernel/printk

# Usar ftrace para debugging avanzado
echo 1 > /sys/kernel/debug/tracing/events/syscalls/enable
```

## 📈 Rendimiento

- **Frecuencia de muestreo**: 1 Hz (1 segundo)
- **Buffer circular**: 1024 muestras
- **Overhead del timer**: ~10μs por callback
- **Memoria utilizada**: ~8KB para buffers
- **Latencia de lectura**: <1ms