import simpy
import random
import source
import resources
import foods
import drinks
from data.load_data import load_data
from collections import deque

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

        if action == "GO_TO_SPAWN_ZONE" or action == "GO_TO_ENTRANCE_ZONE" or action == "GO_TO_CHILL_ZONE" or action == "GO_TO_FUN_ZONE":
            location = action.replace("GO_TO_", "")
            location = source.Locations[location]
            yield self.festival.process(member.go_to(location))

        if action == "GO_TO_TENT_AREA":

            if member.state["tent_area_ticket"] == False and self.state["money"] <= festival.prices["camping_area_price"]:
                member.festival.process(member.withdraw())

            yield self.festival.process(member.go_to_tent_area(festival))

            if member.accommodation["built"] == False:
                camping_area = member.choose_stall(festival, "tent_area")

                if len(camping_area) > 1:
                    camping_area = member.find_area_with_more_space(camping_area)
                else:
                    camping_area = camping_area[0]

                yield self.festival.process(member.pitch_tent(camping_area))

        elif action == "SMOKE":
            yield self.festival.process(member.smoke())
    
        elif action == "GO_TO_FESTIVAL_AREA": #vyřešit určení správného vstupu v resources
            entrances = resources.find_stalls_in_zone(self, festival, "entrances")
            entrance = member.identify_entrance(entrances)

            if entrance == None:
                print(f"ČAS {self.festival.now:.2f}: CHYBA! {member.name} {member.surname} nemůže jít z {member.state["location"].value} do festivalového areálu!")

            yield self.festival.process(member.go_to_festival_area(entrance))

        elif action == "WITHDRAW":
            stall = member.choose_stall(festival, "atm")
            yield self.festival.process(member.withdraw(stall))

        elif action == "GO_FOR_FOOD":
            food = member.choose_food(festival)
            
            if food is None:
                stall_atm = member.choose_stall(festival, "atm")
                yield self.festival.process(member.withdraw(stall_atm))
                food = member.choose_food(festival)

            stall = member.choose_stall(festival, "foods", food)
            yield self.festival.process(member.go_for_food(stall, food))
            
            stall = resources.find_stall_with_shortest_queue_in_zone(member, festival, "tables")

            if stall:
                yield self.festival.process(member.sit(stall, food=food))
            else:
                print(f"ČAS {self.festival.now:.2f}: {member.name} {member.surname} si sní {food} za pochodu.")
                yield self.festival.process(member.eat(food))

        elif action == "GO_FOR_DRINK":
            drink, alcohol_type = member.choose_drink(festival)

            if drink is None:
                stall_atm = member.choose_stall(festival, "atm")
                yield self.festival.process(member.withdraw(stall_atm))
            
            stall = member.choose_stall(festival, "drinks", drink)
            yield self.festival.process(member.go_for_drink(festival, stall, drink, alcohol_type))

            if member.state["free_time"] > 0:
                stall = resources.find_stall_with_shortest_queue_in_zone(member, festival, "tables")

                if stall:
                    yield self.festival.process(member.sit(stall, drink=drink))
                
                else:
                    print(f"ČAS {self.festival.now:.2f}: {member.name} {member.surname} si vypije {drink} za pochodu.")
                    yield self.festival.process(member.drink(drink))
        
        elif action == "GO_TO_TOILET":
            need = member.decide_bathroom_action()
            toilet = member.choose_toilet(festival, need)
            yield self.festival.process(member.go_to_toilet(toilet, need))
            stall = member.choose_stall(festival, "handwashing_station")
            yield self.festival.process(member.wash(stall))

        elif action == "GO_TO_SHOWER":
            shower_price = 50 #upravit přes gui

            if member.state["money"] < shower_price:
                print(f"ČAS {self.festival.now:2f}: {self.name} {self.surname} nemá dost peněz na sprchu a musí si jít vybrat peníze!")
                stall = member.choose_stall(festival, "atm")
                yield self.festival.process(member.withdraw(stall))

            shower = member.choose_stall(festival, "showers")
            yield self.festival.process(member.go_to_shower(shower))

        elif action == "BRACELET_EXCHANGE":

            if member.state["money"] <= festival.prices["on_site_price"] and member.state["pre_sale_ticket"] == False:
                stall = member.choose_stall(festival, "atm")
                yield self.festival.process(member.withdraw(stall))

            booth = member.choose_stall(festival, "ticket_booth")
            yield self.festival.process(member.bracelet_exchange(festival, booth))

        elif action == "PITCH_TENT":

            if member.state["money"] <= festival.get_price("camping_area_price"):
                stall = member.choose_stall(festival, "atm")
                yield self.festival.process(member.withdraw(stall))

            camping_area = member.choose_stall(festival, "tent_area")

            if len(camping_area) > 1:
                camping_area = member.find_area_with_more_space(camping_area)
            else:
                camping_area = camping_area[0]

            yield self.festival.process(member.pitch_tent(camping_area))

        elif action == "CHARGE_PHONE":

            if member.state["money"] <= festival.prices["charging_phone_price"]:
                stall = member.choose_stall(festival, "atm")
                yield self.festival.process(member.withdraw(stall))

            stalls = member.choose_stall(festival, "charging_stall")

            if len(stalls) > 1:
                stall = member.find_area_with_more_space(stalls)
            else:
                stall = stalls[0]

            yield self.festival.process(member.charge_phone(stall, festival))
        
        elif action == "RETURN_CUP":
            stall = member.choose_stall(festival, "cup_return")
            yield self.festival.process(member.return_cup(stall, festival))

        elif action == "WASH":
            stall = member.choose_stall(festival, "handwashing_station")
            yield self.festival.process(member.wash(stall))
        
        elif action == "BRUSH_TEETH":
            stall = member.choose_stall(festival, "handwashing_station")
            yield self.festival.process(member.brush_teeth(stall))

        elif action == "SIT":
            stall = member.choose_stall(festival, "tables")
            yield self.festival.process(member.sit(stall))

    def group_decision_making(self, festival):
        """Zvolí všem návštěvníkům skupiny akci a zavolá její spuštění"""

        while True:
            if self.mode == source.Groups_modes.INDIVIDUALLY: 

                for member in self.members:
                    member.update_stats(festival)      
                    member.state["sociability"] -= random.uniform(0.2, 0.5) 
                    action = member.next_move()

                    yield from self.start_action(festival, member, action)

            elif self.type == source.Groups.FAMILY:

                parents = [members for members in self.members if members.age_category == source.Age_category.ADULT]
                parent = random.choice(parents)
                action = parent.next_move()

                for member in self.members:
                    member.update_stats(festival) 
                    yield from self.start_action(festival, member, action)   

            elif self.mode == source.Groups_modes.IN_GROUP:

                leader = random.choice(self.members)
                action = leader.next_move()

                for member in self.members:
                    member.update_stats(festival) 
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

    def update_stats(self, festival):
        factor = 1
        self.state["energy"] -= factor * random.uniform(0.1, 0.5)
        self.state["hunger"] -= self.qualities["hunger_frequency"] * random.uniform(0.1, 0.5)
        self.state["thirst"] -= factor * random.uniform(0.1, 0.5)
        self.state["wc"] -= factor * random.uniform(0.1, 0.5)
        self.state["hygiene"] -= factor * random.uniform(0.1, 0.5)
        self.state["drunkenness"] -= max(0, self.qualities["alcohol_tolerance"] * random.uniform(0.1, 0.5))

        if self.inventory["phone"] != None:
            self.inventory["phone"].battery -= random.uniform(0.1, 0.5)

        if self.preference["smoker"] == True:
            self.state["nicotine"] -= self.state["level_of_addiction"] * random.uniform(0.1, 0.5)

        self.charging(festival.charging_phones)

    def next_move(self):
        """funkce, která rozhodne následující krok návštěvníka"""
        need = self.urgent_need()
        return self.resolve_need(need)
    
    def urgent_need(self):
        #povinné kroky při příjezdu

        if self.state["entry_bracelet"] == False and self.accommodation["built"] == False:
            return random.choice(list(["living", "bracelet_exchange"]))

        elif self.state["entry_bracelet"] == False:
            return "bracelet_exchange"
        
        elif self.accommodation["built"] == False:
            return "living"

        needs_scores = {}

        needs_scores["hunger"] = 100 - self.state["hunger"]
        needs_scores["thirst"] = 100 - self.state["thirst"]
        needs_scores["wc"] = 100 - self.state["wc"]
        needs_scores["hygiene"] = 100 - self.state["hygiene"]
        needs_scores["energy"] = 100 - self.state["energy"]
        
        if self.state["money"] < 1000:
            low_money_score = 50 + ((1000 - self.state["money"]) / 100) * 5
            needs_scores["low_money"] = low_money_score

        if self.inventory["phone"] != None:
            if self.inventory["phone"].battery < 50:
                low_battery_score = 100 - self.inventory["phone"].battery
                needs_scores["phone_dead"] = low_battery_score

        # kouření řešíš zvlášť
        smoke = self.deciding_smoking()
        if smoke:
            return smoke
   
        return max(needs_scores, key=needs_scores.get)


    def deciding_smoking(self):
        """funkce která rozhodne zda si kuřák chce zapálit cigaretu"""

        if self.preference["smoker"] == True:
            craving_for_a_cigarette = random.randint(0, 12 - self.state["level_of_addiction"])

            if craving_for_a_cigarette <= 2 and self.state["nicotine"] != 100:
                return "smoking"   

            elif self.state["nicotine"] < 30 or self.state["mood"] < 30:
                return "smoking"
        
        return None

