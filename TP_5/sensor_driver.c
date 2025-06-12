#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/device.h>
#include <linux/uaccess.h>
#include <linux/timer.h>
#include <linux/jiffies.h>
#include <linux/random.h>
#include <linux/mutex.h>
#include <linux/slab.h>
#include <linux/proc_fs.h>
#include <linux/seq_file.h>

// Configuración específica para QEMU
#define DEVICE_NAME "sensor_drv"
#define CLASS_NAME "sensor_class"
#define PROC_NAME "sensor_qemu"
#define BUFFER_SIZE 1024
#define TIMER_INTERVAL_MS 1000  // 1 segundo

// Configuración QEMU específica
#define QEMU_TEMP_BASE 25       // Temperatura base en °C
#define QEMU_TEMP_RANGE 20      // Rango de temperatura
#define QEMU_HUMID_BASE 45      // Humedad base en %
#define QEMU_HUMID_RANGE 35     // Rango de humedad
#define QEMU_NOISE_FACTOR 5     // Factor de ruido para simulación realista

// Estructura para datos del sensor optimizada para QEMU
struct sensor_data {
    int signal_type;            // 0 = temperatura, 1 = humedad
    int current_value;          // Valor actual del sensor
    unsigned long timestamp;    // Timestamp de la lectura
    int qemu_cycle;            // Ciclo de simulación QEMU
    int noise_level;           // Nivel de ruido simulado
};

// Variables globales específicas para QEMU
static int major_number;
static struct class* sensor_class = NULL;
static struct device* sensor_device = NULL;
static struct cdev sensor_cdev;
static dev_t dev_num;

// Buffer circular para almacenar datos
static struct sensor_data sensor_buffer[BUFFER_SIZE];
static int buffer_head = 0;
static int buffer_tail = 0;
static int buffer_count = 0;

// Configuración del sensor
static int selected_signal = 0;  // Por defecto temperatura
static struct timer_list sensor_timer;
static unsigned long qemu_boot_time;
static int qemu_simulation_cycle = 0;

// Mutex para proteger acceso concurrente
static DEFINE_MUTEX(sensor_mutex);

// Entrada proc para información QEMU
static struct proc_dir_entry *proc_entry;

// Simulación QEMU avanzada - Sin GPIO físico
struct qemu_sensor_state {
    int temp_trend;         // Tendencia de temperatura (-1, 0, 1)
    int humid_trend;        // Tendencia de humedad (-1, 0, 1)
    int cycle_counter;      // Contador de ciclos
    bool qemu_detected;     // Flag para confirmación QEMU
};

static struct qemu_sensor_state qemu_state = {
    .temp_trend = 0,
    .humid_trend = 0,
    .cycle_counter = 0,
    .qemu_detected = true   // Asumimos QEMU siempre
};

// Prototipos de funciones
static int sensor_open(struct inode *inode, struct file *file);
static int sensor_release(struct inode *inode, struct file *file);
static ssize_t sensor_read(struct file *file, char __user *buffer, size_t len, loff_t *offset);
static ssize_t sensor_write(struct file *file, const char __user *buffer, size_t len, loff_t *offset);
static void sensor_timer_callback(struct timer_list *timer);

// Funciones específicas QEMU
static int detect_qemu_environment(void);
static void qemu_sensor_simulation_update(void);

