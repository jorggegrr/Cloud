import mariadb
import json
import time
from collections import deque
from statistics import mean

# Clase para representar un worker
class Worker:
    def __init__(self, id, ram_free, memory_free, disk_free):
        self.id = id
        self.ram_free = ram_free
        self.memory_free = memory_free
        self.disk_free = disk_free

    def can_host_slice(self, slice_rams, slice_memory, slice_disks):
        return (self.ram_free >= slice_rams and
                self.memory_free >= slice_memory and
                self.disk_free >= slice_disks)

    def deploy_slice(self, slice_rams, slice_memory, slice_disks):
        self.ram_free -= slice_rams
        self.memory_free -= slice_memory
        self.disk_free -= slice_disks

# Función para obtener los recursos actuales de la base de datos
def get_current_resources():
    cnx = mariadb.connect(user='root', password='root', host='10.0.0.1', database='mydb')
    cursor = cnx.cursor()

    cursor.execute("SELECT * FROM recursos")
    rows = cursor.fetchall()

    workers = []
    for row in rows:
        data = json.loads(row[2])
        workers.append(Worker(row[0], data['total_memory_gb'], data['free_memory_gb'], data['cpu_usage_per_vcpu']))

    cursor.close()
    cnx.close()
    return workers

# Función para calcular los pesos de los recursos basado en el historial
def calculate_weights():
    cnx = mariadb.connect(user='root', password='root', host='10.0.0.1', database='mydb')
    cursor = cnx.cursor()

    cursor.execute("SELECT * FROM historico LIMIT 1000")
    rows = cursor.fetchall()

    ram_values = []
    memory_values = []
    disk_values = []

    for row in rows:
        data = json.loads(row[1])
        for worker_data in data:
            ram_values.append(worker_data['freecpu'])
            memory_values.append(worker_data['freememory'])
            disk_values.append(worker_data['freedisk'])

    ram_weight = mean(ram_values) / 3
    memory_weight = mean(memory_values) / 3
    disk_weight = mean(disk_values) / 3

    cursor.close()
    cnx.close()
    return ram_weight, memory_weight, disk_weight

# Función para tomar la decisión de despliegue
def deploy_slice(workers, slice_rams, slice_memory, slice_disks):
    ram_weight, memory_weight, disk_weight = calculate_weights()

    def calculate_prio(worker):
        return (worker.ram_free * ram_weight) + (worker.memory_free * memory_weight) + (worker.disk_free * disk_weight)

    workers.sort(key=calculate_prio, reverse=True)

    for worker in workers:
        if worker.can_host_slice(slice_rams, slice_memory, slice_disks):
            worker.deploy_slice(slice_rams, slice_memory, slice_disks)
            return worker.id

    return None

# Datos iniciales de los workers
workers = get_current_resources()

# Parámetros del slice que se desea desplegar
slice_rams = 3  # GB de RAM requerida
slice_memory = 6  # GB de memoria requerida
slice_disks = 3  # Discos requeridos

# Intentar desplegar el slice
deployed_worker_id = deploy_slice(workers, slice_rams, slice_memory, slice_disks)

if deployed_worker_id is not None:
    print(f"Slice desplegado en el Worker {deployed_worker_id}")
else:
    print("No se pudo desplegar el Slice en ningún Worker")
