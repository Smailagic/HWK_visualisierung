import pandas as pd
from collections import Counter
import itertools

# Pfad zur Excel-Datei
excel_file_path = 'auto.xlsx'

# Lade das Excel-Dokument
try:
    df = pd.read_excel(excel_file_path)
    print("Excel-Datei erfolgreich geladen.")
except Exception as e:
    print(f"Fehler beim Laden der Excel-Datei: {e}")
    exit()

# Zeige die ersten paar Zeilen der Tabelle, um sicherzustellen, dass die Daten korrekt geladen wurden
print("\nDaten aus der Excel-Datei:")
print(df.head())  # Überprüfe, ob die Spalten und Werte richtig geladen wurden

# Liste zum Speichern aller Werte aus der Kategorie 'values'
values_list = []

# Counter für Kombinationen
combination_counts = Counter()

# Überprüfe, ob die richtigen Zeilen (D2 bis D13) und die Spalte "values" existieren
for index, row in df.iterrows():
    if index >= 1 and index <= 12:  # Beschränkung auf Zeilen D2 bis D13 (Index 1 bis 12)
        values = row['values']  # Zugriff auf die 'values'-Spalte
        
        # Zeige die 'values' für jedes Produkt "auto"
        print(f"Extrahierte Werte aus 'values' für Index {index}: {values}")
        
        # Überprüfe, ob 'values' ein String ist
        if isinstance(values, str):
            # Wenn 'values' ein String ist, gehe davon aus, dass die Werte durch Kommas getrennt sind
            split_values = [value.strip() for value in values.split(',')]  # Entferne Leerzeichen
            print(f"Geteilte Werte: {split_values}")
            
            # Zähle Kombinationen innerhalb dieser Zeile
            for n in range(2, len(split_values) + 1):  # Kombiniere 2er bis n-er Kombinationen
                for combo in itertools.combinations(split_values, n):
                    combination_counts[combo] += 1
            
            values_list.extend(split_values)
        elif isinstance(values, list):  # Falls 'values' eine Liste ist
            print(f"Liste aus 'values': {values}")
            # Zähle Kombinationen innerhalb dieser Zeile
            for n in range(2, len(values) + 1):  # Kombiniere 2er bis n-er Kombinationen
                for combo in itertools.combinations(values, n):
                    combination_counts[combo] += 1
            
            values_list.extend(values)

# Wenn keine Werte extrahiert wurden, zeige eine Nachricht an
if not values_list:
    print("Keine Werte in der 'values'-Spalte gefunden oder keine Datensätze mit 'product' = 'auto'.")

# Zähle die Häufigkeit der einzelnen Elemente in der 'values'-Liste
value_counts = Counter(values_list)

# Zeige die Häufigkeit der einzelnen Elemente und Kombinationen in der Konsole an
if value_counts:
    print("\nHäufigkeit der einzelnen Werte:")
    print(value_counts)

if combination_counts:
    print("\nHäufigkeit der Kombinationen:")
    print(combination_counts)

# Schreibe das Ergebnis in eine Textdatei 'rezultat2.txt'
try:
    with open('rezultat2.txt', 'w', encoding='utf-8') as file:
        file.write("Häufigkeit der einzelnen Werte:\n")
        for value, count in value_counts.items():
            file.write(f"{value}: {count}\n")
        
        file.write("\nHäufigkeit der Kombinationen:\n")
        for combo, count in combination_counts.items():
            file.write(f"{', '.join(combo)}: {count}\n")
    
    print("\nHäufigkeit der Elemente und Kombinationen wurde erfolgreich in 'rezultat2.txt' geschrieben.")
except Exception as e:
    print(f"Fehler beim Schreiben der Datei: {e}")






