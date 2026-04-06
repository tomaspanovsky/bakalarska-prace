class SimulationController:
    def __init__(self, festival_env, festival):
        self.festival_env = festival_env
        self.festival = festival
        self.shown_logs = 0
        self.simulation_state = create_simulation_state(self.festival.get_stalls())

    def move_forward_by_time(self, time):
        stop_time = self.festival_env.now + time

        while self.festival_env.now < stop_time:
            try:
                self.festival_env.step()
            except StopIteration:
                break

    def move_forward_to_next_event(self):
        try:
            self.festival_env.step()
        except StopIteration:
            pass
    
    def increase_shown_logs(self, number):
        self.shown_logs += number

    def get_number_of_shown_logs(self):
        return self.shown_logs

    def get_festival(self):
        return self.festival

    def get_simulation_state(self):
        return self.simulation_state
    
    def get_actual_time(self):
        return self.festival_env.now    
    
    
def create_simulation_state(stalls_by_zone):
    simulation_state = {
        "time": 0,
        "zones": {}
    }

    for zone_name, stalls in stalls_by_zone.items():
        simulation_state["zones"][zone_name] = {
            "num_people_in_zone": 0,
            "stalls": {}
        }

        for stall in stalls:
            print(stall.stall_name)
            simulation_state["zones"][zone_name]["stalls"][stall.get_name()] = {"id": stall.id, "num_people_served": 0, "num_people_in_queue": 0, "capacity": stall.get_capacity()}

    return simulation_state