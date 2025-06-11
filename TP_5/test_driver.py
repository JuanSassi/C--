#!/usr/bin/env python3
"""
Script de pruebas para verificar el funcionamiento del driver de sensores.
Ejecuta pruebas básicas antes de usar la aplicación principal.
"""

import os
import sys
import time
import subprocess

def print_header(title):
    print("\n" + "="*50)
    print(f" {title}")
    print("="*50)

def print_status(message, success=True):
    status = "✓" if success else "✗"
    color = "\033[92m" if success else "\033[91m"
    reset = "\033[0m"
    print(f"{color}[{status}]{reset} {message}")

def run_command(cmd, check_output=False):
    """Ejecuta un comando y retorna el resultado"""
    try:
        if check_output:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        else:
            result = subprocess.run(cmd, shell=True)
            return result.returncode == 0, "", ""
    except Exception as e:
        return False, "", str(e)

def test_driver_compilation():
    """Prueba la compilación del driver"""
    print_header("PRUEBA 1: Compilación del Driver")
    
    # Verificar que existe el código fuente
    if not os.path.exists("sensor_driver.c"):
        print_status("sensor_driver.c no encontrado", False)
        return False
    
    print_status("Archivo fuente encontrado")
    
    # Verificar Makefile
    if not os.path.exists("Makefile"):
        print_status("Makefile no encontrado", False)
        return False
    
    print_status("Makefile encontrado")
    
    # Compilar
    print("Compilando driver...")
    success, stdout, stderr = run_command("make clean && make", check_output=True)
    
    if success and os.path.exists("sensor_driver.ko"):
        print_status("Compilación exitosa")
        return True
    else:
        print_status("Error en compilación", False)
        if stderr:
            print(f"Error: {stderr}")
        return False

def test_driver_loading():
    """Prueba la carga del driver"""
    print_header("PRUEBA 2: Carga del Driver")
    
    # Verificar si ya está cargado
    success, stdout, stderr = run_command("lsmod | grep sensor_driver", check_output=True)
    if success:
        print("Driver ya está cargado, descargando...")
        run_command("sudo rmmod sensor_driver")
    
    # Cargar driver
    print("Cargando driver...")
    success, stdout, stderr = run_command("sudo insmod sensor_driver.ko", check_output=True)
    
    if not success:
        print_status("Error cargando driver", False)
        if stderr:
            print(f"Error: {stderr}")
        return False
    
    # Verificar que se cargó
    success, stdout, stderr = run_command("lsmod | grep sensor_driver", check_output=True)
    if success:
        print_status("Driver cargado correctamente")
        return True
    else:
        print_status("Driver no aparece en lsmod", False)
        return False

def test_device_creation():
    """Prueba la creación del dispositivo"""
    print_header("PRUEBA 3: Dispositivo de Carácter")
    
    # Esperar un poco para que udev cree el dispositivo
    time.sleep(2)
    
    # Verificar dispositivo
    if os.path.exists("/dev/sensor_drv"):
        print_status("Dispositivo /dev/sensor_drv creado")
        
        # Verificar permisos
        stat_info = os.stat("/dev/sensor_drv")
        print(f"Propietario: {stat_info.st_uid}:{stat_info.st_gid}")
        print(f"Permisos: {oct(stat_info.st_mode)[-3:]}")
        
        return True
    else:
        print_status("Dispositivo /dev/sensor_drv no encontrado", False)
        print("Verificando /proc/devices...")
        
        success, stdout, stderr = run_command("cat /proc/devices | grep sensor", check_output=True)
        if success:
            print("Driver registrado en /proc/devices:")
            print(stdout)
            print("El dispositivo debería crearse automáticamente...")
        
        return False

