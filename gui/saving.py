import json
import os
import tkinter as tk
from tkinter import filedialog

def save(zones_data):
    result = {"ACTIONS_BY_LOCATIONS": {},
              "STALLS_BY_LOCATIONS": {},
              "ACTIONS_MOVING": {}}

    location_map = {
        "Vstupní zóna": "ENTRANCE_ZONE",
        "Festivalový areál": "FESTIVAL_AREA",
        "Stanové městečko": "TENT_AREA",
        "Chill zóna": "CHILL_ZONE",
        "Zábavní zóna": "FUN_ZONE",
        "Spawn zóna": "SPAWN_ZONE"
    }

    for zone_name, zone_info in zones_data.items():
        print(zone_name, zone_info)

        for instance in zone_info["instances"]:
            location_key = location_map.get(zone_name, zone_name.upper().replace(" ", "_"))
            action = {}
            stalls = []
            traces = []
            
            print("aktuální instance:", instance)

            food_stalls = ["Pizza stánek", "Burger stánek", "Gyros stánek", "Grill stánek", "Bel hranolky stánek", "Langoš stánek", "Sladký stánek"]
            drink_stalls = ["Nealko stánek", "Pivní stánek", "Red Bull stánek", "Stánek s míchanými drinky"]
            atractions = ["Bungee-jumping", "Horská dráha", "Lavice", "Kladivo"]

            # seznam objektů v dané zóně
            for obj in instance.get("objects", []):
                obj_name = obj["object"].lower()
                stall = {"name": None, "x": None, "y": None, "type": None, "cz_name": None}

                if "podium" in obj_name:
                    continue

                if "cammel" in obj_name:
                    stall["name"] = "cigars_tent"

                if "autogramiády" in obj_name:
                    stall["name"] = "signing_stall"

                if "toitoiky" in obj_name:
                    stall["name"] = "toitoi"
                    action["wc"] = "GO_TO_TOILET"

                elif "vstup" in obj_name:
                    stall["name"] = "entry"

                elif "umývárna" in obj_name:
                    stall["name"] = "handwashing_station"
                    action["dirty"] = "WASH"

                elif "stoly" in obj_name:
                    stall["name"] = "tables"
                    action["sitting"] = "SIT"

                elif "bankomat" in obj_name:
                    stall["type"] = "atm"
                    stall["name"] = "atm"
                    action["low_money"] = "WITHDRAW" 

                elif "sprchy" in obj_name:
                    stall["name"] = "showers"
                    action["hygiene"] = "GO_TO_SHOWER"

                elif "merch" in obj_name:
                    stall["name"] = "merch_stall"
                    action["meet_band"] = "GO_TO_SIGNING_SESSION"

                elif "dobíjecí" in obj_name:
                    stall["name"] = "charging_stall"
                    action["phone_dead"] = "CHARGE_PHONE"

                elif "pokladna" in obj_name:
                    stall["name"] = "ticket_booth"
                    action["bracelet_exchange"] = "BRACELET_EXCHANGE"

                elif "louka na stanování" in obj_name:
                    stall["name"] = "meadow_for_living"

                elif "podium" in obj_name: 
                    action["band_playing"] = "GO_TO_CONCERT"

                elif "vodníma" in obj_name:
                    stall["name"] = "water_pipe_stall"

                elif "cigaretový" in obj_name:
                    stall["name"] = "cigaret_stall"
                    action["low_cigars"] = "BUY_CIGARS"

                elif "chill" in obj_name:
                    stall["name"] = "chill_stall"
                    action["tiredness"] = "GO_CHILL"

                elif any(food_stall.lower() in obj_name for food_stall in food_stalls):
                    stall["type"] = "foods"
                    
                    if "pizza" in obj_name:
                        stall["name"] = "pizza_stall"
                    elif "burger" in obj_name:
                        stall["name"] = "burger_stall"
                    elif "gyros" in obj_name:
                        stall["name"] = "gyros_stall"
                    elif "grill" in obj_name:
                        stall["name"] = "grill_stall"
                    elif "bel" in obj_name:
                        stall["name"] = "belgian_fries_stall"
                    elif "langoš" in obj_name:
                        stall["name"] = "langos_stall"
                    elif "sladký" in obj_name:
                        stall["name"] = "sweet_stall"

                    action["hunger"] = "GO_FOR_FOOD"

                elif any(drink_stall.lower() in obj_name for drink_stall in drink_stalls):
                    stall["type"] = "drinks"
                    
                    if "nealko" in obj_name:
                        stall["name"] = "nonalcohol_stall"
                    if "pivní" in obj_name:
                        stall["name"] = "beer_stall"
                    if "red bull" in obj_name:
                        stall["name"] = "redbull_stall"
                    
                    if "míchanými" in obj_name:
                        stall["name"] = "cocktail_stall"

                    action["thirst"] = "GO_FOR_DRINK"

                elif any(atraction.lower() in obj_name for atraction in atractions):

                    if "bungee" in obj_name:
                        stall["name"] = "bungee_jumping"

                    elif "horská" in obj_name:
                        stall["name"] = "roallercoaster"
                    
                    elif "lavice" in obj_name:
                        stall["name"] = "hammer_attraction"
 
                    action["atraction_desire"] = "GO_TO_ATRACTION"

                stall["x"] = obj["x"]
                stall["y"] = obj["y"]
                stall["cz_name"] = obj_name

                if stall["type"] == None:
                    stall["type"] = "Others"

                stalls.append(stall)
                
            result["ACTIONS_BY_LOCATIONS"][location_key] = action
            result["STALLS_BY_LOCATIONS"][location_key] = stalls

            for line in instance.get("lines", []):

                if line != []:
                    other = line["other_zone"]

                    if isinstance(other, dict):
                        destination = other["type"]
                        destination = location_map.get(destination, destination)
                        destination = "GO_TO_" + destination
                        traces.append(destination)

                        result["ACTIONS_MOVING"][location_key] = traces

                        line["other_zone"] = other["type"]

    file_path = filedialog.asksaveasfilename(
    defaultextension=".json",    
    filetypes=[("JSON files", "*.json")],
    title="Uložit soubor jako"
    )

    data = [result, zones_data]
    
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        data_dir = os.path.join(project_root, "data")
        os.makedirs(data_dir, exist_ok=True)

        internal_path = os.path.join(data_dir, "festival_settings.json")

        with open(internal_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print("Soubor uložen do:", file_path)
    else:
        print("Uživatel zrušil uložení")
   