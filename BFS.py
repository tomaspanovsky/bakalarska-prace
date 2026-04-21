from data.load_data import load_data
from collections import deque

def resolve_need(type, need, instance, actual_zone=None):
        """Najde akci pro danou potřebu – buď přímo v aktuální zóně, nebo najde nejkratší cestu do zóny, kde to lze splnit."""
        actions_by_locations = load_data("ACTIONS_BY_LOCATIONS")

        if not actual_zone:
            if type == "visitor":
                actual_zone = instance.get_actual_zone()
            
            elif type == "group":
                actual_zone = instance.get_group_actual_zone()


            if actual_zone in ("STAGE_STANDING", "SIGNING_STALL"):
                actual_zone = "FESTIVAL_AREA"

            
        if need in actions_by_locations[actual_zone]:
            return actions_by_locations[actual_zone][need]

        target_zones = []

        for zone_name, actions in actions_by_locations.items():
            if need in actions:
                target_zones.append(zone_name)

        if not target_zones:
            print(f"ERROR: Žádná připojená zóna neumí uspokojit potřebu {need}")
            return None
        
        return BFS(actual_zone, target_zones)

        
def get_zone_from_move_command(move):
    zone = move.replace("GO_TO_", "")
    if "_ENTRY_" in zone:
        zone = zone.split("_ENTRY_")[0]
    return zone.strip()


def find_the_way(actual_zone, target_zone):
    
    return BFS(actual_zone, [target_zone])

def BFS(actual_zone, target_zones):
    actions_moving = load_data("ACTIONS_MOVING")

    queue = deque([(actual_zone, [])])
    visited = set()

    while queue:
        zone, path = queue.popleft()

        if zone in visited:
            continue
        visited.add(zone)

        # Pokud jsme v cílové zóně
        if zone in target_zones:
            return path[0] if path else None

        # Projdi sousedy
        for move in actions_moving.get(zone, []):
            next_zone = get_zone_from_move_command(move)  # STRING
            queue.append((next_zone, path + [move]))

    return None
