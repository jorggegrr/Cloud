import click
import networkx as nx
import matplotlib.pyplot as plt
from rich.console import Console
from rich.table import Table
import mariadb
import hashlib
import os
import json
import uuid
import asciinet
from PIL import Image
import tempfile
import datetime
import logging
from datetime import datetime

# Incio logging- jlgr
def log_event(username, role, message):
    # Define la ruta base donde se guardarán los logs
    base_path = "/home/ubuntu/Cloud"
    # Asegúrate de que el directorio exista
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    
    # Define el nombre del archivo de log basado en la fecha actual
    log_filename = os.path.join(base_path, f"LOG_{datetime.now().strftime('%d%m%Y')}.txt")
    
    # Escribe el evento en el archivo de log
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_filename, 'a') as log_file:
        log_file.write(f"{current_time}, {username}, {role}, {message}\n")

IMAGE_DIR = '/home/ubuntu/imagenes'
IMAGE_DATA_FILE = os.path.join(IMAGE_DIR, 'image_data.json')
JSON_FILE = '/home/ubuntu/slice_info.json'

username=None

# Zonas de disponibilidad
availability_zones = {
    '1': {'name': 'worker1', 'vcpus': 4, 'ram': 16, 'disk': 100},
    '2': {'name': 'worker2', 'vcpus': 8, 'ram': 32, 'disk': 200},
    '3': {'name': 'worker3', 'vcpus': 16, 'ram': 64, 'disk': 400}
}

def select_availability_zone(username, role):
    try:
        display_menu("Zonas de disponibilidad", {key: f"{value['name']} (vCPUs: {value['vcpus']}, RAM: {value['ram']} GB, Disco: {value['disk']} GB)" for key, value in availability_zones.items()}, username, role)  # Pasa username y role aquí
        zone_choice = prompt_for_choice(availability_zones.keys(), username, role)
        log_event(username, role, "Seleccionó zona de disponibilidad")
        return availability_zones[zone_choice]
    except Exception as e:
        log_event(username, role, f"Error seleccionando zona de disponibilidad: {str(e)}")
        console.print("[bold red]Error al seleccionar zona de disponibilidad.[/]")
def load_image_data(username, role):
    try:
        if os.path.exists(IMAGE_DATA_FILE):
            with open(IMAGE_DATA_FILE, 'r') as f:
                return json.load(f)
        else:
            return {}
        log_event(username, role, "Cargó datos de imagen exitosamente")
    except Exception as e:
        log_event(username, role, f"Error cargando datos de imagen: {str(e)}")
        console.print("[bold red]Error al cargar datos de imagen.[/]")


def save_image_data(data, username, role):
    try:
        with open(IMAGE_DATA_FILE, 'w') as f:
            json.dump(data, f)
        log_event(username, role, "Datos de imagen guardados exitosamente")
    except Exception as e:
        log_event(username, role, f"Error al guardar datos de imagen: {str(e)}")
        console.print("[bold red]Error al guardar datos de imagen.[/]")

def list_images(username, role):
    try:
        data = load_image_data(username, role)
        for id, info in data.items():
            console.print(f"Nombre: {info['filename']}, ID: {id}, Tamaño: {info['size']}")
        log_event(username, role, "Listado de imágenes mostrado correctamente")
    except Exception as e:
        log_event(username, role, f"Error al listar imágenes: {str(e)}")
        console.print("[bold red]Error al listar imágenes.[/]")

def upload_image(username, role):
    try:
        uploaded_images = load_image_data(username, role)
        files = os.listdir(IMAGE_DIR)
        available_files = [f for f in files if f not in uploaded_images.values()]
        console.print("Imágenes disponibles para subir:")
        for i, filename in enumerate(available_files, start=1):
            console.print(f"{i}. {filename}")

        file_index = int(console.input("Seleccione el número de la imagen a subir: ")) - 1
        filename = available_files[file_index]
        id = str(uuid.uuid4())
        filepath = os.path.join(IMAGE_DIR, filename)
        size = os.path.getsize(filepath)
        uploaded_images[id] = {'filename': filename, 'size': size}
        save_image_data(uploaded_images, username, role)
        console.print(f"[bold green]Imagen {filename} subida con éxito con el ID {id}.[/]")
        log_event(username, role, f"Imagen {filename} subida exitosamente con ID {id}")
    except Exception as e:
        log_event(username, role, f"Error al subir imagen: {str(e)}")
        console.print(f"[bold red]Error al subir imagen: {str(e)}[/]")


console = Console()

def select_image(username, role):
    try:
        list_images(username, role)
        image_id = console.input("Ingrese el ID de la imagen a utilizar: ")
        data = load_image_data(username, role)
        if image_id in data:
            log_event(username, role, f"Imagen seleccionada correctamente: {data[image_id]['filename']}")
            return data[image_id]['filename']
        else:
            raise ValueError("ID de imagen inválido")
    except ValueError as e:
        console.print(f"[bold red]{str(e)}, por favor intente de nuevo.[/]")
        log_event(username, role, str(e))
        return select_image(username, role)

