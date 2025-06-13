# Import der benötigten Bibliotheken
import numpy as np
import matplotlib.pyplot as plt
import mplcursors

# Schritt 1: Beispiel-Daten erstellen
# Erstelle Zufallsdaten für x und y
x = np.random.rand(10)
y = np.random.rand(10)

# Labels für jeden Punkt (hier einfach nummeriert)
labels = [f"Point {i}" for i in range(10)]

# Maskierte Arrays erstellen
# In diesem Beispiel maskieren wir den 3. Punkt (Index 2)
masked_x = np.ma.masked_array(x, mask=[False, False, True, False, False, False, False, False, False, False])
masked_y = np.ma.masked_array(y, mask=[False, False, True, False, False, False, False, False, False, False])

# Schritt 2: Scatterplot erstellen
# Ein matplotlib-Figur und Achse erstellen
fig, ax = plt.subplots()

# Zeichne die Punkte als Streudiagramm
# Nur unmaskierte Punkte werden angezeigt
scatter = ax.scatter(masked_x, masked_y)

# Schritt 3: Labels für Hover-Effekte vorbereiten
# Wir erstellen ein Dictionary, das den Index eines Punktes mit seinem Label verbindet
# Maskierte Punkte werden dabei ignoriert
node_hover_labels = {i: labels[i] for i in range(len(x)) if not masked_x.mask[i]}

# Schritt 4: Interaktive Anmerkungen hinzufügen
# Definiere eine Funktion, die ausgeführt wird, wenn ein Punkt im Diagramm angeklickt oder mit der Maus berührt wird
def on_add(sel):
    """
    Diese Funktion wird von mplcursors aufgerufen, wenn ein Punkt ausgewählt wird.
    Sie setzt den Text der Annotation auf das passende Label.
    """
    target = sel.target  # Die Koordinaten des ausgewählten Punkts
    # Finde den Index des Punkts anhand der x-Werte des maskierten Arrays
    try:
        index = np.where(masked_x == target[0])[0][0]
        # Setze den Text der Annotation auf das Label aus node_hover_labels
        sel.annotation.set_text(node_hover_labels.get(index, "Unknown Point"))
    except IndexError:
        # Falls der Punkt nicht gefunden wird (z. B. wenn er maskiert ist), setze einen leeren Text
        sel.annotation.set_text("")

# Schritt 5: mplcursors für interaktive Anmerkungen aktivieren
# Erstelle einen Cursor und verbinde ihn mit der on_add-Funktion
cursor = mplcursors.cursor(scatter, hover=True)
cursor.connect("add", on_add)

# Schritt 6: Diagramm anzeigen
# Zeige die matplotlib-Grafik an
plt.title("Interactive Scatter Plot with Masked Data")
plt.xlabel("X-Axis")
plt.ylabel("Y-Axis")
plt.show()
