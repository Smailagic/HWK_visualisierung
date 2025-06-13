import pandas as pd
from collections import Counter

# Pfad zur Excel-Datei
excel_file_path = 'filtered_ads.xlsx'

# Lade das Excel-Dokument
try:
    df = pd.read_excel(excel_file_path)
    print("Excel-Datei erfolgreich geladen.")
except Exception as e:
    print(f"Fehler beim Laden der Excel-Datei: {e}")
    exit()

# Counter für die Häufigkeit der Kombinationen
product_leistung_counts = Counter()  # Häufigkeit von 'Leistung' in Kombination mit 'product'
place_leistung_counts = Counter()  # Häufigkeit von 'Leistung' in Kombination mit 'place'
brand_leistung_counts = Counter()  # Häufigkeit von 'Leistung' in Kombination mit 'brand'
leistung_count = 0  # Gesamtzahl der Datensätze, die 'Leistung' in der 'values'-Spalte enthalten

# Durchlaufe alle Zeilen im DataFrame
for index, row in df.iterrows():
    values = row['values']  # Zugriff auf die 'values'-Spalte
    product = row['product']  # Zugriff auf die 'product'-Spalte
    place = row['place']  # Zugriff auf die 'place'-Spalte
    brand = row['brand']  # Zugriff auf die 'brand'-Spalte

    # Überprüfe, ob 'Leistung' in der 'values'-Spalte enthalten ist
    if isinstance(values, str) and 'Leistung' in values:
        # Zähle die Gesamtzahl der Datensätze, die 'Leistung' enthalten
        leistung_count += 1
        
        # Zähle die Kombinationen von 'Leistung' mit den 'product'-Werten
        product_leistung_counts[product] += 1
        
        # Zähle die Kombinationen von 'Leistung' mit den 'place'-Werten
        place_leistung_counts[place] += 1

        # Zähle die Kombinationen von 'Leistung' mit den 'brand'-Werten
        brand_leistung_counts[brand] += 1

# Berechne die Prozentsätze für 'place'
place_percentage = {}
if leistung_count > 0:
    for place, count in place_leistung_counts.items():
        place_percentage[place] = (count / leistung_count) * 100

# Sortiere die Ergebnisse nach Häufigkeit
sorted_product_leistung_counts = sorted(product_leistung_counts.items(), key=lambda x: x[1], reverse=True)
sorted_place_leistung_counts = sorted(place_leistung_counts.items(), key=lambda x: x[1], reverse=True)
sorted_brand_leistung_counts = sorted(brand_leistung_counts.items(), key=lambda x: x[1], reverse=True)
sorted_place_percentage = sorted(place_percentage.items(), key=lambda x: x[1], reverse=True)

# Exportiere die Ergebnisse in eine Textdatei
output_file_path = 'Leistung.txt'

# Schreibe die Ergebnisse in die Textdatei
with open(output_file_path, 'w', encoding='utf-8') as file:
    # Häufigkeit von 'Leistung' in Kombination mit 'product' (Filter: Häufigkeit >= 2)
    file.write("Häufigkeit von 'Leistung' in Kombination mit 'product' (sortiert nach Häufigkeit):\n")
    for product, count in sorted_product_leistung_counts:
        if count >= 2:
            file.write(f"{product}: {count}\n")
    
    # Häufigkeit von 'Leistung' in Kombination mit 'place' (absolute Häufigkeit, Filter: Häufigkeit >= 2)
    file.write("\nHäufigkeit von 'Leistung' in Kombination mit 'place' (absolute Häufigkeit):\n")
    for place, count in sorted_place_leistung_counts:
        if count >= 2:
            file.write(f"{place}: {count}\n")

    # Prozentsatz der Häufigkeit von 'Leistung' in Kombination mit 'place' (bezogen auf alle 'Leistung'-Datensätze, Filter: Häufigkeit >= 2)
    file.write("\nProzentuale Häufigkeit von 'Leistung' in Kombination mit 'place' (bezogen auf alle 'Leistung'-Datensätze):\n")
    for place, percentage in sorted_place_percentage:
        if place_leistung_counts[place] >= 2:
            file.write(f"{place}: {percentage:.2f}%\n")

    # Häufigkeit von 'Leistung' in Kombination mit 'brand' (Filter: Häufigkeit >= 2)
    file.write("\nHäufigkeit von 'Leistung' in Kombination mit 'brand' (sortiert nach Häufigkeit):\n")
    for brand, count in sorted_brand_leistung_counts:
        if count >= 2:
            file.write(f"{brand}: {count}\n")

print(f"Die Ergebnisse wurden erfolgreich in die Datei '{output_file_path}' geschrieben.")
