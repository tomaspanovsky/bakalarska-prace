import simpy
import random
import source
import resources
import foods
import drinks
import times
from data.load_data import load_data
from outputs.code import logs
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
        #if self.festival.now >= 840:
        #    breakpoint()

        """Tato funkce pro daného návštěvníka spustí zvolenou akci"""
        if action != "GO_TO_CONCERT" and member.state["location"] == source.Locations.STAGE_STANDING:
            member.state["location"] = source.Locations.FESTIVAL_AREA

        if action == "GO_TO_SPAWN_ZONE" or action == "GO_TO_ENTRANCE_ZONE" or action == "GO_TO_CHILL_ZONE" or action == "GO_TO_FUN_ZONE":
            location = action.replace("GO_TO_", "")
            location = source.Locations[location]
            yield self.festival.process(member.go_to(location, festival))

        if action == "GO_TO_TENT_AREA":
            member.state["money"] = 50
            if member.state["tent_area_ticket"] == False and member.state["money"] <= festival.get_price("camping_area_price"):
                action = member.next_move(festival, "low_money")
                yield self.festival.process(self.start_action(festival, member, action))

            yield self.festival.process(member.go_to_tent_area(festival))

            if member.accommodation["built"] == False:
                yield self.festival.process(self.start_action(festival, member, "pitch_tent"))

        elif action == "SMOKE":
            yield self.festival.process(member.smoke(festival))
    
        elif action == "GO_TO_FESTIVAL_AREA": #vyřešit určení správného vstupu v resources
            entrances = resources.find_stalls_in_zone(self, festival, "entrances")
            entrance = member.identify_entrance(entrances)

            if entrance == None:

                message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: CHYBA! {member.name} {member.surname} nemůže jít z {member.state["location"].value} do festivalového areálu!"
                print(message)
                logs.log_visitor(member, message)

            yield self.festival.process(member.go_to_festival_area(entrance, festival))

        elif action == "WITHDRAW":
            stall = member.choose_stall(festival, "atm")
            yield self.festival.process(member.withdraw(stall, festival))

        elif action == "GO_FOR_FOOD":
            food = member.choose_food(festival)
            
            if food is None:
                action = member.next_move(festival, "low_money")
                yield self.festival.process(self.start_action(festival, member, action))

            stall = member.choose_stall(festival, "foods", food)
            yield self.festival.process(member.go_for_food(stall, food, festival))

            stall = resources.find_stall_with_shortest_queue_in_zone(member, festival, "tables")

            if stall:
                yield self.festival.process(member.sit(stall, festival, food=food))
            else:
                message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {member.name} {member.surname} si sní {food} za pochodu."
                print(message)
                logs.log_visitor(member, message)
                yield self.festival.process(member.eat(food, festival))

        elif action == "GO_FOR_DRINK":

            drink, alcohol_type = member.choose_drink(festival)
            print(drink)
            print(alcohol_type)
            if drink == None:
                action = member.next_move(festival, "low_money")
                yield self.festival.process(self.start_action(festival, member, action))

            
            stall = member.choose_stall(festival, "drinks", drink)

            if stall == None:
                print("ERROR: Není stánek na pití!")

            yield self.festival.process(member.go_for_drink(festival, stall, drink, alcohol_type))

            if member.state["free_time"] > 0:
                stall = resources.find_stall_with_shortest_queue_in_zone(member, festival, "tables")

                if stall:
                    yield self.festival.process(member.sit(stall, festival, drink=drink))
                
                else:

                    message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {member.name} {member.surname} si vypije {drink} za pochodu."
                    print(message)
                    logs.log_visitor(member, message)
                    
                    yield self.festival.process(member.drink(drink, festival))
        
        elif action == "GO_TO_TOILET":
            need = member.decide_bathroom_action()
            toilet = member.choose_toilet(festival, need)
            yield self.festival.process(member.go_to_toilet(toilet, need, festival))
            stall = member.choose_stall(festival, "handwashing_station")
            yield self.festival.process(member.wash(stall, festival))

        elif action == "GO_TO_SHOWER":

            if member.state["money"] < festival.get_price("shower_price"):
                message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {member.name} {member.surname} nemá dost peněz na sprchu a musí si jít vybrat peníze!"
                print(message)
                logs.log_visitor(member, message)

                action = member.next_move(festival, "low_money")
                yield self.festival.process(self.start_action(festival, member, action))


            shower = member.choose_stall(festival, "showers")
            yield self.festival.process(member.go_to_shower(shower, festival))

        elif action == "BRACELET_EXCHANGE":

            if member.state["money"] <= festival.get_price("on_site_price") and member.state["pre_sale_ticket"] == False:
                
                message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {member.name} {member.surname} nemá koupený lístek z předprodeje a nemá dost peněz na to, aby si koupil lístek a musí si jít vybrat peníze!"
                print(message)
                logs.log_visitor(member, message)

                action = member.next_move(festival, "low_money")
                yield self.festival.process(self.start_action(festival, member, action))

            booth = member.choose_stall(festival, "ticket_booth")
            yield self.festival.process(member.bracelet_exchange(festival, booth))

        elif action == "PITCH_TENT":

            if member.state["money"] <= festival.get_price("camping_area_price"):
                message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {member.name} {member.surname} nemá dost peněz na stanové městečko a musí si jít vybrat peníze!"
                print(message)
                logs.log_visitor(member, message)
        
                action = member.next_move(festival, "low_money")
                yield self.festival.process(self.start_action(festival, member, action))


            camping_area = member.choose_stall(festival, "tent_area")

            if len(camping_area) > 1:
                camping_area = member.find_area_with_more_space(camping_area)
            else:
                camping_area = camping_area[0]

            yield self.festival.process(member.pitch_tent(camping_area, festival))

        elif action == "CHARGE_PHONE":

            if member.state["money"] <= festival.get_price("charging_phone_price"):
                message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {member.name} {member.surname} nemá dost peněz nabití telefonu a musí si jít vybrat peníze!"
                print(message)
                logs.log_visitor(member, message)

                action = member.next_move(festival, "low_money")
                yield self.festival.process(self.start_action(festival, member, action))

            stalls = member.choose_stall(festival, "charging_stall")
            stall = member.find_area_with_more_space(stalls)

            yield self.festival.process(member.charge_phone(stall, festival))
        
        elif action == "RETURN_CUP":
            stall = member.choose_stall(festival, "cup_return")
            yield self.festival.process(member.return_cup(stall, festival))

        elif action == "WASH":
            stall = member.choose_stall(festival, "handwashing_station")
            yield self.festival.process(member.wash(stall, festival))
        
        elif action == "BRUSH_TEETH":
            stall = member.choose_stall(festival, "handwashing_station")
            yield self.festival.process(member.brush_teeth(stall, festival))

        elif action == "SIT":
            stall = member.choose_stall(festival, "tables")
            yield self.festival.process(member.sit(stall, festival))

        elif action == "GO_TO_CONCERT":
            standing_by_stage = member.choose_stall(festival, "standing_at_stage")

            if len(standing_by_stage) == 1:
                standing_by_stage = standing_by_stage[0]

            yield self.festival.process(member.go_to_concert(standing_by_stage, festival))

        elif action == "GO_TO_SIGNING_SESSION":
            signing_stall = member.choose_stall(festival, "signing_stall")
            if len(signing_stall) == 1:
                signing_stall = signing_stall[0]
            yield self.festival.process(member.go_to_signing_session(signing_stall, festival))

        elif action == "BUY_MERCHE":
            merch_stall = member.choose_stall(festival, "merch_stall")
            yield self.festival.process(member.buy_merch(merch_stall, festival))

        elif action == "BUY_CIGARS":

            if resources.can_afford(member, festival.get_price("cigars_price")):
                cigars_stall = member.choose_stall(festival, "smoking")
                yield self.festival.process(member.buy_cigars(cigars_stall, festival))

            else:
                message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {member.name} {member.surname} nemá dost peněz na cigarety a musí si jít vybrat peníze!"
                print(message)
                logs.log_visitor(member, message)

                action = member.next_move(festival, "low_money")
                yield self.festival.process(self.start_action(festival, member, action))

        elif action == "GO_CHILL":
            chill_stall = member.choose_stall(festival, "chill_stall")
            yield self.festival.process(member.go_chill(chill_stall, festival))

        elif action == "GO_SMOKE_WATER_PIPE":

            if resources.can_afford(member, festival.get_price("cigars_price")):
                water_pipe_stall = member.choose_stall(festival, "water_pipe_stall")
                yield self.festival.process(member.go_smoke_water_pipe(water_pipe_stall, festival))

            else:
                message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {member.name} {member.surname} nemá dost peněz na vodní dýmku a musí si jít vybrat peníze!"
                print(message)
                logs.log_visitor(member, message)

                action = member.next_move(festival, "low_money")
                yield self.festival.process(self.start_action(festival, member, action))
        
        elif action == "SLEEP_IN_TENT":
            sleeping_time = random.uniform(240, 480)
            yield self.festival.process(member.sleep_in_tent(sleeping_time, festival))


    def group_decision_making(self, festival):
        """Zvolí všem návštěvníkům skupiny akci a zavolá její spuštění"""

        while True:
            if self.mode == source.Groups_modes.INDIVIDUALLY: 

                for member in self.members:
                    member.update_stats(festival)      
                    member.state["sociability"] -= random.uniform(0.2, 0.5) 
                    action = member.next_move(festival)

                    yield from self.start_action(festival, member, action)

            elif self.type == source.Groups.FAMILY:

                parents = [members for members in self.members if members.age_category == source.Age_category.ADULT]
                parent = random.choice(parents)
                action = parent.next_move(festival)

                for member in self.members:
                    member.update_stats(festival) 
                    yield from self.start_action(festival, member, action)   

            elif self.mode == source.Groups_modes.IN_GROUP:

                leader = random.choice(self.members)
                action = leader.next_move(festival)

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

    def get_name(self):
        name = self.name + " " + self.surname
        return name
    
    def get_data(self):
        data = {"name": self.name, "surname": self.surname, "gender": self.gender, "age_category": self.age_category, "age": self.age, "qualities": self.qualities, "preference": self.preference, "fellows": self.fellows}
        return data
    
    def update_stats(self, festival):

        if self.festival.now >= ((festival.get_actual_day() * 1440) - festival.get_start_time()):
            festival.next_day()

        factor = 1

        self.state["energy"] = min(100, max(0, self.state["energy"] - factor * random.uniform(0.1, 0.5)))
        self.state["hunger"] = min(100, max(0, self.state["hunger"] - self.qualities["hunger_frequency"] * random.uniform(0.1, 0.5)))
        self.state["thirst"] = min(100, max(0, self.state["thirst"] - factor * random.uniform(0.1, 0.5)))
        self.state["wc"] = min(100, max(0, self.state["wc"] - factor * random.uniform(0.1, 0.5)))
        self.state["hygiene"] = min(100, max(0, self.state["hygiene"] - factor * random.uniform(0.1, 0.5)))
        self.state["drunkenness"] = min(100, max(0, self.state["drunkenness"] - self.qualities["alcohol_tolerance"] * random.uniform(0.1, 0.5)))

        if self.inventory["phone"] != None:
            self.inventory["phone"].battery = min(100, max(0, self.inventory["phone"].battery - random.uniform(0.1, 0.5)))

    def next_move(self, festival, need = None):
        """funkce, která rozhodne následující krok návštěvníka"""

        if need == None:
            need = self.urgent_need(festival)

        return self.resolve_need(need)
    
    def urgent_need(self, festival):
        #povinné kroky při příjezdu
        
        if self.state["entry_bracelet"] == False and self.accommodation["built"] == False:
            return random.choice(["living", "bracelet_exchange"])

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
        
        if self.my_band_playing(festival) and self.state["location"] != source.Locations.STAGE_STANDING:
            return "band_playing"            

        if self.my_band_has_signing_session() and self.state["location"] != source.Locations.SIGNING_STALL:
            return "meet_band"
        
        if self.deciding_smoking():
            return "smoke"
    
        need, value = max(needs_scores.items(), key=lambda x: x[1])

        if value <= 40 and self.some_band_playing(festival):
            return "band_playing"
        else:
            return need

    def my_band_playing(self, festival):
        my_bands = self.preference["favourite_bands"]
        my_bands = sorted(my_bands, key=lambda x: x["start_playing_time"])
        
        if self.shows_will_end(festival):
            return False
        
        for band in my_bands:
            my_band_start_playing = band["start_playing_time"]
            my_band_end_playing = band["end_playing_time"]

            if my_band_start_playing - 20 < self.festival.now < my_band_end_playing:
                return True
        
        return False
    
    def shows_will_end(self, festival):
        limit = festival.get_time("last_show_ends") - 15
        return self.festival.now >= limit

    def some_band_playing(self, festival):
        if self.shows_will_end(festival):
            return False
        
        lineup = festival.get_lineup()
        day = festival.get_actual_day() - 1

        if len(lineup) == day:
            return False
        
        return (lineup[day][0]["start_playing_time"] - 20) < self.festival.now < lineup[day][len(lineup[0])-1]["end_playing_time"] - 5
        
    def any_bands_this_day(festival):
        day = festival.get_actual_day() - 1
        

    def my_band_has_signing_session(self):
        my_bands = self.preference["favourite_bands"]
        my_bands = sorted(my_bands, key=lambda x: x["start_signing_session"])

        for band in my_bands:
            my_band_start_signing = band["start_signing_session"]
            my_band_end_signing = band["end_signing_session"]

            if my_band_start_signing - 30 < self.festival.now < my_band_end_signing:
                return True
        
        return False

    def deciding_smoking(self):
        """funkce která rozhodne zda si kuřák chce zapálit cigaretu"""

        if self.preference["smoker"] == True:
            craving_for_a_cigarette = random.randint(0, 12 - self.state["level_of_addiction"])

            if craving_for_a_cigarette <= 2 and self.state["nicotine"] != 100:
                return True 

            elif self.state["nicotine"] < 30 or self.state["mood"] < 30:
                return True
        
        return False