def select_flavor(username, role):
    try:
        flavors = {
            '1': {'name': 'm1.tiny', 'vcpus': 1, 'disk': 1, 'ram': 512},
            '2': {'name': 'm1.small', 'vcpus': 1, 'disk': 20, 'ram': 2048}
        }
        display_menu("Flavors disponibles", {key: f"{value['name']} (VCPUs: {value['vcpus']}, Disk: {value['disk']} GB, RAM: {value['ram']} MB)" for key, value in flavors.items()}, username, role)
        flavor_choice = prompt_for_choice(flavors.keys(), username, role)
        log_event(username, role, f"Flavor seleccionado: {flavors[flavor_choice]['name']}")
        return flavors[flavor_choice]
    except Exception as e:
        log_event(username, role, f"Error al seleccionar flavor: {str(e)}")
        console.print("[bold red]Error al seleccionar flavor.[/]")



def display_menu(title, options, username, role):
    try:
        table = Table(title=title, show_header=False, title_justify="left")
        for key, value in options.items():
            table.add_row(f"[bold cyan]{key}[/]", value)
        console.print(table)
        log_event(username, role, f"Menú mostrado: {title}")
    except Exception as e:
        log_event(username, role, f"Error al mostrar menú '{title}': {str(e)}")
        console.print(f"[bold red]Error al mostrar menú '{title}': {str(e)}[/]")

def prompt_for_choice(options, username, role):
    choice = None
    while choice not in options:
        try:
            choice = console.input("[bold magenta]Seleccione una opción: [/]").strip()
            if choice not in options:
                console.print("[bold red]Opción inválida, por favor intente de nuevo.[/]")
                log_event(username, role, "Intento fallido de selección de opción: Usuario ingresó opción inválida.")
        except Exception as e:
            log_event(username, role, f"Error al solicitar selección de opción: {str(e)}")
            console.print(f"[bold red]Error al solicitar selección de opción: {str(e)}[/]")
            break
    return choice

def login():
    try:
        cnx = mariadb.connect(user='root', password='Cisco12345',
                                      host='127.0.0.1',
                                      database='mydb')
        cursor = cnx.cursor()
        global username
        username = console.input("Usuario: ")
        password = console.input("Contraseña: ", password=True)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        query = ("SELECT username, password, rol FROM usuario WHERE username = %s AND password = %s")
        cursor.execute(query, (username, password_hash))
        user = cursor.fetchone()
        if user is not None:
            log_event(username, user[2], "Inicio de sesión exitoso")
            console.print("[bold green]Inicio de sesión exitoso.[/]")
            return user[0], user[2]
        else:
            raise ValueError("Usuario o contraseña incorrectos")
    except ValueError as e:
        console.print(f"[bold red]{str(e)}, por favor intente de nuevo.[/]")
        log_event(username, 'unknown', str(e))
        return login()
    finally:
        cursor.close()
        cnx.close()

def main_menu(role, username):
    try:
        options = {
            '1': "Gestión de Slices",
            '2': "Salir"
        }
        if role == 'admin':
            options['3'] = "Gestión de Usuarios"
            options['4'] = "Administrar imágenes"
        display_menu("Menú Principal", options, username, role)
        choice = prompt_for_choice(options, username, role)
        log_event(username, role, "Accedió al menú principal")
        return choice
    except Exception as e:
        log_event(username, role, f"Error en el menú principal: {str(e)}")
        console.print("[bold red]Error en el menú principal.[/]")

def handle_choice(choice, username, role):
    try:
        menu_functions = {
            '1': lambda: slice_management(username, role),
            '2': lambda: None,  # Para salir
            '3': lambda: user_management(username, role) if choice == '3' else lambda: console.print("[red]Opción no válida.[/]"),
            '4': lambda: image_management(username, role) if choice == '4' else lambda: console.print("[red]Opción no válida.[/]")
        }
        func = menu_functions.get(choice, lambda: console.print("[red]Opción no válida.[/]"))
        return func()  # Invocar la función seleccionada pasando los argumentos necesarios
    except Exception as e:
        log_event(username, role, f"Error al manejar la opción {choice}: {str(e)}")
        console.print(f"[bold red]Error al manejar la opción {choice}: {str(e)}[/]")

def image_management(username, role):
    try:
        while True:
            options = {
                '1': "Listar imágenes",
                '2': "Subir imagen",
                '3': "Regresar al Menú Principal"
            }
            display_menu("Administrar imágenes", options, username, role)
            choice = prompt_for_choice(options, username, role)
            if choice == '1':
                list_images(username, role)
            elif choice == '2':
                upload_image(username, role)
            elif choice == '3':
                break
        log_event(username, role, "Gestión de imágenes completada")
    except Exception as e:
        log_event(username, role, f"Error en la gestión de imágenes: {str(e)}")
        console.print(f"[bold red]Error en la gestión de imágenes: {str(e)}[/]")

