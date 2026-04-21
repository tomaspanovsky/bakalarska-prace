import json
import os
import source
from tkinter import filedialog

def load(auto=False):
    """Načte uložený layout a vrátí zones_data."""
    if auto:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        data_dir = os.path.join(project_root, "data")
        internal_path = os.path.join(data_dir, "festival_settings.json")

        if not os.path.exists(internal_path):
            print("Nenalezeno žádné předchozí nastavení v:", internal_path)
            return None

        with open(internal_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        print("Automaticky načteno z:", internal_path)
        return data[1]

    file_path = filedialog.askopenfilename(
        defaultextension=".json",
        filetypes=[("JSON files", "*.json")],
        title="Načíst layout"
    )

    if not file_path:
        print("Uživatel zrušil načítání")
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("Soubor načten z:", file_path)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)
    internal_path = os.path.join(data_dir, "festival_settings.json")

    with open(internal_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("Interní kopie uložena do:", internal_path)

    return data[1]

def load_merch_settings():
    path = source.file_path_merch
    with open(path, "r", encoding="utf-8") as f:
        merch_data = json.load(f)
        return merch_data["bands_merch"], merch_data["festival_merch"]

def load_capacities_settings():
    path = source.file_path_capacities

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
    
def load_fest_prices_settings():
    path = source.file_path_fest_prices

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
    
def load_time_settings():
    path = source.file_path_time_settings

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)