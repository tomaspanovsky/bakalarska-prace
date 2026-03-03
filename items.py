class Phone:
    def __init__(self, battery):
        self.battery = battery

    def charging(self):
        self.battery += 1