def create_user(username, role):
    try:
        cnx = mariadb.connect(user='root', password='Cisco12345',
                                      host='127.0.0.1',
                                      database='mydb')
        cursor = cnx.cursor()
        new_username = console.input("Nombre de usuario: ")
        password = console.input("Contraseña: ", password=True)
        rol_option = console.input("Rol (1 para 'admin', 2 para 'usuario'): ")
        new_role = 'admin' if rol_option == '1' else 'usuario'
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        token = '4b9efd8df8de6f1f0ce461ef5ff19b5f3294776beffb8f1b16ef9f9df6a2b6f2'
        query = ("INSERT INTO usuario (username, password, rol, token) VALUES (%s, %s, %s, %s)")
        cursor.execute(query, (new_username, password_hash, new_role, token))
        cnx.commit()
        console.print(f"[bold green]Usuario {new_username} creado con éxito.[/]")
        log_event(username, role, f"Nuevo usuario creado: {new_username}")
    except Exception as e:
        log_event(username, role, f"Error al crear usuario: {str(e)}")
        console.print(f"[bold red]Error al crear usuario: {str(e)}[/]")
    finally:
        cursor.close()
        cnx.close()

def list_users(username, role):
    try:
        cnx = mariadb.connect(user='root', password='Cisco12345',
                                      host='127.0.0.1',
                                      database='mydb')
        cursor = cnx.cursor()
        query = ("SELECT username, rol FROM usuario")
        cursor.execute(query)
        users = cursor.fetchall()
        for user in users:
            console.print(f"Nombre de usuario: {user[0]}, Rol: {user[1]}")
        log_event(username, role, "Listado de usuarios mostrado correctamente")
    except Exception as e:
        log_event(username, role, f"Error al listar usuarios: {str(e)}")
        console.print(f"[bold red]Error al listar usuarios: {str(e)}[/]")
    finally:
        cursor.close()
        cnx.close()


def tree_topology(username, role):
    log_event(username, role, "Inicio creación de topología tipo árbol.")
    try:
        console.print("[bold green]Creando una topología tipo árbol[/]")
        num_branches = int(console.input("Ingrese el número de ramas: "))
        num_levels = int(console.input("Ingrese el número de niveles: "))

        if num_branches < 1 or num_levels < 1 or (num_branches == 2 and num_levels == 2):
            raise ValueError("Parámetros inválidos para la topología de árbol.")
        
        G = nx.balanced_tree(r=num_branches, h=num_levels)
        nodes = [{'name': f'node{i}', 'id': i} for i in range(nx.number_of_nodes(G))]
        internet_access = console.input("¿El slice tiene salida a internet? (s/n): ").lower() == 's'
        network_links = [{'source': edge[0], 'target': edge[1]} for edge in G.edges()]
        display_topology(G, username, role)  

        log_event(username, role, f"Topología de árbol creada con éxito con {num_branches} ramas y {num_levels} niveles.")
        console.print(f"[bold green]Topología tipo árbol creada con {num_branches} ramas y {num_levels} niveles.[/]")
        return nodes, internet_access, network_links, num_branches, num_levels
    except ValueError as e:
        console.print(f"[bold red]{str(e)}[/]")
        log_event(username, role, str(e))
    except Exception as e:
        log_event(username, role, f"Error inesperado al crear topología de árbol: {str(e)}")
        console.print(f"[bold red]Error inesperado: {str(e)}[/]")

def create_linear_topology(username, role):
    log_event(username, role, "Inicio creación de topología lineal.")
    try:
        console.print("[bold green]Creando una topología lineal[/]")
        num_vms = int(console.input("Ingrese el número inicial de VMs: "))
        if num_vms < 2:
            raise ValueError("Debe haber al menos dos VMs para formar una topología lineal.")

        G = nx.path_graph(num_vms)
        internet_access = console.input("¿El slice tiene salida a internet? (s/n): ").lower() == 's'
        display_topology(G, username, role)  

        while True:
            add_more = console.input("¿Deseas añadir más VMs antes de finalizar? (s/n): ").lower()
            if add_more == 'n':
                break
            num_new_vms = int(console.input("Ingrese el número de nuevas VMs a añadir: "))
            last_vm_id = max(G.nodes)
            for i in range(1, num_new_vms + 1):
                new_vm_id = last_vm_id + i
                G.add_edge(last_vm_id, new_vm_id)
            display_topology(G, username, role)  

        log_event(username, role, f"Topología lineal completada con {len(G.nodes())} VMs.")
        console.print(f"[bold green]Topología lineal finalizada con {len(G.nodes())} VMs.[/]")
    except ValueError as e:
        console.print(f"[bold red]{str(e)}[/]")
        log_event(username, role, str(e))
    except Exception as e:
        log_event(username, role, f"Error inesperado al crear topología lineal: {str(e)}")
        console.print(f"[bold red]Error inesperado: {str(e)}[/]")

