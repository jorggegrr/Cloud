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
<<<<<<< HEAD
from PIL import Image
import tempfile


=======
>>>>>>> d5c7a833d1abcc73d742ddedadec8fb5eb57cf68

IMAGE_DIR = '/home/ubuntu/imagenes'
IMAGE_DATA_FILE = os.path.join(IMAGE_DIR, 'image_data.json')

def load_image_data():
    if os.path.exists(IMAGE_DATA_FILE):
        with open(IMAGE_DATA_FILE, 'r') as f:
            return json.load(f)
    else:
        return {}

def save_image_data(data):
    with open(IMAGE_DATA_FILE, 'w') as f:
        json.dump(data, f)

def list_images():
    data = load_image_data()
    for id, info in data.items():
        console.print(f"Nombre: {info['filename']},ID: {id}, Tamaño: {info['size']}")

def upload_image():
    uploaded_images = load_image_data()
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
    save_image_data(uploaded_images)
    console.print(f"[bold green]Imagen {filename} subida con éxito con el ID {id}.[/]")

console = Console()
<<<<<<< HEAD

=======
>>>>>>> d5c7a833d1abcc73d742ddedadec8fb5eb57cf68

def select_image():
    list_images()
    image_id = console.input("Ingrese el ID de la imagen a utilizar: ")
    data = load_image_data()
    if image_id in data:
        return data[image_id]['filename']
    else:
        console.print("[bold red]ID de imagen inválido, por favor intente de nuevo.[/]")
        return select_image()

def select_flavor():
    flavors = {
        '1': {'name': 'm1.tiny', 'vcpus': 1, 'disk': 1, 'ram': 512},
        '2': {'name': 'm1.small', 'vcpus': 1, 'disk': 20, 'ram': 2048}
    }
    display_menu("Flavors disponibles", {key: f"{value['name']} (VCPUs: {value['vcpus']}, Disk: {value['disk']} GB, RAM: {value['ram']} MB)" for key, value in flavors.items()})
    flavor_choice = prompt_for_choice(flavors.keys())
    return flavors[flavor_choice]

def select_image():
    list_images()
    image_id = console.input("Ingrese el ID de la imagen a utilizar: ")
    data = load_image_data()
    if image_id in data:
        return data[image_id]['filename']
    else:
        console.print("[bold red]ID de imagen inválido, por favor intente de nuevo.[/]")
        return select_image()

def select_flavor():
    flavors = {
        '1': {'name': 'm1.tiny', 'vcpus': 1, 'disk': 1, 'ram': 512},
        '2': {'name': 'm1.small', 'vcpus': 1, 'disk': 20, 'ram': 2048}
    }
    display_menu("Flavors disponibles", {key: f"{value['name']} (VCPUs: {value['vcpus']}, Disk: {value['disk']} GB, RAM: {value['ram']} MB)" for key, value in flavors.items()})
    flavor_choice = prompt_for_choice(flavors.keys())
    return flavors[flavor_choice]





def display_menu(title, options):
    table = Table(title=title, show_header=False, title_justify="left")
    for key, value in options.items():
        table.add_row(f"[bold cyan]{key}[/]", value)
    console.print(table)

def prompt_for_choice(options):
    choice = None
    while choice not in options:
        choice = console.input("[bold magenta]Seleccione una opción: [/]").strip()
        if choice not in options:
            console.print("[bold red]Opción inválida, por favor intente de nuevo.[/]")
    return choice

def login():
    cnx = mariadb.connect(user='root', password='Cisco12345',
                                  host='127.0.0.1',
                                  database='mydb')
    cursor = cnx.cursor()
    while True:
        username = console.input("Usuario: ")
        password = console.input("Contraseña: ", password=True)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        query = ("SELECT username, password, rol FROM usuario WHERE username = %s AND password = %s")
        cursor.execute(query, (username, password_hash))
        user = cursor.fetchone()
        if user is not None:
            console.print("[bold green]Inicio de sesión exitoso.[/]")
            return user[2]
        else:
            console.print("[bold red]Usuario o contraseña incorrectos, por favor intente de nuevo.[/]")
    cursor.close()
    cnx.close()

def main_menu(role):
    options = {
        '1': "Gestión de Slices",
        '2': "Salir"
    }
    if role == 'admin':
        options['3'] = "Gestión de Usuarios"
        options['4'] = "Administrar imágenes"
    display_menu("Menú Principal", options)
    return prompt_for_choice(options)

def handle_choice(choice):
    menu_functions = {
        '1': slice_management,
        '2': lambda: None,  # Para salir
        '3': user_management if choice == '3' else lambda: console.print("[red]Opción no válida.[/]"),
        '4': image_management if choice == '4' else lambda: console.print("[red]Opción no válida.[/]")
    }
    func = menu_functions.get(choice, lambda: console.print("[red]Opción no válida.[/]"))
    return func()

def image_management():
    while True:
        options = {
            '1': "Listar imágenes",
            '2': "Subir imagen",
            '3': "Regresar al Menú Principal"
        }
        display_menu("Administrar imágenes", options)
        choice = prompt_for_choice(options)
        if choice == '1':
            list_images()
        elif choice == '2':
            upload_image()
        elif choice == '3':
            break

