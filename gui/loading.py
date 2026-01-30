import json
import os
from tkinter import filedialog

def load():
    file_path = filedialog.askopenfilename(
        defaultextension=".json",
        filetypes=[("JSON files", "*.json")],
        title="Načíst layout"
    )

    if not file_path:
        print("Uživatel zrušil načítání")
        return None

    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)

    internal_path = os.path.join(data_dir, "festival_settings.json")


    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("Soubor načten z:", file_path)

    with open(internal_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print("Interní kopie uložena do:", internal_path)

    return data[1]

