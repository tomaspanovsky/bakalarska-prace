import times
from outputs.code import logs

class Attraction:
    def __init__(self, env, resource, cz_name, attraction_data, min_fill, max_wait, simulation_start_time):
        self.env = env
        self.cz_name = cz_name
        self.resource = resource
        self.attraction_data = attraction_data
        self.min_fill = min_fill
        self.max_wait = max_wait
        self.simulation_start_time = simulation_start_time

        self.current_riders = 0
        self.ride_start = env.event()
        self.ride_end = env.event()

        env.process(self.run())

    def run(self):
        while True:
            start_wait = self.env.now


            while True:
                filled_ratio = self.current_riders / self.resource.capacity

                if filled_ratio >= 1:
                    break

                if filled_ratio >= self.min_fill and (self.env.now - start_wait) >= (self.max_wait / 2):
                    break

                if self.env.now - start_wait >= self.max_wait and self.current_riders > 0:
                    break

                yield self.env.timeout(1)


            self.ride_start.succeed()
            self.ride_start = self.env.event()

            message = f"ČAS {times.get_real_time(self.env, self.simulation_start_time)}: Atrakce {self.cz_name} zahajuje jízdu s počtem {self.current_riders} návštěvníků."
            print(message)
            logs.log_message(message)
            
            yield self.env.timeout(self.attraction_data["duration"])


            self.ride_end.succeed()
            self.ride_end = self.env.event()

            message = f"ČAS {times.get_real_time(self.env, self.simulation_start_time)}: Atrakce {self.cz_name} ukončila jízdu."
            print(message)
            logs.log_message(message)
    
    def get_current_riders(self):
        return self.current_riders
    
    def add_rider(self):
        self.current_riders += 1

    def sub_rider(self):
        self.current_riders -= 1

    def get_ride_start(self):
        return self.ride_start

    def get_ride_end(self):
        return self.ride_end