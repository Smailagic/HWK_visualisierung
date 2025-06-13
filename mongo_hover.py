from pymongo import MongoClient
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import tkinter as tk
import os
import sys

# Verbindung zu MongoDB herstellen
def get_mongo_data():
    username = "advertis"
    password = "VeDaD"
    host = "ora-02.db.lab.etf.unsa.ba:27017"
    mongo_uri = f"mongodb://{username}:{password}@{host}/?authSource=advertis&authMechanism=SCRAM-SHA-1"

    client = MongoClient(mongo_uri, ssl=False)
    db = client['advertis']
    collection = db['ads']

    projection = {
        "_id": 0,
        "product": 1,
        "values": 1
    }

    documents = collection.find({}, projection)
    return list(documents)

# MongoDB-Daten filtern und in Listen umwandeln
def filter_mongo_data(documents):
    de_values, de_products = [], []
    ba_values, ba_products = [], []

    for doc in documents:
        filtered_values = [item for item in doc['values'] if not (item.startswith('[') and item.endswith(']'))]
        if '[DE]' in doc['values']:
            de_values.append(",".join(filtered_values))
            de_products.append(doc['product'])
        elif '[BA]' in doc['values']:
            ba_values.append(",".join(filtered_values))
            ba_products.append(doc['product'])

    return de_values, de_products, ba_values, ba_products

# Funktion zum Berechnen der Kollokationen
def compute_collocations(values_list, product_list, target):
    collocations = defaultdict(int)

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

# Zielauswahl-Fenster (gelb)
def get_target_from_user(values_list_1, values_list_2):
    root = tk.Tk()
    root.title("Ziel auswählen")
    root.configure(bg="yellow")

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
        tk.Button(root, text=value, command=lambda v=value: select_value(v), bg="yellow").pack(fill="x", pady=2)

    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"+{x}+{y}")

    root.mainloop()
    return selected_value.get()

# Mindesthäufigkeit-Auswahl-Fenster (grün)
def get_minimum_frequency():
    root = tk.Tk()
    root.title("Mindesthäufigkeit auswählen")
    root.configure(bg="green")

    selected_frequency = tk.IntVar(value=3)

    def select_frequency(value):
        selected_frequency.set(value)
        root.destroy()

    for freq in range(1, 8):
        tk.Button(root, text=f"Häufigkeit >= {freq}", command=lambda f=freq: select_frequency(f), bg="green", fg="white").pack(fill="x", pady=2)

    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"+{x}+{y}")

    root.mainloop()
    return selected_frequency.get()

# MongoDB-Daten abrufen und filtern
documents = get_mongo_data()
de_values, de_products, ba_values, ba_products = filter_mongo_data(documents)

# Ziel auswählen
target = get_target_from_user(de_values, ba_values)
if not target:
    print("Kein Ziel ausgewählt. Beende das Programm.")
    sys.exit()

print(f"Berechne Kollokationen für: {target}")

# Mindesthäufigkeit auswählen
min_frequency = get_minimum_frequency()
print(f"Filtere Kollokationen mit einer Mindesthäufigkeit von: {min_frequency}")

# Kollokationen berechnen
collocations_1 = compute_collocations(de_values, de_products, target)
collocations_2 = compute_collocations(ba_values, ba_products, target)

# Wahrscheinlichkeiten berechnen
def calculate_probabilities(collocations):
    total = sum(collocations.values())
    return {pair: weight / total for pair, weight in collocations.items()}

probabilities_1 = calculate_probabilities(collocations_1)
probabilities_2 = calculate_probabilities(collocations_2)

# Kollokationen mit Mindesthäufigkeit filtern
collocations_1_filtered = {key: weight for key, weight in collocations_1.items() if weight >= min_frequency}
collocations_2_filtered = {key: weight for key, weight in collocations_2.items() if weight >= min_frequency}

# Diagramme erstellen
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))

def plot_network(ax, collocations, probabilities, title, values_list, product_list, color):
    G = nx.Graph()
    for (source, target_value), weight in collocations.items():
        G.add_edge(source, target_value, weight=weight, color=color)

    pos = nx.spring_layout(G, k=0.15, iterations=20)

    node_colors = []
    updated_labels = {}
    for node in G.nodes():
        if node == target:
            node_colors.append(color)
            updated_labels[node] = f"{node}"
        elif any(node in value.split(",") for value in values_list):
            node_colors.append("red")
            updated_labels[node] = f"{node}\n({probabilities.get((target, node), 0):.2%})\n(Beleg: {collocations.get((target, node), 0)})"
        elif any(node in product.split(",") for product in product_list):
            node_colors.append("yellow")
            updated_labels[node] = f"{node}\n({probabilities.get((target, node), 0):.2%})\n(Beleg: {collocations.get((target, node), 0)})"
        else:
            node_colors.append("lightgray")
            updated_labels[node] = node

    nx.draw_networkx_nodes(G, pos, node_size=2000, node_color=node_colors, ax=ax)
    nx.draw_networkx_edges(G, pos, width=2, edge_color=color, ax=ax)
    nx.draw_networkx_labels(G, pos, labels=updated_labels, font_size=10, font_weight="bold", ax=ax)
    ax.set_title(title)
    ax.axis("off")

plot_network(ax1, collocations_1_filtered, probabilities_1, f"Kollokationen von '{target}' - Deutsch", de_values, de_products, "blue")
plot_network(ax2, collocations_2_filtered, probabilities_2, f"Kollokationen von '{target}' - Bosnisch", ba_values, ba_products, "green")

# Funktion zum Erstellen des Tooltip-Fensters
def create_tooltip_window():
    tooltip_window = tk.Toplevel()
    tooltip_window.overrideredirect(True)  # Verhindert, dass das Fenster einen Rahmen hat
    tooltip_window.attributes("-topmost", True)  # Tooltip soll immer im Vordergrund sein

    tooltip_label = tk.Label(tooltip_window, text="", font=("Arial", 10), bg="yellow", fg="black", bd=2, relief="solid")
    tooltip_label.pack(padx=10, pady=10)

    return tooltip_window, tooltip_label

# Funktion zur Anzeige des Tooltips
def show_tooltip(event, ax, G, pos, collocations, probabilities, tooltip_window, tooltip_label):
    if event.xdata is None or event.ydata is None:
        tooltip_window.withdraw()
        return

    for node, (x, y) in pos.items():
        distance = ((event.xdata - x) ** 2 + (event.ydata - y) ** 2) ** 0.5
        if distance < 0.1:
            tooltip_window.deiconify()
            x_pixel, y_pixel = ax.transData.transform((event.xdata, event.ydata))
            tooltip_window.geometry(f"+{int(x_pixel + 10)}+{int(y_pixel + 10)}")
            label = f"Element: {node}\nBeleg: {collocations.get((target, node), 0)}\nWahrscheinlichkeit: {probabilities.get((target, node), 0):.2%}"
            tooltip_label.config(text=label)
            return
    tooltip_window.withdraw()

# Tooltip-Fenster und Label erstellen
tooltip_window, tooltip_label = create_tooltip_window()

# Ereignisbindung für Mausbewegungen
fig.canvas.mpl_connect("motion_notify_event", lambda event: show_tooltip(event, ax1, G1, pos1, collocations_1_filtered, probabilities_1, tooltip_window, tooltip_label))

plt.show()