# -----------------------------------------------POHYB---------------------------------------------------------

    def go_to(self, location):
        """Funkce která obsluje návštěvníkův přesun do jiné zóny bez vstupní prohlídky"""

        print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} jde do {location.value}")
        yield self.festival.timeout(10)
        print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} dorazil do {location.value}")
        self.state["location"] = location
    
    def go_to_festival_area(self, entrance):

        yield self.festival.timeout(10)
        print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} přišel ke vstupu.")
        start_waiting = self.festival.now

        with entrance.resource.request() as req:

            will_wait = entrance.resource.count >= entrance.resource.capacity

            yield req

            if will_wait:
                waiting_time = self.festival.now - start_waiting
                print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} čekal/a {waiting_time:.2f} ve frontě u vstupu.")
            else:
                print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} prošel/a vstupem bez čekání.")

            entry_time = random.uniform(1, 5)
            yield self.festival.timeout(entry_time)

            self.state["location"] = source.Locations.FESTIVAL_AREA

            print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} dorazil do festivalového areálu.")

    def go_to_tent_area(self, festival):

        print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} jde do stanového městečka.")
        yield self.festival.timeout(10)

        if self.state["tent_area_ticket"] == None:

            print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} dorazil/a ke stanovému městečku a nemá koupený lístek do stanového městečka.")
            yield self.festival.timeout(random.uniform(2, 5))
            self.state["money"] -= festival.prices["camping_area_price"]
            self.state["tent_area_ticket"] = True
            festival.income += festival.prices["camping_area_price"]
            print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} si koupil/a vstupenku do stanového městečka.")
            self.state["location"] = source.Locations.TENT_AREA

        else:
            yield self.festival.timeout(random.uniform(0, 1))
            print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} již má vstupenku a dorazil do stanového městečka.")
            self.state["location"] = source.Locations.TENT_AREA

    def identify_entrance(self, entrances):
        location = self.state["location"]

        for entrance in entrances:
            if location == entrance.from_zone:
                return entrance

        return entrances[0] #opravit

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
            
            print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} dokouřil, stav nikotinu je: {self.state["nicotine"]}")
        else:
            print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} přestal čekat, až si člen skupiny zapálí.")


