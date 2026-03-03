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
import random
import source

#promene, ktere budou vstupní parametry
settings, capacities = get_user_settings()

if not settings:
    print("Uživatel ukončil program")
    exit()

num_visitors = settings["num_visitors"]
num_days = settings["num_days"]
budget_for_bands = settings["budget_for_bands"]
num_bands = settings["num_bands"]
pre_sale_price = settings["pre_sale_price"]
on_site_price = settings["on_site_price"]
camping_area_price = settings["camping_area_price"]
plastic_cup_price = 80 #dodělat v gui
charging_phone_price = 80 #dodělat v gui
festival_env = simpy.Environment()

capacities["entrance"] = 4
stalls = resources.create_resources(festival_env, capacities)
resources.identify_entrances(stalls["FESTIVAL_AREA"])
food_stalls_names = resources.find_all_type_stall_at_festival(stalls, "foods")
drink_stalls_names = resources.find_all_type_stall_at_festival(stalls, "drinks")
available_foods = foods.find_all_foods_at_festival(food_stalls_names)
available_soft_drinks, available_alcohol_drinks = drinks.find_all_drinks_at_festival(drink_stalls_names)

people, groups_of_visitors, income = visitors.create_visitors(num_visitors, festival_env, available_foods, available_soft_drinks, available_alcohol_drinks, on_site_price, pre_sale_price)
lineup, total_price_for_bands = bands.create_lineup(num_days, budget_for_bands, num_bands)
people = bands.add_favorite_bands_to_visitor(people, lineup)

bands.print_lineup(lineup)
visitors.print_visitors(people)

prices = {"pre_sale_price": pre_sale_price, "on_site_price": on_site_price, "camping_area_price": camping_area_price, "plastic_cup_price": plastic_cup_price, "charging_phone_price" : charging_phone_price}

festival = fest.Festival(festival_env, people, groups_of_visitors, num_days, lineup, income, stalls, prices, random.choice(list(source.Weather)))
festival_env.process(simulation_new.spawn_groups(festival_env, groups_of_visitors, festival))

festival_env.run(until=(num_days * 1140))
