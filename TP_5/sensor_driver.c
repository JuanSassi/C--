#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/device.h>
#include <linux/uaccess.h>
#include <linux/timer.h>
#include <linux/jiffies.h>
#include <linux/gpio.h>
#include <linux/random.h>
#include <linux/mutex.h>

#define DEVICE_NAME "sensor_drv"
#define CLASS_NAME "sensor_class"
#define BUFFER_SIZE 1024
#define TIMER_INTERVAL_MS 1000  // 1 segundo

// Estructura para datos del sensor
struct sensor_data {
    int signal_type;        // 0 = señal 1, 1 = señal 2
    int current_value;      // Valor actual del sensor
    unsigned long timestamp; // Timestamp de la lectura
};

// Variables globales
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
static int selected_signal = 0;  // Por defecto señal 1
static struct timer_list sensor_timer;

// Mutex para proteger acceso concurrente
static DEFINE_MUTEX(sensor_mutex);

// Simulación de GPIOs (en QEMU usaremos valores simulados)
#define GPIO_SIGNAL1 18
#define GPIO_SIGNAL2 19

// Prototipos de funciones
static int sensor_open(struct inode *inode, struct file *file);
static int sensor_release(struct inode *inode, struct file *file);
static ssize_t sensor_read(struct file *file, char __user *buffer, size_t len, loff_t *offset);
static ssize_t sensor_write(struct file *file, const char __user *buffer, size_t len, loff_t *offset);
static void sensor_timer_callback(struct timer_list *timer);

// Estructura de operaciones del archivo
static struct file_operations fops = {
    .open = sensor_open,
    .read = sensor_read,
    .write = sensor_write,
    .release = sensor_release,
};

// Función para leer señal simulada
static int read_sensor_value(int signal_type) {
    int base_value, noise;
    
    if (signal_type == 0) {
        // Señal 1: Simulamos temperatura (20-40°C)
        base_value = 20 + (jiffies % 20);
        get_random_bytes(&noise, sizeof(noise));
        return base_value + (noise % 5) - 2;  // ±2°C de ruido
    } else {
        // Señal 2: Simulamos humedad (30-80%)
        base_value = 30 + (jiffies % 50);
        get_random_bytes(&noise, sizeof(noise));
        return base_value + (noise % 10) - 5;  // ±5% de ruido
    }
}

// Callback del timer
static void sensor_timer_callback(struct timer_list *timer) {
    struct sensor_data data;
    
    mutex_lock(&sensor_mutex);
    
    // Leer el sensor seleccionado
    data.signal_type = selected_signal;
    data.current_value = read_sensor_value(selected_signal);
    data.timestamp = jiffies;
    
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
    
    printk(KERN_INFO "sensor_drv: Leída señal %d, valor: %d\n", 
           data.signal_type, data.current_value);
}

// Función open
static int sensor_open(struct inode *inode, struct file *file) {
    printk(KERN_INFO "sensor_drv: Device abierto\n");
    return 0;
}

// Función release
static int sensor_release(struct inode *inode, struct file *file) {
    printk(KERN_INFO "sensor_drv: Device cerrado\n");
    return 0;
}

// Función read - devuelve datos del sensor
static ssize_t sensor_read(struct file *file, char __user *buffer, size_t len, loff_t *offset) {
    struct sensor_data data;
    char output_buffer[256];
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
    
    // Formatear los datos para la aplicación de usuario
    output_len = snprintf(output_buffer, sizeof(output_buffer),
                         "%d,%d,%lu\n", 
                         data.signal_type, data.current_value, data.timestamp);
    
    if (len < output_len) {
        return -EINVAL;
    }
    
    if (copy_to_user(buffer, output_buffer, output_len)) {
        return -EFAULT;
    }
    
    return output_len;
}

// Función write - configura qué señal leer
static ssize_t sensor_write(struct file *file, const char __user *buffer, size_t len, loff_t *offset) {
    char input_buffer[10];
    int new_signal;
    
    if (len >= sizeof(input_buffer)) {
        return -EINVAL;
    }
    
    if (copy_from_user(input_buffer, buffer, len)) {
        return -EFAULT;
    }
    
    input_buffer[len] = '\0';
    
    if (kstrtoint(input_buffer, 10, &new_signal) != 0) {
        return -EINVAL;
    }
    
    if (new_signal != 0 && new_signal != 1) {
        printk(KERN_WARNING "sensor_drv: Señal inválida %d. Use 0 o 1\n", new_signal);
        return -EINVAL;
    }
    
    mutex_lock(&sensor_mutex);
    if (selected_signal != new_signal) {
        selected_signal = new_signal;
        // Limpiar buffer al cambiar de señal
        buffer_head = buffer_tail = buffer_count = 0;
        printk(KERN_INFO "sensor_drv: Cambiado a señal %d, buffer limpiado\n", selected_signal);
    }
    mutex_unlock(&sensor_mutex);
    
    return len;
}

// Función de inicialización del módulo
static int __init sensor_init(void) {
    int result;
    
    printk(KERN_INFO "sensor_drv: Inicializando driver de sensores\n");
    
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
    
    // Inicializar timer
    timer_setup(&sensor_timer, sensor_timer_callback, 0);
    mod_timer(&sensor_timer, jiffies + msecs_to_jiffies(TIMER_INTERVAL_MS));
    
    printk(KERN_INFO "sensor_drv: Driver registrado exitosamente con major %d\n", major_number);
    return 0;
}

// Función de limpieza del módulo
static void __exit sensor_exit(void) {
    // Detener timer
    del_timer_sync(&sensor_timer);
    
    // Limpiar en orden inverso
    device_destroy(sensor_class, dev_num);
    class_destroy(sensor_class);
    cdev_del(&sensor_cdev);
    unregister_chrdev_region(dev_num, 1);
    
    printk(KERN_INFO "sensor_drv: Driver desinstalado\n");
}

module_init(sensor_init);
module_exit(sensor_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Grupo C--");
MODULE_DESCRIPTION("Character Device Driver para sensores duales");
MODULE_VERSION("1.0");