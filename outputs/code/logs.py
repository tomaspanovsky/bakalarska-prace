import json
from enum import Enum

visitors_logs = {}
all_messages = []
stalls_stats = {}

class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        return json.JSONEncoder.default(self, obj)

def add_visitor_to_logs(visitor):
    name = visitor.get_name()

    visitors_logs[name] = {
        "data": visitor.get_data(),
        "experience": []
    }

def log_visitor(visitor, message):
    name = visitor.get_name()
    visitors_logs[name]["experience"].append(message)
    log_message(message)

def log_message(message):
    all_messages.append(message)

def add_stalls_to_logs(stalls):

    for zone, zone_stalls in stalls.items():
        stalls_in_zone = []

        for stall in zone_stalls:
            
            stall_data = {"id": stall.id, "stall_name": stall.stall_name, "stall_cz_name": stall.stall_cz_name, "max_queue_length": 0, "max_wait_time": 0}
            stalls_in_zone.append(stall_data)

        stalls_stats[zone] = stalls_in_zone

def log_stalls_stats(stall):
    pass


def save_logs(festival):

    with open("outputs/visitors_expiriance.json", "w", encoding="utf-8") as f:
        json.dump(visitors_logs, f, indent=4, ensure_ascii=False, cls=EnumEncoder)

    with open("outputs/all_messages.json", "w", encoding="utf-8") as f:
        json.dump(all_messages, f, indent=4, ensure_ascii=False, cls=EnumEncoder)

    with open("outputs/lineup.json", "w", encoding="utf-8") as f:
        json.dump(festival.get_lineup(), f, indent=4, ensure_ascii=False, cls=EnumEncoder)

    with open("outputs/stalls_stats", "w", encoding="utf-8") as f:
        json.dump(stalls_stats, f, indent=4, ensure_ascii=False, cls=EnumEncoder)