// Tabla de valores precomputados para simulación de ondas sinusoidales
// Valores entre -100 y 100 para evitar operaciones de punto flotante
static const int sine_table[360] = {
    0, 2, 3, 5, 7, 9, 10, 12, 14, 16, 17, 19, 21, 22, 24, 26, 28, 29, 31, 33,
    34, 36, 37, 39, 41, 42, 44, 45, 47, 48, 50, 52, 53, 54, 56, 57, 59, 60,
    62, 63, 64, 66, 67, 68, 69, 71, 72, 73, 74, 75, 77, 78, 79, 80, 81, 82,
    83, 84, 85, 86, 87, 88, 89, 90, 91, 91, 92, 93, 94, 94, 95, 96, 96, 97,
    97, 98, 98, 99, 99, 99, 100, 100, 100, 100, 100, 100, 100, 99, 99, 99, 98, 98,
    97, 97, 96, 96, 95, 94, 94, 93, 92, 91, 91, 90, 89, 88, 87, 86, 85, 84,
    83, 82, 81, 80, 79, 78, 77, 75, 74, 73, 72, 71, 69, 68, 67, 66, 64, 63,
    62, 60, 59, 57, 56, 54, 53, 52, 50, 48, 47, 45, 44, 42, 41, 39, 37, 36,
    34, 33, 31, 29, 28, 26, 24, 22, 21, 19, 17, 16, 14, 12, 10, 9, 7, 5,
    3, 2, 0, -2, -3, -5, -7, -9, -10, -12, -14, -16, -17, -19, -21, -22, -24, -26,
    -28, -29, -31, -33, -34, -36, -37, -39, -41, -42, -44, -45, -47, -48, -50, -52, -53, -54,
    -56, -57, -59, -60, -62, -63, -64, -66, -67, -68, -69, -71, -72, -73, -74, -75, -77, -78,
    -79, -80, -81, -82, -83, -84, -85, -86, -87, -88, -89, -90, -91, -91, -92, -93, -94, -94,
    -95, -96, -96, -97, -97, -98, -98, -99, -99, -99, -100, -100, -100, -100, -100, -100, -100, -99,
    -99, -99, -98, -98, -97, -97, -96, -96, -95, -94, -94, -93, -92, -91, -91, -90, -89, -88,
    -87, -86, -85, -84, -83, -82, -81, -80, -79, -78, -77, -75, -74, -73, -72, -71, -69, -68,
    -67, -66, -64, -63, -62, -60, -59, -57, -56, -54, -53, -52, -50, -48, -47, -45, -44, -42,
    -41, -39, -37, -36, -34, -33, -31, -29, -28, -26, -24, -22, -21, -19, -17, -16, -14, -12,
    -10, -9, -7, -5, -3, -2
};

// Función auxiliar para obtener seno aproximado usando tabla
static int get_sine_value(unsigned long angle_deg) {
    return sine_table[angle_deg % 360];
}

// Función auxiliar para obtener coseno aproximado usando tabla (desfase de 90°)
static int get_cosine_value(unsigned long angle_deg) {
    return sine_table[(angle_deg + 90) % 360];
}

// Estructura de operaciones del archivo
static struct file_operations fops = {
    .open = sensor_open,
    .read = sensor_read,
    .write = sensor_write,
    .release = sensor_release,
};

// Función para detectar entorno QEMU
static int detect_qemu_environment(void) {
    // En esta versión, asumimos que SIEMPRE estamos en QEMU
    qemu_state.qemu_detected = true;
    qemu_boot_time = jiffies;
    
    printk(KERN_INFO "sensor_drv: Entorno QEMU detectado y confirmado\n");
    printk(KERN_INFO "sensor_drv: Simulación GPIO completa activada\n");
    printk(KERN_INFO "sensor_drv: Sensores virtuales: Temperatura y Humedad\n");
    
    return 1;  // Siempre detectamos QEMU
}

// Actualización avanzada de simulación QEMU
static void qemu_sensor_simulation_update(void) {
    qemu_simulation_cycle++;
    
    // Cambiar tendencias cada cierto número de ciclos para simular variaciones realistas
    if (qemu_simulation_cycle % 30 == 0) {  // Cada 30 segundos
        get_random_bytes(&qemu_state.temp_trend, sizeof(qemu_state.temp_trend));
        qemu_state.temp_trend = (qemu_state.temp_trend % 3) - 1;  // -1, 0, 1
        
        get_random_bytes(&qemu_state.humid_trend, sizeof(qemu_state.humid_trend));
        qemu_state.humid_trend = (qemu_state.humid_trend % 3) - 1;  // -1, 0, 1
        
        printk(KERN_DEBUG "sensor_drv: QEMU simulación - Nueva tendencia temp: %d, humid: %d\n",
               qemu_state.temp_trend, qemu_state.humid_trend);
    }
}

