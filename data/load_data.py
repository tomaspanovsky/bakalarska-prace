import json
import os

def load_data(data_type = None):
    here = os.path.dirname(__file__)
    file_path_settings = os.path.join(here, "festival_settings.json")

    with open(file_path_settings, "r", encoding="utf-8") as f:
        data = json.load(f)

        if data_type:
            return data[0][data_type]
        else:
            return data[1]