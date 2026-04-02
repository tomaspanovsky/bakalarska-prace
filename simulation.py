import simpy
import random
import source
import resources
import foods
import items
import times
import copy
from data.load_data import load_data
from outputs.code import logs
from collections import deque

class Group:
    def __init__(self, festival, members, type): #typ = rodina/skupina/jednotlivec
        self.env = festival
        self.id = id
        self.members = members
        self.type = type

    def start_action(self, festival, member, action):
        """Tato funkce pro daného návštěvníka spustí zvolenou akci"""

        direct_connections = ["GO_TO_SPAWN_ZONE", "GO_TO_ENTRANCE_ZONE", "GO_TO_CHILL_ZONE", "GO_TO_FUN_ZONE", "GO_TO_FESTIVAL_AREA"]
        member.is_busy = True
        
        if action != "GO_TO_CONCERT" and member.state["location"] == source.Locations.STAGE_STANDING:
            member.state["location"] = source.Locations.FESTIVAL_AREA

        if action in direct_connections:
            location = action.replace("GO_TO_", "")
            location = source.Locations[location]
            yield self.env.process(member.go_to(location, festival))

        elif "ENTRY" in action: 
            location = action.rsplit("_ENTRY_", 1)[0]
            entry_id = action.rsplit("_", 1)[1]

            entrances = resources.find_stalls_in_zone(self, festival, "entrances")
            entry = member.identify_entrance(entrances, entry_id)

            if entry is None:

                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: CHYBA! {member.name} {member.surname} nemůže jít z {member.state["location"].value} do festivalového areálu!"
                print(message)
                logs.log_visitor(member, message)

            yield self.env.process(member.go_to_festival_area(entry, festival))

        if action == "GO_TO_TENT_AREA":
            yield self.env.process(member.go_to_tent_area(festival))

        elif action == "SMOKE":
            yield self.env.process(member.smoke(festival))

        elif action == "WITHDRAW":
            stall = member.choose_stall(festival, "atm")
            yield self.env.process(member.withdraw(stall, festival))

        elif action == "GO_FOR_FOOD":
            food = member.choose_food(festival)
            
            if food is None:
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {member.name} {member.surname} nemá dost peněz na to aby si mohl koupit jídlo a bude si muset jít vybrat peníze."
                print(message)
                logs.log_visitor(member, message)
                member.is_busy = False
                member.state["low_money"] = True
            
            else:
                stall = member.choose_stall(festival, "foods", food)
                yield self.env.process(member.go_for_food(stall, food, festival))

                stall = resources.find_stall_with_shortest_queue_in_zone(member, festival, "tables")

                if stall:
                    yield self.env.process(member.sit(stall, festival, food=food))

                else:
                    message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {member.name} {member.surname} si sní {food} za pochodu."
                    print(message)
                    logs.log_visitor(member, message)
                    yield self.env.process(member.eat(food, festival))

        elif action == "GO_FOR_DRINK":

            drink, alcohol_type = member.choose_drink(festival)
           
            if drink == None:

                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {member.name} {member.surname} nemá dost peněz na to aby si mohl koupit pití a bude si muset jít vybrat peníze."
                print(message)
                logs.log_visitor(member, message)
                member.is_busy = False
                member.state["low_money"] = True
                return

            stall = member.choose_stall(festival, "drinks", drink)

            if stall is None:
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {member.name} {member.surname} si chce koupit {drink}, ale v zóně není žádný stánek, který by ho prodával."
                print(message)
                logs.log_visitor(member, message)
                member.is_busy = False
                return

            yield self.env.process(member.go_for_drink(festival, stall, drink, alcohol_type))

            if member.state["free_time"] > 0:
                stall = resources.find_stall_with_shortest_queue_in_zone(member, festival, "tables")

                if stall:
                    yield self.env.process(member.sit(stall, festival, drink=drink))
                
                else:
                    message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {member.name} {member.surname} si vypije {drink} za pochodu."
                    print(message)
                    logs.log_visitor(member, message)
                    
                    yield self.env.process(member.drink(drink, festival))
        
        elif action == "GO_TO_TOILET":
            need = member.decide_bathroom_action()
            toilet = member.choose_toilet(festival, need)
            yield self.env.process(member.go_to_toilet(toilet, need, festival))

            stall = member.choose_stall(festival, "handwashing_station")

            if stall is not None:
                yield self.env.process(member.wash(stall, festival))
            else:
                member.state["clean_hands"] = False

        elif action == "GO_TO_SHOWER":

            if not member.can_afford(festival.get_price("shower_price")):
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {member.name} {member.surname} nemá dost peněz na sprchu a musí si jít vybrat peníze."
                print(message)
                logs.log_visitor(member, message)
                member.is_busy = False
                member.state["low_money"] = True
                return

            shower = member.choose_stall(festival, "showers")
            yield self.env.process(member.go_to_shower(shower, festival))

        elif action == "BRACELET_EXCHANGE":

            if (not member.can_afford(festival.get_price("on_site_price")) and not member.state["pre_sale_ticket"]) or (not member.can_afford(festival.get_price("camping_area_price") and not member.state["tent_area_ticket"])):
                
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {member.name} {member.surname} nemá koupený lístek z předprodeje, nebo nemá koupení lístek do stanového městečka, a nemá dost peněz, musí si tedy jít vybrat peníze do bankomatu."
                print(message)
                logs.log_visitor(member, message)
                member.is_busy = False
                member.state["low_money"] = True
                return
            
            booth = member.choose_stall(festival, "ticket_booth")
            yield self.env.process(member.bracelet_exchange(festival, booth))

        elif action == "PITCH_TENT":
            camping_area = member.choose_stall(festival, "tent_area")

            if len(camping_area) > 1:
                camping_area = member.find_area_with_more_space(camping_area)
            else:
                camping_area = camping_area[0]

            yield self.env.process(member.pitch_tent(camping_area, festival))

        elif action == "CHARGE_PHONE":

            if not member.can_afford(festival.get_price("charging_phone_price")):
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {member.name} {member.surname} nemá dost peněz nabití telefonu a musí si jít vybrat peníze."
                print(message)
                logs.log_visitor(member, message)
                member.is_busy = False
                member.state["low_money"] = True
                False

            stalls = member.choose_stall(festival, "charging_stall")
            stall = member.find_area_with_more_space(stalls)

            yield self.env.process(member.charge_phone(stall, festival))
        
        elif action == "RETURN_CUP":
            stall = member.choose_stall(festival, "cup_return")
            yield self.env.process(member.return_cup(stall, festival))

        elif action == "WASH":
            stall = member.choose_stall(festival, "handwashing_station")
            yield self.env.process(member.wash(stall, festival))
        
        elif action == "BRUSH_TEETH":
            stall = member.choose_stall(festival, "handwashing_station")
            yield self.env.process(member.brush_teeth(stall, festival))

        elif action == "SIT":
            stall = member.choose_stall(festival, "tables")
            yield self.env.process(member.sit(stall, festival))

        elif action == "GO_TO_CONCERT":
            standing_by_stage = member.choose_stall(festival, "standing_at_stage")

            if len(standing_by_stage) == 1:
                standing_by_stage = standing_by_stage[0]

            yield self.env.process(member.go_to_concert(standing_by_stage, festival))

        elif action == "GO_TO_SIGNING_SESSION":
            signing_stall = member.choose_stall(festival, "signing_stall")
            if len(signing_stall) == 1:
                signing_stall = signing_stall[0]
            yield self.env.process(member.go_to_signing_session(signing_stall, festival))

        elif action == "BUY_MERCH":
            merch_stall = member.choose_stall(festival, "merch_stall")
            yield self.env.process(member.buy_merch(merch_stall, festival))

        elif action == "BUY_CIGARS":
            if member.can_afford(festival.get_price("cigars_price")):
                cigars_stall = member.choose_stall(festival, "smoking")
                yield self.env.process(member.buy_cigars(cigars_stall, festival))

            else:
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {member.name} {member.surname} nemá dost peněz na cigarety a musí si jít vybrat peníze."
                print(message)
                member.is_busy = False
                member.state["low_money"] = True
                return

        elif action == "GO_CHILL":
            chill_stall = member.choose_stall(festival, "chill_stall")
            yield self.env.process(member.go_chill(chill_stall, festival))

        elif action == "GO_SMOKE_WATER_PIPE":

            if member.can_afford(festival.get_price("cigars_price")):
                water_pipe_stall = member.choose_stall(festival, "water_pipe_stall")
                yield self.env.process(member.go_smoke_water_pipe(water_pipe_stall, festival))

            else:
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {member.name} {member.surname} nemá dost peněz na vodní dýmku a musí si jít vybrat peníze."
                print(message)
                logs.log_visitor(member, message)
                member.is_busy = False
                member.state["low_money"] = True
                return
        
        elif action == "SLEEP_IN_TENT":

            stall = member.choose_stall(festival, "handwashing_station")

            if stall is not None:
                yield self.env.process(member.brush_teeth(stall, festival))
                yield self.env.process(member.sleep_in_tent(festival))
                yield self.env.process(member.brush_teeth(stall, festival))

            else:
                yield self.env.process(member.sleep_in_tent(festival))

        elif action == "GO_TO_ATTRACTION":
            attraction = member.choose_attraction(festival)

            if attraction is None:
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Na festivalu bohužel není žádná vhodná atrakce pro {member.age_category.value}, takže {member.name} {member.surname} nemůže jít na žádnou atrakci."
                print(message)
                logs.log_visitor(member, message)
                member.is_busy = False
                return

            elif not member.can_afford(festival.get_price(attraction.get_name())):
                member.state["low_money"] = True
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {member.name} {member.surname} nemá na atrakci {attraction} dost peněz, a bude si muset jít vybrat."
                print(message)
                logs.log_visitor(member, message)
                member.is_busy = False

            else:
                yield self.env.process(member.go_to_attraction(attraction, festival))
        
        elif action == "TAKE_PHONE":
            stall = member.find_charging_stall(festival)
            yield self.env.process(member.take_phone(stall, festival))

        member.is_busy = False
        member.state["group_mode"] = True

    def group_decision_making(self, festival):

        while True:
            if self.type == source.Groups.INDIVIDUAL:
                for member in self.members:
                    member.update_stats(festival)

                    if not member.is_busy:
                        action = member.next_move(festival)
                        self.env.process(self.start_action(festival, member, action))

            elif self.type == source.Groups.FAMILY:
                parents = [m for m in self.members if m.age_category == source.Age_category.ADULT]
                parent = random.choice(parents)
                
                for member in self.members:
                    member.update_stats(festival)

                free_members = [m for m in self.members if not m.is_busy]

                if len(free_members) != len(self.members):
                    yield self.env.timeout(1)
                    continue
                
                action = parent.next_move(festival)
                
                for member in self.members:                   
                    if not member.is_busy:
                        self.env.process(self.start_action(festival, member, action))

            elif self.type == source.Groups.GROUP:

                together_actions = ["SIT", "GO_CHILL", "GO_SMOKE_WATER_PIPE", "SLEEP_IN_TENT", "GO_TO_ATTRACTION", "PITCH_TENT", "BRACELET_EXCHANGE"]
                priority_solo_actions = ["GO_TO_CONCERT", "WITHDRAW", "GO_TO_TOILET", "GO_TO_SHOWER", "GO_TO_SIGNING_SESSION", "GO_FOR_FOOD", "GO_FOR_DRINK", "SMOKE"]

                
                for member in self.members:
                    member.update_stats(festival)

                group_mode_members = [m for m in self.members if m.state["group_mode"]]
                free_members = [m for m in self.members if not m.is_busy]

                if free_members:

                    free_group_members = [m for m in group_mode_members if not m.is_busy]

                    if len(free_group_members) != len(group_mode_members):
                        yield self.env.timeout(1)
                        continue 

                    members_actions = [m.next_move(festival) for m in free_members]

                    action_counts = {}
                    for act in members_actions:
                        action_counts[act] = action_counts.get(act, 0) + 1

                    most_popular_action = max(action_counts, key=action_counts.get)


                    for member, member_action in zip(free_members, members_actions):

                        if member_action in priority_solo_actions:
                            member.is_busy = True
                            member.state["group_mode"] = False
                            self.env.process(self.start_action(festival, member, member_action))
                            continue

                        if most_popular_action in together_actions:
                            member.is_busy = True
                            self.env.process(self.start_action(festival, member, most_popular_action))
                            continue

                        member.is_busy = True
                        self.env.process(self.start_action(festival, member, member_action))

            yield self.env.timeout(1)
    