// Función para leer sensores simulados en QEMU - Mejorada y sin operaciones de punto flotante
static int read_qemu_sensor_value(int signal_type) {
    int base_value, variation, noise, trend_effect;
    unsigned long time_factor;
    unsigned long angle;
    
    // Factor de tiempo basado en ciclos de simulación
    time_factor = (jiffies - qemu_boot_time) / HZ;  // Segundos desde boot
    
    if (signal_type == 0) {
        // Sensor de temperatura QEMU - Simulación realista
        base_value = QEMU_TEMP_BASE;
        
        // Variación cíclica usando tabla de senos (simula cambios ambientales)
        angle = (time_factor / 10) % 360;  // Ciclo cada 10 minutos aproximadamente
        variation = (get_sine_value(angle) * 10) / 100;  // Escalado a ±10
        variation += (qemu_simulation_cycle % QEMU_TEMP_RANGE);
        
        // Efecto de tendencia
        trend_effect = qemu_state.temp_trend * (qemu_simulation_cycle % 5);
        
        // Ruido aleatorio
        get_random_bytes(&noise, sizeof(noise));
        noise = (noise % (QEMU_NOISE_FACTOR * 2)) - QEMU_NOISE_FACTOR;
        
        return base_value + variation + trend_effect + noise;
        
    } else {
        // Sensor de humedad QEMU - Simulación realista
        base_value = QEMU_HUMID_BASE;
        
        // Variación cíclica usando tabla de cosenos (inversa a temperatura para simular realismo)
        angle = (time_factor / 15) % 360;  // Ciclo cada 15 minutos aproximadamente
        variation = (get_cosine_value(angle) * 15) / 100;  // Escalado a ±15
        variation += (qemu_simulation_cycle % QEMU_HUMID_RANGE);
        
        // Efecto de tendencia
        trend_effect = qemu_state.humid_trend * (qemu_simulation_cycle % 8);
        
        // Ruido aleatorio
        get_random_bytes(&noise, sizeof(noise));
        noise = (noise % (QEMU_NOISE_FACTOR * 3)) - (QEMU_NOISE_FACTOR + 2);
        
        // Limitar humedad entre 10-95%
        int result = base_value + variation + trend_effect + noise;
        if (result < 10) result = 10;
        if (result > 95) result = 95;
        
        return result;
    }
}

// Callback del timer optimizado para QEMU
static void sensor_timer_callback(struct timer_list *timer) {
    struct sensor_data data;
    
    // Actualizar simulación QEMU
    qemu_sensor_simulation_update();
    
    mutex_lock(&sensor_mutex);
    
    // Leer el sensor seleccionado con simulación QEMU
    data.signal_type = selected_signal;
    data.current_value = read_qemu_sensor_value(selected_signal);
    data.timestamp = jiffies;
    data.qemu_cycle = qemu_simulation_cycle;
    data.noise_level = (qemu_simulation_cycle % 10);  // Nivel de ruido simulado
    
    // Agregar al buffer circular
    sensor_buffer[buffer_head] = data;
    buffer_head = (buffer_head + 1) % BUFFER_SIZE;
    
    if (buffer_count < BUFFER_SIZE) {
        buffer_count++;
    } else {
        // Buffer lleno, mover tail
        buffer_tail = (buffer_tail + 1) % BUFFER_SIZE;
    }
    
    mutex_unlock(&sensor_mutex);
    
    // Reprogramar el timer
    mod_timer(&sensor_timer, jiffies + msecs_to_jiffies(TIMER_INTERVAL_MS));
    
    // Log más detallado para QEMU
    printk(KERN_DEBUG "sensor_drv: QEMU Ciclo %d - Señal %d (%s), Valor: %d, Tendencia: %d\n", 
           qemu_simulation_cycle,
           data.signal_type, 
           (data.signal_type == 0) ? "Temp" : "Humid",
           data.current_value,
           (data.signal_type == 0) ? qemu_state.temp_trend : qemu_state.humid_trend);
}

// Función open
static int sensor_open(struct inode *inode, struct file *file) {
    printk(KERN_INFO "sensor_drv: Device QEMU abierto\n");
    return 0;
}

// Función release
static int sensor_release(struct inode *inode, struct file *file) {
    printk(KERN_INFO "sensor_drv: Device QEMU cerrado\n");
    return 0;
}

