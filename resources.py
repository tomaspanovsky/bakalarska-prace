import json
import simpy

class Stall:
    def __init__(self, stall_type, resource, id):
        self.stall_type = stall_type
        self.resource = resource
        self.id = id

def create_resources(env, capacities):

    with open("data/festival_settings.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        data = data[0]
        data = data["STALLS_BY_LOCATIONS"]
    
    for location in data:
        objected_stall = []
        i = 1
        data[location].sort()
        previous_stall = None

        for stall in data[location]:

            if previous_stall and previous_stall != stall:
                i = 1

            previous_stall = stall

            objected_stall.append(Stall(location + "_" + stall, 
                                        simpy.Resource(env, capacity=capacities[stall]),
                                        i))
            i += 1    
"""
capacities = {}
capacities["pizza_stall"] = 2
capacities["burger_stall"] = 2
capacities["gyros_stall"] = 2
capacities["grill_stall"] = 2
capacities["belgian_fries_stall"] = 2
capacities["langos_stall"] = 2
capacities["sweet_stall"] = 2
capacities["ticket_booth"] = 2
capacities["toitoi"] = 2
capacities["handwashing_station"] = 2
capacities["tables"] = 2
capacities["standing"] = 2
capacities["merch_stall"] = 2
capacities["sigining_stall"] = 2
capacities["charging_stall"] = 2
capacities["charging_stall_mobile"] = 2
capacities["showers"] = 2
capacities["tents"] = 2
capacities["cigars_tent"] = 2
capacities["water_pipe_stall"] = 2
capacities["chill_stall"] = 2
capacities["bungee_jumping"] = 2
capacities["roallercoaster"] = 2
capacities["bench_attraction"] = 2
capacities["hammer_attraction"] = 2
capacities["nonalcohol_stall"] = 2
capacities["beer_stall"] = 2
capacities["redbull_stall"] = 2
capacities["atm"] = 1

env = simpy.Environment()
create_resources(env, capacities)
"""