def create_bus_topology(username, role):
    log_event(username, role, "Inicio creación de topología tipo bus.")
    try:
        console.print("[bold green]Creando una topología tipo bus[/]")
        num_vms = int(console.input("Ingrese el número inicial de VMs: "))
        if num_vms < 2:
            raise ValueError("Debe haber al menos dos VMs para formar una topología tipo bus.")

        G = nx.path_graph(num_vms)
        internet_access = console.input("¿El slice tiene salida a internet? (s/n): ").lower() == 's'
        display_topology(G, username, role)  

        while True:
            add_more = console.input("¿Deseas añadir más VMs antes de finalizar? (s/n): ").lower()
            if add_more == 'n':
                break
            num_new_vms = int(console.input("Ingrese el número de nuevas VMs a añadir: "))
            last_vm_id = max(G.nodes)
            for i in range(1, num_new_vms + 1):
                new_vm_id = last_vm_id + i
                G.add_edge(last_vm_id, new_vm_id)
            display_topology(G, username, role)  

        log_event(username, role, f"Topología tipo bus completada con {len(G.nodes())} VMs.")
        console.print(f"[bold green]Topología tipo bus finalizada con {len(G.nodes())} VMs.[/]")
    except ValueError as e:
        console.print(f"[bold red]{str(e)}[/]")
        log_event(username, role, str(e))
    except Exception as e:
        log_event(username, role, f"Error inesperado al crear topología tipo bus: {str(e)}")
        console.print(f"[bold red]Error inesperado: {str(e)}[/]")

def create_mesh_topology(username, role):
    log_event(username, role, "Inicio creación de topología en malla.")
    try:
        num_vms = int(console.input("Ingrese el número inicial de VMs: "))
        if num_vms < 2:
            raise ValueError("Debe haber al menos dos VMs para formar una topología en malla.")

        G = nx.complete_graph(num_vms)
        internet_access = console.input("¿El slice tiene salida a internet? (s/n): ").lower() == 's'
        display_topology(G, username, role)  
        while True:
            add_more = console.input("¿Deseas añadir más VMs antes de finalizar? (s/n): ").lower()
            if add_more == 'n':
                break
            num_new_vms = int(console.input("Ingrese el número de nuevas VMs a añadir: "))
            last_vm_id = max(G.nodes)
            for i in range(1, num_new_vms + 1):
                new_vm_id = last_vm_id + i
                G.add_edge(last_vm_id, new_vm_id)
            display_topology(G, username, role)  

        log_event(username, role, f"Topología en malla completada con {len(G.nodes())} VMs.")
        console.print(f"[bold green]Topología en malla finalizada con {len(G.nodes())} VMs.[/]")
    except ValueError as e:
        console.print(f"[bold red]{str(e)}[/]")
        log_event(username, role, str(e))
    except Exception as e:
        log_event(username, role, f"Error inesperado al crear topología en malla: {str(e)}")
        console.print(f"[bold red]Error inesperado: {str(e)}[/]")



def display_topology(G, username, role, topology_type="General", bus_node=None):
    try:
        log_event(username, role, f"Displaying {topology_type} topology.")
        plt.figure(figsize=(12, 4), constrained_layout=True)  # Ajusta el tamaño de la figura

        if topology_type == "Bus":
            num_nodes = len(G.nodes()) - 1
            spacing = 12 / num_nodes
            pos = {node: (i * spacing, 0) for i, node in enumerate(G.nodes()) if node != bus_node}
            if bus_node is not None:
                pos[bus_node] = (num_nodes // 2 * spacing, -0.1)

            nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=800)
            labels = {node: f'node{node}' for node in G.nodes()}
            nx.draw_networkx_labels(G, pos, labels, font_size=12, font_color='black', verticalalignment='bottom')

            for node in G.nodes():
                if node != bus_node:
                    plt.plot([pos[node][0], pos[bus_node][0]], [pos[node][1], pos[bus_node][1]], 'k-', lw=2)
            plt.plot([min(pos.values())[0], max(pos.values())[0]], [pos[bus_node][1], pos[bus_node][1]], 'k-', lw=2)

        else:
            pos = nx.spring_layout(G)
            nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=1000, font_size=16)
            plt.title(f'Topología de {topology_type}')

        plt.grid(False)
        plt.axis('off')
        plt.tight_layout()

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp:
            plt.savefig(temp.name, dpi=300)
            temp_image_name = temp.name

        os.system(f'viu {temp_image_name}')
        os.remove(temp_image_name)

        log_event(username, role, f"{topology_type} topology displayed successfully.")
    except Exception as e:
        log_event(username, role, f"Failed to display {topology_type} topology: {str(e)}")
        console.print(f"[bold red]Failed to display topology due to an error: {str(e)}[/]")

