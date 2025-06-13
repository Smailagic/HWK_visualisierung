import os
import shutil

# Ordnernamen
values_folder = "values"
dt_werbungen_folder = "Dt_Werbungen"

# Zielordner
ba_values_folder = "BA_Werbungen_Values"
ba_text_folder = "BA_Werbungen_Text"
de_values_folder = "DE_Werbungen_Values"
de_text_folder = "DE_Werbungen_Text"

# Zielordner erstellen, falls sie nicht existieren
os.makedirs(ba_values_folder, exist_ok=True)
os.makedirs(ba_text_folder, exist_ok=True)
os.makedirs(de_values_folder, exist_ok=True)
os.makedirs(de_text_folder, exist_ok=True)

# Dateien im Values-Ordner durchsuchen
for file_name in os.listdir(values_folder):
    if file_name.endswith(".txt"):
        # Pfad zur aktuellen Datei im Values-Ordner
        values_file_path = os.path.join(values_folder, file_name)
        
        # Pfad zur korrespondierenden Datei im Dt_Werbungen-Ordner
        dt_werbungen_file_path = os.path.join(dt_werbungen_folder, file_name)
        
        # Dateiinhalt auslesen
        with open(values_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Prüfen auf Werte [BA] und [DE]
        if "[BA]" in content:
            # Datei in BA-Werbungen verschieben
            shutil.copy(values_file_path, os.path.join(ba_values_folder, file_name))
            if os.path.exists(dt_werbungen_file_path):
                shutil.copy(dt_werbungen_file_path, os.path.join(ba_text_folder, file_name))
        elif "[DE]" in content:
            # Datei in DE-Werbungen verschieben
            shutil.copy(values_file_path, os.path.join(de_values_folder, file_name))
            if os.path.exists(dt_werbungen_file_path):
                shutil.copy(dt_werbungen_file_path, os.path.join(de_text_folder, file_name))

print("Dateien wurden erfolgreich in die entsprechenden Ordner verschoben!")