# -----------------------------------------------POHYB---------------------------------------------------------

    def go_to(self, location, festival):
        """Funkce která obsluje návštěvníkův přesun do jiné zóny bez vstupní prohlídky"""

        message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} jde do {location.value}"
        print(message)
        logs.log_visitor(self, message)

        yield self.festival.timeout(10)

        message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} dorazil do {location.value}"
        print(message)
        logs.log_visitor(self, message)
        
        self.state["location"] = location
    
    def go_to_festival_area(self, entrance, festival):

        yield self.festival.timeout(10)

        message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} přišel ke vstupu."
        print(message)
        logs.log_visitor(self, message)
        
        start_waiting = self.festival.now

        with entrance.resource.request() as req:

            will_wait = entrance.resource.count >= entrance.resource.capacity

            yield req

            if will_wait:
                waiting_time = self.festival.now - start_waiting
                message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} čekal/a {waiting_time} ve frontě u vstupu."
                print(message)
                logs.log_visitor(self, message)
            else:
                message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} prošel/a vstupem bez čekání."
                print(message)
                logs.log_visitor(self, message)

            entry_time = random.uniform(1, 5)
            yield self.festival.timeout(entry_time)

            self.state["location"] = source.Locations.FESTIVAL_AREA

            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} dorazil do festivalového areálu."
            print(message)
            logs.log_visitor(self, message)

    def go_to_tent_area(self, festival):

        message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} jde do stanového městečka."
        print(message)
        logs.log_visitor(self, message)

        yield self.festival.timeout(10)

        if self.state["tent_area_ticket"] == None:

            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} dorazil/a ke stanovému městečku a nemá koupený lístek do stanového městečka."
            print(message)
            logs.log_visitor(self, message)

            yield self.festival.timeout(random.uniform(2, 5))
            self.state["money"] -= festival.get_price("camping_area_price")
            self.state["tent_area_ticket"] = True
            festival.add_income(festival.get_price("camping_area_price"))

            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} si koupil/a vstupenku do stanového městečka."
            print(message)
            logs.log_visitor(self, message)

            self.state["location"] = source.Locations.TENT_AREA

        else:
            yield self.festival.timeout(random.uniform(0, 1))
            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} již má vstupenku a dorazil do stanového městečka."
            print(message)
            logs.log_visitor(self, message)
            
            self.state["location"] = source.Locations.TENT_AREA

    def identify_entrance(self, entrances):
        location = self.state["location"]

        for entrance in entrances:
            if location == entrance.from_zone:
                return entrance

        return entrances[0] #opravit

    def smoke(self, festival):
        #Funkce která obsluhuje návštěvníkovo kouření cigaret

        if self.preference["smoker"] == True:

            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} si zapálil cigaretu a začal kouřit."
            print(message)
            logs.log_visitor(self, message)

        else:
            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} začal čekat, než si člen skupiny zapálí cigaretu."
            print(message)
            logs.log_visitor(self, message)

        yield self.festival.timeout(random.uniform(5, 10))
        
        if self.preference["smoker"] == True:

            self.state["cigarettes"] -= 1
            self.state["nicotine"] = min(self.state["nicotine"] + 30, 100)
            self.state["mood"] += min(self.state["mood"] + 30, 100)
            
            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} dokouřil, stav nikotinu je: {self.state["nicotine"]}"
            print(message)
            logs.log_visitor(self, message)

        else:
            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} přestal čekat, až si člen skupiny zapálí."
            print(message)
            logs.log_visitor(self, message)

