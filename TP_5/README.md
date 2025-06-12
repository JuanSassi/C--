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
