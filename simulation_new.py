import simpy
import random
import source
import resources
import foods
import drinks
from data.load_data import load_data
from collections import deque
global income

num_entrance = 5
num_booths = 3
occupied = [0] * num_entrance
ticket_booths_occupied = [0] * num_booths
cena_listku_predprodej = 1000
on_site_ticket_price = cena_listku_predprodej + 200
cena_stanoveho_mestecka = 200
income = 0

class Group:
    def __init__(self, festival, members, type, mode): #typ = rodina/skupina/jednotlivec, rezim(mode) = skupinove/individualne
        self.festival = festival
        self.id = id
        self.members = members
        self.type = type
        self.mode = mode

    def group_change_mode(self):
        """Tato funkce přepiná chování účastníků ve skupině každý sám za sebe/společná aktivita"""

        if self.mode == source.Groups_modes.INDIVIDUALLY:
            self.mode = source.Groups_modes.IN_GROUP
        else:
            self.mode = source.Groups_modes.INDIVIDUALLY

    def start_action(self, festival, member, action):
        """Tato funkce pro daného návštěvníka spustí zvolenou akci"""

        if action == "smoking":
            yield self.festival.process(member.smoke())

        if action == "go_to":
            yield self.festival.process(member.go_to())
        
        if action == "go_to_festival_area": #vyřešit určení správného vstupu v resources
            entrances = resources.find_stalls_in_zone(self, festival, "entrances")
            entrance = member.identify_entrance(entrances)

            if entrance == None:
                print(f"ČAS {self.festival.now:.2f}: CHYBA!! {member.name} {member.surname} nemůže jít z {self.state["location"].value} do festivalového areálu!")

            yield self.festival.process(member.go_to_festival_area(entrance))

        if action == "withdraw":
            yield self.festival.process(member.withdraw())

        if action == "go_for_food":
            food = member.choose_food(festival)

            if "GO_TO" in food:                             #návštěvník musí přejít do jiné zóny kde se prodává jídlo
                location = food.split("GO_TO_")[1]

                for loc in source.Locations:
                    if loc.name == location:
                        location = loc

                print(f"ČAS {self.festival.now:.2f}: {member.name} {member.surname} musí jít do zóny {location.value}, aby si mohl/a koupit něco k jídlu")
                yield self.festival.process(member.go_to(location, location.value))
                food = member.choose_food(festival)
            
            if food is None:
                yield self.festival.process(member.withdraw())

            stall = member.choose_stall(festival, food, "foods")
            yield self.festival.process(member.go_for_food(stall, food))
            yield self.festival.process(member.eat(food))

        if action == "go_for_drink":
            drink = member.choose_drink(festival)

            if "GO_TO" in drink:                             
                location = drink.split("GO_TO_")[1]

                for loc in source.Locations:
                    if loc.name == location:
                        location = loc
                
                print(f"ČAS {self.festival.now:.2f}: {member.name} {member.surname} musí jít do zóny {location.value}, aby si mohl/a koupit něco k pití")
                yield self.festival.process(member.go_to(location, location.value))
                drink = member.choose_drink(festival)

            if drink is None:
                yield self.festival.process(member.withdraw())
            
            stall = member.choose_stall(festival, drink, "drinks")
            yield self.festival.process(member.go_for_drink(stall, drink))
            yield self.festival.process(member.drink(drink))
        
        if action == "go_to_toilet":
            need = member.decide_bathroom_action()
            toilet = member.choose_toilet(festival)
                
    def group_decision_making(self, festival):
        """Zvolí všem návštěvníkům skupiny akci a zavolá její spuštění"""

        while True:
            if self.mode == source.Groups_modes.INDIVIDUALLY: 

                for member in self.members:
                    member.update_stats()      
                    member.state["sociability"] -= random.uniform(0.2, 0.5) 
                    action = member.next_move()

                    yield from self.start_action(festival, member, action)

            elif self.type == source.Groups.FAMILY:

                parents = [members for members in self.members if members.age_category == source.Age_category.ADULT]
                parent = random.choice(parents)
                action = parent.next_move()

                for member in self.members:
                    member.update_stats() 
                    yield from self.start_action(festival, member, action)   

            elif self.mode == source.Groups_modes.IN_GROUP:

                leader = random.choice(self.members)
                action = leader.next_move()

                for member in self.members:
                    member.update_stats() 
                    yield from self.start_action(festival, member, action)
    