# -----------------------------------------------JÍDLO---------------------------------------------------------

    def choose_food(self, festival):
        """Vybere návštěvníkovi jídlo, které si dá viz algoritmy/jidlo.png"""

        if self.state["hunger"] <= 30:
            return foods.choose_food_with_great_satiety_in_actual_zone(self, festival)
        
        else:

            presence, stall = foods.is_my_favourite_food_in_actual_zone(self, festival)
            if presence is True:

                if resources.is_big_queue_at_stall(self, stall):
                    stall = foods.find_food_stall_with_shortest_queue_in_zone(self, festival)
                    return foods.choose_random_food_from_stall(self, stall)

                else:
                    if resources.can_afford(self, source.foods[self.preference["favourite_food"]]):
                        return self.preference["favourite_food"]
                    else: 
                        return None
                
            else:
                return foods.choose_random_food_from_actual_zone(self, festival)

    def go_for_food(self, stall, food, festival):
        """funkce která simuluje návštěvníkovo koupení jídla ve stánku"""
        
        price = source.foods[food]["price"]
        time_min, time_max = source.foods[food]["preparation_time"]

        message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} přišel ke stánku {stall.stall_name}."
        print(message)
        logs.log_visitor(self, message)

        start_waiting = self.festival.now

        # čekání na stánek
        with stall.resource.request() as req:
            
            will_wait = stall.resource.count >= stall.resource.capacity

            yield req

            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} přišel na řadu a je u stánku {stall.stall_cz_name}"
            print(message)
            logs.log_visitor(self, message)

            if will_wait:
                waiting_time = self.festival.now - start_waiting
                
                message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} čekal/a {waiting_time} ve frontě u stánku {stall.stall_cz_name} minut."
                print(message)
                logs.log_visitor(self, message)
            
            preparation_time = random.randint(time_min, time_max)

            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} čeká na {food} a příprava bude trvat {preparation_time}"
            print(message)
            logs.log_visitor(self, message)

            yield self.festival.timeout(preparation_time)
            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} dostal {food}"
            print(message)
            logs.log_visitor(self, message)
            
        self.state["money"] -= price
            
    def eat(self, food, festival):
        eating_time_min, eating_time_max = source.foods[food]["eating_time"]
        eating_time = random.randint(eating_time_min, eating_time_max)
        satiety = source.foods[food]["satiety"]

        message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} začal/a jíst {food}"
        print(message)
        logs.log_visitor(self, message)
        yield self.festival.timeout(eating_time)
        self.state["hunger"] = min(100, self.state["hunger"] + satiety)
        message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} dojedl/a {food}, aktuální stav hladu je: {self.state["hunger"]}"
        print(message)
        logs.log_visitor(self, message)

