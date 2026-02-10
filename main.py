from gui.gui import get_user_settings
import simpy
import visitors
import bands
import locations
import resources_zaloha
import simulation


#promene, ktere budou vstupní parametry
income = 0
settings, capacities = get_user_settings()

if not settings:
    print("Uživatel ukončil program")
    exit()

num_visitors = settings['num_visitors']
num_days = settings['num_days']
budget_for_bands = settings['budget_for_bands']
num_bands = settings['num_bands']

festival = simpy.Environment()
tent_area = locations.create_tent_area(num_visitors)
resources_zaloha.create_resources(festival, tent_area)
people, groups_of_visitors = visitors.create_visitors(num_visitors, income, festival)
lineup, total_price_for_bands = bands.create_lineup(num_days, budget_for_bands, num_bands)
people = bands.add_favorite_bands_to_visitor(people, lineup)

bands.print_lineup(lineup)
visitors.print_visitors(people)

festival.process(simulation.spawn_groups(festival, groups_of_visitors))

festival.run(until=(num_days * 1140))
