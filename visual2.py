import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

# Funktion zum Berechnen der Kollokationen
def compute_collocations(values_list, product_list, target="Leistungsfähigkeit"):  # Ziel auf "Leistungsfähigkeit" geändert
    collocations = defaultdict(int)

    # Durch jede Zeile iterieren
    for values, products in zip(values_list, product_list):
        values = [v.strip() for v in values.split(",")]
        products = [p.strip() for p in products.split(",")]

        # Wenn "Leistungsfähigkeit" in der values-liste ist, Kollokationen berechnen
        if target in values:  # Hier wird überprüft, ob "Leistungsfähigkeit" in der values-Liste vorkommt
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

# Subplots für zwei Diagramme nebeneinander erstellen
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))

# Netzwerkdiagramm für filtered_ads.xlsx (blau) - auf der linken Seite
G1 = nx.Graph()
for (source, target), weight in collocations_1.items():
    G1.add_edge(source, target, weight=weight, color='blue')

edges1 = G1.edges()
colors1 = [G1[u][v]['color'] for u, v in edges1]
weights1 = [G1[u][v]['weight'] for u, v in edges1]

node_colors1 = []
for node in G1.nodes():
    if any(node in value.split(",") for value in values_list_1):
        node_colors1.append('red')
    elif any(node in product.split(",") for product in product_list_1):
        node_colors1.append('yellow')
    else:
        node_colors1.append('lightgray')

pos1 = nx.spring_layout(G1, k=0.15, iterations=20)
nx.draw_networkx_nodes(G1, pos1, node_size=2000, node_color=node_colors1, ax=ax1)
nx.draw_networkx_edges(G1, pos1, edgelist=edges1, edge_color=colors1, width=weights1, ax=ax1)
nx.draw_networkx_labels(G1, pos1, font_size=10, font_weight='bold', ax=ax1)

ax1.set_title("Kollokationen von 'Leistungsfähigkeit' - Deutschland")
ax1.axis('off')

# Netzwerkdiagramm für filtered_ads_BA.xlsx (grün) - auf der rechten Seite
G2 = nx.Graph()
for (source, target), weight in collocations_2.items():
    G2.add_edge(source, target, weight=weight, color='green')

edges2 = G2.edges()
colors2 = [G2[u][v]['color'] for u, v in edges2]
weights2 = [G2[u][v]['weight'] for u, v in edges2]

node_colors2 = []
for node in G2.nodes():
    if any(node in value.split(",") for value in values_list_2):
        node_colors2.append('red')
    elif any(node in product.split(",") for product in product_list_2):
        node_colors2.append('yellow')
    else:
        node_colors2.append('lightgray')

pos2 = nx.spring_layout(G2, k=0.15, iterations=20)
nx.draw_networkx_nodes(G2, pos2, node_size=2000, node_color=node_colors2, ax=ax2)
nx.draw_networkx_edges(G2, pos2, edgelist=edges2, edge_color=colors2, width=weights2, ax=ax2)
nx.draw_networkx_labels(G2, pos2, font_size=10, font_weight='bold', ax=ax2)

ax2.set_title("Kollokationen von 'Leistungsfähigkeit' - Bosnien")
ax2.axis('off')

plt.tight_layout()
plt.show()

