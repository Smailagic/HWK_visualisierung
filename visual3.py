import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import matplotlib.colors as mcolors

# Funktion zum Berechnen der Kollokationen
def compute_collocations(values_list, product_list, target="Tradition"):
    collocations = defaultdict(int)

    # Durch jede Zeile iterieren
    for values, products in zip(values_list, product_list):
        values = [v.strip() for v in values.split(",")]
        products = [p.strip() for p in products.split(",")]

        # Wenn "Tradition" in der values-liste ist, Kollokationen berechnen
        if target in values:
            # Kollokationen mit anderen Werten in der values-liste
            for value in values:
                if value != target:
                    collocations[(target, value)] += 1
            # Kollokationen mit den Produkten in der product-liste
            for product in products:
                collocations[(target, product)] += 1
    
    return collocations

# Daten einlesen aus beiden Excel-Dateien
file_1 = 'filtered_ads.xlsx'
file_2 = 'filtered_ads_BA.xlsx'

df1 = pd.read_excel(file_1)
df2 = pd.read_excel(file_2)

# Extrahiere die values- und product-liste aus den entsprechenden Spalten
values_list_1 = df1['values'].dropna()  # Werte aus Spalte "values"
product_list_1 = df1['product'].dropna()  # Werte aus Spalte "product"

values_list_2 = df2['values'].dropna()  # Werte aus Spalte "values"
product_list_2 = df2['product'].dropna()  # Werte aus Spalte "product"

# Kollokationen berechnen
collocations_1 = compute_collocations(values_list_1, product_list_1)
collocations_2 = compute_collocations(values_list_2, product_list_2)

# Filtere Kollokationen, die weniger als 3 Mal auftreten
collocations_1 = {key: weight for key, weight in collocations_1.items() if weight >= 3}
collocations_2 = {key: weight for key, weight in collocations_2.items() if weight >= 3}

# Netzwerkdiagramm erstellen
G = nx.Graph()

# Knoten und Kanten für filtered_ads.xlsx (blau)
for (source, target), weight in collocations_1.items():
    G.add_edge(source, target, weight=weight, color='blue')

# Knoten und Kanten für filtered_ads_BA.xlsx (grün)
for (source, target), weight in collocations_2.items():
    G.add_edge(source, target, weight=weight, color='green')

# Zeichnen des Diagramms
edges = G.edges()
colors = [G[u][v]['color'] for u, v in edges]
weights = [G[u][v]['weight'] for u, v in edges]

# Knotenfarben festlegen
node_colors = []
for node in G.nodes():
    if node == "Tradition":
        # Spezialbehandlung für "Tradition"
        node_colors.append('black')
    elif any(node in value.split(",") for value in values_list_1) or any(node in value.split(",") for value in values_list_2):
        node_colors.append('red')
    elif any(node in product.split(",") for product in product_list_1) or any(node in product.split(",") for product in product_list_2):
        node_colors.append('yellow')
    else:
        node_colors.append('lightgray')  # Für alle anderen Knoten

# Berechne den Farbverlauf basierend auf der Gewichtung der Kanten
norm = mcolors.Normalize(vmin=min(weights), vmax=max(weights))  # Normalisieren der Gewichtung für Farbverlauf
cmap = plt.cm.get_cmap('coolwarm')  # Farbverlauf (von Blau nach Rot)

# Kantenfarbe mit dem Farbverlauf anwenden
edge_colors = [cmap(norm(weight)) for weight in weights]

# Knotenfarbe: Helligkeit basierend auf der Anzahl der Kollokationen (je mehr Kollokationen, desto heller)
node_sizes = [500 + 100 * sum(weight for (u, v), weight in collocations_1.items() if u == node or v == node) for node in G.nodes()]

# 2. Heatmap-Visualisierung
# Erstellen einer Achse für den Farbverlauf
fig, ax = plt.subplots(figsize=(12, 12))  # Neue Achse für die Farbskala

# Visualisierung im Heatmap-Stil
pos = nx.spring_layout(G, k=0.15, iterations=20)

# Knoten und Kanten zeichnen
nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, ax=ax)
nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color=edge_colors, width=weights, ax=ax)
nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold', font_color='black', labels={node: node for node in G.nodes()}, ax=ax)

# Spezialbehandlung für "Leistung"
if "Tradition" in G.nodes():
    nx.draw_networkx_nodes(G, pos, nodelist=["Tradition"], node_size=3000, node_color='black', ax=ax)
    nx.draw_networkx_labels(G, pos, labels={"Tradition": "Tradition"}, font_size=12, font_weight='bold', font_color='white', ax=ax)

# Farblegende hinzufügen
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])  # Leeres Array für die Farbskala

# Farbskala an die Achse anheften
cbar = fig.colorbar(sm, ax=ax, orientation='vertical', label='Kantenstärke (Kollokationen)')

plt.title("Heatmap der Kollokationen von 'Tradition'")
plt.axis('off')
plt.show()
