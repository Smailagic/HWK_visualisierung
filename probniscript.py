from docx import Document

def extract_bold_words(input_file, output_file):
    try:
        doc = Document(input_file)
        bold_words = []
       
        for paragraph in doc.paragraphs:
            for run in paragraph.runs:
                if run.bold and not run.italic:  # Prüfen, ob der Text fett markiert ist
                    bold_words.append(run.text.strip())
        
        with open(output_file, "w", encoding="utf-8") as f:
            for word in bold_words:
                if word:  # Leere Einträge vermeiden
                    f.write(word + "\n")
        print(f"Fett markierte Wörter wurden erfolgreich in '{output_file}' gespeichert.")
    except Exception as e:
        print(f"Fehler: {e}")
input_file = "probnipython.docx"  
output_file = "fett_markierte_woerter.txt"  

extract_bold_words(input_file, output_file)
