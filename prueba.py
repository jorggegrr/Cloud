import click
import networkx as nx
import matplotlib.pyplot as plt
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

def tree_topology():
    console.print("[bold green]Creando una topología tipo árbol[/]")

    # Pedir al usuario que ingrese el número de ramas y niveles
    num_branches = int(console.input("Ingrese el número de ramas: "))
    num_levels = int(console.input("Ingrese el número de niveles: "))

    # Validación de los parámetros
    if num_branches < 1 or num_levels < 1 or (num_branches == 2 and num_levels == 2):
        console.print("[bold red]Parámetros inválidos, intente de nuevo.[/]")
        return

    # Crear el árbol usando networkx
    G = nx.balanced_tree(r=num_branches, h=num_levels)

    # Dibujar el árbol
    pos = nx.spring_layout(G)  # Posicionamiento de los nodos
    nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=500, font_size=8)
    plt.show()

    console.print(f"[bold green]Topología tipo árbol creada con {num_branches} ramas y {num_levels} niveles.[/]")

def topology_management():
    while True:
        options = {
            '1': "Crear topología predefinida - Árbol",
            '2': "Regresar al Menú Principal"
        }
        display_menu("Gestión de Topología", options)
        choice = prompt_for_choice(options)
        if choice == '1':
            tree_topology()
        elif choice == '2':
            break

@click.command()
def main():
    # Este es un ejemplo simplificado. Asume que el usuario es un administrador.
    role = 'admin'

    if role == 'admin':
        while True:
            options = {
                '1': "Gestión de Topología",
                '2': "Salir"
            }
            display_menu("Menú Principal", options)
            choice = prompt_for_choice(options)
            if choice == '1':
                topology_management()
            elif choice == '2':
                console.print("[bold green]Saliendo del sistema...[/]")
                break

if __name__ == '__main__':
    main()
