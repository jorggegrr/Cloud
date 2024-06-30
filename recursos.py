import paramiko
import mariadb
import json
import time


def log_to_database(cursor, module_name, username, role, message):
    """Función para registrar eventos en la tabla de logs."""
    try:
        query = "INSERT INTO logs_monitoreo_recursos (nombre_modulo, username, role, message) VALUES (%s, %s, %s, %s);"
        cursor.execute(query, (module_name, username, role, message))
        cursor.connection.commit()  # Forzar un commit después de insertar el log
        print("Log command executed successfully.")  # Imprimir confirmación de que el comando se ejecutó
    except Exception as e:
        print(f"Error logging to database: {e}")  # Capturar y mostrar cualquier error durante el logueo

def get_resource_data(hostname, username, password):
    """Obtiene datos de uso de vCPU, RAM y disco a través de SSH."""
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=password)
    
    # Total vCPUs
    _, stdout, _ = ssh.exec_command("nproc")
    total_vcpus = int(stdout.read().decode().strip())
    
    # Memoria total y usada (GB)
    _, stdout, _ = ssh.exec_command("free -m | grep Mem | awk '{print $2}'")  # Memoria total (MB)
    total_memory_mb = int(stdout.read().decode().strip())
    total_memory_gb = round(total_memory_mb / 1024, 2)
    
    _, stdout, _ = ssh.exec_command("free -m | awk 'NR==2{print $3}'")  # Memoria usada (MB)
    used_memory_mb = int(stdout.read().decode().strip())
    used_memory_gb = round(used_memory_mb / 1024, 2)
    
    # Memoria libre (GB)
    free_memory_gb = round(total_memory_gb - used_memory_gb, 2)
    
    # Disco total y usado
    _, stdout, _ = ssh.exec_command("df -h | awk '$NF==\"/\"{print $2}'")  # Disco total
    total_disk = stdout.read().decode().strip()
    
    _, stdout, _ = ssh.exec_command("df -h | awk '$NF==\"/\"{print $3}'")  # Disco usado
    used_disk = stdout.read().decode().strip()
    
    # Disco libre
    total_disk_gb = float(total_disk[:-1])  # Suponiendo que el formato es algo como "50G"
    used_disk_gb = float(used_disk[:-1])  # Suponiendo que el formato es algo como "20G"
    free_disk_gb = round(total_disk_gb - used_disk_gb, 2)
    
    # Calcular el uso por vCPU usando mpstat
    cpu_usage_per_vcpu = []
    _, stdout, _ = ssh.exec_command("mpstat -P ALL 1 1 | awk '$3 ~ /[0-9]/ && $3 != \"CPU\" {print $3}'")
    cpu_lines = stdout.readlines()
    
    # Filtrar solo las primeras `total_vcpus` líneas válidas
    for line in cpu_lines:
        if len(cpu_usage_per_vcpu) < total_vcpus:
            try:
                cpu_usage = float(line.strip())
                cpu_usage_per_vcpu.append(cpu_usage)
            except ValueError:
                pass  # Ignorar líneas que no se pueden convertir a float
    
    # Calcular el uso total de CPU y el total teórico de CPU
    total_cpu_usage = round(sum(cpu_usage_per_vcpu), 2)
    total_cpu_capacity = 100 * total_vcpus
    free_cpu = total_cpu_capacity - total_cpu_usage
    
    ssh.close()
    
    return hostname, total_memory_gb, free_memory_gb, total_disk, free_disk_gb, [total_cpu_usage, total_cpu_capacity], free_cpu

def update_database(data):
    try:
        cnx = mariadb.connect(
            user='root',
            password='root',
            host='10.0.0.1',
            database='mydb'
        )
        cursor = cnx.cursor()

        json_data = json.dumps(data)

        # Consulta "upsert" para actualizar o insertar
        query = "INSERT INTO recursos (hostname, datos) VALUES (%s, %s) ON DUPLICATE KEY UPDATE datos = VALUES(datos);"
        cursor.execute(query, (data['hostname'], json_data))
        
        # print(f"Datos de {hostname} actualizados o insertados en la base de datos.")

        cnx.commit()
        log_to_database(cursor, 'recursos', 'admin', 'system', f"Datos actualizados o insertados para {data['hostname']}")
   
    except mariadb.Error as e:
        print(f"Error al actualizar la base de datos: {e}")
        if cursor:  # Verificar si el cursor aún está disponible para usar
            log_to_database(cursor, 'recursos', 'admin', 'system', f"Error al actualizar datos históricos: {e}")

    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()

def update_historico(consolidated_data):
    try:
        cnx = mariadb.connect(
            user='root',
            password='root',
            host='10.0.0.1',
            database='mydb'
        )
        cursor = cnx.cursor()

        json_data = json.dumps(consolidated_data)

        query = "INSERT INTO historico (data) VALUES (%s)"
        cursor.execute(query, (json_data,))
        cnx.commit()
        log_to_database(cursor, 'recursos', 'admin', 'system', "Datos históricos actualizados.")
  
    except mariadb.Error as e:
        print(f"Error al actualizar la base de datos: {e}")
        if cursor:  # Verificar si el cursor aún está disponible para usar
            log_to_database(cursor, 'recursos', 'admin', 'system', f"Error al actualizar datos históricos: {e}")

    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()

# Configuración de las máquinas a monitorear
workers = {
    "10.0.0.30": "Worker1",
    "10.0.0.40": "Worker2",
    "10.0.0.50": "Worker3",
}

# Credenciales SSH (asumiendo las mismas para todas las máquinas)
username = "ubuntu"
password = "ubuntu"

def main_loop():
    # Configuración inicial y bucle principal
    while True:
        consolidated_data = []
        # Lógica para obtener y actualizar datos
        for worker_ip, worker_name in workers.items():
            hostname, total_memory_gb, free_memory_gb, total_disk, free_disk_gb, cpu_usage, free_cpu = get_resource_data(worker_ip, username, password)
            data = {
                'hostname': worker_name,
                'total_memory_gb': f"{total_memory_gb} GB",
                'free_memory_gb': f"{free_memory_gb} GB",
                'total_disk': total_disk,
                'free_disk': f"{free_disk_gb} GB",
                'cpu_usage_per_vcpu': cpu_usage,
            }
            update_database(data)
            consolidated_data.append({
                'hostname': worker_name,
                'freecpu': free_cpu,
                'freememory': free_memory_gb,
                'freedisk': free_disk_gb,
            })
        
        # Actualizar la tabla historico con los datos consolidados
        update_historico(consolidated_data)
        
        # Esperar 3 segundos antes de volver a ejecutar
        time.sleep(3)

if __name__ == "__main__":
    main_loop()
