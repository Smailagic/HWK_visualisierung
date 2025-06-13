from pymongo import MongoClient
import pandas as pd

# Deine Verbindungseinstellungen
username = "advertis"
password = "VeDaD"
host = "ora-02.db.lab.etf.unsa.ba:27017"
mongo_uri = f"mongodb://{username}:{password}@{host}/?authSource=advertis&authMechanism=DEFAULT"

# Verbinde mit MongoDB ohne SSL
client = MongoClient(
    mongo_uri,
    ssl=False  # SSL deaktivieren
)

# Zugriff auf die Datenbank und Sammlung
db = client['advertis']
collection = db['ads']  # Zugriff auf die 'ads' Sammlung

# Abrufen der ersten 5 Dokumente mit spezifischen Feldern (_id, product, brand, place, values)
projection = {
    "_id": 1,
    "product": 1,
    "brand": 1,
    "place": 1,
    "values": 1
}

documents = collection.find({}, projection).limit(5)

# Umwandeln der abgerufenen Daten in eine Liste von Dictionaries
data = list(documents)

# Überprüfen, ob Daten vorhanden sind
if data:
    # Erstelle ein DataFrame aus den abgerufenen Daten
    df = pd.DataFrame(data)

    # Speichern in eine Excel-Datei
    df.to_excel('ads_daten_filtered.xlsx', index=False, engine='openpyxl')
    print("Daten aus der Sammlung 'ads' wurden erfolgreich in die Excel-Datei geschrieben!")
else:
    print("Keine Daten in der Sammlung 'ads' gefunden.")