class Visitor:

    def __init__(self, festival, id, name, surname, gender, age_category, age, qualities, state, preference, accommodation, fellows, inventory):
        self.festival = festival
        self.id = id 
        self.name = name
        self.surname = surname
        self.gender = gender
        self.age_category = age_category
        self.age = age
        self.qualities = qualities
        self.state = state
        self.preference = preference
        self.accommodation = accommodation
        self.fellows = fellows
        self.inventory = inventory

    def update_stats(self):
        factor = 1
        self.state["tiredness"] -= factor * random.uniform(0.1, 0.5)
        self.state["hunger"] -= self.qualities["hunger_frequency"] * random.uniform(0.2, 0.5)
        self.state["thirst"] -= factor * random.uniform(0.1, 0.5)
        self.state["wc"] -= factor * random.uniform(0.1, 0.5)
        self.state["hygiene"] -= factor * random.uniform(0.1, 0.5)
        self.state["drunkenness"] -= max(self.qualities["alcohol_tolerance"] * random.uniform(0.1, 0.5), 0)

        if self.preference["smoker"] == True:
            self.state["nicotine"] -= self.state["level_of_addiction"] * random.uniform(0.1, 0.5)

        

    def next_move(self):
        """funkce, která rozhodne následující krok návštěvníka"""

        need = self.urgent_need()
        return self.resolve_need(need)

        return "go_to_toilet"
    
        if self.preference["smoker"] == True:
            smoking = self.deciding_smoking()

            if smoking is not None:
                return smoking
            else:
                return "go_for_food"
            
        return "go_for_food"
    
    def urgent_need(self):
        return "hunger"


    def deciding_smoking(self):
        """funkce která rozhodne zda si kuřák chce zapálit cigaretu"""

        if self.preference["smoker"] == True:
            craving_for_a_cigarette = random.randint(0, 12 - self.state["level_of_addiction"])

            if craving_for_a_cigarette <= 2 and self.state["nicotine"] != 100:
                return "smoke"   

            elif self.state["nicotine"] < 30 or self.state["mood"] < 30:
                return "smoke"
        
        return None

# -----------------------------------------------POHYB---------------------------------------------------------

    def go_to(self, location, zone_name):
        """Funkce která obsluje návštěvníkův přesun do jiné zóny bez vstupní prohlídky"""

        print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} jde do {zone_name}")
        yield self.festival.timeout(10)
        print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} dorazil do {zone_name}")
        self.state["location"] = location

    def go_to_festival_area(self, entrance):
        """Funkce která obsluje návštěvníkův přesun do festivalového areálu včetně vstupní kontroly"""
        
        yield self.festival.timeout(10)
        print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} přišel ke vstupu {entrance.id}.")
        start_waiting = self.festival.now

        with entrance.request() as req:

            if entrance.queue_length > 0:
                print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} čeká ve frontě u vstupu do areálu {entrance.id}.")
                entrance.queue_length += 1
                
            yield req 
            entrance.queue_length -= 1
            entry_time = random.randint(1, 5)
            yield self.festival.timeout(entry_time)
            self.state["location"] = source.Locations.FESTIVAL_AREA

            control_time = self.festival.now - start_waiting
            print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} prošel kontrolou {entrance.id}, čekal/a {control_time:.2f} a je ve Festivalovém areálu.")
    
    def identify_entrance(self, entrances):
        location = self.state["location"]

        for entrance in entrances:
            if location == entrance.from_zone:
                return entrance

        return None

    def smoke(self):
        #Funkce která obsluhuje návštěvníkovo kouření cigaret

        if self.preference["smoker"] == True:
             print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} si zapálil cigaretu a začal kouřit.")

        else:
            print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} začal čekat, než si člen skupiny zapálí cigaretu.")

        yield self.festival.timeout(random.uniform(5, 10))
        
        if self.preference["smoker"] == True:

            self.state["cigarettes"] -= 1
            self.state["nicotine"] = min(self.state["nicotine"] + 30, 100)
            self.state["mood"] += min(self.state["mood"] + 30, 100)
            
            print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} Dokouřil.")
        else:
            print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} přestal čekat, až si člen skupiny zapálí.")


