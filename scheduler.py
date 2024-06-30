import mariadb
import json
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

# Función para obtener los recursos actuales de la tabla asignados
def get_current_resources():
    cnx = mariadb.connect(user='root', password='root', host='10.0.0.1', database='mydb')
    cursor = cnx.cursor()

    cursor.execute("SELECT worker_name, ram_free_gb, memory_free_gb, disk_free FROM asignados")
    rows = cursor.fetchall()

    workers = []
    for row in rows:
        workers.append(Worker(row[0], row[1], row[2], row[3]))

    cursor.close()
    cnx.close()
    return workers

# Función para obtener los recursos actuales de la tabla recursos
def get_real_time_resources():
    cnx = mariadb.connect(user='root', password='root', host='10.0.0.1', database='mydb')
    cursor = cnx.cursor()

    cursor.execute("SELECT hostname, datos FROM recursos")
    rows = cursor.fetchall()

    workers = []
    for row in rows:
        data = json.loads(row[1])
        free_memory_gb = float(data['free_memory_gb'].split()[0])  # Extraer el valor numérico de '1.26 GB'
        free_disk_gb = float(data['free_disk'].split()[0])  # Extraer el valor numérico de '5.8 GB'
        free_vcpus = sum([100 - usage for usage in data['cpu_usage_per_vcpu']])  # Calcular vCPUs libres
        workers.append(Worker(row[0], free_memory_gb, free_disk_gb, free_vcpus))

    cursor.close()
    cnx.close()
    return workers

# Función para calcular los pesos de los recursos basado en la tabla promedio
def calculate_weights():
    cnx = mariadb.connect(user='root', password='root', host='10.0.0.1', database='mydb')
    cursor = cnx.cursor()

    cursor.execute("SELECT ram_avg, disk_avg, cpu_avg FROM promedio")
    rows = cursor.fetchall()

    ram_values = [row[0] for row in rows]
    memory_values = [row[1] for row in rows]
    disk_values = [row[2] for row in rows]

    max_ram = 2  # GB de RAM
    max_memory = 10  # GB de memoria
    max_disk = 200  # Suma del espacio libre en los discos

    ram_weight = mean(ram_values) / max_ram
    memory_weight = mean(memory_values) / max_memory
    disk_weight = mean(disk_values) / max_disk

    cursor.close()
    cnx.close()
    return ram_weight, memory_weight, disk_weight

# Función para tomar la decisión de despliegue en el primer nivel
def deploy_slice_level1(workers, slice_rams, slice_memory, slice_disks):
    ram_weight, memory_weight, disk_weight = calculate_weights()

    def calculate_prio(worker):
        return (worker.ram_free * ram_weight) + (worker.memory_free * memory_weight) + (worker.disk_free * disk_weight)

    workers.sort(key=calculate_prio, reverse=True)

    for worker in workers:
        if worker.can_host_slice(slice_rams, slice_memory, slice_disks):
            worker.deploy_slice(slice_rams, slice_memory, slice_disks)
            update_worker_resources(worker)
            return worker.id

    return None

# Función para tomar la decisión de despliegue en el segundo nivel
def deploy_slice_level2(workers, slice_rams, slice_memory, slice_disks):
    ram_weight, memory_weight, disk_weight = calculate_weights()

    def calculate_prio(worker):
        return (worker.ram_free * ram_weight) + (worker.memory_free * memory_weight) + (worker.disk_free * disk_weight)

    workers.sort(key=calculate_prio, reverse=True)

    for worker in workers:
        if worker.can_host_slice(slice_rams, slice_memory, slice_disks):
            worker.deploy_slice(slice_rams, slice_memory, slice_disks)
            return worker.id

    return None

# Función para actualizar los recursos del worker en la tabla asignados
def update_worker_resources(worker):
    cnx = mariadb.connect(user='root', password='root', host='10.0.0.1', database='mydb')
    cursor = cnx.cursor()

    update_query = """
    UPDATE asignados
    SET ram_free_gb = ?, memory_free_gb = ?, disk_free = ?
    WHERE worker_name = ?
    """
    cursor.execute(update_query, (worker.ram_free, worker.memory_free, worker.disk_free, worker.id))

    cnx.commit()
    cursor.close()
    cnx.close()

# Parámetros del slice que se desea desplegar
slice_rams = int(input("Ingrese la cantidad de RAM requerida (GB): "))  # GB de RAM requerida
slice_memory = int(input("Ingrese la cantidad de memoria requerida (GB): "))  # GB de memoria requerida
slice_disks = int(input("Ingrese la cantidad de discos requeridos: "))  # Discos requeridos

# Datos iniciales de los workers
workers_level1 = get_current_resources()

# Intentar desplegar el slice en el primer nivel
deployed_worker_id = deploy_slice_level1(workers_level1, slice_rams, slice_memory, slice_disks)

if deployed_worker_id is not None:
    print(f"Slice desplegado en el Worker {deployed_worker_id} en el primer nivel")
else:
    # Intentar desplegar el slice en el segundo nivel
    workers_level2 = get_real_time_resources()
    deployed_worker_id = deploy_slice_level2(workers_level2, slice_rams, slice_memory, slice_disks)
    
    if deployed_worker_id is not None:
        print(f"Slice desplegado en el Worker {deployed_worker_id} en el segundo nivel")
    else:
        print("No se pudo desplegar el Slice en ningún Worker")
