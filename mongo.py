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

# Zugriff auf die Datenbank und Sammlung (Collection)
db = client['advertis']  # Ersetze 'advertis' mit dem Namen deiner MongoDB-Datenbank
collection = db['deine_collection']  # Ersetze 'deine_collection' mit dem Namen deiner Sammlung

# Abrufen der Daten aus der Sammlung
documents = collection.find()  # Abrufen aller Dokumente

# Umwandeln der Daten in eine Liste von Dictionaries
data = list(documents)

# Überprüfen, ob Daten vorhanden sind
if data:
    # Erstelle ein DataFrame aus den abgerufenen Daten
    df = pd.DataFrame(data)
    
    # Speichern in eine Excel-Datei
    df.to_excel('mongodb_daten.xlsx', index=False, engine='openpyxl')
    print("Daten wurden erfolgreich in die Excel-Datei geschrieben!")
else:
    print("Keine Daten gefunden.")