# -----------------------------------------------JÍDLO---------------------------------------------------------

    def choose_food(self, festival):
        """Vybere návštěvníkovi jídlo, které si dá viz algoritmy/jidlo a pití.png"""

        if resources.is_type_stalls_in_actual_zone(self, festival, "foods"):

            if self.state["hunger"] <= 30:
                return foods.choose_food_with_great_satiety_in_actual_zone(self, festival)
            
            else:

                presence, stall = foods.is_my_favourite_food_in_actual_zone(self, festival)
                if presence is True:

                    if resources.is_big_queue_at_stall(stall):
                        stall = foods.find_food_stall_with_shortest_queue_in_zone(self, festival)
                        return foods.choose_random_food_from_stall(self, stall)

                    else:
                        if resources.can_afford(self, source.foods[self.preference["favourite_food"]]):
                            return self.preference["favourite_food"]
                        else: 
                            return None
                    
                else:
                    return foods.choose_random_food_from_actual_zone(self, festival)
    
        else:        
            return resources.find_nearest_zone_with_stall(self, "hunger")
    
        
    def go_for_food(self, stall, food):
        """funkce která simuluje návštěvníkovo koupení jídla ve stánku"""
        
        price = source.foods[food]["price"]
        time_min, time_max = source.foods[food]["preparation_time"]

        # čekání na stánek
        with stall.resource.request() as req:
            
            if stall.queue_length > 0:
                print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} začal čekat ve frontě u stánku {stall.stall_cz_name} v zóně {self.state["location"].value}")

            yield req
            stall.queue_length += 1
            print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} přišel na řadu a je u stánku {stall.stall_cz_name}")

            preparation_time = random.randint(time_min, time_max)

            print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} čeká na {food} a příprava bude trvat {preparation_time:.2f}")
            yield self.festival.timeout(preparation_time)
            print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} dostal {food}")

        self.state["money"] -= price
            
    def eat(self, food):
        eating_time_min, eating_time_max = source.foods[food]["eating_time"]
        eating_time = random.randint(eating_time_min, eating_time_max)
        satiety = source.foods[food]["satiety"]

        print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} začal/a jíst {food}")
        yield self.festival.timeout(eating_time)
        self.state["hunger"] = min(100, self.state["hunger"] + satiety)
        print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} dojedl/a {food}, aktuální stav hladu je: {self.state["hunger"]}")


# -----------------------------------------------STOLY---------------------------------------------------------------