def create_ring_topology(username, role):
    log_event(username, role, "Inicio creación de topología en anillo.")
    try:
        num_vms = int(console.input("Ingrese el número inicial de VMs: "))
        if num_vms < 3:
            raise ValueError("Debe haber al menos tres VMs para formar una topología en anillo.")

        G = nx.cycle_graph(num_vms)
        internet_access = console.input("¿El slice tiene salida a internet? (s/n): ").lower() == 's'
        display_topology(G, username, role, "Anillo")

        while True:
            add_more = console.input("¿Deseas añadir más VMs antes de finalizar? (s/n): ").lower()
            if add_more == 'n':
                break

            num_new_vms = int(console.input("Ingrese el número de nuevas VMs a añadir: "))
            # Ajustamos el ID más alto actual para asegurar que no haya solapamiento
            last_vm_id = max(G.nodes) + 1
            total_vms = len(G.nodes) + num_new_vms

            # Eliminar todas las conexiones antiguas y agregar todos los nodos de nuevo para reconstruir el anillo
            G = nx.cycle_graph(total_vms)
            nodes = [{'name': f'node{i}', 'id': i} for i in range(nx.number_of_nodes(G))]
            network_links = [{'source': edge[0], 'target': edge[1]} for edge in G.edges()]
            display_topology(G, username, role, "Anillo")

        log_event(username, role, f"Topología en anillo completada con {len(G.nodes())} VMs.")
        console.print(f"[bold green]Topología en anillo finalizada con {len(G.nodes())} VMs.[/]")
    except ValueError as e:
        console.print(f"[bold red]{str(e)}[/]")
        log_event(username, role, str(e))
    except Exception as e:
        log_event(username, role, f"Error inesperado al crear topología en anillo: {str(e)}")
        console.print(f"[bold red]Error inesperado: {str(e)}[/]")

