from outputs.code import logs

class Festival:
    def __init__(self, env, visitors, groups, num_days, line_up, income, stalls, prices, times, weather, merch):
        self.env = env
        self.visitors = visitors
        self.groups = groups
        self.num_days = num_days
        self.line_up = line_up
        self.income = income
        self.stalls = stalls
        self.prices = prices
        self.times = times
        self.weather = weather
        self.actual_day = 1
        self.merch = merch
        self.charging_phones = []
        self.pause_between_shows = None

    def add_phone(self, phone):
        self.charging_phones.append(phone)
    
    def get_price(self, price_of_what):
        return self.prices[price_of_what]
    
    def get_charging_phones(self):
        return self.charging_phones

    def get_income(self):
        return self.income
    
    def add_income(self, income):
        self.income += income

    def get_start_time(self):
        return self.times["simulation_start_time"]
    
    def get_time(self, time_of_what):
        return self.times[time_of_what]
    
    def set_pause_between_shows(self, pause):
        self.pause_between_shows = pause

    def get_pause(self):
        return self.pause_between_shows
    
    def get_lineup(self):
        return self.line_up
    
    def get_actual_day(self):
        return self.actual_day
    
    def next_day(self):
        self.actual_day += 1
        logs.log_message(f"{self.actual_day}. DEN:")
    
    def get_merch(self):
        return self.merch
    
    def set_merch(self, merch):
        self.merch = merch

    def get_stalls(self):
        return self.stalls

    def get_festival_length(self):
        return self.num_days
    
    def get_attractions(self):
        attraction_stalls = []
        for stall in self.stalls["FUN_ZONE"]:
            if stall.stall_type == "attraction":
                attraction_stalls.append(stall)

        return attraction_stalls
    
    def get_num_visitors(self):
        return len(self.visitors)