#!/usr/bin/env python3
"""
Aplicación de usuario para leer datos del sensor driver
y graficarlos en tiempo real
"""

import matplotlib
matplotlib.use('TkAgg')  # Configurar backend antes de importar pyplot
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
from collections import deque
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

class SensorReader:
    def __init__(self, device_path="/dev/sensor_drv"):
        self.device_path = device_path
        self.current_signal = 0
        self.data_lock = threading.Lock()
        
        # Buffers para cada señal
        self.signal1_data = deque(maxlen=100)  # Últimos 100 puntos
        self.signal1_times = deque(maxlen=100)
        self.signal2_data = deque(maxlen=100)
        self.signal2_times = deque(maxlen=100)
        
        # Variables de control
        self.running = False
        self.reader_thread = None
        
    def set_signal(self, signal_type):
        """Configura qué señal leer (0 o 1)"""
        try:
            with open(self.device_path, 'w') as f:
                f.write(str(signal_type))
            
            with self.data_lock:
                self.current_signal = signal_type
                # Limpiar datos de la señal anterior al cambiar
                if signal_type == 0:
                    self.signal1_data.clear()
                    self.signal1_times.clear()
                else:
                    self.signal2_data.clear()
                    self.signal2_times.clear()
                    
            return True
        except Exception as e:
            print(f"Error configurando señal: {e}")
            return False
    
    def read_data(self):
        """Hilo para leer datos continuamente del driver"""
        try:
            while self.running:
                try:
                    with open(self.device_path, 'r') as f:
                        line = f.readline().strip()
                        
                    if line:
                        # Parsear formato del driver C: signal_type,value,timestamp,qemu_cycle,noise_level,environment
                        parts = line.split(',')
                        if len(parts) >= 3:  # Al menos los primeros 3 campos son necesarios
                            try:
                                signal_type = int(parts[0])
                                value = int(parts[1])
                                timestamp = int(parts[2])
                                
                                # Convertir timestamp a tiempo actual
                                current_time = time.time()
                                
                                with self.data_lock:
                                    if signal_type == 0:
                                        self.signal1_data.append(value)
                                        self.signal1_times.append(current_time)
                                    else:
                                        self.signal2_data.append(value)
                                        self.signal2_times.append(current_time)
                                        
                            except ValueError:
                                continue
                    else:
                        time.sleep(0.5)  # Esperar más tiempo si no hay datos
                        continue
                        
                    time.sleep(0.1)  # Pequeña pausa para no saturar la CPU
                        
                except FileNotFoundError:
                    print(f"Error: Dispositivo {self.device_path} no encontrado")
                    break
                except PermissionError:
                    print(f"Error: Sin permisos para leer {self.device_path}")
                    break
                except Exception as e:
                    if self.running:
                        print(f"Error leyendo datos: {e}")
                    time.sleep(1)  # Esperar antes de reintentar
                        
        except Exception as e:
            print(f"Error crítico en lectura: {e}")
    
    def start_reading(self):
        """Inicia la lectura de datos"""
        if not self.running:
            self.running = True
            self.reader_thread = threading.Thread(target=self.read_data)
            self.reader_thread.daemon = True
            self.reader_thread.start()
    
    def stop_reading(self):
        """Detiene la lectura de datos"""
        self.running = False
        if self.reader_thread and self.reader_thread.is_alive():
            self.reader_thread.join(timeout=2)
    
    def get_current_data(self):
        """Obtiene los datos actuales para graficar"""
        with self.data_lock:
            if self.current_signal == 0:
                return (list(self.signal1_times), list(self.signal1_data), 
                       "Temperatura (°C)", "Señal 1: Temperatura")
            else:
                return (list(self.signal2_times), list(self.signal2_data),
                       "Humedad (%)", "Señal 2: Humedad")

