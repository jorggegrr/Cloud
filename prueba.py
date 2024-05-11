import click
import networkx as nx
import matplotlib.pyplot as plt
from rich.console import Console
from rich.table import Table
import tempfile
import os
from PIL import Image

console = Console()
#hola
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

def display_and_save_graph(G):
    pos = nx.spring_layout(G)  # Posicionamiento de los nodos
    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, with_labels=True, node_color='lightgreen', edge_color='gray', node_size=1000, font_size=12)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp:
        plt.savefig(temp.name, dpi=300)  # Aumentar DPI para una imagen más clara
        temp_image_name = temp.name

    img = Image.open(temp_image_name)
    img.show()  # Usar un visor de imágenes externo para mejor calidad
    os.remove(temp_image_name)  # Eliminar el archivo temporal

def create_linear_topology():
    console.print("[bold green]Creando una topología lineal[/]")

    num_vms = int(console.input("Ingrese el número inicial de VMs: "))
    if num_vms < 2:
        console.print("[bold red]Debe haber al menos dos VMs para formar una topología lineal.[/]")
        return

    G = nx.path_graph(num_vms)
    display_and_save_graph(G)

    while True:
        add_more = console.input("¿Deseas añadir más VMs antes de finalizar? (s/n): ").lower()
        if add_more == 'n':
            break

        num_new_vms = int(console.input("Ingrese el número de nuevas VMs a añadir: "))
        last_vm_id = max(G.nodes)
        for i in range(1, num_new_vms + 1):
            new_vm_id = last_vm_id + i
            target_vm_id = int(console.input(f"Seleccione hacia qué ID de VM existente desea enlazar la nueva VM {new_vm_id}: "))
            if target_vm_id in G.nodes:
                G.add_edge(new_vm_id, target_vm_id)
            else:
                console.print("[bold red]ID de VM inválido, por favor intente de nuevo.[/]")
                i -= 1  # decrement to retry this iteration
        display_and_save_graph(G)

    console.print(f"[bold green]Topología lineal finalizada con {len(G.nodes)} VMs.[/]")

def create_ring_topology():
    console.print("[bold green]Creando una topología en anillo[/]")

    num_vms = int(console.input("Ingrese el número inicial de VMs: "))
    if num_vms < 3:
        console.print("[bold red]Debe haber al menos tres VMs para formar una topología en anillo.[/]")
        return

    G = nx.cycle_graph(num_vms)
    display_and_save_graph(G)

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
        display_and_save_graph(G)

    console.print(f"[bold green]Topología en anillo finalizada con {len(G.nodes)} VMs.[/]")

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
    pos = nx.spring_layout(G)  # Posicionamiento de los nodos
    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=1000, font_size=12)

    # Guardar la imagen en un archivo temporal
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp:
        plt.savefig(temp.name, dpi=300)  # Aumentar DPI para una imagen más clara
        temp_image_name = temp.name

    # Abrir la imagen para mostrar
    img = Image.open(temp_image_name)
    img.show()  # Usar un visor de imágenes externo para mejor calidad

    # Eliminar el archivo temporal
    os.remove(temp_image_name)

    console.print(f"[bold green]Topología tipo árbol creada con {num_branches} ramas y {num_levels} niveles.[/]")

def create_mesh_topology():
    console.print("[bold green]Creando una topología en malla[/]")

    num_vms = int(console.input("Ingrese el número inicial de VMs: "))
    if num_vms < 2:
        console.print("[bold red]Debe haber al menos dos VMs para formar una topología en malla.[/]")
        return

    # Crear una topología en malla completa
    G = nx.complete_graph(num_vms)
    display_and_save_graph(G)

    while True:
        add_more = console.input("¿Deseas añadir más VMs antes de finalizar? (s/n): ").lower()
        if add_more == 'n':
            break

        num_new_vms = int(console.input("Ingrese el número de nuevas VMs a añadir: "))
        last_vm_id = max(G.nodes) + 1  # Comenzamos a añadir VMs desde el siguiente ID disponible
        total_vms = len(G.nodes) + num_new_vms

        # Reconstruir la topología en malla con las VMs adicionales
        G = nx.complete_graph(total_vms)
        display_and_save_graph(G)

    console.print(f"[bold green]Topología en malla finalizada con {len(G.nodes)} VMs.[/]")


def display_and_save_graph_bus(G):
    plt.figure(figsize=(12, 3))  # Configura el tamaño de la figura
    plt.title('Topología de Bus')

    # Ajusta las posiciones de los nodos en la línea horizontal y=0
    pos = {node: (node, 0) for node in G.nodes()}

    # Dibuja los nodos
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=800)

    # Dibuja los IDs de los nodos sobre cada nodo
    nx.draw_networkx_labels(G, {key: (val[0], val[1] + 0.1) for key, val in pos.items()}, font_size=12, verticalalignment='bottom')

    # Dibuja las conexiones verticales al bus
    for node in G.nodes():
        plt.plot([node, node], [0, -0.1], 'k-', lw=2)  # Conexiones verticales

    # Dibuja la línea del bus
    if G.nodes():
        plt.plot([min(G.nodes()), max(G.nodes())], [-0.1, -0.1], 'k-', lw=2)  # Línea del bus

    # Configuración adicional de la visualización
    plt.grid(False)  # Desactiva la cuadrícula
    plt.axis('off')  # Oculta los ejes
    plt.show()

def create_bus_topology():
    console.print("[bold green]Creando una topología tipo bus[/]")

    num_vms = int(console.input("Ingrese el número inicial de VMs: "))
    if num_vms < 2:
        console.print("[bold red]Debe haber al menos dos VMs para formar una topología tipo bus.[/]")
        return

    G = nx.path_graph(num_vms)  # Crea una topología inicial tipo bus
    display_and_save_graph_bus(G)

    while True:
        add_more = console.input("¿Deseas añadir más VMs antes de finalizar? (s/n): ").lower()
        if add_more == 'n':
            break

        num_new_vms = int(console.input("Ingrese el número de nuevas VMs a añadir: "))
        last_vm_id = max(G.nodes())
        for i in range(1, num_new_vms + 1):
            new_vm_id = last_vm_id + i
            G.add_node(new_vm_id)
            G.add_edge(new_vm_id - 1, new_vm_id)

        display_and_save_graph_bus(G)

    console.print(f"[bold green]Topología tipo bus finalizada con {len(G.nodes())} VMs.[/]")



def topology_management():

    
    while True:
        options = {
            '1': "Crear topología predefinida - Lineal",
            '2': "Crear topología predefinida - Árbol",
            '3': "Crear topología predefinida - Anillo",
            '4': "Crear topología predefinida - Malla",
            '5': "Crear topología predefinida - Bus",
            '6': "Regresar al Menú Principal"
        }
        display_menu("Gestión de Topología", options)
        choice = prompt_for_choice(options)
        if choice == '1':
            create_linear_topology()
        elif choice == '2':
            tree_topology()
        elif choice == '3':
            create_ring_topology()
        elif choice == '4':
            create_mesh_topology()
        elif choice == '5':
            create_bus_topology()
        elif choice == '6':
            break


@click.command()
def main():
    # Este es un ejemplo simplificado. Asume que el usuario es un administrador.
    role = 'admin'

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
