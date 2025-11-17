import json

def save(zones_data):
    result = {"ACTIONS_BY_LOCATIONS": {}}

    location_map = {
        "Vstupní zóna": "ENTRANCE_ZONE",
        "Festivalový areál": "FESTIVAL_AREA",
        "Stanové městečko": "TENT_AREA",
        "Chill zóna": "CHILL_ZONE",
        "Zábavní zóna": "FUN_ZONE"
    }

    for zone_name, zone_info in zones_data.items():
        for instance in zone_info["instances"]:
            location_key = location_map.get(zone_name, zone_name.upper().replace(" ", "_"))
            actions = {}

            food_stalls = ["Pizza stánek", "Burger stánek", "Gyros stánek", "Grill stánek", "Bel hranolky stánek", "Langoš stánek", "Sladký stánek"]


            # seznam objektů v dané zóně
            for obj in instance.get("objects", []):
                obj_name = obj["object"].lower()

                if "toitoiky" in obj_name:
                    actions["wc"] = "GO_TO_TOILET"
                elif "sprchy" in obj_name:
                    actions["hygiene"] = "GO_TO_SCHOWER"
                elif "pokladna" in obj_name:
                    actions["bracelet_exchange"] = "BRACELET_EXCHANGE"
                elif any(food_stall.lower() in obj_name for food_stall in food_stalls):
                    actions["hunger"] = "GO_FOR_FOOD"

            result["ACTIONS_BY_LOCATIONS"][location_key] = actions

    with open("data/festival_layout.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

   