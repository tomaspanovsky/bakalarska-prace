import gui.gui as gui
from outputs.code import logs

class SimulationController:
    def __init__(self, festival_env, festival):
        self.festival_env = festival_env
        self.festival = festival
        self.shown_logs = 0
        self.simulation_state = create_simulation_state(festival.get_stalls())
        self.auto_mode = False
        self.loaded = False
        self.simulation_end_time = festival.get_num_days() * 1440

    def set_is_loaded(self):
        self.is_loaded = True

    def set_is_not_loaded(self):
        self.loaded = False

    def get_is_loaded(self):
        return self.loaded
        
    def move_forward_by_time(self, time):
        stop_time = self.festival_env.now + time

        while self.festival_env.now < stop_time:
            if self.festival_env.now < self.simulation_end_time:
                self.festival_env.step()
            else:
                logs.log_message("Simulace úspěšně dokončena.")


    def start_smooth_simulation(self):
        self.auto_mode = True

    def stop_smooth_simulation(self):
        self.auto_mode = False

    def get_auto_mode_state(self):
        return self.auto_mode
    
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

    def get_env(self):
        return self.festival_env
    
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
            stall_name = stall.get_name()

            if stall_name not in simulation_state["zones"][zone_name]["stalls"]:
                simulation_state["zones"][zone_name]["stalls"][stall_name] = []

            if stall_name == "standing_at_stage":
               
               simulation_state["zones"][zone_name]["stalls"][stall_name].append({
                "id": stall.get_id(),
                "cz_name": stall.get_cz_name(),
                "num_people_served": 0,
                "num_people_in_first_lines": 0,
                "num_people_in_the_middle": 0,
                "num_people_in_back": 0,
                "capacity": stall.get_capacity()
            })

            else:
                simulation_state["zones"][zone_name]["stalls"][stall_name].append({
                    "id": stall.get_id(),
                    "cz_name": stall.get_cz_name(),
                    "num_people_served": 0,
                    "num_people_in_queue": 0,
                    "capacity": stall.get_capacity()
                })

    return simulation_state