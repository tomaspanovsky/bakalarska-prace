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
        if self.mode == source.Groups_modes.INDIVIDUALLY:
            self.mode = source.Groups_modes.IN_GROUP
        else:
            self.mode = source.Groups_modes.INDIVIDUALLY

    def start_action(self, member, action):

        if action == "go_to_entrance_zone":
            yield self.festival.process(member.go_to_entrance_zone())
        
        elif action == "go_to_tent_area":
            yield self.festival.process(member.go_to_tent_area())

        elif action == "go_to_festival_area":
            yield self.festival.process(member.go_to_festival_area(resources.entrances))

        elif action == "bracelet_exchange":
            yield self.festival.process(member.bracelet_exchange(resources.ticket_booths))

        elif action == "smoke":
            yield self.festival.process(member.smoke())

        elif action == "pitch_tent":
            yield self.festival.process(member.pitch_tent(resources.tent_area))

        elif action == "go_to_the_toilet":
            toitoi = member.choose_toitoi()
            yield self.festival.process(member.go_to_the_toilet(toitoi))

        elif action == "go_for_drink":
            pass

        elif action == "go_for_food":
            stall, food = member.choose_stall_with_food()
            yield self.festival.process(member.go_for_food(stall, food))

        elif action == "go_to_tent":
            pass

        elif action == "go_to_schower":
            yield self.festival.process(member.go_to_shower(resources.showers))

        elif action == "go_watch_band":
            pass
        
        elif action == "go_withdraw_money":
            pass

    def group_decision_making(self):
        while True:
            if self.mode == source.Groups_modes.INDIVIDUALLY: 

                for member in self.members:             
                    action = member.next_move()

                    yield from self.start_action(member, action)

            elif self.type == source.Groups.FAMILY:

                parents = [members for members in self.members if members.age_category == source.Age_category.ADULT]
                parent = random.choice(parents)
                action = parent.next_move()

                for member in self.members:
                    yield from self.start_action(member, action)   

            elif self.mode == source.Groups_modes.IN_GROUP:

                leader = random.choice(self.members)
                action = leader.next_move()

                for member in self.members:
                    yield from self.start_action(member, action)
    
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

    def next_move(self):
        #funkce, která rozhodne následující krok návštěvníka
        #v každém rozhodovacím průchodu se kuřákům dá možnost zapálit si cigaretu
        if self.preference["smoker"] == source.Yes_no.YES:
            craving_for_a_cigarette = random.randint(0, 12 - self.state["level_of_addiction"])

            if craving_for_a_cigarette <= 2 and self.state["nicotine"] != 100:
                return "smoke"   

            elif self.state["nicotine"] < 30 or self.state["mood"] < 30:
                return "smoke"
            
            self.state["nicotine"] -= 0.5 * self.state["level_of_addiction"] #když si kuřák nezapálí, sníží se mu úroveň potřeby nikotinu podle jeho úrovně závislosti

        #rozhodnutí se bude odvíjet na základě aktuální pozice návštěvníka

        #věci co se budou návštěvníkovi pravidelně odčítat při každém rozhodování
        self.state["hunger"] -= random.uniform(self.qualities["hunger_frequency"] * 0.5, 5) # hlad se odečte vždycky v rozmenzí 0-5, a generuje se v závislosti na hladovosti účastníka
        self.state["wc"] -= random.uniform(1,5)

        need = self.urgent_need()
        location = self.state["location"]

        if (location == source.Locations.TRAIN_STATION or location == source.Locations.PARKING_LOT): #výběr akce, pokud se návštěvník nachází ve výchozích lokacích (parkoviště/nádraží)
            return source.Actions_moves.GO_TO_ENTRANCE_ZONE.value

        elif location in source.ACTIONS_BY_LOCATIONS and need in source.ACTIONS_BY_LOCATIONS[location]:
                return source.ACTIONS_BY_LOCATIONS[location][need] 
    
        elif location == source.Locations.ENTRANCE_ZONE and need == source.Actions_onetime.PITCH_TENT.value:
            return source.Actions_moves.GO_TO_TENT_AREA.value
        
        elif location == source.Locations.TENT_AREA:
            return source.Actions_moves.GO_TO_ENTRANCE_ZONE.value
        
        elif location == source.Locations.FESTIVAL_AREA:
            return source.Actions_moves.GO_TO_ENTRANCE_ZONE.value
            


    def go_to_entrance_zone(self):
        self.state["location"] = source.Locations.ENTRANCE_ZONE
        print(f"{self.name} {self.surname} jde do vstupní zóny {self.festival.now:.2f}")
        yield self.festival.timeout(10)

    def go_to_tent_area(self):
        self.state["location"] = source.Locations.TENT_AREA
        print(f"{self.name} {self.surname} jde do stanového městečka {self.festival.now:.2f}")
        yield self.festival.timeout(10)

    def go_to_festival_area(self, entrances):
        
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

            self.state["location"] == source.Locations.FESTIVAL_AREA

            print(f"{self.name} {self.surname} prošel kontrolou {entrance_id + 1} v čase {self.festival.now:.2f}, čekal {queue_waiting_time:.2f}s, kontrola trvala {entry_time:.2f}")

        occupied[entrance_id] -= 1
        print(occupied)

    def urgent_need(self):

        #Když nemají pásek na ruce a ani postavený stan -> vybere se jedna z těchto 2 možností, pokud mají jednu věc už splněnou -> vybere se jim ta druhá.
        if self.state["entry_bracelet"] == source.Yes_no.NO or self.accommodation["built"] == source.Yes_no.NO:
            if self.state["entry_bracelet"] == source.Yes_no.NO:
                if self.accommodation["built"] == source.Yes_no.NO:
                    if self.state["location"] == source.Locations.TENT_AREA:  #speciální případ kdy nemají ani jedno, ale předchozí průchod návštěvníka poslal do stanového městečka, tím pádem se mu vybere stavění stanu automaticky.
                        return source.Actions_onetime.PITCH_TENT.value
                    else: 
                        action = random.choice(list(source.Actions_onetime))
                        return action.value
                else:
                    return source.Actions_onetime.BRACELET_EXCHANGE.value
            else:
                return source.Actions_onetime.PITCH_TENT.value 
               
        #Když mají základní 2 potřeby splněné(stan/pásek na ruce pro vstup), tak se řídí podle potřeby s nejnižší hodnotou
        else:
            needs = { "hunger": self.state["hunger"], "thirst": self.state["thirst"], "tiredness": self.state["tiredness"], "mood": self.state["mood"], "wc": self.state["wc"], "hygiene": self.state["hygiene"], "sociability": self.state["sociability"]}
            highest_need = min(needs, key=needs.get)
            
            return highest_need
    
    def go_to_the_toilet(self, toitoi):
        # Funkce simulující návštěvníka jdoucího na WC

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
    
    def go_to_shower(self, shower):
        #funkce obsluhjící návštěvníka ve sprše

        self.state["money"] -= 50

        if self.gender == source.Gender.MALE:
            shower_time = random.uniform(100, 200)
        else:
            shower_time = random.uniform(250, 350)

        with shower.request() as req:
            print(f"{self.name} {self.surname} čeká na volnou sprchu v čase {self.festival.now:.2f}")
            yield req

            print(f"{self.name} {self.surname} vchází do sprchy v čase {self.festival.now:.2f}")
            yield self.festival.timeout(shower_time)
            print(f"{self.name} {self.surname} odchází ze sprchy v čase {self.festival.now:.2f}")

    def choose_toitoi(self):
    # Pokud je muž, má na výběr i pisoár, pokud žena, jen klasické toiky
        if self.state["location"] == source.Locations.FESTIVAL_AREA:
            if self.gender == source.Gender.MALE:
                return resources.toitoi_festival_area_urinal + resources.toitoi_festival_area
            else:
                return resources.toitoi_festival_area

        elif self.state["location"] == source.Locations.TENT_AREA:
            if self.gender == source.Gender.MALE:
                return resources.toitoi_tent_area_urinal + resources.toitoi_tent_area
            else:
                return resources.toitoi_tent_area

        elif self.state["location"] == source.Locations.ENTRANCE_ZONE:
            if self.gender == source.Gender.MALE:
                return resources.toitoi_entrance_zone_urinal + resources.toitoi_entrance_zone
            else:
                return resources.toitoi_entrance_zone

        elif self.state["location"] == source.Locations.CHILL_ZONE:
            if self.gender == source.Gender.MALE:
                return resources.toitoi_chill_zone_urinal + resources.toitoi_chill_zone
            else:
                return resources.toitoi_chill_zone

    def bracelet_exchange(self, ticket_booths):
        #funkce, která simuluje návštěvníkovo ukázání lístku u pokladny, výměnou za pásek na ruku umožňující vstup do arálu.
        #Případně si návštěvník může lístek koupit v pokladně na místě, pokud ho nemá z předprodeje

        yield self.festival.timeout(random.expovariate(1/2))

        ticket_booth_id = ticket_booths_occupied.index(min(ticket_booths_occupied))
        ticket_booth = ticket_booths[ticket_booth_id]
        ticket_booths_occupied[ticket_booth_id] += 1
        
        with ticket_booth.request() as req:
            print(f"{self.name} {self.surname} čeká u pokladny {ticket_booth_id + 1} v čase {self.festival.now:.2f}")
            yield req

            if self.state["pre_sale_ticket"] == source.Yes_no.YES:
                bracelet_exchange_time = random.uniform(2,5)
            else:
                bracelet_exchange_time = random.uniform(4, 8)

            yield self.festival.timeout(bracelet_exchange_time)
            
            self.state["entry_bracelet"] = source.Yes_no.YES

            if self.state["pre_sale_ticket"] == source.Yes_no.NO and self.age > 14:
                self.state["money"] = self.state["money"] - on_site_ticket_price
                global income
                income += on_site_ticket_price
                print(f"{self.name} {self.surname} si byl pro pásek, a odešel z pokladen v čase {self.festival.now:.2f} a kupoval lístek na místě")
            
            else:
                print(f"{self.name} {self.surname} si byl pro pásek, a odešel z pokladen v čase {self.festival.now:.2f} a měl lístek z předprodeje")

        ticket_booths_occupied[ticket_booth_id] -= 1

    def pitch_tent(self, tent_area):
        #funkce která obsluhuje návštěvníkovo stavění stanu
        pitch_time = random.uniform(50,100)

        if self.accommodation["owner"] == source.Yes_no.NO:
            self.accommodation["built"] = source.Yes_no.YES
            print(f"{self.name} {self.surname} pomáhá kolegovi postavit stan v čase {self.festival.now:.2f}")
            yield self.festival.timeout(pitch_time)

        else:
            for i in tent_area:
                if i == []:
                    i.append(self.inventory[0])
                    self.accommodation["built"] = source.Yes_no.YES
                    print(f"{self.name} {self.surname} staví stan v čase {self.festival.now:.2f}")
                    yield self.festival.timeout(pitch_time)
        
    
    def smoke(self):
        #Funkce která obsluhuje návštěvníkovo kouření cigaret

        yield self.festival.timeout(random.uniform(5, 10))

        if self.preference["smoker"] == source.Yes_no.YES:

            self.state["cigarettes"] -= 1
            self.state["nicotine"] = min(self.state["nicotine"] + 30, 100)
            self.state["mood"] += min(self.state["mood"] + 30, 100)
            print(f"{self.name} {self.surname} si zapálil cigaretu.")

        else:
            print(f"{self.name} {self.surname} čekal až si člen skupiny zapálí.")

    def choose_stall_with_food(self):
        #funkce která návštěvníkovi vybere stánek s jídlem podle jeho oblíbeného jídla
        stall, food = self.choose_food() 
        match self.state["location"]:
            case source.Locations.ENTRANCE_ZONE:                                           
                match stall:
                    case "gyros_stall":
                        return resources.stall_entrance_zone_gyros, food
                    case "grill_stall":
                        return resources.stall_entrance_zone_grill, food
                    case "pizza_stall":
                        return resources.stall_entrance_zone_pizza, food
                    case "burger_stall":
                        return resources.stall_entrance_zone_burger, food
                    case "langos_stall":
                        return resources.stall_entrance_zone_langos, food
                    case "sweet_stall":
                        return resources.stall_entrance_zone_sweet, food
                    case "belgian_fries_stall":
                        return resources.stall_entrance_zone_fries, food
                
    def choose_food(self):
        #vybere jídlo, které si návštěvník chce dát -> 50% šance že si dá své oblíbené jídlo, 50% že to bude něco jiného.
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
        # funkce která simuluje návštěvníkovo koupení jídla ve stánku
        price = source.foods[food]["price"]
        time_min, time_max = source.foods[food]["preparation_time"]
        satiety = source.foods[food]["satiety"]

        # funkce skončí, když návštěvník nemá dost peněz
        if self.state["money"] < price:
            print(f"{self.name} {self.surname} nemá dost peněz na {food} (má {self.state["money"]}, cena {price})")
            return
        
        # čekání na stánek
        with stall.request() as req:
            print(f"{self.name} {self.surname} čeká na {food} v čase {self.festival.now:.2f}")
            yield req

            preparation_time = random.randint(time_min, time_max)
            print(f"{self.name} {self.surname} dostává {food}, příprava trvá {preparation_time:.2f}")
            yield self.festival.timeout(preparation_time)

            self.state["money"] -= price
            self.state["hunger"] += satiety
            print(f"{self.name} {self.surname} snědl {food}, aktuální stav hladu je: {min(100,self.state["hunger"])}")

def spawn_groups(env, groups_list):
    i = 0

    for group in groups_list:
        i +=1

        # čeká náhodný čas před spawnem další skupiny
        yield env.timeout(random.expovariate(1/5))
        print(f"Skupina číslo {i} dorazila na nádraží v čase {env.now:.2f}")
        env.process(group.group_decision_making())
