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
            drink_stalls = ["Nealko stánek", "Pivní stánek", "Red Bull stánek"]
            atractions = ["Bungee-jumping", "Horská dráha", "Lavice", "Kladivo"]

            # seznam objektů v dané zóně
            for obj in instance.get("objects", []):
                obj_name = obj["object"].lower()
                stall = []

                if "toitoiky" in obj_name:
                    stall.append("toitoi")
                    action["wc"] = "GO_TO_TOILET"

                elif "umývárna" in obj_name:
                    stall.append("handwashing_station")
                    action["dirty"] = "WASH"

                elif "stoly" in obj_name:
                    stall.append("tables")
                    action["sitting"] = "SIT"

                elif "bankomat" in obj_name:
                    stall.append("atm")
                    action["low_money"] = "WITHDRAW" 

                elif "sprchy" in obj_name:
                    stall.append("showers")
                    action["hygiene"] = "GO_TO_SHOWER"

                elif "merch" in obj_name:
                    stall.append("merch_stall")
                    action["meet_band"] = "GO_TO_SIGNING_SESSION"

                elif "dobíjecí" in obj_name:
                    stall.append("charging_stall")
                    action["phone_dead"] = "CHARGE_PHONE"

                elif "pokladna" in obj_name:
                    stall.append("ticket_booth")
                    action["bracelet_exchange"] = "BRACELET_EXCHANGE"

                elif "louka_na_stanovani" in obj_name:
                    stall.append("meadow for living")

                elif "podium" in obj_name: 
                    action["band_playing"] = "GO_TO_CONCERT"

                elif "vodníma" in obj_name:
                    stall.append("water_pipe_stall")

                elif "cigaretový" in obj_name:
                    stall.append("cigaret_stall")
                    action["low_cigars"] = "BUY_CIGARS"

                elif "chill" in obj_name:
                    stall.append("chill_stall")
                    action["tiredness"] = "GO_CHILL"

                elif any(food_stall.lower() in obj_name for food_stall in food_stalls):
                    
                    if "pizza" in obj_name:
                        stall.append("pizza_stall")
                    elif "burger" in obj_name:
                        stall.append("burger_stall")
                    elif "gyros" in obj_name:
                        stall.append("gyros_stall")
                    elif "grill" in obj_name:
                        stall.append("grill_stall")
                    elif "bel" in obj_name:
                        stall.append("belgian_fries_stall")
                    elif "langoš" in obj_name:
                        stall.append("langos_stall")
                    elif "sladký" in obj_name:
                        stall.append("sweet_stall")

                    action["hunger"] = "GO_FOR_FOOD"

                elif any(drink_stall.lower() in obj_name for drink_stall in drink_stalls):
                    
                    if "nealko" in obj_name:
                        stall.append("nonalcohol_stall")
                    if "pivní" in obj_name:
                        stall.append("beer_stall")
                    if "red bull" in obj_name:
                        stall.append("redbull_stall")

                    action["thirst"] = "GO_FOR_DRINK"

                if any(atraction.lower() in obj_name for atraction in atractions):

                    if "bungee" in obj_name:
                        stall.append("bungee_jumping")

                    elif "horská" in obj_name:
                        stall.append("roallercoaster")
                    
                    elif "lavice" in obj_name:
                        stall.append("hammer_attraction")
 
                    action["atraction_desire"] = "GO_TO_ATRACTION"

                stall.append(obj["x"])
                stall.append(obj["y"])
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
   