# -----------------------------------------------JÍDLO---------------------------------------------------------

    def choose_food(self, festival):
        """Vybere návštěvníkovi jídlo, které si dá viz algoritmy/jidlo.png"""

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

    def go_for_food(self, stall, food):
        """funkce která simuluje návštěvníkovo koupení jídla ve stánku"""
        
        price = source.foods[food]["price"]
        time_min, time_max = source.foods[food]["preparation_time"]

        print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} přišel ke stánku {stall.stall_name}.")
        start_waiting = self.festival.now

        # čekání na stánek
        with stall.resource.request() as req:
            
            will_wait = stall.resource.count >= stall.resource.capacity

            yield req

            print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} přišel na řadu a je u stánku {stall.stall_cz_name}")
            
            if will_wait:
                waiting_time = self.festival.now - start_waiting
                print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} čekal/a {waiting_time:.2f} ve frontě u stánku {stall.stall_cz_name}.")

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

    def sit(self, stall, food = None, drink = None, type_of_alcohol = None):
        yield self.festival.timeout(random.uniform(0, 2))
        print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} hledá místo u stolu k sednutí")
        yield self.festival.timeout(random.uniform(0, 2))

        if stall.resource.count >= stall.resource.capacity:
            impatience_index = self.qualities["impatience"] * random.uniform(0.5, 1.5)

            if impatience_index > 5:
                print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} si nemá kam sednout a jde pryč")
                return None

            else:
                print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} si nemá kam sednout ale počká než se uvolní místo u stolu.")
        
        start_waiting = self.festival.now
        with stall.resource.request() as req:

            yield req

            waiting_time = self.festival.now - start_waiting
            print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} si sedl ke stolu.")


            if waiting_time > 0:
                print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} čekal na volné místo u stolu {waiting_time}.")

            start_sitting = self.festival.now

            if food and drink:
                yield self.festival.process(self.eat(food))
                yield self.festival.process(self.drink(drink))
                sitting_time = self.festival.now - start_sitting

            elif food:
                
                yield self.festival.process(self.eat(food))
                sitting_time = self.festival.now - start_sitting

            elif drink:

                yield self.festival.process(self.drink(drink))
                sitting_time = self.festival.now - start_sitting

            else:
                sitting_time = random.uniform(0 , self.state["free_time"])
                yield self.festival.timeout(sitting_time)
                print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} odchází od stolu.")

            self.state["energy"] = min(100, self.state["energy"] + ((sitting_time / 60) * 20))