# -----------------------------------------------STOLY---------------------------------------------------------------

    def sit(self, stall, festival, food = None, drink = None):
        """Funkce, která obsluju návštěvníkův pokus najít volný stůl a sednout si"""

        yield self.festival.timeout(random.uniform(0, 2))
        message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} hledá místo u stolu k sednutí"
        print(message)
        logs.log_visitor(self, message)
        
        yield self.festival.timeout(random.uniform(0, 2))

        if stall.resource.count >= stall.resource.capacity:
            patience_index = self.qualities["patience"] * random.uniform(0.5, 1.5)

            if patience_index > 5:
                message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} si nemá kam sednout a jde pryč"
                print(message)
                logs.log_visitor(self, message)
                return None

            else:
                message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} si nemá kam sednout ale počká než se uvolní místo u stolu."
                print(message)
                logs.log_visitor(self, message)

        start_waiting = self.festival.now
        with stall.resource.request() as req:

            yield req

            waiting_time = self.festival.now - start_waiting
            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} si sedl ke stolu."
            print(message)
            logs.log_visitor(self, message)

            if waiting_time > 0:
                message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} čekal na volné místo u stolu {waiting_time} minut."
                print(message)
                logs.log_visitor(self, message)

            start_sitting = self.festival.now

            if food and drink:
                yield self.festival.process(self.eat(food, festival))
                yield self.festival.process(self.drink(drink, festival))
                sitting_time = self.festival.now - start_sitting

            elif food:
                
                yield self.festival.process(self.eat(food, festival))
                sitting_time = self.festival.now - start_sitting

            elif drink:

                yield self.festival.process(self.drink(drink, festival))
                sitting_time = self.festival.now - start_sitting

            else:
                sitting_time = random.uniform(0 , self.state["free_time"])
                yield self.festival.timeout(sitting_time)

                message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} odchází od stolu."
                print(message)
                logs.log_visitor(self, message)

            self.state["energy"] = min(100, self.state["energy"] + ((sitting_time / 60) * 20))

