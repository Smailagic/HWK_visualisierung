import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import tkinter as tk
import os
import sys

# Funktion zum Berechnen der Kollokationen
def compute_collocations(values_list, product_list, target):
    collocations = defaultdict(int)

    # Berechnung der Kollokationen für alle Elemente
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

# Zielauswahl-Fenster
def get_target_from_user(values_list_1, values_list_2):
    root = tk.Tk()
    root.title("Ziel auswählen")

    unique_values = set()
    for values in values_list_1:
        unique_values.update(v.strip() for v in values.split(","))
    for values in values_list_2:
        unique_values.update(v.strip() for v in values.split(","))

    sorted_unique_values = sorted(unique_values)
    if "Ästhetik" in sorted_unique_values:
        sorted_unique_values.remove("Ästhetik")
        sorted_unique_values.insert(0, "Ästhetik")

    selected_value = tk.StringVar(value="")

    def select_value(value):
        nonlocal selected_value
        selected_value.set(value)
        root.destroy()

    for value in sorted_unique_values:
        tk.Button(root, text=value, command=lambda v=value: select_value(v)).pack(fill="x", pady=2)

    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"+{x}+{y}")

    root.mainloop()
    return selected_value.get()

# Mindesthäufigkeit-Auswahl-Fenster
def get_minimum_frequency():
    root = tk.Tk()
    root.title("Mindesthäufigkeit auswählen")

    selected_frequency = tk.IntVar(value=3)

    def select_frequency(value):
        selected_frequency.set(value)
        root.destroy()

    for freq in range(1, 8):
        tk.Button(root, text=f"Häufigkeit >= {freq}", command=lambda f=freq: select_frequency(f)).pack(fill="x", pady=2)

    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"+{x}+{y}")

    root.mainloop()
    return selected_frequency.get()

# Daten einlesen
file_1 = "filtered_ads.xlsx"
file_2 = "filtered_ads_BA.xlsx"

df1 = pd.read_excel(file_1)
df2 = pd.read_excel(file_2)

values_list_1 = df1["values"].dropna()
product_list_1 = df1["product"].dropna()
values_list_2 = df2["values"].dropna()
product_list_2 = df2["product"].dropna()

# Ziel auswählen
target = get_target_from_user(values_list_1, values_list_2)
if not target:
    print("Kein Ziel ausgewählt. Beende das Programm.")
else:
    print(f"Berechne Kollokationen für: {target}")

    # Mindesthäufigkeit auswählen
    min_frequency = get_minimum_frequency()
    print(f"Filtere Kollokationen mit einer Mindesthäufigkeit von: {min_frequency}")

    # Kollokationen berechnen
    collocations_1 = compute_collocations(values_list_1, product_list_1, target)
    collocations_2 = compute_collocations(values_list_2, product_list_2, target)

    # Wahrscheinlichkeiten berechnen
    def calculate_probabilities(collocations):
        total = sum(collocations.values())
        return {pair: weight / total for pair, weight in collocations.items()}

    probabilities_1 = calculate_probabilities(collocations_1)
    probabilities_2 = calculate_probabilities(collocations_2)

    # Kollokationen mit Mindesthäufigkeit filtern
    collocations_1_filtered = {key: weight for key, weight in collocations_1.items() if weight >= min_frequency}
    collocations_2_filtered = {key: weight for key, weight in collocations_2.items() if weight >= min_frequency}

    # Netzwerk erstellen
    G = nx.Graph()

    # Füge Knoten und Kanten für die Deutsch-Daten hinzu
    for (source, target_value), weight in collocations_1_filtered.items():
        G.add_edge(source, target_value, weight=weight, label=f"{probabilities_1.get((target, target_value), 0):.2%}")

    # Füge Knoten und Kanten für die Bosnisch-Daten hinzu
    for (source, target_value), weight in collocations_2_filtered.items():
        G.add_edge(source, target_value, weight=weight, label=f"{probabilities_2.get((target, target_value), 0):.2%}")

    # Visualisierung des Netzwerks
    pos = nx.spring_layout(G, k=0.15, iterations=20)
    plt.figure(figsize=(12, 12))

    # Knoten und Kanten zeichnen
    edge_labels = nx.get_edge_attributes(G, 'label')
    node_labels = nx.get_node_attributes(G, 'label')

    nx.draw(G, pos, with_labels=True, node_color="skyblue", node_size=3000, font_size=10, font_weight="bold", width=2)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    plt.title(f"Netzwerkdiagramm der Kollokationen für '{target}'", fontsize=15)
    plt.show()