# ------------------------------------------------PITÍ----------------------------------------------------------------
    def choose_drink(self, festival):
        """Vybere návštěvníkovi, které pití dá viz jidlo a pití.png"""

        if self.preference["alcohol_consumer"] == True:

            if self.is_visitor_drunk():
                presence, stall = drinks.is_my_favourite_drink_in_actual_zone(self, festival, "soft_drink")
                if presence is True:
                    if resources.is_big_queue_at_stall(stall):
                        stall = drinks.find_drink_stall_with_shortest_queue_in_zone(self, festival)
                        return drinks.choose_random_drink_from_stall(self, stall, "soft_drink"), None
                    else:
                        if resources.can_afford(self, source.drinks[self.preference["favourite_soft_drink"]]):
                            return self.preference["favourite_soft_drink"]
                        else:
                            return None
                else:
                    return drinks.choose_random_drink_from_actual_zone(self, festival, "soft_drink"), None
            else:
                kinds_of_alcohol = drinks.what_kind_of_alcohol_is_in_actual_zone(self, festival)
                alcohol_type = self.choose_type_of_alcohol(kinds_of_alcohol)

                if alcohol_type == "favourite_alcohol":
                    if resources.can_afford(self, source.drinks[self.preference["favourite_alcohol"]]):
                        return self.preference["favourite_alcohol"], None
                    else:
                        return None 
                else: 
                    return drinks.choose_random_drink_from_actual_zone(self, festival, alcohol_type), alcohol_type 
                    
        else:
            presence, stall = drinks.is_my_favourite_drink_in_actual_zone(self, festival, "soft_drink")

            if presence is True:

                if resources.is_big_queue_at_stall(stall):
                    stall = drinks.find_drink_stall_with_shortest_queue_in_zone(self, festival)
                    return drinks.choose_random_drink_from_stall(self, stall, "soft_drink"), None
                
                else:
                    if resources.can_afford(self, source.drinks[self.preference["favourite_soft_drink"]]):
                        return self.preference["favourite_soft_drink"], None
                    else:
                        return None
                        
            else:
                return drinks.choose_random_drink_from_actual_zone(self, festival, "soft_drink"), None
        
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
    
    def go_for_drink(self, festival, stall, drink, alcohol_type):
        """funkce která simuluje návštěvníkovo koupení jídla ve stánku"""

        plastic_cup_price = festival.prices["plastic_cup_price"]
        price = source.drinks[drink]["price"]
        time_min, time_max = source.drinks[drink]["preparation_time"]
        start_waiting = self.festival.now

        # čekání na stánek
        with stall.resource.request() as req:

            yield req
            will_wait = stall.resource.count >= stall.resource.capacity
            print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} přišel na řadu a je u stánku {stall.stall_cz_name} v zóně {self.state["location"].value}")

            if will_wait:
                waiting_time = self.festival.now - start_waiting
                print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} čekal u stánku {stall.stall_cz_name} {waiting_time}")
            

            preparation_time = random.randint(time_min, time_max)

            print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} čeká na {drink} a příprava bude trvat {preparation_time:.2f}")
            yield self.festival.timeout(preparation_time)

            if alcohol_type is not None:
                if self.inventory["plastic_cup"] == None:
                    self.inventory["plastic_cup"] == True
                    self.state["money"] -= plastic_cup_price
                    print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} neměl kelímek a musel si koupit nový")
                
            print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} dostal {drink}")

        self.state["money"] -= price

    def drink(self, drink_name):
        drink_data = source.drinks[drink_name]
        drinking_time_min = drink_data["drinking_time"][0]
        drinking_time_max = drink_data["drinking_time"][1]
        drinking_time = random.uniform(drinking_time_min, drinking_time_max)

        print(f"ČAS {self.festival.now:.2f}: {self.name} začal/a pít {drink_name}.")
        yield self.festival.timeout(drinking_time)
        print(f"ČAS {self.festival.now:.2f}: {self.name} dopil/a {drink_name}.")

        if "hydration" in drink_data:
            self.state["thirst"] += drink_data["hydration"]

        if "drunkness" in drink_data:
            self.state["drunkenness"] += drink_data["drunkness"]

        if "energy" in drink_data:
            self.state["energy"] += drink_data["energy"]
