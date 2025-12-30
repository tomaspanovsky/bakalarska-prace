import json
from tkinter import filedialog
def load():
    file_path = filedialog.askopenfilename(
    defaultextension=".json",    
    filetypes=[("JSON files", "*.json")],
    title="Načíst layout"
    )

    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            data = data[1]

        print("Soubor načten z:", file_path)
    else:
        print("Uživatel zrušil načítání")

    return data