# ------------------------------------------------PITÍ----------------------------------------------------------------
    def choose_drink(self, festival):
        """Vybere návštěvníkovi, které pití dá viz jidlo a pití.png"""

        drink_stalls_in_zone = resources.find_stalls_in_zone(self, festival, "drinks")

        if self.preference["alcohol_consumer"] == True:

            if self.is_visitor_drunk():
                presence, stall = drinks.is_my_favourite_drink_in_actual_zone(self, festival, "soft_drink", drink_stalls_in_zone)

                if presence is True:
                    if resources.is_big_queue_at_stall(stall):
                        stall = drinks.find_drink_stall_with_shortest_queue_in_zone(self, festival)
                        return drinks.choose_random_drink_from_stall(self, stall, "soft_drink"), None
                    else:
                        if resources.can_afford(self, source.drinks[self.preference["favourite_soft_drink"]]):
                            return self.preference["favourite_soft_drink"]
                        else:
                            return None, None
                else:
                    return drinks.choose_random_drink_from_actual_zone(self, festival, "soft_drink", drink_stalls_in_zone), None
            
            else:
                kinds_of_alcohol = drinks.what_kind_of_alcohol_is_in_actual_zone(self, festival, drink_stalls_in_zone)
                alcohol_type = self.choose_type_of_alcohol(kinds_of_alcohol)

                if alcohol_type == "favourite_alcohol":
                    if resources.can_afford(self, source.drinks[self.preference["favourite_alcohol"]]):
                        return self.preference["favourite_alcohol"], None
                    else:
                        return None, None
                else: 
                    return drinks.choose_random_drink_from_actual_zone(self, festival, alcohol_type, drink_stalls_in_zone), alcohol_type 
                    
        else:
            presence, stall = drinks.is_my_favourite_drink_in_actual_zone(self, festival, "soft_drink", drink_stalls_in_zone)

            if presence is True:

                if resources.is_big_queue_at_stall(stall):
                    stall = drinks.find_drink_stall_with_shortest_queue_in_zone(self, festival)
                    return drinks.choose_random_drink_from_stall(self, stall, "soft_drink"), None
                
                else:
                    if resources.can_afford(self, source.drinks[self.preference["favourite_soft_drink"]]):
                        return self.preference["favourite_soft_drink"], None
                    else:
                        return None, None
                        
            else:
                return drinks.choose_random_drink_from_actual_zone(self, festival, "soft_drink", drink_stalls_in_zone), None
        
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

        plastic_cup_price = festival.get_price("plastic_cup_price")
        price = source.drinks[drink]["price"]
        time_min, time_max = source.drinks[drink]["preparation_time"]
        start_waiting = self.festival.now

        # čekání na stánek
        with stall.resource.request() as req:

            yield req
            will_wait = stall.resource.count >= stall.resource.capacity
            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} přišel na řadu a je u stánku {stall.stall_cz_name} v zóně {self.state["location"].value}"
            print(message)
            logs.log_visitor(self, message)

            if will_wait:
                waiting_time = self.festival.now - start_waiting
                message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} čekal u stánku {stall.stall_cz_name} {waiting_time}"
                print(message)
                logs.log_visitor(self, message)

            preparation_time = random.randint(time_min, time_max)

            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} čeká na {drink} a příprava bude trvat {preparation_time}"
            print(message)
            logs.log_visitor(self, message)
            yield self.festival.timeout(preparation_time)

            if alcohol_type is not None:
                if self.inventory["plastic_cup"] == None:
                    self.inventory["plastic_cup"] == True
                    self.state["money"] -= plastic_cup_price
                    message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} neměl kelímek a musel si koupit nový"
                    print(message)
                    logs.log_visitor(self, message)

            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} dostal {drink}"
            print(message)
            logs.log_visitor(self, message)

        self.state["money"] -= price

    def drink(self, drink_name, festival):
        drink_data = source.drinks[drink_name]
        drinking_time_min = drink_data["drinking_time"][0]
        drinking_time_max = drink_data["drinking_time"][1]
        drinking_time = random.uniform(drinking_time_min, drinking_time_max)

        message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} začal/a pít {drink_name}."
        print(message)
        logs.log_visitor(self, message)
        
        yield self.festival.timeout(drinking_time)
        
        message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} dopil/a {drink_name}."
        print(message)
        logs.log_visitor(self, message)

        if "hydration" in drink_data:
            self.state["thirst"] = min(drink_data["hydration"] + self.state["thirst"], 100)

        if "drunkness" in drink_data:
            self.state["drunkenness"] = min(drink_data["drunkness"] + self.state["drunkenness"], 100)

        if "energy" in drink_data:
            self.state["energy"] = min(self.state["energy"] + drink_data["energy"], 100)

# -----------------------------------------------VÝBĚR PENĚZ---------------------------------------------------------

    def withdraw(self, atm, festival):
        yield self.festival.timeout(random.uniform(0, 2))

        start_waiting = self.festival.now
        message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} přišel k bankomatu."
        print(message)
        logs.log_visitor(self, message)
        with atm.resource.request() as req:
            
            yield req
            waiting_time = self.festival.now - start_waiting

            if waiting_time > 0:
                message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} čekal/a ve frontě u bankomatu {waiting_time} minut."
                print(message)
                logs.log_visitor(self, message)

            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} přišel/a na řadu a začal/a vybírat peníze."
            print(message)
            logs.log_visitor(self, message)
            
            yield self.festival.timeout(random.uniform(1, 5))

            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} dokončil/a výběr peněz."
            print(message)
            logs.log_visitor(self, message)

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
  
    def go_to_toilet(self, toilet, need, festival):
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
            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} přišel k {toilet.stall_cz_name}"
            print(message)
            logs.log_visitor(self, message)

            yield req

            if will_wait:
                waiting_time = self.festival.now - start_waiting
                message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} čekal na volnou {toilet.stall_cz_name} {waiting_time}"
                print(message)
                logs.log_visitor(self, message)

            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} vchází na {toilet.stall_cz_name}."
            print(message)
            logs.log_visitor(self, message)

            yield self.festival.timeout(wc_time)
            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} odchází z {toilet.stall_cz_name}."
            print(message)
            logs.log_visitor(self, message)

    def wash(self, stall, festival):
        yield self.festival.timeout(random.uniform(0, 2))

        start_waiting = self.festival.now
        message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} přišel/a k umývárně."
        print(message)
        logs.log_visitor(self, message)

        with stall.resource.request() as req:
            
            yield req
            waiting_time = self.festival.now - start_waiting

            if waiting_time > 0:
                message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} čekal/a {waiting_time}, než se u umývárny uvolní místo."
                print(message)
                logs.log_visitor(self, message)


            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} si začal/a umývat ruce."
            print(message)
            logs.log_visitor(self, message)

            yield self.festival.timeout(random.uniform(0, 1.5))
            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} dokončil/a umytí rukou."
            print(message)
            logs.log_visitor(self, message)

            self.state["hygiene"] += random.randint(10, 20)
        
    def brush_teeth(self, stall, festival):
        yield self.festival.timeout(random.uniform(0, 2))

        start_waiting = self.festival.now

        message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} přišel/a k umývárně."
        print(message)
        logs.log_visitor(self, message)

        with stall.resource.request() as req:
            
            yield req
            waiting_time = self.festival.now - start_waiting

            if waiting_time > 0:
                message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} čekal/a {waiting_time}, než se u umývárny uvolní místo."
                print(message)
                logs.log_visitor(self, message)

            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} si začal/a čistit zuby."
            print(message)
            logs.log_visitor(self, message)

            yield self.festival.timeout(random.uniform(0, 1.5))
            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} dokončil/a čištění zubů."
            print(message)
            logs.log_visitor(self, message)
            self.state["hygiene"] += random.randint(15, 30)