# -----------------------------------------------VÝBĚR PENĚZ---------------------------------------------------------

    def withdraw(self, atm):
        yield self.festival.timeout(random.uniform(0, 2))

        start_waiting = self.festival.now
        print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} přišel k bankomatu.")
        
        with atm.resource.request() as req:
            
            yield req
            waiting_time = self.festival.now - start_waiting

            if waiting_time > 0:
                print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} čekal/a ve frontě u bankomatu {waiting_time}.")
            
            print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} přišel/a na řadu a začal/a vybírat peníze.")
            yield self.festival.timeout(random.uniform(1, 5))
            print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} dokončil/a výběr peněz.")

            self.state["money"] += random.randint(1000, 10000)

# --------------------------------------------- WC & UMÝVÁRNA---------------------------------------------------------
    def decide_bathroom_action(self):
        
        need_index = random.uniform(0, 100 - self.state["wc"])
        if need_index > 30:
            return "big"
        else:
            return "small"
        
    def choose_toilet(self, festival, need):
        toilets = resources.find_stalls_in_zone(self, festival, "toitoi")
        toilets = random.choice(list(toilets))
        urinals = toilets.resource[0]
        toitois = toilets.resource[1]
        free_urinals = []
        free_toitois = []

        for toitoi in toitois:
            if toitoi.resource.count + len(toitoi.resource.queue) == 0:
                free_toitois.append(toitoi)
                 
        if self.gender == source.Gender.FEMALE:

            if free_toitois != []:
                return random.choice(list(free_toitois))
            else:
                return random.choice(list(toitois))
            
        elif self.gender == source.Gender.MALE and need == "small":

            for urinal in urinals:
                if urinal.resource.count + len(urinal.resource.queue) == 0:
                    free_urinals.append(urinal)

            if free_urinals != []:
                return random.choice(list(free_urinals))
            
        if free_toitois != []:
            return random.choice(list(free_toitois))
        
        else:
            return random.choice(list(toitois))
  
    def go_to_toilet(self, toilet, need):
        """Funkce která obsluje návštěvníka na wc"""
    
        # Velká potřeba
        if need == "big":
    
            self.state["wc"] = min(100, self.state["wc"] + random.uniform(50, 70))

            if self.gender == source.Gender.MALE:
                wc_time = random.uniform(10, 30)

            else:
                wc_time = random.uniform(8, 12)
    
        # Malá potřeba
        else:
            self.state["wc"] = min(100, self.state["wc"] + random.uniform(20, 50))
            
            if self.gender == source.Gender.MALE:
                wc_time = random.uniform(0.5, 1.5)

            else:
                wc_time = random.uniform(1, 3)  

        start_waiting = self.festival.now

        with toilet.resource.request() as req:
            
            will_wait = toilet.resource.count >= toilet.resource.capacity
            print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} přišel k {toilet.stall_cz_name}")

            yield req

            if will_wait:
                waiting_time = self.festival.now - start_waiting
                print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} čekal na volnou {toilet.stall_cz_name} {waiting_time}")

            print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} vchází na {toilet.stall_cz_name}.")

            yield self.festival.timeout(wc_time)
            print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} odchází z {toilet.stall_cz_name}.")

    def wash(self, stall):
        yield self.festival.timeout(random.uniform(0, 2))

        start_waiting = self.festival.now
        print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} přišel/a k umývárně.")
        
        with stall.resource.request() as req:
            
            yield req
            waiting_time = self.festival.now - start_waiting

            if waiting_time > 0:
                print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} čekal/a {waiting_time}, než se u umývárny uvolní místo.")
            
            print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} si začal/a umývat ruce.")
            yield self.festival.timeout(random.uniform(0, 1.5))
            print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} dokončil/a umytí rukou.")

            self.state["hygiene"] += random.randint(10, 20)
        
    def brush_teeth(self, stall):
        yield self.festival.timeout(random.uniform(0, 2))

        start_waiting = self.festival.now
        print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} přišel/a k umývárně.")
        
        with stall.resource.request() as req:
            
            yield req
            waiting_time = self.festival.now - start_waiting

            if waiting_time > 0:
                print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} čekal/a {waiting_time}, než se u umývárny uvolní místo.")
            
            print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} si začal/a čistit zuby.")
            yield self.festival.timeout(random.uniform(0, 1.5))
            print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} dokončil/a čištění zubů.")

            self.state["hygiene"] += random.randint(15, 30)

