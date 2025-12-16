import json

def save(zones_data):
    result = {"ACTIONS_BY_LOCATIONS": {},
              "STALLS_BY_LOCATIONS": {},
              "ACTIONS_MOVING": {}}

    location_map = {
        "Vstupní zóna": "ENTRANCE_ZONE",
        "Festivalový areál": "FESTIVAL_AREA",
        "Stanové městečko": "TENT_AREA",
        "Chill zóna": "CHILL_ZONE",
        "Zábavní zóna": "FUN_ZONE"
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

                if "toitoiky" in obj_name:
                    stalls.append("toitoi")
                    action["wc"] = "GO_TO_TOILET"

                elif "sprchy" in obj_name:
                    stalls.append("showers")
                    action["hygiene"] = "GO_TO_SCHOWER"

                elif "pokladna" in obj_name:
                    stalls.append("ticket_booth")
                    action["bracelet_exchange"] = "BRACELET_EXCHANGE"
                    
                elif "podium" in obj_name: 
                    action["band_playing"] = "GO_TO_CONCERT"

                elif any(food_stall.lower() in obj_name for food_stall in food_stalls):
                    
                    if "pizza" in obj_name:
                        stalls.append("pizza_stall")
                    elif "burger" in obj_name:
                        stalls.append("burger_stall")
                    elif "gyros" in obj_name:
                        stalls.append("gyros_stall")
                    elif "grill" in obj_name:
                        stalls.append("grill_stall")
                    elif "bel" in obj_name:
                        stalls.append("belgian_fries_stall")
                    elif "langoš" in obj_name:
                        stalls.append("langos_stall")
                    elif "sladký" in obj_name:
                        stalls.append("sweet_stall")

                    action["hunger"] = "GO_FOR_FOOD"

                elif any(drink_stall.lower() in obj_name for drink_stall in drink_stalls):
                    
                    if "nealko" in obj_name:
                        stalls.append("nonalcohol_stall")
                    if "pivní" in obj_name:
                        stalls.append("beer_stall")
                    if "red bull" in obj_name:
                        stalls.append("redbull_stall")

                    action["thirst"] = "GO_FOR_DRINK"

                if any(atraction.lower() in obj_name for atraction in atractions):
                    action["atraction_desire"] = "GO_TO_ATRACTION"

                result["ACTIONS_BY_LOCATIONS"][location_key] = action
                result["STALLS_BY_LOCATIONS"][location_key] = stalls

            line = instance.get("lines", [])

            if line != []:
                destination = line[0]
                destination = destination["other_zone"]["type"]
                destination = location_map.get(destination, [])
                destination = "GO_TO_" + destination
                result["ACTIONS_MOVING"][location_key] = destination

    with open("data/festival_settings.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

   