import json
import os
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

    # uložíme interní kopii
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)
    internal_path = os.path.join(data_dir, "festival_settings.json")

    with open(internal_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("Interní kopie uložena do:", internal_path)

    return data[1]

def deserialize_zones(serialized):
    zones = {}

    for zone_name, zone_data in serialized.items():
        zones[zone_name] = {
            "multiple": zone_data["multiple"],
            "instances": []
        }

        for inst in zone_data["instances"]:
            original_inst = inst.copy()

            # obnovíme původní strukturu lines
            if "lines" in inst:
                restored_lines = []
                for line in inst["lines"]:
                    restored_line = {
                        "id": line["id"],
                        "other_zone": {
                            "type": line["other_zone"]["zone"]
                        }
                    }

                    # pokud tam byl entry flag, vrátíme ho zpět
                    if "entry" in line:
                        restored_line["other_zone"]["entry"] = line["entry"]

                    restored_lines.append(restored_line)

                original_inst["lines"] = restored_lines

            zones[zone_name]["instances"].append(original_inst)

    return zones