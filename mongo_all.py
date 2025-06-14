from pymongo import MongoClient
import pandas as pd

# Deine Verbindungseinstellungen
username = "advertis"
password = "VeDaD"
host = "ora-02.db.lab.etf.unsa.ba:27017"
mongo_uri = f"mongodb://{username}:{password}@{host}/?authSource=advertis&authMechanism=SCRAM-SHA-1"

# Verbinde mit MongoDB ohne SSL
client = MongoClient(
    mongo_uri,
    ssl=False  # SSL deaktivieren
)

# Zugriff auf die Datenbank und Sammlung
db = client['advertis']
collection = db['ads']  # Zugriff auf die 'ads' Sammlung

# Abrufen der Datensätze mit den benötigten Feldern
projection = {
    "_id": 1,
    "product": 1,
    "brand": 1,
    "place": 1,
    "values": 1
}

documents = collection.find({}, projection)

# Listen für die gefilterten Daten
de_data = []
ba_data = []

# Durchlaufe die Dokumente und filtere die `values`-Liste
for doc in documents:
    # Filtere Elemente aus der values-Liste, die in eckigen Klammern sind
    filtered_values = [item for item in doc['values'] if not (item.startswith('[') and item.endswith(']'))]
    
    # Überprüfe, ob '[DE]' oder '[BA]' in den Werten enthalten sind
    if '[DE]' in doc['values']:
        de_data.append({**doc, 'values': filtered_values})  # Füge die gefilterten Daten hinzu
    elif '[BA]' in doc['values']:
        ba_data.append({**doc, 'values': filtered_values})  # Füge die gefilterten Daten hinzu

# Wenn Daten für [DE] vorhanden sind, exportiere sie in eine Excel-Datei
if de_data:
    de_df = pd.DataFrame(de_data)
    de_df.to_excel('ads_de_data.xlsx', index=False, engine='openpyxl')
    print("Daten mit [DE] wurden erfolgreich in 'ads_de_data.xlsx' exportiert!")

# Wenn Daten für [BA] vorhanden sind, exportiere sie in eine Excel-Datei
if ba_data:
    ba_df = pd.DataFrame(ba_data)
    ba_df.to_excel('ads_ba_data.xlsx', index=False, engine='openpyxl')
    print("Daten mit [BA] wurden erfolgreich in 'ads_ba_data.xlsx' exportiert!")

# Falls keine Daten für [DE] oder [BA] vorhanden sind
if not de_data and not ba_data:
    print("Keine passenden Daten mit [DE] oder [BA] in der 'values'-Liste gefunden.")
