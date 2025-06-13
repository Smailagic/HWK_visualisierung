import pandas as pd
import os

# Pfad zur Excel-Datei
excel_file_path = 'filtered_ads_DE.xlsx'

# Lade das Excel-Dokument
df = pd.read_excel(excel_file_path)
print("Excel-Datei erfolgreich geladen.")

# Verzeichnis für die Ausgabe der TXT-Dateien erstellen
output_dir = 'txt_za_inception'
os.makedirs(output_dir, exist_ok=True)

# Dictionary zum Verfolgen der Dateiindizes
file_counters = {}

# Iteriere über jede Zeile in der Tabelle
for index, row in df.iterrows():
    product = str(row['product']).strip()
    brand = str(row['brand']).strip()
    place = str(row['place']).strip()
    text = str(row['Text']).strip()

    # Generiere den Basis-Dateinamen
    base_filename = f"{product}__{brand}__{place}"

    # Erhöhe den Zähler für diesen Basisnamen
    if base_filename not in file_counters:
        file_counters[base_filename] = 1
    else:
        file_counters[base_filename] += 1

    # Endgültiger Dateiname mit laufender Nummer
    filename = f"{base_filename}_{file_counters[base_filename]}.txt"
    file_path = os.path.join(output_dir, filename)

    # Schreibe den Text in die Datei
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(text)
        print(f"Datei erstellt: {filename}")
    except Exception as e:
        print(f"Fehler beim Schreiben der Datei {filename}: {e}")

print("Alle Dateien wurden erfolgreich exportiert.")









