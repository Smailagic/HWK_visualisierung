import json
import pandas as pd

# Funktion zum Überprüfen, ob [DE] in den values vorhanden ist
def contains_de(values):
    if isinstance(values, list):  # Sicherstellen, dass values eine Liste ist
        return '[DE]' in values
    return False

# Funktion zum Extrahieren von Werten, die nicht [DDR], [60-90] oder [DE] enthalten
def extract_valid_values(values):
    exclude_values = ['[DDR]', '[60-90]', '[DE]']
    if isinstance(values, list):  # Sicherstellen, dass values eine Liste ist
        return [value for value in values if value not in exclude_values]
    return []

# Funktion zum Extrahieren von Texten aus dem 'images'-Feld
def extract_text_from_images(images):
    texts = []
    if isinstance(images, list):  # Sicherstellen, dass images eine Liste ist
        for image in images:
            image_text = image.get('text', [])
            if isinstance(image_text, list):
                texts.extend(image_text)  # Füge alle Texte hinzu
    return ' | '.join(texts)  # Verbinde Texte mit einem Trennzeichen

# Pfad zur JSON-Datei
json_file_path = 'ads.json'

# Lade den JSON-Datensatz
try:
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
except Exception as e:
    print(f"Fehler beim Laden der JSON-Datei: {e}")
    exit()

# Liste für gefilterte Daten
filtered_data = []

# Durchlaufe alle Datensätze
for record in data:
    values = record.get('values', [])
    images = record.get('images', [])  # Extrahiere das 'images'-Feld

    # Wenn der Datensatz [DE] enthält und nicht [DDR] oder [60-90], verarbeite ihn weiter
    if contains_de(values):
        # Extrahiere die relevanten Informationen
        product = record.get('product', '')
        brand = record.get('brand', '')
        place = record.get('place', '')

        # Extrahiere nur die gültigen Werte aus der 'values'-Kategorie
        valid_values = extract_valid_values(values)

        # Extrahiere Texte aus dem 'images'-Feld
        extracted_texts = extract_text_from_images(images)

        # Füge den Datensatz zur Liste hinzu
        filtered_data.append({
            'product': product,
            'brand': brand,
            'place': place,
            'valid_values': ', '.join(valid_values),  # Kombiniere alle gültigen Werte in einem String
            'text': extracted_texts  # Füge extrahierte Texte hinzu
        })

# Erstelle einen DataFrame aus den gefilterten Daten
df = pd.DataFrame(filtered_data)

# Wenn keine Daten vorhanden sind, geben wir eine Nachricht aus
if df.empty:
    print("Keine gültigen Daten gefunden.")
else:
    # Exportiere den DataFrame nach Excel
    output_excel_path = 'filtered_ads_DE.xlsx'
    try:
        df.to_excel(output_excel_path, index=False)  # 'encoding' entfernt
        print(f'Daten wurden erfolgreich in die Excel-Datei exportiert: {output_excel_path}')
    except Exception as e:
        print(f"Fehler beim Exportieren der Excel-Datei: {e}")
