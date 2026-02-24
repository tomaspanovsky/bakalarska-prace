import json
import simpy
import source
from data.load_data import load_data

class Stall:
    def __init__(self, stall_type, stall_name, stall_cz_name, zone, resource, id, x, y):
        self.stall_type = stall_type
        self.stall_name = stall_name
        self.stall_cz_name = stall_cz_name
        self.zone = zone
        self.resource = resource
        self.id = id
        self.x = x
        self.y = y
        self.queue_length = 0
        self.from_zone = None

def create_resources(env, capacities):
    stalls = {"ENTRANCE_ZONE" : [], "TENT_AREA" : [], "FESTIVAL_AREA" : [], "CHILL_ZONE" : [], "ATRACTION_ZONE" : []}

    stalls_in_locations = load_data("STALLS_BY_LOCATIONS")

    for location in stalls_in_locations:
        objected_stall = []
        i = 1
       
        stalls_in_locations[location].sort(key=get_name)
        previous_stall = None

        for stall in stalls_in_locations[location]:

            if previous_stall and previous_stall != stall["name"]:
                i = 1

            previous_stall = stall["name"]

            if stall["name"] == "toitoi":
                multiple_stall = multiple_resources(env, stall, capacities, location)
                objected_stall.append(Stall(stall["type"],
                                            stall["name"],
                                            stall["cz_name"],
                                            location,
                                            multiple_stall,
                                            i,
                                            stall["x"],
                                            stall["y"]))
            else:
                objected_stall.append(Stall(stall["type"],
                                            stall["name"],
                                            stall["cz_name"],
                                            location,
                                            simpy.Resource(env, capacity=capacities[stall["name"]]),
                                            i,
                                            stall["x"],
                                            stall["y"]))
            i += 1

        stalls[location] = objected_stall
    return stalls

def multiple_resources(env, stall, capacities, location):
    urinals = []
    toitois = []
    stalls = ["toitoi"]

    for i in range(capacities[stall["name"]]):
        name = stall["name"]
        cz_name = stall["cz_name"]

        if stall["name"] == "toitoi" and i < capacities["toitoi"] // 3:
            name = "urinal"
            cz_name = "pisoar"

            urinals.append(Stall(stall["type"],
                            name,
                            cz_name,
                            location,
                            simpy.Resource(env, capacity=1),
                            i,
                            stall["x"],
                            stall["y"]))
        else:
            name = "toitoi"
            cz_name = "toitoi"
            toitois.append(Stall(stall["type"],
                            name,
                            cz_name,
                            location,
                            simpy.Resource(env, capacity=1),
                            i,
                            stall["x"],
                            stall["y"]))
            
    stalls.append(urinals, toitois)
    return stalls

def identify_entrances(stalls):
    zones = load_data()
    entrances = []

    location_map = {
        "Vstupní zóna": "ENTRANCE_ZONE",
        "Festivalový areál": "FESTIVAL_AREA",
        "Stanové městečko": "TENT_AREA",
        "Chill zóna": "CHILL_ZONE",
        "Zábavní zóna": "FUN_ZONE",
        "Spawn zóna": "SPAWN_ZONE"
    }

    for stall in stalls:
        if stall.stall_name == "entrance":
            entrances.append(stall)
    
    for zone_name, zone_data in zones.items():

        for instance in zone_data["instances"]:
            lines = instance.get("lines", [])

            for line in lines:
                other_zone = line.get("other_zone")

                if other_zone == "Festivalový areál":
                    entrances[0].from_zone = location_map[zone_name]
                    del entrances[0]
            

def get_name(stall):
    return stall["name"]

def is_big_queue_at_stall(stall):
    return stall.queue_length >= 10

def find_stall_with_shortest_queue_in_zone(self, festival, type, name=None):
    "Vrátí stánek s nejmenší frontou v dané zóně, při zadání name vrátí konkrétní stánek s nejmenší frontou"
    stalls = find_stalls_in_zone(self, festival, type, name)
    stall_with_shortest_queue = stalls[0]

    for stall in stalls:
        if stall.queue_length < stall_with_shortest_queue.queue_length:
            stall_with_shortest_queue = stall

    return stall_with_shortest_queue


def find_stalls_in_zone(self, festival, type, name=None):
    """Vrátí stánky konkrétního typu v dané zóně, případně i stánky daného jména"""

    stalls = []
    
    if type == "entrances":
        location = "FESTIVAL_AREA"
    else:
        location = self.state["location"].name

    for stall in festival.stalls[location]:
        if stall.stall_type == type:
            if name:
                if stall.stall_name == name:            
                    stalls.append(stall)
            else:
                stalls.append(stall)
    return stalls

def is_type_stalls_in_actual_zone(self, festival, type):
    """Vrátí True, pokud je hledaný typ stánku v zóně"""

    for stall in festival.stalls[self.state["location"].name]:

        if type == "toitoi":
            if stall[0] == "toitoi":
                return True
            
        elif stall.stall_type == type:
            return True
    
    return False

def find_all_type_stall_at_festival(all_stalls, type):
    all_food_stalls_at_festival = []

    for zone_name, stalls in all_stalls.items():
        for stall in stalls:
            if stall.stall_type == type:
                all_food_stalls_at_festival.append(stall.stall_name)
    
    return all_food_stalls_at_festival

def find_nearest_zone_with_stall(self, need):
    connections = load_data("ACTIONS_MOVING")
    possible_actions = load_data("ACTIONS_BY_LOCATIONS")
    actual_location = self.state["location"]
    possibilites = connections[actual_location.name]

    for moving in possibilites:
        zone = moving.split("GO_TO_")[1]

        if need in possible_actions[zone].keys():
            return moving
    
    print("Error: Není připojená zona s daným požadavkem")
    return None

def can_afford(self, what):
    return self.state["money"] > what["price"]