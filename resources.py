import json

with open("data/festival_settings.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    data = data[0]
    data = data["STALLS_BY_LOCATIONS"]

def create_resources(env, capacities):
    pass