class Visitor:
    def __init__(self, festival, id, name, surname, gender, age_category, age, qualities, state, preference, accommodation, fellows, inventory):
        self.env = festival
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
        self.is_busy = False
        self.last_actions = {}
        self.actual_goal = None

    def hygiene_routine(self):
        while True:
            yield self.env.timeout(10)

            if self.env.now - self.state["last_teeth_clean_time"] >= 1200:
                self.state["clean_teeth"] = False
    
    def cooldown_actions(self):
        while True:
            yield self.env.timeout(1)

            to_delete = self.env.now - 30
            self.last_actions = {action: time for action, time in self.last_actions.items() if time >= to_delete}

    
    def get_name(self):
        name = self.name + " " + self.surname
        return name
    
    def get_data(self):
        data = {"name": self.name, "surname": self.surname, "gender": self.gender, "age_category": self.age_category, "age": self.age, "qualities": self.qualities, "preference": self.preference, "fellows": self.fellows}
        return data
    

    def update_stats(self, festival):

        if self.env.now >= ((festival.get_actual_day() * 1440) - festival.get_start_time()):
            festival.next_day()

        factor = 0.5

        self.state["energy"] = min(100, max(0, self.state["energy"] - factor * random.uniform(0.1, 0.5)))
        self.state["hunger"] = min(100, max(0, self.state["hunger"] - self.qualities["hunger_frequency"] * random.uniform(0.1, 0.5)))
        self.state["thirst"] = min(100, max(0, self.state["thirst"] - factor * random.uniform(0.1, 0.5)))
        self.state["wc"] = min(100, max(0, self.state["wc"] - factor * random.uniform(0.1, 0.5)))
        self.state["hygiene"] = min(100, max(0, self.state["hygiene"] - factor * random.uniform(0.1, 0.5)))
        self.state["drunkenness"] = min(100, max(0, self.state["drunkenness"] - self.qualities["alcohol_tolerance"] * random.uniform(0.1, 0.5)))
        
        mood_penalty = self.get_mood_penalty()
        self.state["mood"] == min(100, max(0, self.state["mood"] - mood_penalty)) 
        
        if self.preference["smoker"]:
            self.state["nicotine"] = min(100, max(0, self.state["nicotine"] - (factor * self.state["level_of_addiction"] * 0.1)))

        if self.inventory["phone"][0]:
            self.inventory["phone"][0].battery = min(100, max(0, self.inventory["phone"][0].battery - random.uniform(0.1, 0.5)))

