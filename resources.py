import simpy

#promene, udávající počet resources
num_entries = 5
num_ticket_booth = 3

#pocty_wc
num_toitoi_festival_area = 10
num_toitoi_festival_area_urinal = 10
num_toitoi_tent_area = 10
num_toitoi_tent_area_urinal = 10
num_toitoi_entrance_zone = 10
num_toitoi_entrance_zone_urinal = 10
num_toitoi_chill_zone = 10
num_toitoi_chill_zone_urinal = 10

num_shower_units = 2

#preddefinovani resources

#lokace
tent_area = None
ticket_booths = None
entrances = None

#wc
toitoi_festival_area = None
toitoi_festival_area_urinal = None
toitoi_tent_area = None
toitoi_tent_area_urinal = None
toitoi_entrance_zone = None
toitoi_entrance_zone_urinal = None
toitoi_chill_zone = None
toitoi_chill_zone_urinal = None

#sprchy
showers = None

#jídlo
stall_entrance_zone_pizza = None
stall_entrance_zone_burger = None
stall_entrance_zone_gyros = None
stall_entrance_zone_grill = None
stall_entrance_zone_fries = None
stall_entrance_zone_langos = None
stall_entrance_zone_sweet = None

# Resources
def create_resources(environment, tent_area_actual):
    global  tent_area, ticket_booths, entrances, toitoi_festival_area, toitoi_festival_area_urinal, toitoi_tent_area, toitoi_tent_area_urinal,\
            toitoi_entrance_zone, toitoi_entrance_zone_urinal, toitoi_chill_zone, toitoi_chill_zone_urinal, showers,\
            stall_entrance_zone_pizza, stall_entrance_zone_burger, stall_entrance_zone_gyros, stall_entrance_zone_grill, stall_entrance_zone_fries, \
            stall_entrance_zone_langos, stall_entrance_zone_sweet
    
    tent_area = tent_area_actual
    ticket_booths = [simpy.Resource(environment, capacity=1) for _ in range(num_ticket_booth)]
    entrances = [simpy.Resource(environment, capacity=1) for _ in range(num_entries)]

    #wc
    toitoi_festival_area = [simpy.Resource(environment, capacity=1) for _ in range(num_toitoi_festival_area)]
    toitoi_festival_area_urinal = [simpy.Resource(environment, capacity=1) for _ in range(num_toitoi_festival_area_urinal)]
    toitoi_tent_area = [simpy.Resource(environment, capacity=1) for _ in range(num_toitoi_tent_area)]
    toitoi_tent_area_urinal = [simpy.Resource(environment, capacity=1) for _ in range(num_toitoi_tent_area_urinal)]
    toitoi_entrance_zone = [simpy.Resource(environment, capacity=1) for _ in range(num_toitoi_entrance_zone)]
    toitoi_entrance_zone_urinal = [simpy.Resource(environment, capacity=1) for _ in range(num_toitoi_entrance_zone_urinal)]
    toitoi_chill_zone = [simpy.Resource(environment, capacity=1) for _ in range(num_toitoi_chill_zone)]
    toitoi_chill_zone_urinal = [simpy.Resource(environment, capacity=1) for _ in range(num_toitoi_chill_zone_urinal)]

    #sprchy
    showers = [simpy.Resource(environment, capacity=5) for _ in range(num_shower_units)]

    #jídlo
    stall_entrance_zone_pizza = simpy.Resource(environment, capacity=1)
    stall_entrance_zone_burger = simpy.Resource(environment, capacity=1)
    stall_entrance_zone_gyros = simpy.Resource(environment, capacity=1)
    stall_entrance_zone_grill = simpy.Resource(environment, capacity=1)
    stall_entrance_zone_fries = simpy.Resource(environment, capacity=1)
    stall_entrance_zone_langos = simpy.Resource(environment, capacity=1)
    stall_entrance_zone_sweet = simpy.Resource(environment, capacity=1)