# -------------------------------------------------SPRCHY ---------------------------------------------------------
            
    def go_to_shower(self, shower, festival):
        """funkce obsluhjící návštěvníka ve sprše"""
        
        if self.gender == source.Gender.MALE:
            shower_time = random.uniform(5, 15)
        else:
            shower_time = random.uniform(12, 20)

        with shower.resource.request() as req:
            start_waiting = self.festival.now
            will_wait = shower.resource.count >= shower.resource.capacity

            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} přišel/la ke sprchám"
            print(message)
            logs.log_visitor(self, message)

            yield req

            if will_wait:
                waiting_time = self.festival.now - start_waiting
                message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} čekal/a na volnou spruchu {waiting_time}"
                print(message)
                logs.log_visitor(self, message)

            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} vchází do sprchy."
            print(message)
            logs.log_visitor(self, message)

            yield self.festival.timeout(shower_time)
            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} odchází ze sprchy."
            print(message)
            logs.log_visitor(self, message)       
        
        self.state["money"] -= festival.get_price("shower_price")
        self.state["hygiene"] = 100

# --------------------------------------------STANOVÉ MĚSTEČKO------------------------------------------------------

    def pitch_tent(self, camping_area, festival):
            #funkce která obsluhuje návštěvníkovo stavění stanu
            
            yield self.festival.timeout(random.uniform(0, 2))

            num_fellows = len(self.fellows)
            pitch_time = random.uniform(15, 20) - num_fellows * 1.5
            free_space = False
            i = -1

            for position in camping_area.resource:
                i += 1

                if position == []:
                    free_space = True

                    if self.accommodation["owner"] == False:
                        
                        message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} pomáhá kolegovi postavit stan."
                        print(message)
                        logs.log_visitor(self, message)

                        yield self.festival.timeout(pitch_time)
                        message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} s kolegou dostavěli stan."
                        print(message)
                        logs.log_visitor(self, message)
                    else:        
                        position.append(self.inventory["tent"])
                        message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} staví stan."
                        print(message)
                        logs.log_visitor(self, message)
                        
                        yield self.festival.timeout(pitch_time)
                        message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} dostavěl stan."
                        print(message)
                        logs.log_visitor(self, message)


                    self.accommodation["i"] = i
                    self.accommodation["built"] = True
                    self.accommodation["camping_area"] = camping_area
                    break
                
            if not free_space:
                message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: Došlo místo ve stanovém městečku!"
                print(message)
                logs.log_visitor(self, message)

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
            return areas[0]

    def sleep_in_tent(self, time, festival):
        
        yield self.festival.timeout(random.uniform(0, 2))

        message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} došel/a do stanu."
        print(message)
        logs.log_visitor(self, message)

        with self.accommodation["camping_area"].resource[self.accommodation["i"]][0].request() as req:
            
            yield req
            
            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} jde spát."
            print(message)
            logs.log_visitor(self, message)
            
            yield self.festival.timeout(time)
            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} se vzbudil/a."
            print(message)
            logs.log_visitor(self, message)

            self.state["energy"] += (time / 60) * 12.5

# ------------------------------------------------POKLADNY ---------------------------------------------------------
    def bracelet_exchange(self, festival, ticket_booth):
        #funkce, která simuluje návštěvníkovo ukázání lístku u pokladny, výměnou za pásek na ruku umožňující vstup do arálu.
        #Případně si návštěvník může lístek koupit v pokladně na místě, pokud ho nemá z předprodeje
        
        with ticket_booth.resource.request() as req:

            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} přišel/la k pokladnám."
            print(message)
            logs.log_visitor(self, message)
            
            start_waiting = self.festival.now
            will_wait = ticket_booth.resource.count >= ticket_booth.resource.capacity

            yield req
            
            if will_wait:
                waiting_time = self.festival.now - start_waiting
                message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} čekal ve frontě u pokladny {waiting_time}"
                print(message)
                logs.log_visitor(self, message)

            if self.state["pre_sale_ticket"] == True:
                bracelet_exchange_time = random.uniform(1,2)
            else:
                bracelet_exchange_time = random.uniform(2, 3)

            yield self.festival.timeout(bracelet_exchange_time)
            
            self.state["entry_bracelet"] = True

            if self.state["pre_sale_ticket"] == False and self.age > 14:
                self.state["money"] -= festival.get_price("on_site_price")
                festival.add_income(festival.get_price("on_site_price"))

                message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} si koupil lístek na místě, dostal pásek, a odešel z pokladny."
                print(message)
                logs.log_visitor(self, message)
            else:
                message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} měl lístek koupený z předprodeje, dostal pásek, a odešel z pokladny."
                print(message)
                logs.log_visitor(self, message)