#-----------------------------------------------------------------ROZHODOVÁNÍ NÁSLEDUJÍCÍHO KROKU NÁVŠTĚVNÍKA---------------------------------------------------------------

    def next_move(self, festival, need = None):
        """funkce, která rozhodne následující krok návštěvníka"""

        actions_by_locations = load_data("ACTIONS_BY_LOCATIONS")
        self.state["free_time"] = self.how_much_time_i_have()
        position_backup = None
        
        if self.state["location"] == source.Locations.STAGE_STANDING or self.state["location"] == source.Locations.SIGNING_STALL:
            position_backup = self.state["location"]
            self.state["location"] = source.Locations.FESTIVAL_AREA

        if need is None:
            permit = False

            while not permit:

                if self.actual_goal and self.actual_goal in actions_by_locations[self.state["location"].name].values():
                    action = self.actual_goal
                    self.actual_goal = None

                    if position_backup:
                        self.state["location"] = position_backup

                    return action
                
                elif self.actual_goal and self.actual_goal not in actions_by_locations[self.state["location"].name].values():
                    need = self.urgent_need(festival)

                elif not self.actual_goal:
                    need = self.urgent_need(festival)
                    self.actual_goal = source.NEEDS_ACTIONS[need]
                    
                action = self.resolve_need(need)

                if action not in self.last_actions:
                    permit = True
                    if "GO_TO" not in action:
                        self.last_actions[action] = self.env.now

        else:
            action = self.resolve_need(need)

        if position_backup:
            self.state["location"] = position_backup

        return action
    
    def urgent_need(self, festival):

        if not self.state["tent_area_ticket"]:
            return "bracelet_exchange"

        if self.state["tent_area_ticket"] and not self.state["entry_bracelet"]:
            return random.choice(["living", "bracelet_exchange"])
        
        if not self.accommodation["built"]:
            return "living"
        
        if not self.inventory["phone"][0]:
            if (self.env.now - self.inventory["phone"][1]["time"]) > 80:
                if random.random() > 0.5:
                    return "phone_ready"
                
            elif (self.env.now - self.inventory["phone"][1]["time"]) > 100:
                return "phone_ready"

        if self.state["low_money"]:
            return "low_money"

        if not self.state["clean_teeth"]:
            return "brushing_teeth"
        
        if not self.state["clean_hands"]:
            return "dirty_hand"
        
        actual_day = (festival.get_actual_day() - 1)

        if actual_day == 0:
            actual_day += 1

        midnight = actual_day * 1440
        midnight -= festival.get_start_time()
        sleeping_time = midnight + 150
    
        if self.env.now > sleeping_time:
            return "energy"
        
        needs_scores = {}

        needs_scores["hunger"] = 100 - self.state["hunger"]
        needs_scores["thirst"] = 100 - self.state["thirst"]
        needs_scores["wc"] = 100 - self.state["wc"]
        needs_scores["hygiene"] = 100 - self.state["hygiene"]
        needs_scores["energy"] = 100 - self.state["energy"]
        
        if self.state["money"] < 1000:
            low_money_score = 50 + ((1000 - self.state["money"]) / 100) * 5
            needs_scores["low_money"] = low_money_score

        if self.inventory["phone"][0] is not None:
            if self.inventory["phone"][0].battery < 50:
                low_battery_score = 100 - self.inventory["phone"][0].battery
                needs_scores["phone_dead"] = low_battery_score
        
        if self.preference["smoker"] is True:

            if self.state["cigarettes"] <= 10:
                buy_cigars_index = self.state["cigarettes"] * random.uniform(0.5, 1.5)

                if buy_cigars_index <= 8:
                    return "low_cigars"
                
        end_of_festival = festival.get_festival_length() * 1440 - festival.get_start_time()

        if (end_of_festival - self.env.now < 180) and self.inventory["plastic_cup"] is True:
            returning_index = random.randint(1,5)

            if returning_index <= 3:
                return "cup_return"

        if self.my_band_playing(festival) and self.state["location"] != source.Locations.STAGE_STANDING:
            return "band_playing"            

        if self.my_band_has_signing_session() and self.state["location"] != source.Locations.SIGNING_STALL:
            return "meet_band"
        
        if self.deciding_smoking():
            return "smoking"
        
        if self.do_i_want_sit(festival):
            return "sitting"
        
        if self.do_i_feel_tired(festival):
            return "tiredness"
    
        need, value = max(needs_scores.items(), key=lambda x: x[1])

        merch_score = self.do_i_want_merch(festival)

        if random.randint(0, 100) < merch_score:
            return "want_merch"

        if random.randint(0, 100) < self.do_i_want_go_to_attraction(festival):
            return "attraction_desire"
        
        if random.randint(0, 100) < self.do_i_want_water_pipe(festival):
            return "smoking_water_pipe"     
        
        if value <= 40 and self.some_band_playing(festival):
            return "band_playing"
    
        else:
            return need
    
    def get_mood_penalty(self):
        mood_penalty = 0

        if self.state["hunger"] < 50:
            mood_penalty += (50 - self.state["hunger"]) * 0.2

        if self.state["thirst"] < 50:
            mood_penalty += (50 - self.state["thirst"]) * 0.3

        if self.state["energy"] < 50:
            mood_penalty += (50 - self.state["energy"]) * 0.25

        if self.state["hygiene"] < 50:
            mood_penalty += (50 - self.state["hygiene"]) * 0.15

        if self.state["wc"] < 50:
            mood_penalty += (50 - self.state["wc"]) * 0.2

        if self.state["drunkenness"] > 70:
            mood_penalty += (self.state["drunkenness"] - 70) * 0.3

        return mood_penalty

    def how_much_time_i_have(self):

        if self.state["entry_bracelet"] == False and self.accommodation["built"] == False:
            return 0

        time_to_concert = 1440
        time_to_signing_session = 1440

        for band in self.preference["favourite_bands"]: 
            time = band["start_playing_time"] - self.env.now

            if time >= 0 and time < time_to_concert:
                time_to_concert = time

            time = band["start_signing_session"] - self.env.now

            if time >= 0 and time < time_to_signing_session:
                time_to_signing_session = time

        time_to_concert -= 10
        time_to_signing_session -= 10
        time_to_concert = min(120, time_to_concert)
        time_to_signing_session = min(120, time_to_signing_session)

        return min(time_to_concert, time_to_signing_session)

    def do_i_want_merch(self, festival):
        merch_score = 0

        if self.state["money"] > 1500:
            merch_score += 10

        if self.state["mood"] > 50:
            merch_score += 10

        if not self.my_band_playing(festival):
            merch_score += 10
        
        if not self.my_band_has_signing_session():
            merch_score += 10
        
        merch_score += self.qualities["tendency_to_spend"]

        return merch_score
    
    def do_i_want_sit(self, festival):
        """Rozhodnutí, zda si návštěvník chce sednout ke stolu."""
        
        if self.my_band_playing(festival):
            return False

        if self.state["hunger"] < 30 or self.state["thirst"] < 30 or self.state["wc"] < 30:
            return False

        #if self.inventory.get("drink_in_hand", False): - možná předělat systém sezení u stolu
        #    return random.random() < 0.6  # 60% šance

        if 40 < self.state["energy"] < 70 and self.state["free_time"] >= 10:
            return random.random() < 0.5

        return False
     
    def do_i_feel_tired(self, festival):
        """Rozhodnutí, zda chce návštěvník jít chillovat do chill zóny."""

        if self.state["energy"] <= 20 or self.state["energy"] >= 70:
            return False

        if self.state["hunger"] < 30 or self.state["thirst"] < 30 or self.state["wc"] < 30:
            return False

        if self.my_band_playing(festival):
            return False

        tiredness_score = (70 - self.state["energy"])
        return random.randint(0, 100) < tiredness_score

    def do_i_want_go_to_attraction(self, festival):
        score = 0

        score += max(0, self.state["mood"] - 50) / 2

        score += max(0, self.state["energy"] - 40) / 2

        urgent = min(self.state["hunger"], self.state["thirst"], self.state["wc"], self.state["hygiene"])
        score += urgent / 5

        if self.state["money"] > 500:
            score += 10

        score += self.qualities["tendency_to_spend"]

        return score

    def do_i_want_water_pipe(self, festival):
        
        if self.age < 18:
            return 0
        
        if self.state["hunger"] < 40 or self.state["thirst"] < 40 or self.state["wc"] < 40:
            return 0
        
        if self.state["energy"] < 30:
            return 0
        
        if self.state["money"] < festival.get_price("water_pipe_price"):
            return 0

        score = 20

        if self.preference["smoker"]:
            score += 20

        if self.state["location"] == source.Locations.CHILL_ZONE:
            score += 20

        if self.state["free_time"] > 60:
            score += 20

        return score

    def my_band_playing(self, festival):
        my_bands = self.preference["favourite_bands"]
        my_bands = sorted(my_bands, key=lambda x: x["start_playing_time"])
        
        if self.shows_will_end(festival):
            return False
        
        for band in my_bands:
            my_band_start_playing = band["start_playing_time"]
            my_band_end_playing = band["end_playing_time"]

            if my_band_start_playing - 20 < self.env.now < my_band_end_playing:
                return True
        
        return False
    
    def shows_will_end(self, festival):
        limit = festival.get_time("last_show_ends") - 15
        return self.env.now >= limit

    def some_band_playing(self, festival):
        if self.shows_will_end(festival):
            return False
        
        lineup = festival.get_lineup()
        day = festival.get_actual_day() - 1

        if len(lineup) == day:
            return False
        
        return (lineup[day][0]["start_playing_time"] - 20) < self.env.now < lineup[day][len(lineup[0])-1]["end_playing_time"] - 5
        
    def any_bands_this_day(festival):
        day = festival.get_actual_day() - 1
        
    def my_band_has_signing_session(self):
        my_bands = self.preference["favourite_bands"]
        my_bands = sorted(my_bands, key=lambda x: x["start_signing_session"])

        for band in my_bands:
            my_band_start_signing = band["start_signing_session"]
            my_band_end_signing = band["end_signing_session"]

            if my_band_start_signing - 30 < self.env.now < my_band_end_signing:
                return True
        
        return False

    def deciding_smoking(self):
        """funkce která rozhodne zda si kuřák chce zapálit cigaretu"""

        if self.preference["smoker"] == True:
            craving_for_a_cigarette = random.randint(0, 15 - self.state["level_of_addiction"])

            if craving_for_a_cigarette <= 4 and self.state["nicotine"] <= 50:
                return True 

        return False

