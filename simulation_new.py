import simpy
import random
import source
import resources
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

    def start_action(self, member, action, stalls):
        """Tato funkce pro daného návštěvníka spustí zvolenou akci"""

        if action == "smoking":
            yield self.festival.process(member.smoke())

        if action == "go_to":
            yield self.festival.process(member.go_to())
        
        if action == "go_to_festival_area":
            yield self.festival.process(member.go_to_festival_area())

        if action == "go_for_food":
            stall, food = member.choose_stall_with_food(stalls)
            yield self.festival.process(member.go_for_food(stall, food))


    def group_decision_making(self, stalls):
        """Zvolí všem návštěvníkům skupiny akci a zavolá její spuštění"""

        while True:
            if self.mode == source.Groups_modes.INDIVIDUALLY: 

                for member in self.members:
                    member.update_stats()      
                    member.state["sociability"] -= random.uniform(0.2, 0.5) 
                    action = member.next_move()

                    yield from self.start_action(member, action, stalls)

            elif self.type == source.Groups.FAMILY:

                parents = [members for members in self.members if members.age_category == source.Age_category.ADULT]
                parent = random.choice(parents)
                action = parent.next_move()

                for member in self.members:
                    member.update_stats() 
                    yield from self.start_action(member, action, stalls)   

            elif self.mode == source.Groups_modes.IN_GROUP:

                leader = random.choice(self.members)
                action = leader.next_move()

                for member in self.members:
                    member.update_stats() 
                    yield from self.start_action(member, action, stalls)
    
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
        self.state["tiredness"] -= factor * random.uniform(0.2, 0.5)
        self.state["hunger"] -= factor * random.uniform(0.2, 0.5)
        self.state["thirst"] -= factor * random.uniform(0.2, 0.5)
        self.state["wc"] -= factor * random.uniform(0.2, 0.5)
        self.state["hygiene"] -= factor * random.uniform(0.2, 0.5)

        if self.preference["smoker"] == True:
            self.state["nicotine"] -= self.state["level_of_addiction"] * random.uniform(0.1, 0.5)

    def next_move(self):
        """funkce, která rozhodne následující krok návštěvníka"""
        return "go_for_food"
        """
        if self.state["smoker"] == True:
            smoking = self.deciding_smoking()

            if smoking is not None:
                return smoking
            else:
                return "go_for_food"
        """

    def deciding_smoking(self):
        """funkce která rozhodne zda si kuřák chce zapálit cigaretu"""

        if self.preference["smoker"] == True:
            craving_for_a_cigarette = random.randint(0, 12 - self.state["level_of_addiction"])

            if craving_for_a_cigarette <= 2 and self.state["nicotine"] != 100:
                return "smoke"   

            elif self.state["nicotine"] < 30 or self.state["mood"] < 30:
                return "smoke"
        
        return None


    def go_to(self, location, zone_name):
        """Funkce která obsluje návštěvníkův přesun do jiné zóny bez vstupní prohlídky"""

        print(f"{self.name} {self.surname} jde do {zone_name} v čase {self.festival.now:.2f}")
        yield self.festival.timeout(10)
        print(f"{self.name} {self.surname} dorazil do {zone_name} {self.festival.now:.2f}")
        self.state["location"] = location

    def go_to_festival_area(self, entrances):
        """Funkce která obsluje návštěvníkův přesun do festivalového areálu včetně vstupní kontroly"""

        yield self.festival.timeout(random.expovariate(1/5))
        prichod_time = self.festival.now

        entrance_id = occupied.index(min(occupied))
        entrance = entrances[entrance_id]
        occupied[entrance_id] += 1

        print(f"{self.name} {self.surname}, přišel ke vstupu {entrance_id + 1} v čase {prichod_time:.2f}")
        print(occupied)

        with entrance.request() as req:
            queue_start = self.festival.now  
            yield req 

            queue_waiting_time = self.festival.now - queue_start  
            entry_time = random.uniform(1, 3)
            yield self.festival.timeout(entry_time)

            self.state["location"] = source.Locations.FESTIVAL_AREA

            print(f"{self.name} {self.surname} prošel kontrolou {entrance_id + 1} v čase {self.festival.now:.2f}, čekal {queue_waiting_time:.2f}s, kontrola trvala {entry_time:.2f}")

        occupied[entrance_id] -= 1
        print(occupied)


    def smoke(self):
        #Funkce která obsluhuje návštěvníkovo kouření cigaret

        yield self.festival.timeout(random.uniform(5, 10))

        if self.preference["smoker"] == True:

            self.state["cigarettes"] -= 1
            self.state["nicotine"] = min(self.state["nicotine"] + 30, 100)
            self.state["mood"] += min(self.state["mood"] + 30, 100)
            print(f"{self.name} {self.surname} si zapálil cigaretu.")

        else:
            print(f"{self.name} {self.surname} čekal až si člen skupiny zapálí.")

    #JÍDLO

    def choose_stall_with_food(self, stalls):
        #funkce která návštěvníkovi vybere stánek s jídlem podle jeho preferovaného jídla
        
        all_food_stalls_at_festival = self.find_all_foods_stall_at_festival(stalls)
        all_available_food = self.find_all_foods_at_festival(all_food_stalls_at_festival)
        stall, food = self.choose_food()

    def find_all_foods_stall_at_festival(self, all_stalls):
        all_food_stalls_at_festival = []

        for stall_zones in all_stalls.values():
            for stall in stall_zones:
                if stall.stall_type == "foods":
                    all_food_stalls_at_festival.append(stall.stall_name)
        
        return all_food_stalls_at_festival
    
    def find_all_foods_at_festival(self, food_stalls_at_festival):
        available_food = []

        for stall_name in food_stalls_at_festival:
            
            stall_name = "_".join(stall_name.split("_")[2:])
            if stall_name in source.stalls:
                available_food.extend(source.stalls[stall_name])
    
        return available_food


    def choose_food(self):
        """vybere jídlo, které si návštěvník chce dát -> 50% šance že si dá své oblíbené jídlo, 50% že to bude něco jiného."""
        #Když má velký hlad (pod 30%) -> vybere něco s největší sytostí
        
        if self.state["hunger"] <= 30:
            
            food_to_choose = list(source.foods.items())
            random.shuffle(food_to_choose)
            max_satiety = 0

            for food_name, qualities in food_to_choose:
                if qualities["satiety"] > max_satiety:
                    max_satiety = qualities["satiety"]
                    food = food_name

        else:
            
            food_faktor = random.randint(1,2)
        
            if food_faktor == 1:
                food = self.preference["favourite_food"]
            
            else:
                food = random.choice(list(source.foods.keys()))
        


        for stall_name, foods in source.stalls.items():
            if food in foods:
                return stall_name, food
            
        print(f"Food '{food}' nemá přiřazený stánek!")
        return None, None

    def go_for_food(self, stall, food):
        """funkce která simuluje návštěvníkovo koupení jídla ve stánku"""
        
        price = source.foods[food]["price"]
        time_min, time_max = source.foods[food]["preparation_time"]
        satiety = source.foods[food]["satiety"]

        # funkce skončí, když návštěvník nemá dost peněz
        if self.state["money"] < price:
            print(f"{self.name} {self.surname} nemá dost peněz na {food} (má {self.state["money"]}, cena {price})")
            return
        
        # čekání na stánek
        with stall.request() as req:

            print(f"{self.name} {self.surname} začal čekat ve frontě u stánku {stall} v čase {self.festival.now:.2f}")
            yield req
            print(f"{self.name} {self.surname} přišel na řadu a je u stánku {stall} v čase {self.festival.now:.2f}")

            preparation_time = random.randint(time_min, time_max)

            print(f"{self.name} {self.surname} čeká na {food} a příprava bude trvat {preparation_time:.2f}")
            yield self.festival.timeout(preparation_time)
            print(f"{self.name} {self.surname} dostal {food} a začal jíst {preparation_time:.2f}")

            eating_time_min, eating_time_max = source.foods[food]["eating_time"]
            eating_time = random.randint(eating_time_min, eating_time_max)

            print(f"{self.name} {self.surname} dojedl {food}, aktuální stav hladu je: {min(100,self.state["hunger"])}")

            self.state["money"] -= price
            self.state["hunger"] += satiety

def spawn_groups(env, groups_list, stalls):
    i = 0

    for group in groups_list:
        i += 1

        yield env.timeout(random.randint(1,5))
        print(f"Skupina číslo {i} dorazila na festival(spawn zona) v čase {env.now:.2f}")
        env.process(group.group_decision_making(stalls))
