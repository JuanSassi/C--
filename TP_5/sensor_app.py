#!/usr/bin/env python3
"""
Aplicación de usuario para leer datos del sensor driver
y graficarlos en tiempo real - VERSIÓN CORREGIDA
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
                    
            print(f"Cambiado a señal {signal_type}")
            return True
        except Exception as e:
            print(f"Error configurando señal: {e}")
            return False
    
    def read_data(self):
        """Hilo para leer datos continuamente del driver"""
        try:
            with open(self.device_path, 'r') as f:
                while self.running:
                    try:
                        line = f.readline().strip()
                        if line:
                            # Parsear: signal_type,value,timestamp
                            parts = line.split(',')
                            if len(parts) == 3:
                                signal_type = int(parts[0])
                                value = int(parts[1])
                                timestamp = int(parts[2])
                                
                                # Convertir timestamp de jiffies a segundos relativos
                                current_time = time.time()
                                
                                with self.data_lock:
                                    if signal_type == 0:
                                        self.signal1_data.append(value)
                                        self.signal1_times.append(current_time)
                                    else:
                                        self.signal2_data.append(value)
                                        self.signal2_times.append(current_time)
                        
                        time.sleep(0.1)  # Pequeña pausa para no saturar la CPU
                        
                    except ValueError:
                        continue
                    except Exception as e:
                        if self.running:
                            print(f"Error leyendo datos: {e}")
                        break
                        
        except Exception as e:
            print(f"Error abriendo dispositivo: {e}")
    
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
        self.root.title("Monitor de Sensores")
        self.root.geometry("1000x700")
        
        # Configurar cierre adecuado
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Frame de control superior
        control_frame = ttk.Frame(self.root)
        control_frame.pack(pady=10, fill=tk.X)
        
        # Selector de señal
        signal_frame = ttk.LabelFrame(control_frame, text="Selección de Señal")
        signal_frame.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.X, expand=True)
        
        self.signal_var = tk.IntVar(value=0)
        ttk.Radiobutton(signal_frame, text="Señal 1 (Temperatura)", 
                       variable=self.signal_var, value=0, 
                       command=self.change_signal).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(signal_frame, text="Señal 2 (Humedad)", 
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
        
        # Status label
        self.status_var = tk.StringVar(value="Listo - Selecciona una señal e inicia el monitoreo")
        status_label = ttk.Label(self.root, textvariable=self.status_var, 
                                background='lightgray', relief=tk.SUNKEN)
        status_label.pack(fill=tk.X, padx=5, pady=2)
        
        # Configurar matplotlib embebido en tkinter
        self.setup_plot()
        
        # Variables para la animación
        self.start_time = None
        self.animation = None
        
    def setup_plot(self):
        """Configura el gráfico embebido en tkinter"""
        # Crear figura
        self.fig, self.ax = plt.subplots(figsize=(12, 6))
        self.ax.set_xlabel('Tiempo (s)')
        self.ax.set_ylabel('Valor')
        self.ax.set_title('Datos del Sensor')
        self.ax.grid(True, alpha=0.3)
        
        # Línea del gráfico
        self.line, = self.ax.plot([], [], 'b-', linewidth=2, marker='o', markersize=3)
        
        # Embebir matplotlib en tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Toolbar de matplotlib
        toolbar_frame = ttk.Frame(self.root)
        toolbar_frame.pack(fill=tk.X, padx=5)
        
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()
        
    def change_signal(self):
        """Callback para cambio de señal"""
        signal = self.signal_var.get()
        signal_name = "Temperatura" if signal == 0 else "Humedad"
        self.status_var.set(f"Cambiando a Señal {signal + 1} ({signal_name})")
        
        if self.sensor.set_signal(signal):
            # Limpiar gráfico al cambiar señal
            self.ax.clear()
            self.ax.set_xlabel('Tiempo (s)')
            self.ax.grid(True, alpha=0.3)
            self.line, = self.ax.plot([], [], 'b-', linewidth=2, marker='o', markersize=3)
            
            # Actualizar título
            unit = "°C" if signal == 0 else "%"
            self.ax.set_ylabel(f'{signal_name} ({unit})')
            self.ax.set_title(f'Señal {signal + 1}: {signal_name}')
            
            # Resetear tiempo de inicio
            self.start_time = time.time()
            self.canvas.draw()
            
            self.status_var.set(f"Señal {signal + 1} ({signal_name}) seleccionada")
        else:
            self.status_var.set("Error cambiando señal")
    
    def animate(self, frame):
        """Función de animación para actualizar el gráfico"""
        try:
            times, values, ylabel, title = self.sensor.get_current_data()
            
            if times and values and self.start_time:
                # Convertir tiempos absolutos a relativos
                rel_times = [(t - self.start_time) for t in times]
                
                # Actualizar datos del gráfico
                self.line.set_data(rel_times, values)
                
                # Ajustar límites
                if rel_times:
                    margin_x = max(1, max(rel_times) * 0.05)
                    margin_y = max(1, (max(values) - min(values)) * 0.1)
                    
                    self.ax.set_xlim(-margin_x, max(rel_times) + margin_x)
                    self.ax.set_ylim(min(values) - margin_y, max(values) + margin_y)
                
                # Actualizar etiquetas
                self.ax.set_ylabel(ylabel)
                self.ax.set_title(title)
                
                # Actualizar status
                if values:
                    last_value = values[-1]
                    signal_num = self.signal_var.get() + 1
                    self.status_var.set(f"Monitoreando Señal {signal_num} - Último valor: {last_value}")
            
            return self.line,
            
        except Exception as e:
            print(f"Error en animación: {e}")
            return self.line,
    
    def start_monitoring(self):
        """Inicia el monitoreo"""
        if not os.path.exists(self.sensor.device_path):
            messagebox.showerror("Error", 
                               f"Dispositivo {self.sensor.device_path} no encontrado.\n"
                               "Asegúrate de que el driver esté cargado.")
            return
        
        self.status_var.set("Iniciando monitoreo...")
        
        # Configurar señal inicial
        self.sensor.set_signal(self.signal_var.get())
        
        # Iniciar lectura
        self.sensor.start_reading()
        self.start_time = time.time()
        
        # Iniciar animación
        try:
            self.animation = animation.FuncAnimation(
                self.fig, self.animate, 
                interval=500,  # Actualizar cada 500ms
                blit=False,
                cache_frame_data=False  # Evitar el warning
            )
            
            # Actualizar botones
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
            self.status_var.set("Monitoreo iniciado")
            
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
            print(f"Error cerrando aplicación: {e}")
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
    print("Monitor de Sensores")
    print("==================")
    
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
        print("Asegúrate de que el driver esté cargado con:")
        print("sudo insmod sensor_driver.ko")
        print()
        
        # Preguntar si continuar anyway para testing
        try:
            response = input("¿Continuar de todas formas para testing? (s/N): ").lower()
            if response != 's':
                sys.exit(1)
        except:
            pass  # Si no hay input disponible, continuar
    
    # Ejecutar GUI
    try:
        app = SensorGUI()
        app.run()
    except Exception as e:
        print(f"Error ejecutando aplicación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()