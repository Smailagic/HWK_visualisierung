import plotly.graph_objects as go
import networkx as nx

# Daten für Produkte und ihre Häufigkeiten
produkte = [
    'Rasierer', 'Mehl', 'Auto', 'Bekleidung', 'Gesichtspflege', 'Hörgeräte', 
    'Waschmittel', 'Bausparkasse', 'Deodorant', 'Kapseln', 'Krankenkasse', 
    'Medikament', 'Parfüm', 'Reinigungsmittel', 'Versicherung', 'Aluminiumleiter', 
    'BH', 'Blumenversand', 'Einbaumülleimer', 'Enzyklopädie', 'Fernseher', 
    'Feuchte Toilettentücher', 'Handy', 'Kaffevollautomat', 'Kleber', 'Kofferraumwannen', 
    'Küche', 'Milch', 'Saft', 'Tücher'
]
haeufigkeiten = [
    123, 5, 4, 4, 42, 4, 4, 3, 3, 3, 3, 3, 3, 3, 3, 
    2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 29
]

# Netzwerk erstellen
G = nx.Graph()

# Füge den Knoten 'Leistung' hinzu
G.add_node('Leistung')

# Füge die Produktknoten und Kanten mit den entsprechenden Häufigkeiten hinzu
for produkt, haeufigkeit in zip(produkte, haeufigkeiten):
    G.add_node(produkt)
    G.add_edge('Leistung', produkt, weight=haeufigkeit)

# Positionsbestimmung für Knoten
pos = nx.spring_layout(G, seed=42)

# Extrahieren der Kanten und deren Gewichte (Häufigkeit)
edges = G.edges(data=True)
edge_x = []
edge_y = []
edge_width = []

# Kantenpositionen und Breite basierend auf Häufigkeit
for edge in edges:
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    edge_x.append(x0)
    edge_x.append(x1)
    edge_y.append(y0)
    edge_y.append(y1)
    edge_width.append(edge[2]['weight'])

# Knotenpositionen und Text
node_x = []
node_y = []
node_text = []

for node in G.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)
    node_text.append(node)

# Visualisierung erstellen
fig = go.Figure()

# Kanten hinzufügen
fig.add_trace(go.Scatter(
    x=edge_x,
    y=edge_y,
    line=dict(width=0.5, color='gray'),
    mode='lines'
))

# Knoten hinzufügen
fig.add_trace(go.Scatter(
    x=node_x,
    y=node_y,
    mode='markers+text',
    text=node_text,
    marker=dict(size=10, color='blue'),
    textposition='top center'
))

# Layout anpassen
fig.update_layout(
    title='Netzwerkdiagramm der Kombination von "Leistung" mit Produkten',
    showlegend=False,
    xaxis=dict(showgrid=False, zeroline=False),
    yaxis=dict(showgrid=False, zeroline=False),
    hovermode='closest'
)

fig.show()