def slice_management(username, role):
    while True:
        options = {
            '1': "Crear Slice",
            '2': "Listar Slices",
            '3': "Mostrar JSON de Slice",
            '4': "Mostrar Topología",
            '5': "Regresar al Menú Principal"
        }
        display_menu("Gestión de Slices", options, username, role)
        choice = prompt_for_choice(options, username, role)

        if choice == '1':
            log_event(username, role, "Intentando crear un nuevo slice.")
            slice_name = console.input("Nombre del Slice: ")

            cnx = mariadb.connect(user='root', password='Cisco12345', host='127.0.0.1', database='mydb')
            cursor = cnx.cursor()
            query = "SELECT JSON FROM SLICE WHERE username = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            
            # Verifica si ya existe un slice con el mismo nombre
            slices = []
            if result:
                slices = json.loads(result[0]) if result[0] else []

            if any(s.get('slice_name') == slice_name for s in slices):
                console.print("[bold red]Ya existe un slice con ese nombre, por favor intente de nuevo.[/]")
                continue

            architecture_options = {
                '1': "Linux",
                '2': "Openstack"
            }
            display_menu("Selección de arquitectura", architecture_options, username, role)
            architecture_choice = prompt_for_choice(architecture_options, username, role)

            image_name = select_image(username, role)
            flavor = select_flavor(username, role)

            template_options = {
                '1': "Plantilla (Árbol)",
                '2': "Plantilla (Lineal)",
                '3': "Plantilla (Bus)",
                '4': "Plantilla (Malla)",
                '5': "Plantilla (Anillo)"
            }
            display_menu("Plantilla", template_options, username, role)
            template_choice = prompt_for_choice(template_options, username, role)

            # Procesa según la plantilla elegida
            nodes, internet_access, network_links, topology_type = None, None, None, None
            if template_choice == '1':
                nodes, internet_access, network_links, num_branches, num_levels = tree_topology(username, role)
                topology_type = 'Árbol'
            elif template_choice == '2':
                nodes, internet_access, network_links = create_linear_topology(username, role)
                topology_type = 'Lineal'
            elif template_choice == '3':
                nodes, internet_access, network_links = create_bus_topology(username, role)
                topology_type = 'Bus'
            elif template_choice == '4':
                nodes, internet_access, network_links = create_mesh_topology(username, role)
                topology_type = 'Malla'
            elif template_choice == '5':
                nodes, internet_access, network_links = create_ring_topology(username, role)
                topology_type = 'Anillo'

            # Seleccionar zona de disponibilidad
            availability_zone = select_availability_zone(username, role)

            slice_info = {
                'timestamp': datetime.now().isoformat(),
                'architecture': architecture_options[architecture_choice],
                'slice_name': slice_name,
                'nodes': nodes,
                'topology_type': topology_type,
                'network_links': network_links,
                'internet_access': internet_access,
                'image': image_name,
                'flavor': flavor,
                'availability_zone': availability_zone
            }
            if topology_type == 'Árbol':
                slice_info['num_branches'] = num_branches
                slice_info['num_levels'] = num_levels

            slices.append(slice_info)
            query = "INSERT INTO SLICE (username, JSON) VALUES (%s, %s) ON DUPLICATE KEY UPDATE JSON = %s"
            cursor.execute(query, (username, json.dumps(slices), json.dumps(slices)))
            cnx.commit()

            log_event(username, role, f"Slice '{slice_name}' creado con éxito.")
            console.print(f"[bold green]Slice '{slice_name}' creado con éxito.[/]")

            cursor.close()
            cnx.close()

        elif choice == '2':
            cnx = mariadb.connect(user='root', password='Cisco12345', host='127.0.0.1', database='mydb')
            cursor = cnx.cursor()
            query = "SELECT JSON FROM SLICE WHERE username = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            
            slices = json.loads(result[0]) if result and result[0] else []
            table = Table(title="Slices del Usuario", show_header=True, header_style="bold magenta")
            table.add_column("Nombre", style="dim", width=12)
            table.add_column("Tipo", style="dim")
            table.add_column("Nodos", justify="right")
            table.add_column("Internet", justify="center")

            for s in slices:
                table.add_row(s['slice_name'], s['topology_type'], str(len(s['nodes'])), "Sí" if s['internet_access'] else "No")

            console.print(table)

            cursor.close()
            cnx.close()

        elif choice == '3':
            slice_name = console.input("Nombre del Slice: ")
            cnx = mariadb.connect(user='root', password='Cisco12345', host='127.0.0.1', database='mydb')
            cursor = cnx.cursor()
            query = "SELECT JSON FROM SLICE WHERE username = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            
            slices = json.loads(result[0]) if result and result[0] else []
            found = False
            for s in slices:
                if s['slice_name'] == slice_name:
                    console.print(json.dumps(s, indent=4))
                    found = True
                    break

            if not found:
                console.print("[bold red]Slice no encontrado.[/]")

            cursor.close()
            cnx.close()

        elif choice == '4':
            slice_name = console.input("Nombre del Slice: ")
            cnx = mariadb.connect(user='root', password='Cisco12345', host='127.0.0.1', database='mydb')
            cursor = cnx.cursor()
            query = "SELECT JSON FROM SLICE WHERE username = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            
            slices = json.loads(result[0]) if result and result[0] else []
            found = False
            for s in slices:
                if s['slice_name'] == slice_name:
                    if s['topology_type'] == 'Árbol':
                        G = nx.balanced_tree(r=s['num_branches'], h=s['num_levels'])
                    elif s['topology_type'] == 'Lineal':
                        G = nx.path_graph(len(s['nodes']))
                    elif s['topology_type'] == 'Bus':
                        G = nx.Graph()
                        G.add_nodes_from(range(len(s['nodes'])))
                        for i, link in enumerate(s['network_links']):
                            G.add_edge(link['source'], link['target'])
                    elif s['topology_type'] == 'Malla':
                        G = nx.complete_graph(len(s['nodes']))
                    elif s['topology_type'] == 'Anillo':
                        G = nx.cycle_graph(len(s['nodes']))
                    display_topology(G, s['topology_type'], username, role)
                    found = True
                    break

            if not found:
                console.print("[bold red]Slice no encontrado.[/]")

            cursor.close()
            cnx.close()

        elif choice == '5':
            break

    while True:
        options = {
            '1': "Crear Slice",
            '2': "Listar Slices",
            '3': "Mostrar JSON de Slice",
            '4': "Mostrar Topologia",
            '5': "Regresar al Menú Principal"
        }
        display_menu("Gestión de Slices", options, username, role)
        choice = prompt_for_choice(options, username, role)

        if choice == '1':
            log_event(username, role, "Intentando crear un nuevo slice.")
            slice_name = console.input("Nombre del Slice: ")
            try:
                cnx = mariadb.connect(user='root', password='Cisco12345', host='127.0.0.1', database='mydb')
                cursor = cnx.cursor()
                query = ("SELECT JSON FROM SLICE WHERE username = %s")
                cursor.execute(query, (username,))
                result = cursor.fetchone() 

                if result is not None:
                    slices = json.loads(result[0])
                    if any(data.get('slice_name') == slice_name for data in slices if data is not None):
                        console.print("[bold red]Ya existe un slice con ese nombre, por favor intente de nuevo.[/]")
                        raise ValueError("Nombre de slice duplicado")

                architecture_options = {
                    '1': "Linux",
                    '2': "Openstack"
                }
                display_menu("Selección de arquitectura", architecture_options, username, role)
                architecture_choice = prompt_for_choice(architecture_options, username, role)

                if architecture_choice not in architecture_options:
                    console.print("[bold red]Opción de arquitectura inválida. Intente de nuevo.[/]")
                    continue

                image_name = select_image(username, role)
                flavor = select_flavor(username, role)
                template_options = {
                    '1': "Plantilla (Árbol)",
                    '2': "Plantilla (Lineal)",
                    '3': "Plantilla (Bus)",
                    '4': "Plantilla (Malla)",
                    '5': "Plantilla (Anillo)"
                }
                display_menu("Plantilla", template_options, username, role)
                template_choice = prompt_for_choice(template_options, username, role)

                if template_choice == '1':
                    console.print(f"[bold green]Imagen seleccionada: {image_name}[/]")
                    console.print(f"[bold green]Flavor seleccionado: {flavor['name']} (VCPUs: {flavor['vcpus']}, Disk: {flavor['disk']} GB, RAM: {flavor['ram']} MB)[/]")
                    nodes, internet_access, network_links, num_branches, num_levels = tree_topology(username, role)
                    topology_type = 'Árbol'
                elif template_choice == '2':
                    console.print(f"[bold green]Imagen seleccionada: {image_name}[/]")
                    console.print(f"[bold green]Flavor seleccionado: {flavor['name']} (VCPUs: {flavor['vcpus']}, Disk: {flavor['disk']} GB, RAM: {flavor['ram']} MB)[/]")
                    nodes, internet_access, network_links = create_linear_topology(username, role)
                    topology_type = 'Lineal'
                elif template_choice == '3':
                    console.print(f"[bold green]Imagen seleccionada: {image_name}[/]")
                    console.print(f"[bold green]Flavor seleccionado: {flavor['name']} (VCPUs: {flavor['vcpus']}, Disk: {flavor['disk']} GB, RAM: {flavor['ram']} MB)[/]")
                    nodes, internet_access, network_links = create_bus_topology(username, role)
                    topology_type = 'Bus'
                elif template_choice == '4':
                    console.print(f"[bold green]Imagen seleccionada: {image_name}[/]")
                    console.print(f"[bold green]Flavor seleccionado: {flavor['name']} (VCPUs: {flavor['vcpus']}, Disk: {flavor['disk']} GB, RAM: {flavor['ram']} MB)[/]")
                    nodes, internet_access, network_links = create_mesh_topology(username, role)
                    topology_type = 'Malla'
                elif template_choice == '5':
                    console.print(f"[bold green]Imagen seleccionada: {image_name}[/]")
                    console.print(f"[bold green]Flavor seleccionado: {flavor['name']} (VCPUs: {flavor['vcpus']}, Disk: {flavor['disk']} GB, RAM: {flavor['ram']} MB)[/]")
                    nodes, internet_access, network_links = create_ring_topology(username, role)
                    topology_type = 'Anillo'

                availability_zone = select_availability_zone(username, role)
                console.print(f"[bold green]Zona de disponibilidad seleccionada: {availability_zone['name']} (vCPUs: {availability_zone['vcpus']}, RAM: {availability_zone['ram']} GB, Disco: {availability_zone['disk']} GB)[/]")

                slice_info = {
                    'timestamp': datetime.datetime.now().isoformat(),
                    'architecture': architecture_options[architecture_choice],
                    'slice_name': slice_name,
                    'nodes': nodes,
                    'topology_type': topology_type,
                    'network_links': network_links,
                    'internet_access': internet_access,
                    'image': image_name,
                    'flavor': flavor,
                    'availability_zone': availability_zone
                }
                if topology_type == 'Árbol':
                    slice_info['num_branches'] = num_branches
                    slice_info['num_levels'] = num_levels

                # Almacenar el JSON en la base de datos
                if result is None:
                    query = ("INSERT INTO SLICE (username, JSON) VALUES (%s, %s)")
                    cursor.execute(query, (username, json.dumps([slice_info])))  # Encapsular en una lista
                else:
                    slices = json.loads(result[0])
                    slices.append(slice_info)
                    query = ("UPDATE SLICE SET JSON = %s WHERE username = %s")
                    cursor.execute(query, (json.dumps(slices), username))

                cnx.commit()
                log_event(username, role, f"Slice '{slice_name}' creado con éxito.")
                console.print(f"[bold green]Slice '{slice_name}' creado con éxito.[/]")

            except ValueError as e:
                console.print(f"[bold red]Error: {e}[/]")
            except Exception as e:
                log_event(username, role, f"Error al crear slice: {str(e)}")
                console.print(f"[bold red]Error al crear slice: {str(e)}[/]")
            finally:
                cursor.close()
                cnx.close()
                
        elif choice == '2':
            log_event(username, role, "Listando slices.")
            try:
                cnx = mariadb.connect(user='root', password='Cisco12345', host='127.0.0.1', database='mydb')
                cursor = cnx.cursor()
                query = ("SELECT JSON FROM SLICE WHERE username = %s")
                cursor.execute(query, (username,))
                slices = cursor.fetchall()
                table = Table(title="Slices del Usuario", show_header=True, header_style="bold magenta")
                table.add_column("Nombre", style="dim", width=12)
                table.add_column("Tipo", style="dim")
                table.add_column("Nodos", justify="right")
                table.add_column("Internet", justify="center")
                for slice in slices:
                    slice_data = json.loads(slice[0])
                    for data in slice_data:
                        if data is not None:
                            table.add_row(
                                data['slice_name'],
                                data['topology_type'],
                                str(len(data['nodes'])),
                                "Sí" if data['internet_access'] else "No"
                            )
                console.print(table)
                log_event(username, role, "Slices listados correctamente.")
            except Exception as e:
                log_event(username, role, f"Error al listar slices: {str(e)}")
                console.print(f"[bold red]Error al listar slices: {str(e)}[/]")
            finally:
                cursor.close()
                cnx.close()

        elif choice == '3':
            log_event(username, role, "Mostrando JSON de un slice específico.")
            slice_name = console.input("Nombre del Slice: ")
            try:
                cnx = mariadb.connect(user='root', password='Cisco12345', host='127.0.0.1', database='mydb')
                cursor = cnx.cursor()
                query = ("SELECT JSON FROM SLICE WHERE username = %s")
                cursor.execute(query, (username,))
                slices = cursor.fetchall()
                found = False
                for slice in slices:
                    slice_data = json.loads(slice[0])
                    for data in slice_data:
                        if data is not None and data['slice_name'] == slice_name:
                            console.print(json.dumps(data, indent=4))
                            found = True
                if not found:
                    console.print("[bold red]Slice no encontrado.[/]")
                    log_event(username, role, f"Slice '{slice_name}' no encontrado.")
            except Exception as e:
                log_event(username, role, f"Error al mostrar JSON del slice: {str(e)}")
                console.print(f"[bold red]Error al mostrar JSON del slice: {str(e)}[/]")
            finally:
                cursor.close()
                cnx.close()

        elif choice == '4':
            log_event(username, role, "Mostrando la topología de un slice específico.")
            slice_name = console.input("Nombre del Slice: ")
            try:
                cnx = mariadb.connect(user='root', password='Cisco12345', host='127.0.0.1', database='mydb')
                cursor = cnx.cursor()
                query = ("SELECT JSON FROM SLICE WHERE username = %s")
                cursor.execute(query, (username,))
                slices = cursor.fetchall()
                found = False
                for slice in slices:
                    slice_data = json.loads(slice[0])
                    for data in slice_data:
                        if data is not None and data['slice_name'] == slice_name:
                            bus_node = None
                            if data['topology_type'] == 'Árbol':
                                G = nx.balanced_tree(r=data['num_branches'], h=data['num_levels'])
                            elif data['topology_type'] == 'Lineal':
                                G = nx.path_graph(len(data['nodes']))
                                for link in data['network_links']:
                                    G.add_edge(link['source'], link['target'])
                            elif data['topology_type'] == 'Bus':
                                G = nx.Graph()
                                G.add_nodes_from(range(len(data['nodes'])))
                                bus_node = len(data['nodes']) - 1  # Corrección: El nodo del bus es el último nodo agregado
                                for link in data['network_links']:
                                    G.add_edge(link['source'], link['target'])
                            elif data['topology_type'] == 'Malla':
                                G = nx.complete_graph(len(data['nodes']))
                                for link in data['network_links']:
                                    G.add_edge(link['source'], link['target'])
                            elif data['topology_type'] == 'Anillo':
                                G = nx.cycle_graph(len(data['nodes']))
                                for link in data['network_links']:
                                    G.add_edge(link['source'], link['target'])
                            else:
                                console.print("[bold red]Tipo de topología no reconocido.[/]")
                                continue
                            display_topology(G, username, role, data['topology_type'], bus_node=bus_node)
                            found = True
                if not found:
                    console.print("[bold red]Slice no encontrado.[/]")
                    log_event(username, role, f"Slice '{slice_name}' no encontrado.")
            except Exception as e:
                log_event(username, role, f"Error al mostrar topología del slice: {str(e)}")
                console.print(f"[bold red]Error al mostrar topología del slice: {str(e)}[/]")
            finally:
                cursor.close()
                cnx.close()

        elif choice == '5':
            log_event(username, role, "Regresando al menú principal.")
            break


