import os
import shutil

# Pfade zu den Ordnern
input_folder = "Values_nova"
ba_folder = "BA_Values_n"
de_folder = "DE_Values_n"

# Zielordner erstellen, falls sie nicht existieren
os.makedirs(ba_folder, exist_ok=True)
os.makedirs(de_folder, exist_ok=True)

# Dateien im Ordner "Values" durchsuchen
for file_name in os.listdir(input_folder):
    if file_name.endswith(".txt"):  # Nur TXT-Dateien berücksichtigen
        # Vollständiger Pfad zur Datei
        file_path = os.path.join(input_folder, file_name)
        
        # Dateiinhalt lesen
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Prüfen, ob [BA] oder [DE] im Inhalt vorhanden ist
        if "[BA]" in content:
            # Datei in den BA_Values-Ordner verschieben
            shutil.move(file_path, os.path.join(ba_folder, file_name))
            print(f"'{file_name}' wurde in '{ba_folder}' verschoben.")
        elif "[DE]" in content:
            # Datei in den DE_Values-Ordner verschieben
            shutil.move(file_path, os.path.join(de_folder, file_name))
            print(f"'{file_name}' wurde in '{de_folder}' verschoben.")

print("Alle Dateien wurden verarbeitet!")
