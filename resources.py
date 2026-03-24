import json
import simpy
import locations
import source
import random
import drinks
import attractions
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
        self.from_zone = None
        self.attraction = None

def create_resources(env, capacities, num_visitors, simulation_start_time):
    stalls = {"ENTRANCE_ZONE" : [], "TENT_AREA" : [], "FESTIVAL_AREA" : [], "CHILL_ZONE" : [], "FUN_ZONE" : []}

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
                resource = create_toitois(env, stall, capacities, location)

            elif stall["name"] == "meadow_for_living":
                resource = locations.create_positions(capacities["meadow_for_living"])

            elif stall["name"] == "charging_stall":
                resource = locations.create_positions(capacities["charging_stall_mobile"])

            elif stall["name"] == "stage":
                resource = simpy.Resource(env, capacity=1)
                
            elif stall["name"] == "standing_at_stage":
                resource = []
                
                if num_visitors < 100:
                    cap_sectors = [33,33,34]
                else:
                    cap_sectors = [num_visitors//3] * 3

                    if (cap_sectors[0] + cap_sectors[1] + cap_sectors[2]) != num_visitors:
                        cap_sectors[2] += num_visitors - ((num_visitors // 3) * 3) 

                resource.append(["first_lines", simpy.Resource(env, capacity=cap_sectors[0])])
                resource.append(["middle", simpy.Resource(env, capacity=cap_sectors[1])])
                resource.append(["back", simpy.Resource(env, capacity=cap_sectors[2])])

            elif stall["name"] == "signing_stall":
                resource = [[],[],[],[]]
                resource[0] = simpy.Resource(env, capacity=1)
                resource[1] = simpy.Resource(env, capacity=5)
                resource[2] = simpy.Resource(env, capacity=(capacities[stall["name"]] - 5))
                resource[3] = None

            else:
                resource = simpy.Resource(env, capacity=capacities[stall["name"]])
            
            new_stall = Stall(stall["type"],
                            stall["name"],
                            stall["cz_name"],
                            location,
                            resource,
                            i,
                            stall["x"],
                            stall["y"])
            
            
            if stall["type"] == "attraction":
                attraction_data = source.ATTRACTIONS["attractions"][stall["name"]]
                new_stall.attraction = attractions.Attraction(env, resource, stall["cz_name"], attraction_data, 0.5, 10, simulation_start_time)
                
            i += 1

            objected_stall.append(new_stall)

        stalls[location] = objected_stall
    return stalls

def create_toitois(env, stall, capacities, location):
    urinals = []
    toitois = []
    stalls = []

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
            
    stalls.append(urinals)
    stalls.append(toitois)
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

def is_big_queue_at_stall(visitor, stall):
    return (stall.resource.count + len(stall.resource.queue)) >= visitor.qualities["patience"] * random.uniform(0.5, 1.5)

def find_stall_with_shortest_queue_in_zone(self, festival, type, name=None, stalls=None, alco_nonalco = None, stalls_to_reduce = None):
    "Vrátí stánek s nejmenší frontou v dané zóně, při zadání name vrátí konkrétní stánek s nejmenší frontou"
    
    if not stalls:
        stalls = find_stalls_in_zone(self, festival, type, name, alco_nonalco, stalls_to_reduce=stalls_to_reduce)

    if type == "tent_area" or type == "charging_stall" or type == "standing_at_stage" or type == "signing_stall":
        return stalls

    if stalls == []:
        return None

    if len(stalls) == 1:
        return stalls[0]
    
    else:
        stall_with_least_people = stalls[0]

        least_num_people = len(stall_with_least_people.resource.queue) + stall_with_least_people.resource.count

        for stall in stalls[1:]:
            stall_num_people = len(stall.resource.queue) + stall.resource.count

            if stall_num_people < least_num_people:
                stall_with_least_people = stall
                least_num_people = stall_num_people

        return stall_with_least_people


def find_stalls_in_zone(self, festival, type, name=None, alco_nonalco = None, stalls_to_reduce = None):
    """Vrátí stánky konkrétního typu v dané zóně, případně i stánky daného jména"""

    stalls = []
    
    if type == "entrances" or type == "stage" or type == "signing_stall":
        location = "FESTIVAL_AREA"

    elif self.state["location"] == source.Locations.SIGNING_STALL or self.state["location"] == source.Locations.STAGE_STANDING:
        location = "FESTIVAL_AREA"
    else:
        location = self.state["location"].name

    if stalls_to_reduce:
        where = stalls_to_reduce
    else:
        where = festival.stalls[location]

    for stall in where:

        if stall.stall_type == type:
            if name:
                if stall.stall_name == name:            
                    stalls.append(stall)

            elif alco_nonalco and alco_nonalco == "soft_drinks":
                if drinks.is_soft_drinks_in_stall(stall):
                    stalls.append(stall)
                    
            else:
                stalls.append(stall)

    return stalls

def find_all_type_stall_at_festival(all_stalls, type):
    all_food_stalls_at_festival = []

    for zone_name, stalls in all_stalls.items():
        for stall in stalls:
            if stall.stall_type == type:
                all_food_stalls_at_festival.append(stall.stall_name)
    
    return all_food_stalls_at_festival

def can_afford(self, what):
    if isinstance(what, (int, float)):
        return self.state["money"] > what
    else:
        return self.state["money"] > what["price"]