def user_management(username, role):
    while True:
        options = {
            '1': "Listar Usuarios",
            '2': "Crear Usuario",
            '3': "Regresar al Menú Principal"
        }
        display_menu("Gestión de Usuarios", options)
        choice = prompt_for_choice(options)
        
        if choice == '1':
            log_event(username, role, "Listando usuarios.")
            try:
                list_users(username, role)
                log_event(username, role, "Usuarios listados exitosamente.")
            except Exception as e:
                log_event(username, role, f"Error al listar usuarios: {str(e)}")
                console.print(f"[bold red]Error al listar usuarios: {str(e)}[/]")
        elif choice == '2':
            log_event(username, role, "Creando un nuevo usuario.")
            try:
                create_user(username, role)
                log_event(username, role, "Usuario creado exitosamente.")
            except Exception as e:
                log_event(username, role, f"Error al crear usuario: {str(e)}")
                console.print(f"[bold red]Error al crear usuario: {str(e)}[/]")
        elif choice == '3':
            log_event(username, role, "Regresando al menú principal desde gestión de usuarios.")
            break
@click.command()
def main():
    global username
    console.print("[bold green]¡Bienvenido al Sistema de Gestión de Slices![/]")
    console.print("[bold green]Por favor, ingrese sus datos.[/]")

    try:
        username, role = login()
        log_event(username, role, "Inicio de sesión exitoso.")
    except Exception as e:
        log_event("unknown", "unknown", f"Error al iniciar sesión: {str(e)}")
        console.print(f"[bold red]Error al iniciar sesión: {str(e)}[/]")
        return

    while True:
        try:
            choice = main_menu(role, username)  # Pasa 'username' aquí
            if choice == '2':
                console.print("[bold green]Saliendo del sistema...[/]")
                log_event(username, role, "Saliendo del sistema.")
                break
            handle_choice(choice, username, role)  # Pasa 'username' y 'role' aquí
        except Exception as e:
            log_event(username, role, f"Error inesperado: {str(e)}")
            console.print(f"[bold red]Error inesperado: {str(e)}[/]")

if __name__ == '__main__':
    main()