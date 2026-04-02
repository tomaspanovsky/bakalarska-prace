def create_simulation_state(stalls_by_zone):
    simulation_state = {
        "time": 0,
        "zones": {}
    }

    for zone_name, stalls in stalls_by_zone.items():
        simulation_state["zones"][zone_name] = {
            "people": 0,
            "stalls": {}
        }

        for stall in stalls:
            simulation_state["zones"][zone_name]["stalls"][stall.stall_name] = {"id": stall.id, "people": 0}

    return simulation_state


def simulation_step(env):
    try:
        env.step()
    except StopIteration:
        print("Simulace skončila")
    
def simulation_timeout(env):
    yield env.timeout()