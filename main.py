from gui.gui import get_user_settings
import simpy
import visitors
import bands
import locations
import resources
import simulation_new
import fest
import foods
import drinks


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

festival_env = simpy.Environment()
tent_area = locations.create_tent_area(num_visitors)

stalls = resources.create_resources(festival_env, capacities)
food_stalls_names = resources.find_all_type_stall_at_festival(stalls, "foods")
drink_stalls_names = resources.find_all_type_stall_at_festival(stalls, "drinks")
available_foods = foods.find_all_foods_at_festival(food_stalls_names)
available_soft_drinks, available_alcohol_drinks = drinks.find_all_drinks_at_festival(drink_stalls_names)

people, groups_of_visitors = visitors.create_visitors(num_visitors, income, festival_env, available_foods, available_soft_drinks, available_alcohol_drinks)
lineup, total_price_for_bands = bands.create_lineup(num_days, budget_for_bands, num_bands)
people = bands.add_favorite_bands_to_visitor(people, lineup)

bands.print_lineup(lineup)
visitors.print_visitors(people)

festival = fest.Festival(festival_env, people, groups_of_visitors, num_days, lineup, income, stalls, available_foods, available_soft_drinks, available_alcohol_drinks)
festival_env.process(simulation_new.spawn_groups(festival_env, groups_of_visitors, festival))

festival_env.run(until=(num_days * 1140))