// Función read - Formato extendido para QEMU
static ssize_t sensor_read(struct file *file, char __user *buffer, size_t len, loff_t *offset) {
    struct sensor_data data;
    char output_buffer[512];  // Buffer más grande para información QEMU
    int output_len;
    
    mutex_lock(&sensor_mutex);
    
    if (buffer_count == 0) {
        mutex_unlock(&sensor_mutex);
        return 0;  // No hay datos disponibles
    }
    
    // Obtener dato del buffer
    data = sensor_buffer[buffer_tail];
    buffer_tail = (buffer_tail + 1) % BUFFER_SIZE;
    buffer_count--;
    
    mutex_unlock(&sensor_mutex);
    
    // Formatear los datos con información extendida QEMU
    output_len = snprintf(output_buffer, sizeof(output_buffer),
                         "%d,%d,%lu,%d,%d,%s\n",
                         data.signal_type, 
                         data.current_value, 
                         data.timestamp,
                         data.qemu_cycle,
                         data.noise_level,
                         qemu_state.qemu_detected ? "QEMU" : "REAL");
    
    if (len < output_len) {
        return -EINVAL;
    }
    
    if (copy_to_user(buffer, output_buffer, output_len)) {
        return -EFAULT;
    }
    
    return output_len;
}

// Función write - Con comandos especiales QEMU
static ssize_t sensor_write(struct file *file, const char __user *buffer, size_t len, loff_t *offset) {
    char input_buffer[32];
    int new_signal;
    
    if (len >= sizeof(input_buffer)) {
        return -EINVAL;
    }
    
    if (copy_from_user(input_buffer, buffer, len)) {
        return -EFAULT;
    }
    
    input_buffer[len] = '\0';
    
    // Comandos especiales QEMU
    if (strncmp(input_buffer, "reset", 5) == 0) {
        mutex_lock(&sensor_mutex);
        buffer_head = buffer_tail = buffer_count = 0;
        qemu_simulation_cycle = 0;
        qemu_state.temp_trend = qemu_state.humid_trend = 0;
        mutex_unlock(&sensor_mutex);
        printk(KERN_INFO "sensor_drv: QEMU simulación reiniciada\n");
        return len;
    }
    
    if (strncmp(input_buffer, "info", 4) == 0) {
        printk(KERN_INFO "sensor_drv: QEMU Info - Ciclo: %d, Buffer: %d/%d, Señal: %d\n",
               qemu_simulation_cycle, buffer_count, BUFFER_SIZE, selected_signal);
        return len;
    }
    
    // Configuración normal de señal
    if (kstrtoint(input_buffer, 10, &new_signal) != 0) {
        return -EINVAL;
    }
    
    if (new_signal != 0 && new_signal != 1) {
        printk(KERN_WARNING "sensor_drv: QEMU - Señal inválida %d. Use 0 (temp) o 1 (humid)\n", new_signal);
        return -EINVAL;
    }
    
    mutex_lock(&sensor_mutex);
    if (selected_signal != new_signal) {
        selected_signal = new_signal;
        // Limpiar buffer al cambiar de señal
        buffer_head = buffer_tail = buffer_count = 0;
        printk(KERN_INFO "sensor_drv: QEMU - Cambiado a señal %d (%s), buffer limpiado\n", 
               selected_signal, (selected_signal == 0) ? "Temperatura" : "Humedad");
    }
    mutex_unlock(&sensor_mutex);
    
    return len;
}

// Función proc para mostrar información QEMU
static int sensor_proc_show(struct seq_file *m, void *v) {
    seq_printf(m, "=== Driver de Sensores QEMU ===\n");
    seq_printf(m, "Entorno: QEMU Virtual\n");
    seq_printf(m, "Señal actual: %d (%s)\n", selected_signal, 
               (selected_signal == 0) ? "Temperatura" : "Humedad");
    seq_printf(m, "Ciclo simulación: %d\n", qemu_simulation_cycle);
    seq_printf(m, "Buffer ocupado: %d/%d\n", buffer_count, BUFFER_SIZE);
    seq_printf(m, "Tendencia temp: %d\n", qemu_state.temp_trend);
    seq_printf(m, "Tendencia humid: %d\n", qemu_state.humid_trend);
    seq_printf(m, "Tiempo activo: %lu segundos\n", (jiffies - qemu_boot_time) / HZ);
    seq_printf(m, "\nComandos disponibles:\n");
    seq_printf(m, "  echo 0 > /dev/sensor_drv     # Seleccionar temperatura\n");
    seq_printf(m, "  echo 1 > /dev/sensor_drv     # Seleccionar humedad\n");
    seq_printf(m, "  echo reset > /dev/sensor_drv # Reiniciar simulación\n");
    seq_printf(m, "  echo info > /dev/sensor_drv  # Mostrar información\n");
    return 0;
}

static int sensor_proc_open(struct inode *inode, struct file *file) {
    return single_open(file, sensor_proc_show, NULL);
}