# -----------------------------------------------PITÍ----------------------------------------------------------------
    def choose_drink(self, festival):
        """Vybere návštěvníkovi, které pití dá viz jidlo a pití.png"""

        if resources.is_type_stalls_in_actual_zone(self, festival, "drinks"):

            if self.preference["alcohol_consumer"] == True:

                if self.is_visitor_drunk():
                    presence, stall = drinks.is_my_favourite_drink_in_actual_zone(self, festival, "soft_drink")
                    if presence is True:
                        if resources.is_big_queue_at_stall(stall):
                            stall = drinks.find_drink_stall_with_shortest_queue_in_zone(self, festival)
                            return drinks.choose_random_drink_from_stall(self, stall, "soft_drink")
                        else:
                            if resources.can_afford(self, source.drinks[self.preference["favourite_soft_drink"]]):
                                return self.preference["favourite_soft_drink"]
                            else:
                                return None
                    else:
                        return drinks.choose_random_drink_from_actual_zone(self, festival, "soft_drink")
                else:
                    kinds_of_alcohol = drinks.what_kind_of_alcohol_is_in_actual_zone(self, festival)
                    alcohol_type = self.choose_type_of_alcohol(kinds_of_alcohol)

                    if alcohol_type == "favourite_alcohol":
                        if resources.can_afford(self, source.drinks[self.preference["favourite_alcohol"]]):
                            return self.preference["favourite_alcohol"]
                        else:
                            return None 
                    else: 
                        return drinks.choose_random_drink_from_actual_zone(self, festival, alcohol_type) 
                        
            else:
                presence, stall = drinks.is_my_favourite_drink_in_actual_zone(self, festival, "soft_drink")

                if presence is True:

                    if resources.is_big_queue_at_stall(stall):
                        stall = drinks.find_drink_stall_with_shortest_queue_in_zone(self, festival)
                        return drinks.choose_random_drink_from_stall(self, stall, "soft_drink")
                    
                    else:
                        if resources.can_afford(self, source.drinks[self.preference["favourite_soft_drink"]]):
                            return self.preference["favourite_soft_drink"]
                        else:
                            return None
                         
                else:
                    return drinks.choose_random_drink_from_actual_zone(self, festival, "soft_drink")
        else:
            return resources.find_nearest_zone_with_stall(self, "thirst")
        
    def is_visitor_drunk(self):
        return self.state["drunkenness"] >= 80
    
    def choose_type_of_alcohol(self, kinds_of_alcohol):

        if self.state["drunkenness"] <= 30:
            probabilities = {"favourite_alcohol": 20, "beers": 50, "hard_alcohol": 20, "cocktails": 10}
        elif self.state["drunkenness"] <= 60:
            probabilities = {"favourite_alcohol": 20, "beers": 30, "hard_alcohol": 30, "cocktails": 20}
        else:
            probabilities = {"favourite_alcohol": 20, "beers": 45, "hard_alcohol": 5, "cocktails": 30}

        
        available_probabilities = {}  

        for alcohol_type, weight in probabilities.items():
        
            if kinds_of_alcohol.get(alcohol_type, False):
                available_probabilities[alcohol_type] = weight

        choices = list(available_probabilities.keys())
        weights = list(available_probabilities.values())

        chosen_type_of_alcohol = random.choices(choices, weights=weights, k=1)[0]
        return chosen_type_of_alcohol
    
    def go_for_drink(self, stall, drink):
        """funkce která simuluje návštěvníkovo koupení jídla ve stánku"""
        
        price = source.drinks[drink]["price"]
        time_min, time_max = source.drinks[drink]["preparation_time"]

        # čekání na stánek
        with stall.resource.request() as req:
            
            if stall.queue_length > 0:
                print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} začal čekat ve frontě u stánku {stall.stall_cz_name} v zóně {self.state["location"].value}")

            yield req
            stall.queue_length += 1
            print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} přišel na řadu a je u stánku {stall.stall_cz_name}")

            preparation_time = random.randint(time_min, time_max)

            print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} čeká na {drink} a příprava bude trvat {preparation_time:.2f}")
            yield self.festival.timeout(preparation_time)
            print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} dostal {drink}")

        self.state["money"] -= price

    def drink(self, drink):
        pass
# -----------------------------------------------VÝBĚR PENĚZ---------------------------------------------------------

    def withdraw(self, festival):
        actions = load_data("ACTIONS_BY_LOCATIONS")
        print(actions)

        if actions[self.state["location"]]:
            pass
        self.state["money"] += random.randint(1000, 10000)