# -------------------------------------------------SPRCHY ---------------------------------------------------------
            
    def go_to_shower(self, shower):
        """funkce obsluhjící návštěvníka ve sprše"""
        
        if self.gender == source.Gender.MALE:
            shower_time = random.uniform(5, 15)
        else:
            shower_time = random.uniform(12, 20)

        with shower.resource.request() as req:
            start_waiting = self.festival.now
            will_wait = shower.resource.count >= shower.resource.capacity

            print(f"ČAS {self.festival.now:.2f} {self.name} {self.surname} přišel/la ke sprchám")
            yield req

            if will_wait:
                waiting_time = self.festival.now - start_waiting
                print(f"ČAS {self.festival.now:.2f} {self.name} {self.surname} čekal/a na volnou spruchu {waiting_time}")

            print(f"ČAS: {self.festival.now:.2f} {self.name} {self.surname} vchází do sprchy.")
            yield self.festival.timeout(shower_time)
            print(f"ČAS: {self.festival.now:.2f} {self.name} {self.surname} odchází ze sprchy.")

        self.state["hygiene"] = 100

# --------------------------------------------STANOVÉ MĚSTEČKO------------------------------------------------------

    def pitch_tent(self, camping_area):
            #funkce která obsluhuje návštěvníkovo stavění stanu
            
            yield self.festival.timeout(random.uniform(0, 2))

            num_fellows = len(self.fellows)
            pitch_time = random.uniform(15, 20) - num_fellows * 1.5
            free_space = False
            i = 0

            for position in camping_area.resource:
                i += 1

                if position == []:
                    free_space = True

                    if self.accommodation["owner"] == False:
                        
                        print(f"ČAS: {self.festival.now:.2f}: {self.name} {self.surname} pomáhá kolegovi postavit stan.")
                        yield self.festival.timeout(pitch_time)
                        print(f"ČAS: {self.festival.now:.2f}: {self.name} {self.surname} s kolegou dostavěli stan.")

                    else:        
                        position.append(self.inventory["tent"])
                        print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} staví stan.")
                        yield self.festival.timeout(pitch_time)
                        print(f"ČAS: {self.festival.now:.2f}: {self.name} {self.surname} dostavěl stan.")
                    
                    self.accommodation["i"] = i
                    self.accommodation["built"] = True
                    self.accommodation["camping_area"] = camping_area
                    break
                
            if not free_space:
                print(f"ČAS: {self.festival.now:.2f}: Došlo místo ve stanovém městečku!")

    def find_area_with_more_space(self, areas):
        if len(areas) > 1:

            camping_area = areas[0]
            free_spaces = camping_area.resource[0]

            for area in areas:
                if free_spaces < area.resource[0]:
                    free_spaces = area.resource[0]
                    camping_area = area
            
            return camping_area
        else:
            return areas

    def sleep_in_tent(self, time):
        
        yield self.festival.timeout(random.uniform(0, 2))

        print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} došel/a do stanu.")
        
        with self.accommodation["camping_area"].request() as req:
            
            yield req
            
            print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} jde spát.")
            yield self.festival.timeout(time)
            print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} se vzbudil/a.")

            self.state["energy"] += (time / 60) * 10

