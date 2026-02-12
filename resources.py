import json
import simpy

class Stall:
    def __init__(self, stall_type, resource, id, x, y):
        self.stall_type = stall_type
        self.resource = resource
        self.id = id
        self.x = x
        self.y = y

def create_resources(env, capacities):
    stalls = {"ENTRANCE_ZONE" : [], "TENT_AREA" : [], "FESTIVAL_AREA" : [], "CHILL_ZONE" : [], "ATRACTION_ZONE" : []}

    with open("data/festival_settings.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        stalls_in_locations = data[0]
        stalls_in_locations = stalls_in_locations["STALLS_BY_LOCATIONS"]
    
    for location in stalls_in_locations:
        objected_stall = []
        i = 1
        stalls_in_locations[location].sort()
        previous_stall = None

        for stall in stalls_in_locations[location]:

            if previous_stall and previous_stall != stall[0]:
                i = 1

            previous_stall = stall[0]
            objected_stall.append(Stall(location + "_" + stall[0], 
                                        simpy.Resource(env, capacity=capacities[stall[0]]),
                                        i,
                                        stall[1],
                                        stall[2]))
            i += 1

        stalls[location] = objected_stall     
