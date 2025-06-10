obj-m := sensor_driver.o

# Directorio del kernel (ajustar según tu sistema)
KERNEL_DIR := /lib/modules/$(shell uname -r)/build

# Directorio actual
PWD := $(shell pwd)

# Regla por defecto
all:
	$(MAKE) -C $(KERNEL_DIR) M=$(PWD) modules

# Limpiar archivos generados
clean:
	$(MAKE) -C $(KERNEL_DIR) M=$(PWD) clean

# Instalar el módulo
install:
	sudo insmod sensor_driver.ko

# Desinstalar el módulo
uninstall:
	sudo rmmod sensor_driver

# Mostrar información del módulo
info:
	modinfo sensor_driver.ko

# Mostrar dispositivos registrados
devices:
	cat /proc/devices | grep sensor

# Mostrar mensajes del kernel
dmesg:
	dmesg | tail -20

.PHONY: all clean install uninstall info devices dmesg