# ------------------------------------------------POKLADNY ---------------------------------------------------------
    def bracelet_exchange(self, festival, ticket_booth):
        #funkce, která simuluje návštěvníkovo ukázání lístku u pokladny, výměnou za pásek na ruku umožňující vstup do arálu.
        #Případně si návštěvník může lístek koupit v pokladně na místě, pokud ho nemá z předprodeje
        
        with ticket_booth.resource.request() as req:

            print(f"ČAS: {self.festival.now:.2f}: {self.name} {self.surname} přišel/la k pokladnám.")
            start_waiting = self.festival.now
            will_wait = ticket_booth.resource.count >= ticket_booth.resource.capacity

            yield req
            
            if will_wait:
                waiting_time = self.festival.now - start_waiting
                print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} čekal ve frontě u pokladny {waiting_time}")

            if self.state["pre_sale_ticket"] == True:
                bracelet_exchange_time = random.uniform(1,2)
            else:
                bracelet_exchange_time = random.uniform(2, 3)

            yield self.festival.timeout(bracelet_exchange_time)
            
            self.state["entry_bracelet"] = True

            if self.state["pre_sale_ticket"] == False and self.age > 14:
                self.state["money"] -= festival.prices["on_site_price"]
                festival.income += festival.prices["on_site_price"]

                print(f"ČAS {self.festival.now:2f} {self.name} {self.surname} si koupil lístek na místě, dostal pásek, a odešel z pokladny.")
            
            else:
                print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} měl lístek koupený z předprodeje, dostal pásek, a odešel z pokladny.")