class SensorGUI:
    def __init__(self):
        self.sensor = SensorReader()
        
        # Configurar la ventana principal
        self.root = tk.Tk()
        self.root.title("Monitor de Sensores QEMU")
        self.root.geometry("1200x800")
        
        # Configurar cierre adecuado
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Frame de control superior
        control_frame = ttk.Frame(self.root)
        control_frame.pack(pady=10, fill=tk.X)
        
        # Selector de señal
        signal_frame = ttk.LabelFrame(control_frame, text="Selección de Señal")
        signal_frame.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.X, expand=True)
        
        self.signal_var = tk.IntVar(value=0)
        ttk.Radiobutton(signal_frame, text="Señal 0 (Temperatura)", 
                       variable=self.signal_var, value=0, 
                       command=self.change_signal).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(signal_frame, text="Señal 1 (Humedad)", 
                       variable=self.signal_var, value=1, 
                       command=self.change_signal).pack(side=tk.LEFT, padx=10)
        
        # Botones de control
        button_frame = ttk.LabelFrame(control_frame, text="Control")
        button_frame.pack(side=tk.RIGHT, padx=10, pady=5)
        
        self.start_button = ttk.Button(button_frame, text="Iniciar", 
                                      command=self.start_monitoring)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Detener", 
                                     command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Botón para comandos especiales
        self.reset_button = ttk.Button(button_frame, text="Reset Driver", 
                                      command=self.reset_driver)
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        # Status label con más información
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.status_var = tk.StringVar(value="Listo - Selecciona una señal e inicia el monitoreo")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, 
                                background='lightgray', relief=tk.SUNKEN)
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.data_count_var = tk.StringVar(value="Datos: 0")
        data_label = ttk.Label(status_frame, textvariable=self.data_count_var,
                              background='lightblue', relief=tk.SUNKEN, width=15)
        data_label.pack(side=tk.RIGHT, padx=5)
        
        # Configurar matplotlib embebido en tkinter
        self.setup_plot()
        
        # Variables para la animación
        self.start_time = None
        self.animation = None
        self.animation_counter = 0
        
    def setup_plot(self):
        """Configura el gráfico embebido en tkinter"""
        # Crear figura más grande
        self.fig, self.ax = plt.subplots(figsize=(14, 8))
        self.ax.set_xlabel('Tiempo (s)')
        self.ax.set_ylabel('Valor')
        self.ax.set_title('Datos del Sensor QEMU')
        self.ax.grid(True, alpha=0.3)
        
        # Línea del gráfico con más estilo
        self.line, = self.ax.plot([], [], 'b-', linewidth=2, marker='o', 
                                 markersize=4, alpha=0.8)
        
        # Configurar límites iniciales
        self.ax.set_xlim(0, 60)  # 60 segundos iniciales
        self.ax.set_ylim(0, 100)  # Rango inicial
        
        # Embebir matplotlib en tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Toolbar de matplotlib
        toolbar_frame = ttk.Frame(self.root)
        toolbar_frame.pack(fill=tk.X, padx=5)
        
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()
        
    def reset_driver(self):
        """Resetea el driver usando el comando especial"""
        try:
            with open(self.sensor.device_path, 'w') as f:
                f.write('reset')
            self.status_var.set("Driver reseteado")
        except Exception as e:
            messagebox.showerror("Error", f"Error reseteando driver: {e}")
        
    def change_signal(self):
        """Callback para cambio de señal"""
        signal = self.signal_var.get()
        signal_name = "Temperatura" if signal == 0 else "Humedad"
        self.status_var.set(f"Cambiando a Señal {signal} ({signal_name})")
        
        if self.sensor.set_signal(signal):
            # Limpiar gráfico al cambiar señal
            self.ax.clear()
            self.ax.set_xlabel('Tiempo (s)')
            self.ax.grid(True, alpha=0.3)
            self.line, = self.ax.plot([], [], 'b-', linewidth=2, marker='o', 
                                     markersize=4, alpha=0.8)
            
            # Actualizar título y límites
            unit = "°C" if signal == 0 else "%"
            self.ax.set_ylabel(f'{signal_name} ({unit})')
            self.ax.set_title(f'Señal {signal}: {signal_name}')
            
            # Ajustar límites según el tipo de señal
            if signal == 0:  # Temperatura
                self.ax.set_ylim(0, 60)  # Rango de temperatura
            else:  # Humedad
                self.ax.set_ylim(0, 100)  # Rango de humedad
            
            self.ax.set_xlim(0, 60)
            
            # Resetear tiempo de inicio
            self.start_time = time.time()
            self.canvas.draw()
            
            self.status_var.set(f"Señal {signal} ({signal_name}) seleccionada")
        else:
            self.status_var.set("Error cambiando señal")
    
    def animate(self, frame):
        """Función de animación para actualizar el gráfico"""
        try:
            self.animation_counter += 1
            times, values, ylabel, title = self.sensor.get_current_data()
            
            # Actualizar contador de datos
            self.data_count_var.set(f"Datos: {len(values)}")
            
            if times and values and self.start_time:
                # Convertir tiempos absolutos a relativos
                rel_times = [(t - self.start_time) for t in times]
                
                # Actualizar datos del gráfico
                self.line.set_data(rel_times, values)
                
                # Ajustar límites dinámicamente
                if rel_times and values:
                    # Límites X (tiempo)
                    max_time = max(rel_times)
                    margin_x = max(5, max_time * 0.05)
                    self.ax.set_xlim(-margin_x, max_time + margin_x)
                    
                    # Límites Y (valores)
                    min_val = min(values)
                    max_val = max(values)
                    
                    # Agregar margen basado en el tipo de señal
                    if self.sensor.current_signal == 0:  # Temperatura
                        margin_y = max(5, (max_val - min_val) * 0.2)
                        y_min = max(0, min_val - margin_y)
                        y_max = min(60, max_val + margin_y)
                    else:  # Humedad
                        margin_y = max(5, (max_val - min_val) * 0.2)
                        y_min = max(0, min_val - margin_y)
                        y_max = min(100, max_val + margin_y)
                    
                    self.ax.set_ylim(y_min, y_max)
                
                # Actualizar etiquetas
                self.ax.set_ylabel(ylabel)
                self.ax.set_title(title)
                
                # Actualizar status cada 10 frames para no saturar
                if self.animation_counter % 10 == 0 and values:
                    last_value = values[-1]
                    signal_num = self.signal_var.get()
                    time_elapsed = rel_times[-1] if rel_times else 0
                    self.status_var.set(f"Monitoreando Señal {signal_num} - "
                                      f"Último: {last_value} - Tiempo: {time_elapsed:.1f}s")
            else:
                # Si no hay datos, mostrar mensaje
                if self.animation_counter % 20 == 0:  # Cada 10 segundos aprox
                    signal_num = self.sensor.current_signal
                    self.status_var.set(f"Esperando datos de señal {signal_num}... "
                                      f"(¿Driver cargado?)")
            
            return self.line,
            
        except Exception as e:
            return self.line,
    
    def start_monitoring(self):
        """Inicia el monitoreo"""
        if not os.path.exists(self.sensor.device_path):
            messagebox.showerror("Error", 
                               f"Dispositivo {self.sensor.device_path} no encontrado.\n"
                               "Asegúrate de que el driver esté cargado con:\n"
                               "sudo insmod sensor_driver.ko")
            return
        
        self.status_var.set("Iniciando monitoreo...")
        
        # Configurar señal inicial
        if not self.sensor.set_signal(self.signal_var.get()):
            messagebox.showerror("Error", "No se pudo configurar la señal inicial")
            return
        
        # Iniciar lectura
        self.sensor.start_reading()
        self.start_time = time.time()
        self.animation_counter = 0
        
        # Iniciar animación
        try:
            self.animation = animation.FuncAnimation(
                self.fig, self.animate, 
                interval=500,  # Actualizar cada 500ms
                blit=False,
                cache_frame_data=False
            )
            
            # Actualizar botones
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
            self.status_var.set("Monitoreo iniciado - Esperando datos...")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error iniciando animación: {e}")
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Detiene el monitoreo"""
        self.status_var.set("Deteniendo monitoreo...")
        
        # Detener sensor
        self.sensor.stop_reading()
        
        # Detener animación
        if self.animation:
            try:
                self.animation.event_source.stop()
                self.animation = None
            except:
                pass  # Ignorar errores al detener
        
        # Actualizar botones
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        self.status_var.set("Monitoreo detenido")
    
    def on_closing(self):
        """Maneja el cierre de la aplicación"""
        try:
            self.stop_monitoring()
            time.sleep(0.5)  # Dar tiempo para que se detengan los hilos
            
            # Cerrar matplotlib
            plt.close(self.fig)
            
            # Destruir ventana
            self.root.quit()
            self.root.destroy()
            
        except Exception as e:
            # Forzar cierre
            import sys
            sys.exit(0)
    
    def run(self):
        """Ejecuta la aplicación"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()