# -----------------------------------------------TOITOIKY---------------------------------------------------------
    def decide_bathroom_action(self):
        
        need_index = random.uniform(0, 100 - self.state["wc"])
        if need_index > 30:
            return "big"
        else:
            return "small"
        
    def choose_toilet(self, festival, need):
        if resources.is_type_stalls_in_actual_zone(self, festival, "toitoi"):
            pass
        else:
            resources.find_nearest_zone_with_stall(self, "wc")

    def go_to_the_toilet(self, toitoi):
        """Funkce která obsluje návštěvníka na wc"""

        all_urinals = (resources.toitoi_festival_area_urinal + resources.toitoi_chill_zone_urinal + resources.toitoi_tent_area_urinal + resources.toitoi_entrance_zone_urinal)
        need_index = random.uniform(0, 100 - self.state["wc"])
    
        # Velká potřeba
        if need_index > 30 and toitoi not in all_urinals:
  
            self.state["wc"] = min(100, self.state["wc"] + 50)
            if self.gender == source.Gender.MALE:
                wc_time = random.uniform(180, 250)
            else:
                wc_time = random.uniform(120, 200)
    
        # Malá potřeba
        else:
            self.state["wc"] = min(100, self.state["wc"] + 30)
            if self.gender == source.Gender.MALE:
                wc_time = random.uniform(20, 40)   
            else:
                wc_time = random.uniform(40, 70)  

        toitoi = random.choice(toitoi)
        with toitoi.request() as req:
            print(f"{self.name} {self.surname} čeká na volnou toiku v čase {self.festival.now:.2f}")
            yield req
    
            print(f"{self.name} {self.surname} vchází na toiku v čase {self.festival.now:.2f}")
            yield self.festival.timeout(wc_time)
            print(f"{self.name} {self.surname} odchází z toiky v čase {self.festival.now:.2f}")

# ----------------------------------------------OBECNÉ FUNKCE ---------------------------------------------------------

    def choose_stall(self, festival, item, type_of_item):
        #funkce která návštěvníkovi přiřadí stánek, ke kterému si půjde pro jídlo

        if type_of_item == "foods":
            stalls = source.food_stalls
        elif type_of_item == "drinks":
            stalls = source.drink_stalls

        for key, value in stalls.items():
            if item in value:
                stall_name = key
                break
            
        stalls = resources.find_stalls_in_zone(self, festival, type_of_item, stall_name)
            
        if len(stalls) == 1:
            return stalls[0]
        
        else:
            shortest_queue_stall = stalls[0]

            for stall in stalls:
                if stall.queue_length < shortest_queue_stall.queue_length:
                    shortest_queue_stall = stall
            
            return shortest_queue_stall
        
    def resolve_need(self, need):
        """Pokud lze potřebu vyřešit v aktuální zóně, vrátí akci. Jinak najde nejkratší cestu do zóny, kde to možné je."""

        actual_zone = self.state["location"]
        actions_by_locations = load_data("ACTIONS_BY_LOCATIONS")
        actions_moving = load_data("ACTIONS_MOVING")

        if need in actions_by_locations[actual_zone]:
            return actions_by_locations[actual_zone][need]

        target_zones = [
            zone for zone, actions in actions_by_locations.items() if need in actions
        ]

        if not target_zones:
            return None

        #BFS hledání cesty
        queue = deque([(actual_zone, [])])
        visited = set()

        while queue:
            zone, path = queue.popleft()

            if zone in visited:
                continue
            visited.add(zone)

            # Pokud jsme dorazili do cílové zóny
            if zone in target_zones:
                return path[0] if path else None

            for move in actions_moving.get(zone, []):
                next_zone = move.replace("GO_TO_", "")
                queue.append((next_zone, path + [move]))

        return None
# ------------------------------------------PŘÍJEZD NÁVŠTĚVNÍKŮ--------------------------------------------------------

def spawn_groups(env, groups_list, festival):
    i = 0

    for group in groups_list:
        i += 1

        yield env.timeout(random.randint(1,5))
        print(f"ČAS {env.now:.2f}: Skupina číslo {i} dorazila na festival(spawn zona)")
        env.process(group.group_decision_making(festival))
