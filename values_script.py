import json
import os
import re

# Beispiel: Pfad zu deiner JSON-Datei
input_file = 'values.json'

# Ordnername für die Dateien
output_dir = 'Values'

# Stelle sicher, dass der Ordner existiert, ansonsten erstelle ihn
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Lade die JSON-Datei
with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Funktion, um ungültige Zeichen aus Dateinamen zu entfernen
def clean_filename(filename):
    # Ersetzt ungültige Zeichen durch Unterstriche
    return re.sub(r'[\\/*?:"<>|]', '_', filename)

# Iteriere durch die Datensätze und erstelle die txt-Dateien
for record in data:
    # Hole die relevanten Metadaten
    product = record.get("product", "")
    oid = record.get("_id", {}).get("$oid", "")
    values = record.get("values", [])
    
    # Wenn "values" vorhanden ist und nicht leer, speichere den Inhalt in eine Datei
    if values:
        # Erstelle den Dateinamen im Format "Product_$oid.txt"
        filename = f"{product}_{oid}.txt"
        clean_file_name = clean_filename(filename)
        filepath = os.path.join(output_dir, clean_file_name)
        
        # Bereite den Text für die Datei vor
        values_text = "\n".join(values)  # Verknüpfe die Werte mit einem Zeilenumbruch
        
        # Schreibe den Inhalt von 'values' in die Datei
        with open(filepath, 'w', encoding='utf-8') as txt_file:
            txt_file.write(values_text)

        print(f"Datei '{clean_file_name}' wurde erstellt und im Ordner '{output_dir}' gespeichert.")
