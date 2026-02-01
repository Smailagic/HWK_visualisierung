import tkinter as tk
from tkinter import ttk, PhotoImage
from pathlib import Path
import subprocess
import sys

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Interface mit Buttons")
        self.geometry("400x300")
        self.setup_ui()

    def setup_ui(self):
        # Bild suchen und laden (PNG/GIF oder JPEG mit Pillow)
        base_path = Path(__file__).parent
        img_file = next(base_path.glob('advertis.*'), None)
        image = None
        if img_file:
            try:
                image = PhotoImage(file=str(img_file))
            except tk.TclError:
                try:
                    from PIL import Image, ImageTk
                    img = Image.open(img_file)
                    image = ImageTk.PhotoImage(img)
                except Exception as e:
                    print(f"Fehler beim Verarbeiten des Bildes: {e}")
        else:
            print("Kein Bild mit Namen 'advertis.*' gefunden.")

        # Platzhalter oder echtes Bild anzeigen
        if image:
            img_label = ttk.Label(self, image=image)
            img_label.image = image
            img_label.pack(padx=10, pady=10)
        else:
            ttk.Label(self, text="[Kein Bild verfügbar]").pack(padx=10, pady=10)

        # Buttons
        ttk.Button(self, text="Values", command=self.open_values_popup).pack(pady=5)
        ttk.Button(self, text="Products", command=self.open_products_popup).pack(pady=5)

    def open_values_popup(self):
        content = self._run_script('pop_up.py')
        self._show_popup("Values Pop-up", content)

    def open_products_popup(self):
        content = self._run_script('pop_up_product.py')
        self._show_popup("Products Pop-up", content)

    def _run_script(self, script_name):
        script_path = Path(__file__).parent / script_name
        if not script_path.exists():
            return f"Skript '{script_name}' nicht gefunden."
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                check=True,
                capture_output=True,
                text=True
            )
            return result.stdout or "(Keine Ausgabe)"
        except subprocess.CalledProcessError as e:
            return f"Fehler beim Ausführen von '{script_name}':\n{e.stderr or e}"

    def _show_popup(self, title, content):
        popup = tk.Toplevel(self)
        popup.title(title)
        text = tk.Text(popup, wrap="word", width=50, height=15)
        text.insert("1.0", content)
        text.config(state="disabled")
        text.pack(padx=10, pady=10)
        ttk.Button(popup, text="Schließen", command=popup.destroy).pack(pady=5)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