# ----------------------------------------------NABÍJECÍ STÁNEK ---------------------------------------------------------

    def charge_phone(self, stall, festival):
        """Funkce na nabití najení telefonů návštěvníků"""

        yield self.festival.timeout(random.uniform(1, 3))

        i = -1

        message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} přišel/la k nabíjecímu stánku."    
        print(message)
        logs.log_visitor(self, message)

        free_space = False

        for position in stall.resource:
            i += 1

            if position == []:
                free_space = True

                stall.resource[i] = self.inventory["phone"]
                    
                message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} si dává nabít mobil do nabíjecího stánku."
                print(message)
                logs.log_visitor(self, message)

                yield self.festival.timeout(random.uniform(1,5))
                message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} si dal mobil do nabíjecího stánku."
                print(message)
                logs.log_visitor(self, message)

                self.state["money"] -= festival.get_price("charging_phone_price")
                festival.add_income(festival.get_price("charging_phone_price"))
                festival.add_phone(self.inventory["phone"])
                self.inventory["phone"] = None
                break
            
        if not free_space:
            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: Došly pozice na nabíjení v nabíjecím stánku!"
            print(message)
            logs.log_visitor(self, message)

    def charging(self, phones):
        for phone in phones:
            phone.charging()

# ----------------------------------------------NABÍJECÍ STÁNEK ---------------------------------------------------------

    def return_cup(self, stall, festival):
        yield self.festival.timeout(random.uniform(0, 2))

        start_waiting = self.festival.now
        message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} přišel/a k výkupu kelímků."
        print(message)
        logs.log_visitor(self, message)

        with stall.resource.request() as req:
            
            yield req
            waiting_time = self.festival.now - start_waiting

            if waiting_time > 0:
                message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} čekal/a ve frontě {waiting_time} minut."
                print(message)
                logs.log_visitor(self, message)

            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} přišel/a na řadu a začal/a vracet kelímek."
            print(message)
            logs.log_visitor(self, message)
            
            yield self.festival.timeout(random.uniform(1, 5))

            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} vrátil/a kelímek."
            print(message)
            logs.log_visitor(self, message)

            self.state["money"] += festival.price("plastic_cup_price")
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

        if actual_zone == source.Locations.STAGE_STANDING or actual_zone == source.Locations.SIGNING_STALL:
            actual_zone = source.Locations.FESTIVAL_AREA

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
    
# --------------------------------------------KONCERTY--------------------------------------------------------

    def go_to_concert(self, standing_by_stage, festival, position = None):
        position_map = {"first_lines": "prvních řadách", "middle": "prostředním sektoru", "back": "zadním sektoru"}
        bands = festival.get_lineup()[festival.get_actual_day()-1]
        pause_time = festival.get_pause()
        actual_band = None

        for band in bands:

            if self.festival.now >= (band["start_playing_time"] - pause_time) and (self.festival.now < band["end_playing_time"]):
                actual_band = band
                break

        if self.state["location"] != source.Locations.STAGE_STANDING:
            self.state["location"] = source.Locations.STAGE_STANDING

            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} jde k podiu na koncert kapely {actual_band["band_name"]}."
            print(message)
            logs.log_visitor(self, message)

            yield self.festival.timeout(random.uniform(1, 3))

        else:
            if actual_band:
                resource = self.state["location_stage"]
                position = self.state["location_stage_position"]
                time_to_start = actual_band["start_playing_time"] - self.festival.now

                message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} zůstane u podia i na koncert kapely {actual_band["band_name"]}, který je za {time_to_start} minut."
                print(message)
                logs.log_visitor(self, message)
                yield self.festival.timeout(actual_band["end_playing_time"] - self.festival.now) 

                message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: Koncert skončil a {self.name} {self.surname} přemýšlí, co bude dělat dál."
                print(message)
                logs.log_visitor(self, message)
                return
            
            else:
                return

        if position:
            if position == "first_lines":
                position = position_map[standing_by_stage.resource[0][0]]
                resource = standing_by_stage.resource[0][1]

            elif position == "middle":
                position = position_map[standing_by_stage.resource[1][0]]
                resource = standing_by_stage.resource[1][1]

            else:
                position = position_map[standing_by_stage.resource[2][0]]
                resource = standing_by_stage.resource[2][1]
        
        else:
    
            if standing_by_stage.resource[0][1].count < standing_by_stage.resource[0][1].capacity:
                position = position_map[standing_by_stage.resource[0][0]]
                resource = standing_by_stage.resource[0][1]
            elif standing_by_stage.resource[1][1].count < standing_by_stage.resource[1][1].capacity:
                position = position_map[standing_by_stage.resource[1][0]]
                resource = standing_by_stage.resource[1][1]
            else:
                position = position_map[standing_by_stage.resource[2][0]]
                resource = standing_by_stage.resource[2][1]
        
        self.state["location_stage"] = resource
        self.state["location_stage_position"] = position
        with resource.request() as req:
            
            yield req
    
            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} je u podia v {position} na koncertě kapely {actual_band["band_name"]}."
            print(message)
            logs.log_visitor(self, message)
            
            yield self.festival.timeout(actual_band["end_playing_time"] - self.festival.now)

            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: Koncert skončil a {self.name} {self.surname} přemýšlí, co bude dělat dál."
            print(message)
            logs.log_visitor(self, message)
