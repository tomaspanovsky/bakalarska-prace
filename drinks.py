import source
import random
import resources
from data.load_data import load_data

def find_all_drinks_at_festival(drink_stalls_at_festival):
    drinks = []
    alcohol_drinks = []
    soft_drinks = []

    all_alcohol_drinks = source.alcohol
    all_soft_drinks = source.soft_drinks

    for stall_name in drink_stalls_at_festival:
        
        if stall_name in source.drink_stalls:
            drinks.extend(source.drink_stalls[stall_name])

    soft_drinks = list(set(drinks) & set(all_soft_drinks))
    alcohol_drinks = list(set(drinks) & set(all_alcohol_drinks))
    return soft_drinks, alcohol_drinks

def is_my_favourite_drink_in_actual_zone(self, festival, drink_type):

    stalls = resources.find_stalls_in_zone(self, festival, "drinks")
    
    if drink_type == "soft_drink":
        pref_drink = self.preference["favourite_soft_drink"]

    elif drink_type == "alcohol":
        pref_drink = self.preference["favourite_alcohol"]

    for stall in stalls:

        is_there = is_drink_in_stall(stall, pref_drink)

        if is_there:
            return True, stall
        
    return False, None

def is_drink_in_stall(stall, drink):
    drinks_in_stall = source.drink_stalls[stall.stall_name]

    if drink in drinks_in_stall:
        return True
    else:
        return False

def find_drink_stall_with_shortest_queue_in_zone(self, festival):
    return resources.find_stall_with_shortest_queue_in_zone(self, festival, "drinks")

def choose_random_drink_from_stall(self, stall, drink_type):
    drinks = source.stalls[stall.stall_name]

    if drink_type == "soft_drinks":
        drink_type = source.soft_drinks
    elif drink_type == "alcohol":
        drink_type = source.alcohol
    elif drink_type == "beers":
        drink_type = source.beers
    elif drink_type == "hard_alcohol":
        drink_type = source.hard_alcohol
    elif drink_type == "cocktails":
        drink_type = source.cocktails

    drinks = list(set(drinks) & set(drink_type))
    
    i = 1
    while i <= 3:
        drinks = random.choice(drinks)
        if resources.can_afford(self, source.drinks[drinks]):
            return drinks
        i += 1
    return None

def choose_random_drink_from_actual_zone(self, festival, drink_type):
    available_drinks = []

    if drink_type == "soft_drinks":
        drink_type = source.soft_drinks
    elif drink_type == "alcohol":
        drink_type = source.alcohol
    elif drink_type == "beers":
        drink_type = source.beers
    elif drink_type == "hard_alcohol":
        drink_type = source.hard_alcohol
    elif drink_type == "cocktails":
        drink_type = source.cocktails
    
    stalls = resources.find_stalls_in_zone(self, festival, "drinks")

    for stall in stalls:

        drinks_in_stall = source.drink_stalls[stall.stall_name]
        available_drinks.extend(drinks_in_stall)

    drinks = list(set(available_drinks) & set(drink_type))

    i = 1
    while i <= 3:
        drink = random.choice(drinks)

        if resources.can_afford(self, source.drinks[drink]):
            return drink
        i += 1
    return None

def what_kind_of_alcohol_is_in_actual_zone(self, festival):
    types_stalls = {"favourite_alcohol": False, "beers": False, "hard_alcohol": False, "cocktails": False}

    stalls = resources.find_stalls_in_zone(self, festival, "drinks")

    if is_my_favourite_drink_in_actual_zone(self, festival, "alcohol"):
        types_stalls["favourite_alcohol"] = True

    for stall in stalls:

        if stall.stall_name == "beer_stall":
            types_stalls["beers"] = True
        elif stall.stall_name == "redbull_stall":
            types_stalls["hard_alcohol"] = True
        elif stall.stall_name == "cocktail_stall":
            types_stalls["cocktails"] = True

    return types_stalls