# ---------------------------------------------------------------------POHYB---------------------------------------------------------

    def go_to(self, location, festival):
        """Funkce která obsluje návštěvníkův přesun do jiné zóny bez vstupní prohlídky"""

        message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} jde do {location.value}"
        print(message)
        logs.log_visitor(self, message)

        yield self.env.timeout(10)

        message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} dorazil do {location.value}"
        print(message)
        logs.log_visitor(self, message)
        
        self.state["location"] = location
    
    def go_to_festival_area(self, entrance, festival):

        yield self.env.timeout(10)

        message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} přišel ke vstupu."
        print(message)
        logs.log_visitor(self, message)
        
        start_waiting = self.env.now

        with entrance.resource.request() as req:

            will_wait = entrance.resource.count >= entrance.resource.capacity

            yield req

            if will_wait:
                waiting_time = self.env.now - start_waiting
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} čekal {waiting_time} ve frontě u vstupu."
                print(message)
                logs.log_visitor(self, message)
                logs.log_stalls_stats(entrance, "FESTIVAL_AREA", waiting_time)

            else:
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} prošel vstupem bez čekání."
                print(message)
                logs.log_visitor(self, message)

            entry_time = random.uniform(1, 5)
            yield self.env.timeout(entry_time)

            self.state["location"] = source.Locations.FESTIVAL_AREA

            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} dorazil do festivalového areálu."
            print(message)
            logs.log_visitor(self, message)

    def go_to_tent_area(self, festival):

        message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} jde do stanového městečka."
        print(message)
        logs.log_visitor(self, message)

        if not self.state["tent_area_ticket"]:

            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} dorazil ke stanovému městečku a nemá koupený lístek do stanového městečka."
            print(message)
            logs.log_visitor(self, message)
            return

        else:
            yield self.env.timeout(random.uniform(0, 1))
            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} dorazila do stanového městečka."
            print(message)
            logs.log_visitor(self, message)
            
        self.state["location"] = source.Locations.TENT_AREA

    def identify_entrance(self, entrances, entry_id):

        for entry in entrances:
            if entry.get_id() == int(entry_id):
                return entry

        print("ERROR!!: Vstup nenalezen!")
        return None

    def smoke(self, festival):
        #Funkce která obsluhuje návštěvníkovo kouření cigaret

        if self.preference["smoker"] == True:

            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} si zapálil cigaretu a začal kouřit."
            print(message)
            logs.log_visitor(self, message)

        else:
            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} začal čekat, než si člen skupiny zapálí cigaretu."
            print(message)
            logs.log_visitor(self, message)

        yield self.env.timeout(random.uniform(4, 6))
        
        if self.preference["smoker"] == True:

            self.state["cigarettes"] -= 1
            self.state["nicotine"] = min(self.state["nicotine"] + 30, 100)
            self.state["mood"] += min(self.state["mood"] + 30, 100)
            
            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} dokouřil, stav nikotinu je: {self.state["nicotine"]}"
            print(message)
            logs.log_visitor(self, message)

        else:
            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} přestal čekat, až si člen skupiny zapálí."
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
                    return foods.choose_random_food_from_stall(self, stall, festival)

                else:
                    if self.can_afford(source.foods[self.preference["favourite_food"]]):
                        return self.preference["favourite_food"]
                    else: 
                        return None
                
            else:
                return foods.choose_random_food_from_actual_zone(self, festival)

    def go_for_food(self, stall, food, festival):
        """funkce která simuluje návštěvníkovo koupení jídla ve stánku"""
        
        price = source.foods[food]["price"]
        time_min, time_max = source.foods[food]["preparation_time"]

        message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} přišel ke stánku {stall.stall_name}."
        print(message)
        logs.log_visitor(self, message)

        start_waiting = self.env.now

        # čekání na stánek
        with stall.resource.request() as req:
            
            will_wait = stall.resource.count >= stall.resource.capacity

            yield req

            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} přišel na řadu a je u stánku {stall.get_cz_name()}"
            print(message)
            logs.log_visitor(self, message)

            if will_wait:
                waiting_time = self.env.now - start_waiting
                
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} čekal {waiting_time:.2f} minut ve frontě u stánku {stall.get_cz_name()}."
                print(message)
                logs.log_visitor(self, message)
                logs.log_stalls_stats(stall, self.state["location"].name, waiting_time)

            preparation_time = random.randint(time_min, time_max)

            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} čeká na {food} a příprava bude trvat {preparation_time}"
            print(message)
            logs.log_visitor(self, message)

            yield self.env.timeout(preparation_time)
            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} dostal {food}"
            print(message)
            logs.log_visitor(self, message)
            
        self.state["money"] -= price
            
    def eat(self, food, festival):
        eating_time_min, eating_time_max = source.foods[food]["eating_time"]
        eating_time = random.randint(eating_time_min, eating_time_max)
        satiety = source.foods[food]["satiety"]

        message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} začal jíst {food}"
        print(message)
        logs.log_visitor(self, message)
        yield self.env.timeout(eating_time)
        self.state["hunger"] = min(100, self.state["hunger"] + satiety)
        message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} dojedl {food}, aktuální stav hladu je: {self.state["hunger"]}"
        print(message)
        logs.log_visitor(self, message)

# -----------------------------------------------STOLY---------------------------------------------------------------

    def sit(self, stall, festival, food = None, drink = None):
        """Funkce, která obsluju návštěvníkův pokus najít volný stůl a sednout si"""

        yield self.env.timeout(random.uniform(0, 2))
        message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} hledá místo u stolu k sednutí"
        print(message)
        logs.log_visitor(self, message)
        
        yield self.env.timeout(random.uniform(0, 2))

        if stall.resource.count >= stall.resource.capacity:
            patience_index = self.qualities["patience"] * random.uniform(0.5, 1.5)

            if patience_index > 5:
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} si nemá kam sednout a jde pryč"
                print(message)
                logs.log_visitor(self, message)
                return None

            else:
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} si nemá kam sednout ale počká než se uvolní místo u stolu."
                print(message)
                logs.log_visitor(self, message)

        start_waiting = self.env.now
        with stall.resource.request() as req:

            yield req

            waiting_time = self.env.now - start_waiting
            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} si sedl ke stolu."
            print(message)
            logs.log_visitor(self, message)

            if waiting_time > 0:
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} čekal na volné místo u stolu {waiting_time:.2f} minut."
                print(message)
                logs.log_visitor(self, message)

            start_sitting = self.env.now

            if food and drink:
                yield self.env.process(self.eat(food, festival))
                yield self.env.process(self.drink(drink, festival))
                sitting_time = self.env.now - start_sitting

            elif food:
                
                yield self.env.process(self.eat(food, festival))
                sitting_time = self.env.now - start_sitting

            elif drink:

                yield self.env.process(self.drink(drink, festival))
                sitting_time = self.env.now - start_sitting

            else:
                sitting_time = random.uniform(0 , self.state["free_time"])
                yield self.env.timeout(sitting_time)

                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} odchází od stolu."
                print(message)
                logs.log_visitor(self, message)

            self.state["energy"] = min(100, self.state["energy"] + ((sitting_time / 60) * 20))

