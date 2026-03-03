class Festival:
    def __init__(self, env, visitors, groups, num_days, line_up, income, stalls, prices, weather):
        self.env = env
        self.visitor = visitors
        self.groups = groups
        self.num_days = num_days
        self.line_up = line_up
        self.income = income
        self.stalls = stalls
        self.prices = prices
        self.weather = weather
        self.actual_day = 1
        self.charging_phones = []

    def add_phone(self, phone):
        self.charging_phones.append(phone)
    
    def get_price(self, price_of_what):
        return self.prices[price_of_what]