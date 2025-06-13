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
## Requisitos QEMU

- QEMU instalado (qemu-system-x86_64 o qemu-system-arm)
- Kernel headers para desarrollo de drivers
- Python 3 con matplotlib y tkinter
- X11 forwarding para GUI (si usas SSH)

## Características específicas de QEMU
- **GPIO Simulado**: Los sensores son completamente simulados
- **Valores realistas**: Temperatura (15-45°C) y Humedad (20-90%)
- **Sin hardware real**: No requiere GPIO físico
- **Compatible con x86_64 y ARM**: Funciona en ambas arquitecturas

## Arquitecturas soportadas

- **x86_64**: Emulación estándar de PC
- **ARM**: Emulación de Raspberry Pi (raspi3b)

## Instalación

```bash
./install.sh
```

## Uso
1. **Cargar el driver:**
   ```bash
   sudo ./load_driver.sh
   ```
2. **Ejecutar la aplicación:**
   ```bash
   sudo ./run_app.sh
   ```
3. **Descargar el driver:**
   ```bash
   sudo ./unload_driver.sh
   ```
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

## 📈 RendimientoAdd commentMore actions
- **Frecuencia de muestreo**: 1 Hz (1 segundo)
- **Buffer circular**: 1024 muestras
- **Overhead del timer**: ~10μs por callback
- **Memoria utilizada**: ~8KB para buffers
- **Latencia de lectura**: <1ms