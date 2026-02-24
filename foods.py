import source
import random
import resources
from data.load_data import load_data

def find_all_foods_at_festival(food_stalls_at_festival):
    foods = []

    for stall_name in food_stalls_at_festival:
        
        if stall_name in source.food_stalls:
            foods.extend(source.food_stalls[stall_name])

    return foods


def choose_food_with_great_satiety_in_actual_zone(self, festival):
    
    best_food = None
    best_satiety = 0

    stalls = resources.find_stalls_in_zone(self, festival, "foods")

    for stall in stalls:

        foods_in_stall = source.stalls[stall.stall_name]
        random.shuffle(foods_in_stall)

        for food in foods_in_stall:
            satiety = source.foods[food]["satiety"]

            if satiety > best_satiety:
                if resources.can_afford(self, source.foods[food]):
                    best_satiety = satiety
                    best_food = food

    return best_food

def is_my_favourite_food_in_actual_zone(self, festival):

    stalls = resources.find_stalls_in_zone(self, festival, "foods")

    for stall in stalls:

        is_there = is_food_in_stall(stall, self.preference["favourite_food"])

        if is_there:
            return True, stall
        
    return False, None

def is_food_in_stall(stall, food):
    foods_in_stall = source.stalls[stall.stall_name]

    if food in foods_in_stall:
        return True
    else:
        return False
    
def choose_random_food_from_actual_zone(self, festival):
    available_foods = []
    
    stalls = resources.find_stalls_in_zone(self, festival, "foods")
    for stall in stalls:

        foods_in_stall = source.stalls[stall.stall_name]
        available_foods.extend(foods_in_stall)

    i = 1
    while i <= 3:
        food = random.choice(available_foods)

        if resources.can_afford(self, source.foods[food]):
            return food
        i += 1
    return None

def find_food_stall_with_shortest_queue_in_zone(self, festival):
    return resources.find_stall_with_shortest_queue_in_zone(self, festival, "foods")

def choose_random_food_from_stall(self, stall):
    foods = source.stalls[stall.stall_name]

    i = 1
    while i <= 3:
        food = random.choice(foods)
        if resources.can_afford(self, source.foods[food]):
            return food
        i += 1
    return None

        