def create_user():
    cnx = mariadb.connect(user='root', password='Cisco12345',
                                  host='127.0.0.1',
                                  database='mydb')
    cursor = cnx.cursor()
    username = console.input("Nombre de usuario: ")
    password = console.input("Contraseña: ", password=True)
    rol_option = console.input("Rol (1 para 'admin', 2 para 'usuario'): ")
    rol = 'admin' if rol_option == '1' else 'usuario'
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    token = '4b9efd8df8de6f1f0ce461ef5ff19b5f3294776beffb8f1b16ef9f9df6a2b6f2'
    query = ("INSERT INTO usuario (username, password, rol, token) VALUES (%s, %s, %s, %s)")
    cursor.execute(query, (username, password_hash, rol, token))
    cnx.commit()
    console.print(f"[bold green]Usuario {username} creado con éxito.[/]")
    cursor.close()
    cnx.close()

def list_users():
    cnx = mariadb.connect(user='root', password='Cisco12345',
                                  host='127.0.0.1',
                                  database='mydb')
    cursor = cnx.cursor()
    query = ("SELECT username, rol FROM usuario")
    cursor.execute(query)
    users = cursor.fetchall()
    for user in users:
        console.print(f"Nombre de usuario: {user[0]}, Rol: {user[1]}")
    cursor.close()
    cnx.close()

<<<<<<< HEAD

def tree_topology():
    console.print("[bold green]Creando una topología tipo árbol[/]")

    num_branches = int(console.input("Ingrese el número de ramas: "))
    num_levels = int(console.input("Ingrese el número de niveles: "))

    if num_branches < 1 or num_levels < 1 or (num_branches == 2 and num_levels == 2):
        console.print("[bold red]Parámetros inválidos, intente de nuevo.[/]")
        return

    G = nx.balanced_tree(r=num_branches, h=num_levels)

    pos = nx.spring_layout(G)  # Posicionamiento de los nodos
    nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=500, font_size=8)

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp:
        plt.savefig(temp.name)
        temp_image_name = temp.name

    img = Image.open(temp_image_name)
    img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)  # Cambia ANTIALIAS por LANCZOS
    img.save(temp_image_name)

    os.system(f'viu {temp_image_name}')

    os.remove(temp_image_name)

    console.print(f"[bold green]Topología tipo árbol creada con {num_branches} ramas y {num_levels} niveles.[/]")



=======
def tree_topology():
    console.print("[bold green]Creando una topología tipo árbol[/]")
    num_branches = int(console.input("Ingrese el número de ramas: "))
    num_levels = int(console.input("Ingrese el número de niveles: "))
    if num_branches < 1 or num_levels < 1 or (num_branches == 2 and num_levels == 2):
        console.print("[bold red]Parámetros inválidos, intente de nuevo.[/]")
        return
    G = nx.balanced_tree(r=num_branches, h=num_levels)
    ascii_graph = asciinet.graph_to_ascii(G)
    console.print(ascii_graph)
    console.print(f"[bold green]Topología tipo árbol creada con {num_branches} ramas y {num_levels} niveles.[/]")

    
>>>>>>> d5c7a833d1abcc73d742ddedadec8fb5eb57cf68
def slice_management():
    while True:
        options = {
            '1': "Crear Slice",
            '2': "Regresar al Menú Principal"
        }
        display_menu("Gestión de Slices", options)
        choice = prompt_for_choice(options)
        if choice == '1':
            slice_name = console.input("Nombre del Slice: ")
            architecture_options = {
                '1': "Linux",
                '2': "Openstack"
            }
            display_menu("Selección de arquitectura", architecture_options)
            architecture_choice = prompt_for_choice(architecture_options)
            image_name = select_image()
            flavor = select_flavor()
            template_options = {
                '1': "Plantilla (Árbol)"
            }
            display_menu("Plantilla", template_options)
            template_choice = prompt_for_choice(template_options)
            if template_choice == '1':
                console.print(f"[bold green]Imagen seleccionada: {image_name}[/]")
                console.print(f"[bold green]Flavor seleccionado: {flavor['name']} (VCPUs: {flavor['vcpus']}, Disk: {flavor['disk']} GB, RAM: {flavor['ram']} MB)[/]")
                tree_topology()
        elif choice == '2':
            break

def user_management():
    while True:
        options = {
            '1': "Listar Usuarios",
            '2': "Crear Usuario",
            '3': "Regresar al Menú Principal"
        }
        display_menu("Gestión de Usuarios", options)
        choice = prompt_for_choice(options)
        if choice == '1':
            list_users()
        elif choice == '2':
            create_user()
        elif choice == '3':
            break

@click.command()
def main():
    role = login()
    while True:
        choice = main_menu(role)
        if choice == '2':
            console.print("[bold green]Saliendo del sistema...[/]")
            break
        handle_choice(choice)

if __name__ == '__main__':
    main()