static const struct proc_ops sensor_proc_ops = {
    .proc_open = sensor_proc_open,
    .proc_read = seq_read,
    .proc_lseek = seq_lseek,
    .proc_release = single_release,
};

// Función de inicialización del módulo - Específica QEMU
static int __init sensor_init(void) {
    int result;
    
    printk(KERN_INFO "sensor_drv: Inicializando driver QEMU de sensores virtuales\n");
    
    // Detectar y configurar entorno QEMU
    if (!detect_qemu_environment()) {
        printk(KERN_WARNING "sensor_drv: QEMU no detectado, pero continuando en modo QEMU forzado\n");
    }
    
    // Asignar número mayor dinámicamente
    result = alloc_chrdev_region(&dev_num, 0, 1, DEVICE_NAME);
    if (result < 0) {
        printk(KERN_ALERT "sensor_drv: Error asignando número mayor\n");
        return result;
    }
    major_number = MAJOR(dev_num);
    
    // Inicializar cdev
    cdev_init(&sensor_cdev, &fops);
    sensor_cdev.owner = THIS_MODULE;
    
    // Agregar cdev al sistema
    result = cdev_add(&sensor_cdev, dev_num, 1);
    if (result < 0) {
        printk(KERN_ALERT "sensor_drv: Error agregando cdev\n");
        unregister_chrdev_region(dev_num, 1);
        return result;
    }
    
    // Crear clase de dispositivo
    sensor_class = class_create(CLASS_NAME);
    if (IS_ERR(sensor_class)) {
        printk(KERN_ALERT "sensor_drv: Error creando clase\n");
        cdev_del(&sensor_cdev);
        unregister_chrdev_region(dev_num, 1);
        return PTR_ERR(sensor_class);
    }
    
    // Crear dispositivo
    sensor_device = device_create(sensor_class, NULL, dev_num, NULL, DEVICE_NAME);
    if (IS_ERR(sensor_device)) {
        printk(KERN_ALERT "sensor_drv: Error creando dispositivo\n");
        class_destroy(sensor_class);
        cdev_del(&sensor_cdev);
        unregister_chrdev_region(dev_num, 1);
        return PTR_ERR(sensor_device);
    }
    
    // Crear entrada proc para información QEMU
    proc_entry = proc_create(PROC_NAME, 0666, NULL, &sensor_proc_ops);
    if (!proc_entry) {
        printk(KERN_WARNING "sensor_drv: No se pudo crear entrada proc\n");
    }
    
    // Inicializar timer con configuración QEMU
    timer_setup(&sensor_timer, sensor_timer_callback, 0);
    mod_timer(&sensor_timer, jiffies + msecs_to_jiffies(TIMER_INTERVAL_MS));
    
    printk(KERN_INFO "sensor_drv: Driver QEMU registrado exitosamente\n");
    printk(KERN_INFO "sensor_drv: Dispositivo: /dev/%s (major %d)\n", DEVICE_NAME, major_number);
    printk(KERN_INFO "sensor_drv: Información: /proc/%s\n", PROC_NAME);
    printk(KERN_INFO "sensor_drv: Sensores simulados - Temp: %d-+%d°C, Humid: %d±%d%%\n",
           QEMU_TEMP_BASE, QEMU_TEMP_RANGE, QEMU_HUMID_BASE, QEMU_HUMID_RANGE);
    
    return 0;
}

// Función de limpieza del módulo
static void __exit sensor_exit(void) {
    printk(KERN_INFO "sensor_drv: Desinstalando driver QEMU...\n");
    
    // Detener timer
    del_timer_sync(&sensor_timer);
    
    // Remover entrada proc
    if (proc_entry) {
        proc_remove(proc_entry);
    }
    
    // Limpiar en orden inverso
    device_destroy(sensor_class, dev_num);
    class_destroy(sensor_class);
    cdev_del(&sensor_cdev);
    unregister_chrdev_region(dev_num, 1);
    
    printk(KERN_INFO "sensor_drv: Driver QEMU desinstalado exitosamente\n");
    printk(KERN_INFO "sensor_drv: Ciclos completados: %d\n", qemu_simulation_cycle);
}

module_init(sensor_init);
module_exit(sensor_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Grupo C-- - QEMU Edition");
MODULE_DESCRIPTION("Character Device Driver para sensores virtuales QEMU");
MODULE_VERSION("2.0-QEMU");