# ---------------------------------------------AUTOGRAMIÁDY------------------------------------------------------------

    def go_to_signing_session(self, stall, festival):
        """ resource[0] -> kapela (1), 
            resource[1] -> 5 místa u kapely (podepisování), 
            resource[2] -> fronta (kapacita fronty) - 4 lidi co jsou už u kapely 
            resource[3] -> None, nebo instance kapely, která má zrovna autogramiádu"""

        actual_band = stall.resource[3]
        
        for item in self.inventory["autographs"]:
            if actual_band["band_name"] in item:
                yield self.festival.timeout(1)
                return
        
        message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} jde na autogramiádu kapely {actual_band["band_name"]}."
        print(message)
        logs.log_visitor(self, message)

        yield self.festival.timeout(random.uniform(1,2))

        with stall.resource[2].request() as req_queue:
            start_wait = self.festival.now

            yield req_queue

            if self.festival.now < actual_band["start_signing_session"]:
                message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} je ve frontě a čeká na začátek autogramiády kapely {actual_band["band_name"]}."
                print(message)
                logs.log_visitor(self, message)

                
                yield self.festival.timeout(actual_band["start_signing_session"] - self.festival.now)

            else:
                message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} je ve frontě na autogramiádě kapely {actual_band["band_name"]} a čeká než příjde na řadu."
                print(message)
                logs.log_visitor(self, message)
        
            with stall.resource[1].request() as req_sig:
                
                yield req_sig

                waiting_time = self.festival.now - start_wait
                message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} přišel/a na řadu a právě dostává autogramy od kapely {actual_band["band_name"]}."
                print(message)
                logs.log_visitor(self, message)

                yield self.festival.timeout(random.uniform(0, 2))

                message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} dostal/a autogramy od kapely {actual_band["band_name"]} a čekal na něj ve frontě {waiting_time} minut."
                print(message)
                logs.log_visitor(self, message)
                self.inventory["autographs"].append(f"{actual_band["band_name"]}")

#---------------------------------------------------CHILL ZÓNA----------------------------------------------------------------

#-------------------------------------------CHILL ZÓNA - Cigaretový stánek---------------------------------------------------------
    
    def buy_cigars(self, stall, festival):

        if self.preference["smoker"] == False:
            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} čeká, než si jeho kolega koupí cigarety."
            print(message)
            logs.log_visitor(self, message)
            yield self.timeout(random.uniform(0,2)) #dodělat aby čekal stejně dlouho jako ten co kupuje cigára
            return
        
        how_many_cigars = (self.state["level_of_addiction"] // 2) * 20

        yield self.festival.timeout(random.uniform(0, 2))
        message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} přišel/a k cigaretovému stánku."
        print(message)
        logs.log_visitor(self, message)

        with stall.resource.request as req:

            start_waiting = self.festival.now

            yield req

            if self.festival.now > start_waiting:
                waiting_time = self.festival.now - start_waiting
                message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} čekal ve frontě u cigaretového stánku než přišel na řadu {waiting_time} minut."
                print(message)
                logs.log_visitor(self, message)

            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} kupuje {how_many_cigars // 20} krabiček cigaret."
            print(message)
            logs.log_visitor(self, message)

            yield self.festival.timeout(random.uniform(0,2))

            self.state["money"] - ((how_many_cigars // 20) * festival.get_price("cigars_price"))
            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} nakoupil cigarety a aktuálně jich má {self.state["cigarettes"]}."
            print(message)
            logs.log_visitor(self, message)
                

#-------------------------------------------CHILL ZÓNA - Chill stánek---------------------------------------------------------
    
    def go_chill(self, stall, festival):

        yield self.festival.timeout(random.uniform(0, 2))
        message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} přišel/a k chill stánku."
        print(message)
        logs.log_visitor(self, message)

        with stall.resource.request() as req:

            result = yield req | self.festival.timeout(0)

            if req not in result:
                message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} odešel od chill stánku, protože už je plně obsazený."
                print(message)
                logs.log_visitor(self, message)
                return

            chilling_time = random.uniform(0, self.state["free_time"])
            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} je v chill stánku a bude odpočívat {chilling_time} minut."
            print(message)
            logs.log_visitor(self, message)

            yield self.festival.timeout(chilling_time)
            self.state["energy"] += chilling_time * 0.5

#-------------------------------------------CHILL ZÓNA - Stánek s vodníma dýmkama---------------------------------------------------------

        def go_smoke_water_pipe(self, stall, festival):

            yield self.festival.timeout(random.uniform(0, 2))
            message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} přišel/a k stánku s vodníma dýmkama."
            print(message)
            logs.log_visitor(self, message)

            with stall.resource.request() as req:

                result = yield req | self.festival.timeout(0)

                if req not in result:
                    message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} odešel od stánku s vodníma dýmkama, protože už je plně obsazený."
                    print(message)
                    logs.log_visitor(self, message)
                    return
                
                self.state["money"] -= festival.get_price("water_pipe")
                smoking_time = random.uniform(0, self.state["free_time"])
                message = f"ČAS {times.get_real_time(self.festival, festival.get_start_time())}: {self.name} {self.surname} je ve stánku s vodníma dýmkama a bude odpočívat a kouřit {smoking_time} minut."
                print(message)
                logs.log_visitor(self, message)

                yield self.festival.timeout(smoking_time)
                self.state["energy"] += smoking_time * 0.5
                self.state["nicotine"] += smoking_time * 1.5

#-------------------------------------------------MERCHE---------------------------------------------------------------

    def buy_merche(self, festival):
        pass

# ------------------------------------------PŘÍJEZD NÁVŠTĚVNÍKŮ--------------------------------------------------------

def spawn_groups(env, groups_list, festival):
    i = 0

    for group in groups_list:
        i += 1

        yield env.timeout(random.randint(1,5))
        print(f"ČAS {times.get_real_time(env, festival.get_start_time())}: Skupina číslo {i} dorazila na festival(spawn zona)")
        env.process(group.group_decision_making(festival))