# ------------------------------------------------PITÍ----------------------------------------------------------------
    def choose_drink(self, festival):
        """Vybere návštěvníkovi, které pití dá viz jidlo a pití.png"""

        available_soft_drinks = []
        available_beers = []
        available_hard_alcohol = []
        available_cocktails = []
        available_alcohol = {}

        drink_stalls_in_zone = resources.find_stalls_in_zone(self, festival, "drinks")

        for stall in drink_stalls_in_zone:
            drinks_in_stall = source.drinks_data["stalls"][stall.stall_name]

            for drink in drinks_in_stall:

                if drink in source.soft_drinks and drink not in available_soft_drinks:
                    available_soft_drinks.append(drink)

                if self.preference["alcohol_consumer"] is True:

                    if drink in source.beers and drink not in available_beers:
                        available_beers.append(drink)
                        available_alcohol["beers"] = available_beers

                    elif drink in source.hard_alcohol and drink not in available_hard_alcohol:
                        available_hard_alcohol.append(drink)
                        available_alcohol["hard_alcohol"] = available_hard_alcohol

                    elif drink in source.cocktails and drink not in available_cocktails:
                        available_cocktails.append(drink)
                        available_alcohol["cocktails"] = available_cocktails

        if not available_soft_drinks and self.preference["alcohol_consumer"] is False:
            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} si chce dát nealkoholické pití, ale bohužel se v {self.state['location'].value} žádné nealkoholické pití neprodává, {self.name} {self.surname} si tedy koupí pití později."
            print(message)
            logs.log_visitor(self, message)


        if available_alcohol == {} or self.is_visitor_drunk():

            if available_soft_drinks:
                drink = self.choose_soft_drink(festival, available_soft_drinks)
                alcohol_type = None

        else:
            drink, alcohol_type = self.choose_alcohol(festival, available_alcohol)
        
        return drink, alcohol_type
    
    def choose_soft_drink(self, festival, available_soft_drinks):
        
        fav_soft_drink = self.preference["favourite_soft_drink"]

        if fav_soft_drink in available_soft_drinks:
            
            for stall, values in source.drink_stalls.items():
                if fav_soft_drink in values:
                    searching_stall = stall
                    break

            stalls = resources.find_stalls_in_zone(self, festival, "drinks", searching_stall)
            stall = resources.find_stall_with_shortest_queue_in_zone(self, festival, "drinks", stalls=stalls)
            
            if resources.is_big_queue_at_stall(self, stall):
                
                
                for i in range(3):
                    drink = random.choice(available_soft_drinks)
                    if self.can_afford(source.drinks[drink]["price"]):
                        return drink
                
                return None
                    
            else:
                if self.can_afford(source.drinks[self.preference["favourite_soft_drink"]]):
                    return self.preference["favourite_soft_drink"]
                
        else:
            for i in range(3):
                drink = random.choice(available_soft_drinks)
                if self.can_afford(source.drinks[drink]["price"]):
                    return drink
            
            return None


    def choose_alcohol(self, festival, available_alcohol):

        kinds_of_alcohol = {"favourite_alcohol": False, "beers": False, "hard_alcohol": False, "cocktails": False}

        if any(self.preference["favourite_alcohol"] in alcohol_in_stall for alcohol_in_stall in available_alcohol.values()):
            available_alcohol["favourite_alcohol"] = True
        
        for kind in kinds_of_alcohol:
            if kind in available_alcohol and available_alcohol[kind]:
                kinds_of_alcohol[kind] = True

        alcohol_type = self.choose_type_of_alcohol(kinds_of_alcohol)

        if alcohol_type == "favourite_alcohol":
            if self.can_afford(source.drinks[self.preference["favourite_alcohol"]]):
                return self.preference["favourite_alcohol"], alcohol_type

            else:
                kinds_of_alcohol["favourite_alcohol"] = False
                alcohol_type = self.choose_type_of_alcohol(kinds_of_alcohol)
                drink = random.choice(available_alcohol[alcohol_type])

                for i in range(3):
                    if self.can_afford(source.drinks[drink]["price"]):
                        return drink, alcohol_type
                    
                return None, None
        else:
            drink = random.choice(available_alcohol[alcohol_type])
            for i in range(3):
                if self.can_afford(source.drinks[drink]["price"]):
                    return drink, alcohol_type

            return None, None

        
    def is_visitor_drunk(self):
        return self.state["drunkenness"] >= 75
    
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
        start_waiting = self.env.now

        # čekání na stánek
        with stall.resource.request() as req:

            yield req
            will_wait = stall.resource.count >= stall.resource.capacity
            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} přišel na řadu a je u stánku {stall.get_cz_name()} v zóně {self.state["location"].value}"
            print(message)
            logs.log_visitor(self, message)

            if will_wait:
                waiting_time = self.env.now - start_waiting
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} čekal u stánku {stall.get_cz_name()} {waiting_time}"
                print(message)
                logs.log_visitor(self, message)
                logs.log_stalls_stats(stall, self.state["location"].name, waiting_time)

            preparation_time = random.randint(time_min, time_max)

            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} čeká na {drink} a příprava bude trvat {preparation_time}"
            print(message)
            logs.log_visitor(self, message)
            yield self.env.timeout(preparation_time)

            if drink in source.cup_requirement:
                if self.inventory["plastic_cup"] is None:
                    self.inventory["plastic_cup"] == True
                    self.state["money"] -= plastic_cup_price
                    message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} neměl kelímek a musel si koupit nový"
                    print(message)
                    logs.log_visitor(self, message)

            else:
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} dostal {drink}"
                print(message)
                logs.log_visitor(self, message)

        self.state["money"] -= price

    def drink(self, drink_name, festival):
        drink_data = source.drinks[drink_name]
        drinking_time_min = drink_data["drinking_time"][0]
        drinking_time_max = drink_data["drinking_time"][1]
        drinking_time = random.uniform(drinking_time_min, drinking_time_max)

        message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} začal pít {drink_name}."
        print(message)
        logs.log_visitor(self, message)
        
        yield self.env.timeout(drinking_time)
        
        message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} dopil {drink_name}."
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
        yield self.env.timeout(random.uniform(0, 2))

        start_waiting = self.env.now
        message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} přišel k bankomatu."
        print(message)
        logs.log_visitor(self, message)
        with atm.resource.request() as req:
            
            yield req
            waiting_time = self.env.now - start_waiting

            if waiting_time > 0:
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} čekal ve frontě u bankomatu {waiting_time:.2f} minut."
                print(message)
                logs.log_visitor(self, message)

            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} přišel na řadu a začal vybírat peníze."
            print(message)
            logs.log_visitor(self, message)
            
            yield self.env.timeout(random.uniform(1, 5))

            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} dokončil výběr peněz. Aktulně má u sebe návtěvník {self.state["money"]:.2f} Kč"
            print(message)
            logs.log_visitor(self, message)

            self.state["money"] += random.randint(1000, 10000)
            self.state["low_money"] = False

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

        start_waiting = self.env.now

        with toilet.resource.request() as req:
            
            will_wait = toilet.resource.count >= toilet.resource.capacity
            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} přišel k {toilet.get_cz_name()}"
            print(message)
            logs.log_visitor(self, message)

            yield req

            if will_wait:
                waiting_time = self.env.now - start_waiting
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} čekal na volnou {toilet.get_cz_name()} {waiting_time}"
                print(message)
                logs.log_visitor(self, message)


            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} vchází na {toilet.get_cz_name()}."
            print(message)
            logs.log_visitor(self, message)

            yield self.env.timeout(wc_time)
            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} odchází z {toilet.get_cz_name()}."
            print(message)
            logs.log_visitor(self, message)

    def wash(self, stall, festival):
        yield self.env.timeout(random.uniform(0, 2))

        start_waiting = self.env.now
        message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} přišel k umývárně."
        print(message)
        logs.log_visitor(self, message)

        with stall.resource.request() as req:
            
            yield req
            waiting_time = self.env.now - start_waiting

            if waiting_time > 0:
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} čekal {waiting_time}, než se u umývárny uvolní místo."
                print(message)
                logs.log_visitor(self, message)


            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} si začal umývat ruce."
            print(message)
            logs.log_visitor(self, message)

            yield self.env.timeout(random.uniform(0, 1.5))
            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} dokončil umytí rukou."
            print(message)
            logs.log_visitor(self, message)

            self.state["hygiene"] += random.randint(10, 20)
        
    def brush_teeth(self, stall, festival):
        yield self.env.timeout(random.uniform(0, 2))

        start_waiting = self.env.now

        message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} přišel k umývárně."
        print(message)
        logs.log_visitor(self, message)

        with stall.resource.request() as req:
            
            yield req
            waiting_time = self.env.now - start_waiting

            if waiting_time > 0:
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} čekal {waiting_time}, než se u umývárny uvolní místo."
                print(message)
                logs.log_visitor(self, message)

            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} si začal čistit zuby."
            print(message)
            logs.log_visitor(self, message)

            yield self.env.timeout(random.uniform(0, 1.5))

            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} dokončil čištění zubů."
            print(message)
            logs.log_visitor(self, message)

            self.state["hygiene"] += random.randint(15, 30)
            self.state["clean_teeth"] = True
            self.state["last_teeth_clean_time"] = self.env.now

# -------------------------------------------------SPRCHY ---------------------------------------------------------
            
    def go_to_shower(self, shower, festival):
        """funkce obsluhjící návštěvníka ve sprše"""
        
        if self.gender == source.Gender.MALE:
            shower_time = random.uniform(5, 15)
        else:
            shower_time = random.uniform(12, 20)

        with shower.resource.request() as req:
            start_waiting = self.env.now
            will_wait = shower.resource.count >= shower.resource.capacity

            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} přišel/la ke sprchám"
            print(message)
            logs.log_visitor(self, message)

            yield req

            if will_wait:
                waiting_time = self.env.now - start_waiting
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} čekal na volnou spruchu {waiting_time}"
                print(message)
                logs.log_visitor(self, message)
                logs.log_stalls_stats(shower, self.state["location"].name, waiting_time)

            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} vchází do sprchy."
            print(message)
            logs.log_visitor(self, message)

            yield self.env.timeout(shower_time)
            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} odchází ze sprchy."
            print(message)
            logs.log_visitor(self, message)       
        
        self.state["money"] -= festival.get_price("shower_price")
        self.state["hygiene"] = 100

# --------------------------------------------STANOVÉ MĚSTEČKO------------------------------------------------------

    def pitch_tent(self, camping_area, festival):
            #funkce která obsluhuje návštěvníkovo stavění stanu
            
            yield self.env.timeout(random.uniform(0, 2))

            num_fellows = len(self.fellows)
            pitch_time = random.uniform(15, 20) - num_fellows * 1.5
            free_space = False
            i = -1

            for position in camping_area.positions:
                i += 1

                if position == []:
                    free_space = True

                    if self.accommodation["owner"] == False:
                        
                        message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} pomáhá kolegovi postavit stan."
                        print(message)
                        logs.log_visitor(self, message)

                        yield self.env.timeout(pitch_time)
                        message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} s kolegou dostavěli stan."
                        print(message)
                        logs.log_visitor(self, message)
                    else:        
                        position.append(self.inventory["tent"])
                        message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} staví stan."
                        print(message)
                        logs.log_visitor(self, message)
                        
                        yield self.env.timeout(pitch_time)
                        message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} dostavěl stan."
                        print(message)
                        logs.log_visitor(self, message)


                    self.accommodation["i"] = i
                    self.accommodation["built"] = True
                    self.accommodation["camping_area"] = camping_area
                    break
                
            if not free_space:
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Došlo místo ve stanovém městečku!"
                print(message)
                logs.log_visitor(self, message)

    def find_area_with_more_space(self, areas):
        if len(areas) > 1:

            camping_area = areas[0]
            free_spaces = camping_area.positions[0]

            for area in areas:
                if free_spaces < area.positions[0]:
                    free_spaces = area.positions[0]
                    camping_area = area
            
            return camping_area
        else:
            return areas[0]

    def sleep_in_tent(self, festival):
        
        yield self.env.timeout(random.uniform(0, 2))
        
        if self.accommodation["built"] is True:
            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} došel do stanu."
            print(message)
            logs.log_visitor(self, message)

            with self.accommodation["camping_area"].positions[self.accommodation["i"]][0].request() as req:
                
                yield req
                
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} je ve stanu a chystá se na spaní."
                print(message)
                logs.log_visitor(self, message)
                yield self.env.timeout(random.uniform(1,10))

                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} jde spát."
                print(message)
                logs.log_visitor(self, message)
                
                well_rested = False
                sleeping_time = random.uniform(240, 480)

                while well_rested is not True:

                    yield self.env.timeout(sleeping_time)
                    self.state["energy"] += (sleeping_time / 60) * 12.5

                    if self.state["energy"] >= 80:
                        message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} se vzbudil."
                        print(message)
                        logs.log_visitor(self, message)
                        well_rested = True

                    else:
                        sleeping_time = random.uniform(30, 120)
                    
        else:
            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} nemá žádný přidělený stan, ve kterém by mohl spát."
            print(message)
            logs.log_visitor(self, message)
