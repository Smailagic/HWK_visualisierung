import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import tkinter as tk
import os
import sys

# Funktion zum Berechnen der Kollokationen zwischen Produkt und Values
def compute_collocations(values_list, product_list, target_product):
    collocations = defaultdict(int)

    # Iteriere durch jede Zeile
    for values, products in zip(values_list, product_list):
        values = [v.strip() for v in values.split(",")]
        products = [p.strip() for p in products.split(",")]

        # Wenn das Produkt in der Liste ist, kollokieren mit den Values
        if target_product in products:
            for value in values:
                collocations[(target_product, value)] += 1

    return collocations

# Funktion zur Auswahl eines Produkts (mit Scrollbar)
def get_product_from_user(product_list):
    root = tk.Tk()
    root.title("Produkt auswählen")
    root.configure(bg="yellow")

    # Canvas und Scrollbar erstellen
    canvas = tk.Canvas(root)
    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    # Scrollframe erstellen
    scrollable_frame = tk.Frame(canvas)

    # Scrollable-Frame in Canvas einfügen
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    # Erstelle Buttons für jedes Produkt
    buttons = []
    for product in sorted(set(product_list)):
        button = tk.Button(scrollable_frame, text=product, command=lambda p=product: select_product(p), bg="yellow")
        button.pack(fill="x", pady=2)
        buttons.append(button)

    # Update der Canvas-Größe, wenn alle Buttons hinzugefügt sind
    scrollable_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

    # Funktion zum Auswählen eines Produkts
    selected_product = tk.StringVar(value="")

    def select_product(value):
        nonlocal selected_product
        selected_product.set(value)
        root.destroy()

    # Fenstergröße und Position anpassen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"+{x}+{y}")

    root.mainloop()
    return selected_product.get()

# Funktion zur Auswahl der Mindesthäufigkeit (grünes Pop-up)
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

# Daten einlesen
file_1 = "filtered_ads.xlsx"
file_2 = "filtered_ads_BA.xlsx"

df1 = pd.read_excel(file_1)
df2 = pd.read_excel(file_2)

# Hier werden die Listen nach dem Einlesen der Daten initialisiert
values_list_1 = df1["values"].dropna()
product_list_1 = df1["product"].dropna()
values_list_2 = df2["values"].dropna()
product_list_2 = df2["product"].dropna()

# Produkt aus der Liste auswählen
target_product = get_product_from_user(product_list_1)
if not target_product:
    print("Kein Produkt ausgewählt. Beende das Programm.")
else:
    print(f"Berechne Kollokationen für das Produkt: {target_product}")

    # Mindesthäufigkeit auswählen
    min_frequency = get_minimum_frequency()
    print(f"Filtere Kollokationen mit einer Mindesthäufigkeit von: {min_frequency}")

    # Kollokationen berechnen
    collocations_1 = compute_collocations(values_list_1, product_list_1, target_product)
    collocations_2 = compute_collocations(values_list_2, product_list_2, target_product)

    # Wahrscheinlichkeiten berechnen (alle Kollokationen)
    def calculate_probabilities(collocations):
        total = sum(collocations.values())
        return {pair: weight / total for pair, weight in collocations.items()}

    probabilities_1 = calculate_probabilities(collocations_1)
    probabilities_2 = calculate_probabilities(collocations_2)

    # Kollokationen mit Mindesthäufigkeit filtern (nur für die Visualisierung)
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
            if node == target_product:
                node_colors.append(color)
                updated_labels[node] = f"{node}"
            elif any(node in value.split(",") for value in values_list):
                node_colors.append("red")
                updated_labels[node] = f"{node}\n({probabilities.get((target_product, node), 0):.2%})"
            else:
                node_colors.append("lightgray")
                updated_labels[node] = node

        nx.draw_networkx_nodes(G, pos, node_size=2000, node_color=node_colors, ax=ax)
        nx.draw_networkx_edges(G, pos, width=2, edge_color=color, ax=ax)
        nx.draw_networkx_labels(G, pos, labels=updated_labels, font_size=10, font_weight="bold", ax=ax)
        ax.set_title(title)
        ax.axis("off")

    plot_network(ax1, collocations_1_filtered, probabilities_1, f"Kollokationen von '{target_product}' - Deutsch", values_list_1, product_list_1, "blue")
    plot_network(ax2, collocations_2_filtered, probabilities_2, f"Kollokationen von '{target_product}' - Bosnien", values_list_2, product_list_2, "green")

    # Buttons hinzufügen
    def restart_script():
        plt.close(fig)
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def end_script():
        plt.close(fig)
        sys.exit()

    ax_button_back = plt.axes([0.4, 0.05, 0.2, 0.075])
    button_back = plt.Button(ax_button_back, 'Zurück zur Auswahl', color='blue', hovercolor='lightblue')
    button_back.on_clicked(lambda event: restart_script())

    ax_button_exit = plt.axes([0.7, 0.05, 0.2, 0.075])
    button_exit = plt.Button(ax_button_exit, 'Ende', color='red', hovercolor='pink')
    button_exit.on_clicked(lambda event: end_script())

    # Subplot-Abstände anpassen
    fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.2)  # Platz für Buttons schaffen
    plt.show()
