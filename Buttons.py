import tkinter as tk
from PIL import Image, ImageTk
import webbrowser

def open_link():
    # Link im Standardbrowser öffnen
    webbrowser.open("http://141.147.0.184:3000/")

# Hauptfenster erstellen
root = tk.Tk()
root.title("vedad smailagic")
root.geometry("400x400")  # Fenstergröße festlegen

# Bild laden
image_path = "advertis.png"  # Pfad zur Bilddatei
image = Image.open(image_path)  # Bild mit Pillow öffnen
image = image.resize((300, 80))  # Optional: Bildgröße anpassen (Breite x Höhe)
photo = ImageTk.PhotoImage(image)  # Bild in Tkinter-kompatibles Format umwandeln

# Label mit Bild erstellen
label = tk.Label(root, image=photo, cursor="hand2")  # Cursor als Hand anzeigen
label.pack(pady=20)

# Klick-Event binden
label.bind("<Button-1>", lambda e: open_link())

# Hauptfenster starten
root.mainloop()
