import click
from rich.console import Console
from rich.table import Table
import mariadb
import hashlib
import os
import json
import uuid


IMAGE_DIR = '/imagenes/'
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


def slice_management():
    console.print("[bold green]Acción seleccionada: Gestión de Slices[/]")

def user_management():
    console.print("[bold green]Acción seleccionada: Gestión de Usuarios[/]")

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
