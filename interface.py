import tkinter as tk
from tkinter import PhotoImage
import subprocess

def run_pop_up():
    subprocess.run(["python", "pop_up.py"])

def run_pop_up_product():
    subprocess.run(["python", "pop_up_product.py"])

# Hauptfenster erstellen
root = tk.Tk()
root.title("Interface mit Buttons")
root.geometry("400x300")

# Bild laden
try:
    image = PhotoImage(file="advertis.png")
    img_label = tk.Label(root, image=image)
    img_label.place(x=10, y=10)
except Exception as e:
    print(f"Fehler beim Laden des Bildes: {e}")

# Button "Values"
values_button = tk.Button(root, text="Values", command=run_pop_up, width=15)
values_button.place(x=150, y=100)

# Button "Products"
products_button = tk.Button(root, text="Products", command=run_pop_up_product, width=15)
products_button.place(x=150, y=150)

# Hauptschleife starten
root.mainloop()
