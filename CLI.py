import click
from rich.console import Console
from rich.table import Table

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
    while True:
        console.input("Usuario: ")
        console.input("Contraseña: ", password=True)
        console.print("[bold green]Inicio de sesión exitoso.[/]")
        break

def main_menu():
    options = {
        '1': "Gestión de VMs",
        '2': "Monitorización de Recursos",
        '3': "Gestión de Seguridad",
        '4': "Configuración de Networking",
        '5': "Operaciones de Almacenamiento",
        '6': "Gestión de Usuarios",
        '7': "Registro y Auditoría",
        '8': "Salir"
    }
    display_menu("Menú Principal", options)
    return prompt_for_choice(options)

def handle_choice(choice):
    menu_functions = {
        '1': vm_management,
        '2': resource_monitoring,
        '3': security_management,
        '4': networking_configuration,
        '5': storage_operations,
        '6': user_management,
        '7': audit_logs,
        '8': lambda: None  # Para salir
    }
    func = menu_functions.get(choice, lambda: console.print("[red]Opción no válida.[/]"))
    return func()

def manage_submenu(options):
    while True:
        display_menu("Submenú", options)
        choice = prompt_for_choice(options)
        if choice.endswith('6') or choice.endswith('5'):
            break
        console.print(f"[bold green]Acción seleccionada: {options[choice]}[/]")

def vm_management():
    options = {
        '1.1': "Crear VM",
        '1.2': "Listar todas las VMs",
        '1.3': "Ver detalles de una VM",
        '1.4': "Modificar una VM",
        '1.5': "Eliminar una VM",
        '1.6': "Regresar al Menú Principal"
    }
    manage_submenu(options)

def resource_monitoring():
    options = {
        '2.1': "Ver uso actual de CPU",
        '2.2': "Ver uso actual de Memoria",
        '2.3': "Ver almacenamiento disponible",
        '2.4': "Ver estado de red",
        '2.5': "Regresar al Menú Principal"
    }
    manage_submenu(options)

def security_management():
    options = {
        '3.1': "Administrar reglas de firewall",
        '3.2': "Configurar VPN",
        '3.3': "Revisar políticas de seguridad",
        '3.4': "Auditar accesos y eventos de seguridad",
        '3.5': "Regresar al Menú Principal"
    }
    manage_submenu(options)

def networking_configuration():
    options = {
        '4.1': "Crear red virtual",
        '4.2': "Modificar configuración de red",
        '4.3': "Eliminar red virtual",
        '4.4': "Ver topología de red",
        '4.5': "Regresar al Menú Principal"
    }
    manage_submenu(options)

def storage_operations():
    options = {
        '5.1': "Aprovisionar almacenamiento",
        '5.2': "Expandir almacenamiento existente",
        '5.3': "Liberar espacio de almacenamiento",
        '5.4': "Ver informes de uso de almacenamiento",
        '5.5': "Regresar al Menú Principal"
    }
    manage_submenu(options)

def user_management():
    options = {
        '6.1': "Crear nuevo usuario",
        '6.2': "Listar usuarios",
        '6.3': "Modificar usuario",
        '6.4': "Eliminar usuario",
        '6.5': "Regresar al Menú Principal"
    }
    manage_submenu(options)

def audit_logs():
    options = {
        '7.1': "Ver logs del sistema",
        '7.2': "Exportar logs para auditoría",
        '7.3': "Configurar niveles de log",
        '7.4': "Regresar al Menú Principal"
    }
    manage_submenu(options)

@click.command()
def main():
    """Inicia la aplicación automáticamente al ejecutar el script."""
    login()
    while True:
        choice = main_menu()
        if choice == '8':
            console.print("[bold green]Saliendo del sistema...[/]")
            break
        handle_choice(choice)

if __name__ == '__main__':
    main()