# ------------------------------------------------POKLADNY ---------------------------------------------------------

    def bracelet_exchange(self, festival, ticket_booth):
        #funkce, která simuluje návštěvníkovo ukázání lístku u pokladny, výměnou za pásek na ruku umožňující vstup do arálu.
        #Návštěvník si lístek v pokladně koupí, pokud ho nemá z předprodeje,
        #pokud návštěvník nemá lístek do stanového městečka, koupí si i ten.

        on_site_price = festival.get_price("on_site_price")
        camping_area_price = festival.get_price("camping_area_price")
        
        with ticket_booth.resource.request() as req:

            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} přišel/la k pokladnám."
            print(message)
            logs.log_visitor(self, message)
            
            start_waiting = self.env.now
            will_wait = ticket_booth.resource.count >= ticket_booth.resource.capacity

            yield req
            
            if will_wait:
                waiting_time = self.env.now - start_waiting
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} čekal ve frontě u pokladny {waiting_time}"
                print(message)
                logs.log_visitor(self, message)
                logs.log_stalls_stats(ticket_booth, self.state["location"].name, waiting_time)


            if self.state["pre_sale_ticket"] and self.state["tent_area_ticket"]:
                yield self.env.timeout(random.uniform(1,2))
                
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} měl festivalovou vstupenku i vstupenku do stanového městečka koupený z předprodeje, dostal pásek, a odešel z pokladny."
                print(message)
                logs.log_visitor(self, message)

            elif self.state["pre_sale_ticket"]:
                yield self.env.timeout(random.uniform(2,3))

                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} měl festivalovou vstupenku koupenou z předprodeje ale koupil si na pokladně vstupenku do stanového městečka, dostal pásek, a odešel z pokladny."
                print(message)
                logs.log_visitor(self, message)

                self.state["tent_area_ticket"] = True
                self.state["money"] -= camping_area_price
                festival.add_income(camping_area_price)

            elif self.state["tent_area_ticket"]:
                yield self.env.timeout(random.uniform(2,3))

                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} měl vstupenku do stanového městečka koupenou z předprodeje ale koupil si na pokladně festivalovou vstupenku, dostal pásek, a odešel z pokladny."
                print(message)
                logs.log_visitor(self, message)

                self.state["money"] -= on_site_price
                festival.add_income(on_site_price)

            else:

                yield self.env.timeout(random.uniform(3,4))
                
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} si koupil na pokladně festivalovou vstupenku i vstupenku do festivalového areálu, dostal pásek, a odešel z pokladny."
                print(message)
                logs.log_visitor(self, message)

                self.state["tent_area_ticket"] = True
                self.state["money"] -= camping_area_price
                festival.add_income(camping_area_price)

                
                self.state["money"] -= on_site_price
                festival.add_income(on_site_price)

            self.state["entry_bracelet"] = True
          

# ----------------------------------------------NABÍJECÍ STÁNEK ---------------------------------------------------------

    def charge_phone(self, stall, festival):
        """Funkce na nabití najení telefonů návštěvníků"""

        i = -1

        message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} jde k nabíjecímu stánku."    
        print(message)
        logs.log_visitor(self, message)

        yield self.env.timeout(random.uniform(1, 3))

        with stall.resource.request() as req:
            start_waiting = self.env.now

            yield req

            will_wait = self.env.now - start_waiting
            if will_wait:
                waiting_time = self.env.now - start_waiting

                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} přišel/la k nabíjecímu stánku a čekal ve frontě {waiting_time:.2f} minut."    
                print(message)
                logs.log_visitor(self, message)

            else:
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} přišel/la k nabíjecímu stánku."    
                print(message)
                logs.log_visitor(self, message)

            free_space = False

            for position in stall.positions:
                i += 1

                if position == []:
                    free_space = True
                    phone = self.inventory["phone"][0]
                    stall.positions[i] = phone
                    phone.put_on_charger()

                    self.inventory["phone"][0] = None
                    self.inventory["phone"][1] = {"zone": stall.get_zone(), "stall_id": stall.get_id(), "position": i, "time": self.env.now}

                    message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} si dává nabít mobil do nabíjecího stánku."
                    print(message)
                    logs.log_visitor(self, message)

                    yield self.env.timeout(random.uniform(1,5))
                    message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} si dal mobil do nabíjecího stánku."
                    print(message)
                    logs.log_visitor(self, message)

                    self.state["money"] -= festival.get_price("charging_phone_price")
                    festival.add_income(festival.get_price("charging_phone_price"))
                    break
                
            if not free_space:
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Došly pozice na nabíjení v nabíjecím stánku!"
                print(message)
                logs.log_visitor(self, message)
    
    def take_phone(self, stall, festival):
        i = -1

        message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} jde k nabíjecímu stánku."    
        print(message)
        logs.log_visitor(self, message)

        yield self.env.timeout(random.uniform(1, 3))

        with stall.resource.request() as req:
            start_waiting = self.env.now

            yield req

            will_wait = self.env.now - start_waiting
            if will_wait:
                waiting_time = self.env.now - start_waiting

                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} přišel/la k nabíjecímu stánku a čekal ve frontě {waiting_time:.2f} minut."    
                print(message)
                logs.log_visitor(self, message)

            else:
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} přišel/la k nabíjecímu stánku."    
                print(message)
                logs.log_visitor(self, message)

            done = False

            random.uniform(0.5,1.5)

            for position in stall.positions:
                i += 1

                if i == self.inventory["phone"][1]["position"]:

                    if isinstance(position, items.Phone):
                        phone = position

                        if phone.battery >= 70 and phone.battery <= 90:
                            probability = (phone.battery - 70) / 20 

                            if random.random() < probability:
                                done = True

                        elif phone.battery > 90:
                            done = True

                        if done:    
                            phone.take_from_charger()
                            self.inventory["phone"][0] = phone
                            self.inventory["phone"][1] = None
                            position = []

                        else:
                            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Telefon návštěvníka {self.name} {self.surname} má teprve {position.battery:.2f} procent baterky a tak se {self.name} rozhodl, že ho ještě chvilku nechá nabíjet."    
                            print(message)
                            logs.log_visitor(self, message)

                        break

            if done:
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} dostal zpátky mobil z nabíjecího stánku a aktuální stav jeho baterky je {self.inventory["phone"][0].battery:.2f} procent."    
                print(message)
                logs.log_visitor(self, message)

            else:
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: CHYBA!! Mobil nebyl nalezen!"    

    def find_charging_stall(self, festival):
    
        stalls = festival.get_stalls()
        stalls_in_zone = stalls[self.inventory["phone"][1]["zone"]]

        for stall in stalls_in_zone:
            if stall.stall_name == "charging_stall":
                if stall.id == self.inventory["phone"][1]["stall_id"]:
                    return stall
                
        message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: ERROR!! Nabíjecí stánek s telefonem návštěvníka {self.name} {self.surname} nebyl nalezen!"
        print(message)
        return None
# ----------------------------------------------VRÁCENÍ KELÍMKŮ ---------------------------------------------------------

    def return_cup(self, stall, festival):
        yield self.env.timeout(random.uniform(0, 2))

        start_waiting = self.env.now
        message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} přišel k výkupu kelímků."
        print(message)
        logs.log_visitor(self, message)

        with stall.resource.request() as req:
            
            yield req
            waiting_time = self.env.now - start_waiting

            if waiting_time > 0:
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} čekal ve frontě {waiting_time:.2f} minut."
                print(message)
                logs.log_visitor(self, message)

            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} přišel na řadu a začal vracet kelímek."
            print(message)
            logs.log_visitor(self, message)
            
            yield self.env.timeout(random.uniform(1, 5))

            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} vrátil kelímek."
            print(message)
            logs.log_visitor(self, message)

            self.state["money"] += festival.get_price("plastic_cup_price")
            self.inventory["plastic_cup"] = None

