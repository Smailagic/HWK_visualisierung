
import json

# Beispiel: Pfad zu deiner JSON-Datei
input_file = 'werbungen.json'

# Lade die JSON-Datei
with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Iteriere durch die Datensätze und erstelle die txt-Dateien
for record in data:
    # Hole die relevanten Metadaten
    product = record.get("product", "")
    oid = record.get("_id", {}).get("$oid", "")
    
    # Hole den Text aus der "images"-Liste
    texts = []
    for image in record.get("images", []):
        texts.extend(image.get("text", []))  # Falls "text" eine Liste ist, fügen wir die Elemente hinzu
    
    # Der Text wird zu einem einzigen String zusammengefügt (mit Zeilenumbrüchen)
    full_text = "\n".join(texts)
    
    # Erstelle den Dateinamen im Format "product_oid.txt"
    filename = f"{product}_{oid}.txt"
    
    # Schreibe den Inhalt des 'text'-Feldes in die Datei
    with open(filename, 'w', encoding='utf-8') as txt_file:
        txt_file.write(full_text)

    print(f"Datei '{filename}' wurde erstellt.")