# ----------------------------------------------NABÍJECÍ STÁNEK ---------------------------------------------------------

    def charge_phone(self, stall, festival):
        """Funkce na nabití najení telefonů návštěvníků"""

        yield self.festival.timeout(random.uniform(0, 2))

        i = -1

        print(f"ČAS: {self.festival.now:.2f}: {self.name} {self.surname} přišel/la k nabíjecímu stánku.")    

        free_space = False

        for position in stall.resource:
            i += 1

            if position == []:
                free_space = True

                stall.resource[i] = self.inventory["phone"]
                    
                print(f"ČAS: {self.festival.now:.2f}: {self.name} {self.surname} si dává nabít mobil do nabíjecího stánku.")
                yield self.festival.timeout(random.uniform(1,5))
                print(f"ČAS: {self.festival.now:.2f}: {self.name} {self.surname} si dal mobil do nabíjecího stánku.")
                self.state["money"] -= festival.prices["charging_phone_price"]
                festival.income += festival.prices["charging_phone_price"]
                festival.add_phone(self.inventory["phone"])
                self.inventory["phone"] = None
                break
            
        if not free_space:
            print(f"ČAS: {self.festival.now:.2f}: Došly pozice na nabíjení v nabíjecím stánku!")

    def charging(self, phones):
        for phone in phones:
            phone.charging()

# ----------------------------------------------NABÍJECÍ STÁNEK ---------------------------------------------------------

    def return_cup(self, stall, festival):
        yield self.festival.timeout(random.uniform(0, 2))

        start_waiting = self.festival.now
        print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} přišel/a k výkupu kelímků.")
        
        with stall.resource.request() as req:
            
            yield req
            waiting_time = self.festival.now - start_waiting

            if waiting_time > 0:
                print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} čekal/a ve frontě {waiting_time}.")
            
            print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} přišel/a na řadu a začal/a vracet kelímek.")
            yield self.festival.timeout(random.uniform(1, 5))
            print(f"ČAS {self.festival.now:.2f}: {self.name} {self.surname} vrátil/a kelímek.")

            self.state["money"] += festival.prices["plastic_cup_price"]
            self.inventory["plastic_cup"] = None

# ----------------------------------------------OBECNÉ FUNKCE ---------------------------------------------------------

    def choose_stall(self, festival, type_of_item, item = None):
        #funkce která návštěvníkovi přiřadí stánek, ke kterému si půjde chtěnou věc/akci

        if item:
            if type_of_item == "foods":
                stalls = source.food_stalls
            elif type_of_item == "drinks":
                stalls = source.drink_stalls

            for key, value in stalls.items():
                if item in value:
                    stall_name = key
                    break
            
            return resources.find_stall_with_shortest_queue_in_zone(self, festival, type_of_item, stall_name)
        else:
            return resources.find_stall_with_shortest_queue_in_zone(self, festival, type_of_item)

    def resolve_need(self, need):
        """Pokud lze potřebu vyřešit v aktuální zóně, vrátí akci. Jinak najde nejkratší cestu do zóny, kde to možné je, a vrátí první zónu v této cestě."""

        actual_zone = self.state["location"]
        actions_by_locations = load_data("ACTIONS_BY_LOCATIONS")
        actions_moving = load_data("ACTIONS_MOVING")

        if need in actions_by_locations[actual_zone.name]:
            return actions_by_locations[actual_zone.name][need]

        target_zones = [
            zone for zone, actions in actions_by_locations.items() if need in actions
        ]

        if not target_zones:
            print(f"ERROR: K zóně {actual_zone.value} není připojená žádná zóna, která by uspokojila potřebu {need}")
            return None

        queue = deque([(actual_zone, [])])
        visited = set() #vytvoří práznou množinu

        while queue:
            zone, path = queue.popleft()

            if zone in visited:
                continue
            visited.add(zone)

            # Pokud návštěvník dorazil do zóny poskytující hledanou potřebu
            if zone.name in target_zones:
                if path:
                    return path[0]
                else:
                    return None
                
            # Pokud návtěvník doposud nedorazil do zóny poskytující hledanou potřebu
            for move in actions_moving.get(zone.name, []):
                next_zone = move.replace("GO_TO_", "")
                next_zone = source.Locations[next_zone]
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