# ----------------------------------------------OBECNÉ FUNKCE ---------------------------------------------------------

    def choose_stall(self, festival, type_of_item, item = None):
        #funkce která návštěvníkovi přiřadí stánek, ke kterému si půjde chtěnou věckci

        if item:
            if type_of_item == "foods":
                stalls = source.food_stalls
            elif type_of_item == "drinks":
                stalls = source.drink_stalls

            for key, value in stalls.items():
                if item in value:
                    stall_name = key
                    break
            
            return resources.find_stall_with_shortest_queue_in_zone(self, festival, type_of_item, name=stall_name)
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
                next_zone = self.get_zone_from_move_command(move)
                next_zone = source.Locations[next_zone]
                queue.append((next_zone, path + [move]))

        return None
    
    def get_zone_from_move_command(self, move):
        zone = move.replace("GO_TO_", "")
        if "_ENTRY_" in zone:
            zone = zone.split("_ENTRY_")[0]
        return zone
    
# --------------------------------------------KONCERTY--------------------------------------------------------

    def go_to_concert(self, standing_by_stage, festival, position = None):
        position_map = {"first_lines": "prvních řadách", "middle": "prostředním sektoru", "back": "zadním sektoru"}
        bands = festival.get_lineup()[festival.get_actual_day()-1]
        pause_time = festival.get_pause()
        actual_band = None

        for band in bands:

            if self.env.now >= (band["start_playing_time"] - pause_time) and (self.env.now < band["end_playing_time"]):
                actual_band = band
                break
        
        if actual_band:

            reimaining_time = actual_band["end_playing_time"] - self.env.now 

            if self.state["location"] != source.Locations.STAGE_STANDING:
                self.state["location"] = source.Locations.STAGE_STANDING

                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} jde k podiu na koncert kapely {actual_band["band_name"]}."
                print(message)
                logs.log_visitor(self, message)
                
                time_to_get_by_stage = random.uniform(1, 3)

                if time_to_get_by_stage > reimaining_time:
                    message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} už bohužel koncert kapely {actual_band["band_name"]} nestíhá a tak jde dělat něco jiného."
                    print(message)
                    logs.log_visitor(self, message)
                    yield self.env.timeout(1)
                    return

                yield self.env.timeout(random.uniform(1, 3))

            else:
                
                resource = self.state["location_stage"]
                position = self.state["location_stage_position"]
                time_to_start = actual_band["start_playing_time"] - self.env.now

                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} zůstane u podia i na koncert kapely {actual_band["band_name"]}, který je za {time_to_start:.2f} minut."
                print(message)
                logs.log_visitor(self, message)
                yield self.env.timeout(actual_band["end_playing_time"] - self.env.now) 

                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Koncert skončil a {self.name} {self.surname} přemýšlí, co bude dělat dál."
                print(message)
                logs.log_visitor(self, message)
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

                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} je u podia v {position} na koncertě kapely {actual_band["band_name"]}."
                print(message)
                logs.log_visitor(self, message)
                
                time = actual_band["end_playing_time"] - self.env.now
                if time < 0:
                    breakpoint()
                yield self.env.timeout(time)

                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Koncert skončil a {self.name} {self.surname} přemýšlí, co bude dělat dál."
                print(message)
                logs.log_visitor(self, message)
            
        else:
            yield self.env.timeout(0.0001)
            
# ---------------------------------------------AUTOGRAMIÁDY------------------------------------------------------------

    def go_to_signing_session(self, stall, festival):
        """ resource[0] -> kapela (1), 
            resource[1] -> 5 místa u kapely (podepisování), 
            resource[2] -> fronta (kapacita fronty) - 4 lidi co jsou už u kapely 
            resource[3] -> None, nebo instance kapely, která má zrovna autogramiádu"""

        actual_band = stall.resource[3]
        
        for item in self.inventory["autographs"]:
            if actual_band["band_name"] in item:
                yield self.env.timeout(1)
                return
        
        message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} jde na autogramiádu kapely {actual_band["band_name"]}."
        print(message)
        logs.log_visitor(self, message)

        yield self.env.timeout(random.uniform(1,2))

        with stall.resource[2].request() as req_queue:
            start_wait = self.env.now

            yield req_queue

            if self.env.now < actual_band["start_signing_session"]:
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} je ve frontě a čeká na začátek autogramiády kapely {actual_band["band_name"]}."
                print(message)
                logs.log_visitor(self, message)

                
                yield self.env.timeout(actual_band["start_signing_session"] - self.env.now)

            else:
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} je ve frontě na autogramiádě kapely {actual_band["band_name"]} a čeká než příjde na řadu."
                print(message)
                logs.log_visitor(self, message)
        
            with stall.resource[1].request() as req_sig:
                
                yield req_sig

                waiting_time = self.env.now - start_wait
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} přišel na řadu a právě dostává autogramy od kapely {actual_band["band_name"]}."
                print(message)
                logs.log_visitor(self, message)

                yield self.env.timeout(random.uniform(0, 2))

                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} dostal autogramy od kapely {actual_band["band_name"]} a čekal na něj ve frontě {waiting_time:.2f} minut."
                print(message)
                logs.log_visitor(self, message)
                self.inventory["autographs"].append(f"{actual_band["band_name"]}")

#---------------------------------------------------CHILL ZÓNA----------------------------------------------------------------

#-------------------------------------------CHILL ZÓNA - Cigaretový stánek---------------------------------------------------------
    
    def buy_cigars(self, stall, festival):

        if self.preference["smoker"] == False:
            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} čeká, než si jeho kolega koupí cigarety."
            print(message)
            logs.log_visitor(self, message)
            yield self.env.timeout(random.uniform(0,2)) #dodělat aby čekal stejně dlouho jako ten co kupuje cigára
            return
        
        how_many_cigars = (self.state["level_of_addiction"] // 2) * 20

        yield self.env.timeout(random.uniform(0, 2))
        message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} přišel k cigaretovému stánku."
        print(message)
        logs.log_visitor(self, message)

        with stall.resource.request() as req:

            start_waiting = self.env.now

            yield req

            if self.env.now > start_waiting:
                waiting_time = self.env.now - start_waiting
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} čekal ve frontě u cigaretového stánku než přišel na řadu {waiting_time:.2f} minut."
                print(message)
                logs.log_visitor(self, message)

            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} kupuje {how_many_cigars // 20} krabiček cigaret."
            print(message)
            logs.log_visitor(self, message)

            yield self.env.timeout(random.uniform(0,2))

            self.state["money"] - ((how_many_cigars // 20) * festival.get_price("cigars_price"))
            self.state["cigarettes"] += how_many_cigars
            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} nakoupil cigarety a aktuálně jich má {self.state["cigarettes"]}."
            print(message)
            logs.log_visitor(self, message)
                

#-------------------------------------------CHILL ZÓNA - Chill stánek---------------------------------------------------------
    
    def go_chill(self, stall, festival):

        yield self.env.timeout(random.uniform(0, 2))
        message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} přišel k chill stánku."
        print(message)
        logs.log_visitor(self, message)

        with stall.resource.request() as req:

            result = yield req | self.env.timeout(0)

            if req not in result:
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} odešel od chill stánku, protože už je plně obsazený."
                print(message)
                logs.log_visitor(self, message)
                return

            chilling_time = random.uniform(0, self.state["free_time"])
            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} je v chill stánku a bude odpočívat {chilling_time:.2f} minut."
            print(message)
            logs.log_visitor(self, message)

            yield self.env.timeout(chilling_time)
            self.state["energy"] += chilling_time * 0.5

#-------------------------------------------CHILL ZÓNA - Stánek s vodníma dýmkama---------------------------------------------------------

    def go_smoke_water_pipe(self, stall, festival):

        yield self.env.timeout(random.uniform(0, 2))
        message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} přišel k stánku s vodníma dýmkama."
        print(message)
        logs.log_visitor(self, message)

        with stall.resource.request() as req:

            result = yield req | self.env.timeout(0)

            if req not in result:
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} odešel od stánku s vodníma dýmkama, protože už je plně obsazený."
                print(message)
                logs.log_visitor(self, message)
                return
            
            self.state["money"] -= festival.get_price("water_pipe_price")
            smoking_time = random.uniform(0, self.state["free_time"])
            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} je ve stánku s vodníma dýmkama a bude odpočívat a kouřit {smoking_time:.2f} minut."
            print(message)
            logs.log_visitor(self, message)

            yield self.env.timeout(smoking_time)
            self.state["energy"] += smoking_time * 0.5

            if not self.state.get("nicotine"):
                self.state["nicotine"] = 0

            self.state["nicotine"] += smoking_time * 1.5

