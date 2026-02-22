class Festival:
    def __init__(self, env, visitors, groups, num_days, line_up, income, stalls):
        self.env = env
        self.visitor = visitors
        self.groups = groups
        self.num_days = num_days
        self.line_up = line_up
        self.income = income
        self.stalls = stalls
        self.actual_day = 1

class Zone:
    def __init__(self, env, zone_name, foods_stalls, drink_stalls, other_stalls, connections):
        self.env = env
        self.zone_name = zone_name,
        self.foods_stalls = foods_stalls
        self.drink_stalls = drink_stalls
        self.other_stalls = other_stalls