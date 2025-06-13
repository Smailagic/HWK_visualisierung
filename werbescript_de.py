import json
import os
import re

# Beispiel: Pfad zu deiner JSON-Datei
input_file = 'werbungen_prim.json'

# Ordnername für die deutschen Texte
output_dir = 'Dt_Werbungen'

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
    
    # Hole den Text aus der "images"-Liste
    texts = []
    for image in record.get("images", []):
        texts.extend(image.get("text", []))  # Falls "text" eine Liste ist, fügen wir die Elemente hinzu
    
    # Wenn Texte vorhanden sind, speichere sie in eine Datei
    if texts:
        full_text = "\n".join(texts)
        
        # Erstelle den Dateinamen im Format "product_oid.txt"
        filename = f"{product}_{oid}.txt"
        clean_file_name = clean_filename(filename)
        filepath = os.path.join(output_dir, clean_file_name)
        
        # Schreibe den Inhalt des 'text'-Feldes in die Datei
        with open(filepath, 'w', encoding='utf-8') as txt_file:
            txt_file.write(full_text)

        print(f"Datei '{clean_file_name}' wurde erstellt und im Ordner '{output_dir}' gespeichert.")