def main():
    """Función principal"""
    print("Monitor de Sensores QEMU")
    print("========================")
    print("Driver: /dev/sensor_drv")
    print("Información del driver: /proc/sensor_qemu")
    print()
    
    # Verificar que matplotlib esté disponible
    try:
        import matplotlib.pyplot as plt
        import matplotlib.animation as animation
    except ImportError:
        print("Error: matplotlib no está instalado.")
        print("Instala con: pip install matplotlib")
        sys.exit(1)
    
    # Verificar que el dispositivo existe
    device_path = "/dev/sensor_drv"
    if not os.path.exists(device_path):
        print(f"Advertencia: {device_path} no encontrado.")
        print("Para cargar el driver:")
        print("1. Compila: make")
        print("2. Carga: sudo insmod sensor_driver.ko")
        print("3. Verifica: ls -l /dev/sensor_drv")
        print("4. Info: cat /proc/sensor_qemu")
        print()
        
        # Preguntar si continuar anyway para testing
        try:
            response = input("¿Continuar de todas formas? (s/N): ").lower()
            if response != 's':
                sys.exit(1)
        except:
            pass  # Si no hay input disponible, continuar
    else:
        print(f"✓ Dispositivo {device_path} encontrado")
        
        # Mostrar información del driver si está disponible
        try:
            with open("/proc/sensor_qemu", 'r') as f:
                info = f.read()
                print("Información del driver:")
                print(info)
        except:
            print("Info del driver no disponible en /proc/sensor_qemu")
    
    print("Iniciando interfaz gráfica...")
    
    # Ejecutar GUI
    try:
        app = SensorGUI()
        app.run()
    except Exception as e:
        print(f"Error ejecutando aplicación: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()