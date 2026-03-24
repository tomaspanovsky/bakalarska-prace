from gui.gui import get_user_settings
import simpy
import visitors
import bands
import resources
import simulation
import fest
import foods
import drinks
import random
import source
import times
from outputs.code import logs

#promene, ktere budou vstupní parametry
settings = get_user_settings()

if not settings:
    print("Uživatel ukončil program")
    exit()

num_visitors = settings["num_visitors"]
num_days = settings["num_days"]
budget_for_bands = settings["budget_for_bands"]
num_bands = settings["num_bands"]
prices = settings["prices"]
festival_times = {"simulation_start_time": times.format_time_string_to_mins(settings["simulation_start_time"]), "headliner_time" : settings["headliner_time"], "band_time" : settings["band_time"], "first_show_starts" : times.format_time_string_to_mins(settings["first_show_starts"]), "last_show_ends" : times.format_time_string_to_mins(settings["last_show_ends"]), "signing_time" : int(settings["signing_time"])}
merch = settings["merch"]
capacities = settings["capacities"]

festival_env = simpy.Environment()
capacities["entrance"] = 4
stalls = resources.create_resources(festival_env, capacities, num_visitors, festival_times["simulation_start_time"])
logs.add_stalls_to_logs(stalls)
resources.identify_entrances(stalls["FESTIVAL_AREA"])

food_stalls_names = resources.find_all_type_stall_at_festival(stalls, "foods")
drink_stalls_names = resources.find_all_type_stall_at_festival(stalls, "drinks")
available_foods = foods.find_all_foods_at_festival(food_stalls_names)
available_soft_drinks, available_alcohol_drinks = drinks.find_all_drinks_at_festival(drink_stalls_names)

people, groups_of_visitors, income = visitors.create_visitors(num_visitors, festival_env, available_foods, available_soft_drinks, available_alcohol_drinks, prices["on_site_price"], prices["pre_sale_price"])
lineup, total_price_for_bands = bands.create_lineup(num_days, budget_for_bands, num_bands)
people = bands.add_favorite_bands_to_visitor(people, lineup)
festival = fest.Festival(festival_env, people, groups_of_visitors, num_days, lineup, income, stalls, prices, festival_times, random.choice(list(source.Weather)), merch)
lineup = bands.create_schedule(lineup, festival)
merch = bands.create_merch(festival)
festival.set_merch(merch)

stage = resources.find_stalls_in_zone(festival_env, festival, "stage")
signing_stall = resources.find_stalls_in_zone(festival_env, festival, "signing_stall")
bands.set_bands(festival_env, lineup, stage, signing_stall[0], festival)


bands.print_lineup(lineup)
visitors.print_visitors(people)

festival_env.process(simulation.spawn_groups(festival_env, groups_of_visitors, festival))

logs.log_message("START SIMULACE")
logs.log_message("1. DEN:")

festival_env.run(until=(num_days * 1440))

logs.log_message("SIMULACE UKONČENA")
logs.save_logs(festival)
