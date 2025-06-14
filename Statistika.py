import json
import pandas as pd

# Funktion zum Überprüfen, ob [BA] in den values vorhanden ist
def contains_ba(values):
    return '[BA]' in values

# Funktion zum Extrahieren von Werten, die nicht [BA] oder [YUG] enthalten
def extract_valid_values(values):
    valid_values = []
    # Werte, die ausgeschlossen werden sollen
    exclude_values = ['[BA]', '[YUG]']
    
    for value in values:
        # Wenn der Wert nicht in der Liste der auszuschließenden Werte ist, füge ihn hinzu
        if value not in exclude_values:
            valid_values.append(value)
    
    return valid_values

# Pfad zur JSON-Datei
json_file_path = 'ads.json'

# Lade den JSON-Datensatz
with open(json_file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Liste für gefilterte Daten
filtered_data = []

# Durchlaufe alle Datensätze
for record in data:
    values = record.get('values', [])

    # Wenn der Datensatz [BA] enthält, verarbeite ihn weiter
    if contains_ba(values):
        # Extrahiere die relevanten Informationen
        product = record.get('product', '')
        brand = record.get('brand', '')
        place = record.get('place', '')

        # Extrahiere nur die gültigen Werte aus der 'values'-Kategorie
        valid_values = extract_valid_values(values)

        # Wenn gültige Werte vorhanden sind, füge den Datensatz zur Liste hinzu
        if valid_values:
            filtered_data.append({
                'product': product,
                'brand': brand,
                'place': place,
                'valid_values': ', '.join(valid_values)  # Kombiniere alle gültigen Werte in einem String
            })

# Erstelle einen DataFrame aus den gefilterten Daten
df = pd.DataFrame(filtered_data)

# Wenn keine Daten vorhanden sind, geben wir eine Nachricht aus
if df.empty:
    print("Keine gültigen Daten gefunden.")
else:
    # Exportiere den DataFrame nach Excel
    output_excel_path = 'filtered_ads_BA.xlsx'
    df.to_excel(output_excel_path, index=False)

    print(f'Daten wurden erfolgreich in die Excel-Datei exportiert: {output_excel_path}')

