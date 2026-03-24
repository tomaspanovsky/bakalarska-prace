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
            attractions = ["bungee-jumping", "horská dráha", "lavice", "kladivo", "řetizkáč", "skákací hrad"]

            # seznam objektů v dané zóně
            for obj in instance.get("objects", []):
                obj_name = obj["object"].lower()
                stall = {"name": None, "x": None, "y": None, "type": None, "cz_name": None, "from": None}
                stall_extra = None

                if obj["extra"]:
                    obj_extra = obj["extra"]

                    if obj_extra[0]["object"] == "Stání u podia":
                        stall_extra = {"name": "standing_at_stage", "type": "standing_at_stage",  "x": None, "y": None, "cz_name": None, "from": None}
                        action["band_playing"] = "GO_TO_CONCERT"

                if "podium" in obj_name:
                    stall["type"] = "stage"
                    stall["name"] = "stage"
                
                elif obj_name in attractions:

                    stall["type"] = "attraction"

                    match obj_name:
                        case "bungee-jumping":
                            stall["name"] = "bungee_jumping"
                        case "horská dráha":
                            stall["name"] = "roller_coaster"
                        case "lavice":
                            stall["name"] = "bench"
                        case "kladivo":
                            stall["name"] = "hammer"
                        case "řetizkáč":
                            stall["name"] = "carousel"
                        case "skákací hrad":
                            stall["name"] = "jumping_castle"
                        
                    action["attraction_desire"] = "GO_TO_ATTRACTION"
                
                elif "autogramiády" in obj_name:
                    stall["name"] = "signing_stall"
                    stall["type"] = "signing_stall"
                    action["meet_band"] = "GO_TO_SIGNING_SESSION"

                elif "toitoiky" in obj_name:
                    stall["name"] = "toitoi"
                    stall["type"] = "toitoi"
                    action["wc"] = "GO_TO_TOILET"

                elif "vstup" in obj_name:
                    stall["name"] = "entrance"
                    stall["type"] = "entrances"

                elif "umývárna" in obj_name:
                    stall["name"] = "handwashing_station"
                    stall["type"] = "handwashing_station"
                    action["dirty_hand"] = "WASH"
                    action["brushing_teeth"] = "BRUSH_TEETH"

                elif "stoly" in obj_name:
                    stall["name"] = "tables"
                    stall["type"] = "tables"
                    action["sitting"] = "SIT"

                elif "bankomat" in obj_name:
                    stall["type"] = "atm"
                    stall["name"] = "atm"
                    action["low_money"] = "WITHDRAW" 

                elif "sprchy" in obj_name:
                    stall["name"] = "showers"
                    stall["type"] = "showers"
                    action["hygiene"] = "GO_TO_SHOWER"

                elif "merch" in obj_name:
                    stall["name"] = "merch_stall"
                    stall["type"] = "merch_stall"
                    action["want_merch"] = "BUY_MERCH"

                elif "dobíjecí" in obj_name:
                    stall["name"] = "charging_stall"
                    stall["type"] = "charging_stall"
                    action["phone_dead"] = "CHARGE_PHONE"

                elif "pokladna" in obj_name:
                    stall["name"] = "ticket_booth"
                    stall["type"] = "ticket_booth"
                    action["bracelet_exchange"] = "BRACELET_EXCHANGE"

                elif "louka na stanování" in obj_name:
                    stall["name"] = "meadow_for_living"
                    stall["type"] = "tent_area"
                    action["living"] = "PITCH_TENT"
                    action["energy"] = "SLEEP_IN_TENT"

                elif "podium" in obj_name: 
                    action["band_playing"] = "GO_TO_CONCERT"

                elif "vodníma" in obj_name:
                    stall["name"] = "water_pipe_stall"
                    stall["type"] = "water_pipe_stall"
                    stall["action"] = "GO_SMOKE_WATER_PIPE"

                elif "cigaretový" in obj_name:
                    stall["name"] = "cigaret_stall"
                    stall["type"] = "smoking"
                    action["low_cigars"] = "BUY_CIGARS"

                elif "chill" in obj_name:
                    stall["name"] = "chill_stall"
                    stall["type"] = "chill_stall"
                    action["tiredness"] = "GO_CHILL"
                
                elif "výkup" in obj_name:
                    stall["name"] = "cup_return"
                    stall["type"] = "cup_return"
                    action["cup_return"] = "RETURN_CUP"
                
                elif "merch" in obj_name:
                    stall["name"] = "merch"
                    stall["type"] = "merch"
                    action["want_merch"] = "BUY_MERCH"

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
                
                #akce, které jdou uskutečnit v jakékoliv zóně
                action["smoking"] = "SMOKE"

                stall["x"] = obj["x"]
                stall["y"] = obj["y"]
                stall["cz_name"] = obj_name

                if stall["type"] == None:
                    stall["type"] = "Others"

                stalls.append(stall)
                
                if stall_extra:
                    stall_extra["x"] = obj["x"]
                    stall_extra["y"] = obj["y"]
                    stall_extra["cz_name"] = obj["extra"][0]["object"]
                    stalls.append(stall_extra)
                
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
   