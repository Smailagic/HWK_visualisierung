from pymongo import MongoClient

# Deine Verbindungseinstellungen
username = "advertis"
password = "VeDaD"
host = "ora-02.db.lab.etf.unsa.ba:27017"
mongo_uri = f"mongodb://{username}:{password}@{host}/?authSource=admin"

# Verbinde mit MongoDB ohne SSL
client = MongoClient(
    mongo_uri,
    ssl=False  # SSL deaktivieren
)

# Teste die Verbindung
try:
    db = client.admin  # oder eine andere Datenbank
    print("Verbindung zu MongoDB hergestellt!")
except Exception as e:
    print(f"Verbindungsfehler: {e}")
