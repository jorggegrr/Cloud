import click
from rich.console import Console
from rich.table import Table
import mariadb
import hashlib
import os
import json
import uuid


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
    # Cargar los datos de las imágenes ya subidas
    uploaded_images = load_image_data()

    # Listar los archivos en el directorio de imágenes
    files = os.listdir(IMAGE_DIR)

    # Filtrar la lista para excluir las imágenes ya subidas
    available_files = [f for f in files if f not in uploaded_images.values()]

    # Mostrar las imágenes disponibles
    console.print("Imágenes disponibles para subir:")
    for i, filename in enumerate(available_files, start=1):
        console.print(f"{i}. {filename}")

    # Pedir al usuario que seleccione una imagen para subir
    file_index = int(console.input("Seleccione el número de la imagen a subir: ")) - 1
    filename = available_files[file_index]

    # Generar un ID único para la imagen
    id = str(uuid.uuid4())

    # Obtener el tamaño del archivo
    filepath = os.path.join(IMAGE_DIR, filename)
    size = os.path.getsize(filepath)

    # Guardar los datos de la imagen
    uploaded_images[id] = {'filename': filename, 'size': size}
    save_image_data(uploaded_images)

    console.print(f"[bold green]Imagen {filename} subida con éxito con el ID {id}.[/]")






console = Console()

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
    # Establecer la conexión con la base de datos
    cnx = mariadb.connect(user='root', password='Cisco12345',
                                  host='127.0.0.1',
                                  database='mydb')
    cursor = cnx.cursor()

    while True:
        username = console.input("Usuario: ")
        password = console.input("Contraseña: ", password=True)

        # Generar el hash SHA-256 de la contraseña
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # Ejecutar la consulta SQL
        query = ("SELECT username, password, rol FROM usuario WHERE username = %s AND password = %s")
        cursor.execute(query, (username, password_hash))

        # Verificar si el usuario existe
        user = cursor.fetchone()
        if user is not None:
            console.print("[bold green]Inicio de sesión exitoso.[/]")
            return user[2]
        else:
            console.print("[bold red]Usuario o contraseña incorrectos, por favor intente de nuevo.[/]")

    # Cerrar la conexión con la base de datos
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
    # Establecer la conexión con la base de datos
    cnx = mariadb.connect(user='root', password='Cisco12345',
                                  host='127.0.0.1',
                                  database='mydb')
    cursor = cnx.cursor()

    username = console.input("Nombre de usuario: ")
    password = console.input("Contraseña: ", password=True)
    rol_option = console.input("Rol (1 para 'admin', 2 para 'usuario'): ")

    # Convertir la opción de rol en el string correspondiente
    rol = 'admin' if rol_option == '1' else 'usuario'

    # Generar el hash SHA-256 de la contraseña
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    # Generar un token único para el usuario
    token = '4b9efd8df8de6f1f0ce461ef5ff19b5f3294776beffb8f1b16ef9f9df6a2b6f2'

    # Ejecutar la consulta SQL
    query = ("INSERT INTO usuario (username, password, rol, token) VALUES (%s, %s, %s, %s)")
    cursor.execute(query, (username, password_hash, rol, token))

    # Confirmar la transacción
    cnx.commit()

    console.print(f"[bold green]Usuario {username} creado con éxito.[/]")

    # Cerrar la conexión con la base de datos
    cursor.close()
    cnx.close()

def list_users():
    # Establecer la conexión con la base de datos
    cnx = mariadb.connect(user='root', password='Cisco12345',
                                  host='127.0.0.1',
                                  database='mydb')
    cursor = cnx.cursor()

    # Ejecutar la consulta SQL
    query = ("SELECT username, rol FROM usuario")
    cursor.execute(query)

    # Recuperar todos los usuarios
    users = cursor.fetchall()

    # Imprimir los usuarios
    for user in users:
        console.print(f"Nombre de usuario: {user[0]}, Rol: {user[1]}")

    # Cerrar la conexión con la base de datos
    cursor.close()
    cnx.close()




def slice_management():
    console.print("[bold green]Acción seleccionada: Gestión de Slices[/]")

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
    """Inicia la aplicación automáticamente al ejecutar el script."""
    role = login()
    while True:
        choice = main_menu(role)
        if choice == '2':
            console.print("[bold green]Saliendo del sistema...[/]")
            break
        handle_choice(choice)

if __name__ == '__main__':
    main()