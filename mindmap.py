import networkx as nx
import matplotlib.pyplot as plt

# Erstelle ein Netzwerkgraph
G = nx.DiGraph()  # gerichteter Graph, um die Hierarchie darzustellen

# Hinzufügen von Knoten und Kanten
G.add_node("Zentrum", size=100, color="yellow")  # Hauptknoten
G.add_node("Thema 1", size=50, color="blue")
G.add_node("Thema 2", size=50, color="green")
G.add_node("Unterthema 1.1", size=30, color="orange")
G.add_node("Unterthema 1.2", size=30, color="red")

# Verbindungen (Kanten) zwischen den Knoten
G.add_edge("Zentrum", "Thema 1")
G.add_edge("Zentrum", "Thema 2")
G.add_edge("Thema 1", "Unterthema 1.1")
G.add_edge("Thema 1", "Unterthema 1.2")

# Positionierung der Knoten (manuell für eine bessere Übersichtlichkeit)
pos = {
    "Zentrum": (0, 0),
    "Thema 1": (-1, -1),
    "Thema 2": (1, -1),
    "Unterthema 1.1": (-1.5, -2),
    "Unterthema 1.2": (-0.5, -2)
}

# Zeichnen des Graphen
plt.figure(figsize=(8, 6))

# Knoten zeichnen
node_sizes = [G.nodes[node]["size"] for node in G.nodes()]
node_colors = [G.nodes[node]["color"] for node in G.nodes()]
nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors)

# Kanten zeichnen
nx.draw_networkx_edges(G, pos, width=2, alpha=0.7, edge_color="black")

# Beschriftungen hinzufügen
nx.draw_networkx_labels(G, pos, font_size=12, font_weight="bold", font_color="black")

# Diagramm anzeigen
plt.title("Mindmap Beispiel")
plt.axis("off")
plt.show()
