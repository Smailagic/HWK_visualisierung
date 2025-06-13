import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import tkinter as tk
from tkinter import simpledialog

# Funktion zum Berechnen der Kollokationen
def compute_collocations(values_list, product_list, target):
    collocations = defaultdict(int)

    # Durch jede Zeile iterieren
    for values, products in zip(values_list, product_list):
        values = [v.strip() for v in values.split(",")]
        products = [p.strip() for p in products.split(",")]

        if target in values:
            for value in values:
                if value != target:
                    collocations[(target, value)] += 1
            for product in products:
                collocations[(target, product)] += 1

    return collocations

# Funktion zur Auswahl eines Ziels
def get_target_from_user(values_list_1, values_list_2):
    root = tk.Tk()
    root.withdraw()  # Fenster unsichtbar machen

    # Einzigartige Werte sammeln
    unique_values = set()
    for values in values_list_1:
        unique_values.update(v.strip() for v in values.split(","))
    for values in values_list_2:
        unique_values.update(v.strip() for v in values.split(","))

    sorted_unique_values = sorted(unique_values)
    
    # "Ästhetik" an die erste Stelle setzen, falls vorhanden
    if "Ästhetik" in sorted_unique_values:
        sorted_unique_values.remove("Ästhetik")
        sorted_unique_values.insert(0, "Ästhetik")

    # Pop-up-Fenster zur Auswahl des Ziels
    selected_value = simpledialog.askstring(
        "Ziel auswählen", "Wählen Sie ein Ziel aus der Values-Liste:\n" + "\n".join(sorted_unique_values)
    )
    return selected_value

# Daten einlesen
file_1 = "filtered_ads.xlsx"
file_2 = "filtered_ads_BA.xlsx"

df1 = pd.read_excel(file_1)
df2 = pd.read_excel(file_2)

values_list_1 = df1["values"].dropna()
product_list_1 = df1["product"].dropna()
values_list_2 = df2["values"].dropna()
product_list_2 = df2["product"].dropna()

# Ziel aus der Liste auswählen
target = get_target_from_user(values_list_1, values_list_2)
if not target:
    print("Kein Ziel ausgewählt. Beende das Programm.")
else:
    print(f"Berechne Kollokationen für: {target}")

    # Kollokationen berechnen
    collocations_1 = compute_collocations(values_list_1, product_list_1, target)
    collocations_2 = compute_collocations(values_list_2, product_list_2, target)

    # Filtere Kollokationen, die weniger als 4 Mal auftreten
    collocations_1 = {key: weight for key, weight in collocations_1.items() if weight >= 3}
    collocations_2 = {key: weight for key, weight in collocations_2.items() if weight >= 3}

    # Diagramme erstellen
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))

    def plot_network(ax, collocations, title, values_list, product_list, color):
        G = nx.Graph()
        for (source, target_value), weight in collocations.items():
            G.add_edge(source, target_value, weight=weight, color=color)

        pos = nx.spring_layout(G, k=0.15, iterations=20)

        # Farben der Knoten festlegen
        node_colors = []
        node_labels = {}
        for node in G.nodes():
            if node == target:
                # Knotenfarbe für das target wird gleich wie die Knotenfarbe im Diagramm
                node_colors.append(color)
                node_labels[node] = node  # Text bleibt normal
            elif any(node in value.split(",") for value in values_list):
                node_colors.append("red")
                node_labels[node] = node
            elif any(node in product.split(",") for product in product_list):
                node_colors.append("yellow")
                node_labels[node] = node
            else:
                node_colors.append("lightgray")
                node_labels[node] = node

        nx.draw_networkx_nodes(G, pos, node_size=2000, node_color=node_colors, ax=ax)
        nx.draw_networkx_edges(G, pos, width=2, edge_color=color, ax=ax)

        # Textfarbe für das `target` wird auf schwarz gesetzt
        label_colors = {node: "black" if node == target else "black" for node in node_labels}

        nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10, font_weight="bold", ax=ax, font_color=label_colors)

        ax.set_title(title)
        ax.axis("off")

    # Diagramm 1: filtered_ads.xlsx
    plot_network(ax1, collocations_1, f"Kollokationen von '{target}' - filtered_ads.xlsx", values_list_1, product_list_1, "blue")

    # Diagramm 2: filtered_ads_BA.xlsx
    plot_network(ax2, collocations_2, f"Kollokationen von '{target}' - filtered_ads_BA.xlsx", values_list_2, product_list_2, "green")

    plt.tight_layout()
    plt.show()