def test_device_communication():
    """Prueba la comunicación con el dispositivo"""
    print_header("PRUEBA 4: Comunicación con el Dispositivo")
    
    device_path = "/dev/sensor_drv"
    
    if not os.path.exists(device_path):
        print_status("Dispositivo no disponible", False)
        return False
    
    try:
        # Probar escritura (cambiar señal)
        print("Probando escritura (seleccionar señal 0)...")
        with open(device_path, 'w') as f:
            f.write("0")
        print_status("Escritura exitosa")
        
        # Esperar un poco para que haya datos
        print("Esperando datos del sensor...")
        time.sleep(3)
        
        # Probar lectura
        print("Probando lectura...")
        with open(device_path, 'r') as f:
            data = f.readline().strip()
            if data:
                print(f"Datos recibidos: {data}")
                # Verificar formato: signal_type,value,timestamp
                parts = data.split(',')
                if len(parts) == 3:
                    signal_type = int(parts[0])
                    value = int(parts[1])
                    timestamp = int(parts[2])
                    print(f"  Señal: {signal_type}")
                    print(f"  Valor: {value}")
                    print(f"  Timestamp: {timestamp}")
                    print_status("Formato de datos correcto")
                else:
                    print_status("Formato de datos incorrecto", False)
                    return False
            else:
                print_status("No se recibieron datos", False)
                return False
        
        # Probar cambio de señal
        print("Probando cambio a señal 1...")
        with open(device_path, 'w') as f:
            f.write("1")
        
        time.sleep(2)
        
        with open(device_path, 'r') as f:
            data = f.readline().strip()
            if data:
                parts = data.split(',')
                if len(parts) == 3 and int(parts[0]) == 1:
                    print_status("Cambio de señal exitoso")
                else:
                    print_status("Cambio de señal falló", False)
                    return False
        
        return True
        
    except PermissionError:
        print_status("Error de permisos", False)
        print("Intenta: sudo chmod 666 /dev/sensor_drv")
        return False
    except Exception as e:
        print_status(f"Error de comunicación: {e}", False)
        return False

def test_kernel_messages():
    """Prueba los mensajes del kernel"""
    print_header("PRUEBA 5: Mensajes del Kernel")
    
    print("Últimos mensajes del kernel relacionados con el driver:")
    success, stdout, stderr = run_command("dmesg | grep sensor_drv | tail -10", check_output=True)
    
    if success and stdout:
        print(stdout)
        print_status("Mensajes del kernel disponibles")
        return True
    else:
        print_status("No se encontraron mensajes del kernel", False)
        return False

def test_python_dependencies():
    """Prueba las dependencias de Python"""
    print_header("PRUEBA 6: Dependencias de Python")
    
    required_modules = ['matplotlib', 'numpy', 'tkinter']
    all_ok = True
    
    for module in required_modules:
        try:
            if module == 'tkinter':
                import tkinter
            else:
                __import__(module)
            print_status(f"Módulo {module} disponible")
        except ImportError:
            print_status(f"Módulo {module} NO disponible", False)
            all_ok = False
    
    return all_ok

def run_all_tests():
    """Ejecuta todas las pruebas"""
    print_header("SISTEMA DE PRUEBAS DEL DRIVER DE SENSORES")
    
    tests = [
        ("Compilación del Driver", test_driver_compilation),
        ("Carga del Driver", test_driver_loading),
        ("Creación del Dispositivo", test_device_creation),
        ("Comunicación", test_device_communication),
        ("Mensajes del Kernel", test_kernel_messages),
        ("Dependencias Python", test_python_dependencies),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_status(f"Error ejecutando {test_name}: {e}", False)
            results.append((test_name, False))
    
    # Resumen
    print_header("RESUMEN DE PRUEBAS")
    
    passed = 0
    for test_name, result in results:
        print_status(f"{test_name}: {'PASÓ' if result else 'FALLÓ'}", result)
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{len(results)} pruebas pasaron")
    
    if passed == len(results):
        print_status("¡Todas las pruebas pasaron! El sistema está listo.", True)
        print("\nPuedes ejecutar la aplicación con: ./run_app.sh")
    else:
        print_status("Algunas pruebas fallaron. Revisa los errores anteriores.", False)
        print("\nSoluciones comunes:")
        print("1. Compilación: Instala linux-headers-$(uname -r)")
        print("2. Permisos: Ejecuta como usuario normal, no como root")
        print("3. Dispositivo: Verifica que udev esté funcionando")
        print("4. Python: Instala dependencias con pip install matplotlib numpy")
    
    return passed == len(results)

def cleanup():
    """Limpia recursos de las pruebas"""
    print("\nLimpiando...")
    
    # Descargar driver si está cargado
    success, stdout, stderr = run_command("lsmod | grep sensor_driver", check_output=True)
    if success:
        print("Descargando driver...")
        run_command("sudo rmmod sensor_driver")

def main():
    try:
        # Verificar que se ejecuta como usuario normal
        if os.geteuid() == 0:
            print("Error: No ejecutes este script como root.")
            print("Se pedirá sudo cuando sea necesario.")
            sys.exit(1)
        
        # Ejecutar pruebas
        success = run_all_tests()
        
        # Preguntar si descargar el driver
        if success:
            response = input("\n¿Descargar el driver? (s/N): ").lower()
            if response == 's':
                cleanup()
        
    except KeyboardInterrupt:
        print("\n\nPruebas interrumpidas por el usuario.")
        cleanup()
    except Exception as e:
        print(f"\nError inesperado: {e}")
        cleanup()

if __name__ == "__main__":
    main()