#-------------------------------------------------MERCH---------------------------------------------------------------

    def buy_merch(self, merch_stall, festival):
        """SimPy proces: návštěvník kupuje merch u stánku."""
        
        merch_data = festival.get_merch()
        festival_merch = merch_data["festival_merch"]
        bands_merch = merch_data["bands_merch"]
        favourite_bands = self.preference["favourite_bands"]
        available_bands_items = {}

        message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} se jde podívat k merch stánku."
        print(message)
        logs.log_visitor(self, message)

        self.env.timeout(random.uniform(1,3))

        # 1) Vyber, jestli chce festivalový merch nebo merch kapely
        # (např. 70 % šance na kapelní merch)

        start_waiting = self.env.now

        with merch_stall.resource.request() as req:

            yield req

            waiting_time = self.env.now - start_waiting
            will_wait = self.env.now != start_waiting

            if will_wait:
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} je na řadě u merch stánku a čekal ve frontě {waiting_time:.2f} minut."
            else:
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} je na řadě u merch stánku a nemusel čekat než přijde na řadu."
            
            print(message)
            logs.log_visitor(self, message)

            for name, merch in bands_merch.items():
                for band in favourite_bands:
                    if name == band["band_name"]:
                        available_bands_items[name] = merch
                        break
            
            had_enough = False
            
            while not had_enough:

                filtered_festival_merch = self.filter_festival_merch(copy.deepcopy(festival_merch))
                filtered_bands_merch = self.filter_band_merch(copy.deepcopy(available_bands_items))

                if filtered_bands_merch == {} and filtered_festival_merch == {}:            
                    message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} si již koupil úplně všechen merch, o který měl zájem, a tak odchází z merch stánku."
                    print(message)
                    logs.log_visitor(self, message)
                    return

                elif filtered_bands_merch == {}:
                    message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} si již koupil všechen merch od kapel, které má rád, koupí si tedy něco z festivalového merche."
                    print(message)
                    logs.log_visitor(self, message)
                    available_items = filtered_festival_merch

                elif filtered_festival_merch == {}:
                    message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} si již koupil všechen festivalový merch, koupí si tedy merch od nějaké kapely."
                    print(message)
                    logs.log_visitor(self, message)
                    available_items = filtered_bands_merch

                else:
                    if random.random() < 0.5:
                        available_items = filtered_bands_merch
                    else:
                        available_items = filtered_festival_merch

                item_name, item_info = random.choice(list(available_items.items()))
                band = None

                if item_name in available_bands_items:
                    band = item_name
                    item_name, item_info = random.choice(list(item_info.items()))

                if item_name.endswith(":"):
                    item_name = item_name[:-1]
                    item_name = item_name.lower()
                
                if band:
                    message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} si chce koupit {item_name} od kapely {band}."
                    print(message)
                    logs.log_visitor(self, message)
                else:

                    message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} si chce koupit {item_name}."
                    print(message)
                    logs.log_visitor(self, message)


                if item_info["quantity"] <= 0:
                    message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} si nemůže koupit {item_name}, protože {item_name} už jsou vyprodané."
                    print(message)
                    logs.log_visitor(self, message)
                    return
                
                if self.state["money"] < item_info["price"]:
                    message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} si nemůže koupit {item_name}, protože na {item_name} nemá dost peněz a musí si jít vybrat."
                    print(message)
                    logs.log_visitor(self, message)
                    self.state["low_money"] = True
                    return
                    
                service_time = random.uniform(0.5, 2.0)
                yield self.env.timeout(service_time)

                if band:
                    message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} si koupil {item_name} od kapely {band}."
                    print(message)
                    logs.log_visitor(self, message)

                else:
                    message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} si koupil {item_name}."
                    print(message)
                    logs.log_visitor(self, message)

                item_info["quantity"] -= 1
                self.state["money"] -= item_info["price"]

                if band:
                    item_name = band + "-" + item_name
                    self.inventory["merch"].append(item_name)
                else:
                    self.inventory["merch"].append(item_name)

   
                sold_dict = merch_data["sold"][0]  

                if item_name not in sold_dict:

                    sold_dict[item_name] = {
                        "sell": 1,
                        "gain": item_info["price"]
                    }

                else:
                    sold_dict[item_name]["sell"] += 1
                    sold_dict[item_name]["gain"] += item_info["price"]

                had_enough = random.random() <= 0.5 
    
    def filter_festival_merch(self, festival_merch):

        if self.inventory["merch"] == []:
            return festival_merch
        
        for owned_merch in self.inventory["merch"]:
            first_letter = owned_merch[0]
            owned_merch = chr(ord(first_letter) - 32) + owned_merch[1:] + ":"

            if owned_merch in festival_merch:
                del festival_merch[owned_merch]

        return festival_merch

    def filter_band_merch(self, bands_merch):

        if self.inventory["merch"] == []:
            return bands_merch
        
        for owned_merch in self.inventory["merch"]:

            if "-" in owned_merch:
                band, merch = owned_merch.split("-")

                if merch == "cd":
                    merch = merch[0].upper() + merch[1].upper() + merch[2:] + ":"

                else:
                    merch = merch[0].upper() + merch[1:] + ":"
                
                del bands_merch[band][merch]

                if bands_merch[band] == {}:
                    del bands_merch[band]

        return bands_merch


#-------------------------------------------------ATRAKCE---------------------------------------------------------------
    
    def choose_attraction(self, festival):

        attraction_data = source.ATTRACTIONS["attractions"]
        available_attraction = festival.get_attractions()

        available = [attr.stall_name for attr in available_attraction]

        weighted_choices = []

        for name in available:

            data = attraction_data[name]

            # věkový filtr
            match self.age_category:
                case source.Age_category.CHILD:
                    if data["for"] not in ["all", "kids"]:
                        continue
                case source.Age_category.YOUTH:
                    if data["for"] not in ["all", "youth"]:
                        continue
                case source.Age_category.ADULT:
                    if data["for"] not in ["all","youth", "adults"]:
                        continue

            weight = 10

            weight -= data["adrenaline"]

            # nálada ovlivňuje chuť na adrenalin
            # dobrá nálada → adrenalin nevadí tolik
            # špatná nálada → adrenalin je odpuzující

            mood_factor = (self.state["mood"] - 50) / 10
            weight += mood_factor

            # váha nesmí být záporná
            weight = max(1, int(weight))

            weighted_choices.extend([(name, data)] * weight)

        if not weighted_choices:
            return None

        attraction_name, attraction_data = random.choice(weighted_choices)

        for attr in available_attraction:
            if attraction_name == attr.stall_name:
                attraction = attr
                break
        
        return attraction


    def go_to_attraction(self, attraction, festival):

        attraction_data = attraction.attraction.attraction_data

        yield self.env.timeout(random.uniform(1, 2))

        message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} jde na atrakci {attraction.get_cz_name()}."
        print(message)
        logs.log_visitor(self, message)

        # čekání ve frontě
        with attraction.resource.request() as req:
            
            start_waiting = self.env.now
            yield req

            will_wait = self.env.now - start_waiting

            if will_wait:
                waiting_time = self.env.now - start_waiting
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} je na atrakci {attraction.get_cz_name()}, čekal {waiting_time:.2f} minut, než se dostal na řadu, a teď čeká, než začne jízda."
                print(message)
                logs.log_visitor(self, message)

            else:
                message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} je na atrakci {attraction.get_cz_name()} a čeká než začne jízda."
                print(message)
                logs.log_visitor(self, message)

            attraction.attraction.add_rider()

            yield attraction.attraction.get_ride_start()

            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Návštěvník {self.name} {self.surname} si užívá jízdu na atrakci {attraction.get_cz_name()}."
            print(message)
            logs.log_visitor(self, message)

            yield attraction.attraction.get_ride_end()

            message = f"ČAS {times.get_real_time(self.env, festival.get_start_time())}: Jízda atrakce {attraction.get_cz_name()} skončila a {self.name} {self.surname} odchází z atrakce."
            print(message)
            logs.log_visitor(self, message)

            attraction.attraction.sub_rider()

        self.state["mood"] += attraction_data["fun_gain"]
        self.state["money"] -= festival.get_price(attraction.stall_name)

    def can_afford(self, what):
        if isinstance(what, (int, float)):
            return self.state["money"] > what
        else:
            return self.state["money"] > what["price"]

# ------------------------------------------PŘÍJEZD NÁVŠTĚVNÍKŮ--------------------------------------------------------

def spawn_groups(env, groups_list, festival):
    i = 0
    start_shows = festival.get_time("first_show_starts")
    start_simulation = festival.get_time("simulation_start_time")
    time_to_arrive = start_shows - start_simulation
    spacings = time_to_arrive / festival.get_num_visitors()

    for group in groups_list:
        i += 1

        yield env.timeout(random.uniform(0, spacings))
        message = f"ČAS {times.get_real_time(env, festival.get_start_time())}: Skupina číslo {i} dorazila na festival"
        print(message)
        logs.log_message(message)

        for member in group.members:
            message = f"ČAS {times.get_real_time(env, festival.get_start_time())}: Návštěvník {member.name} {member.surname} dorazil na festival."
            logs.log_visitor(member, message)

        env.process(group.group_decision_making(festival))


