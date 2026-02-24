import simpy
import random
import source
import simulation_new
global income

pre_sale_ticket_price = 1000
on_site_ticket_price = pre_sale_ticket_price + 200
tent_area_price = 200
income = 0


def create_visitors(num_visitors, income, environment, available_foods, available_soft_drinks, available_alcohol_drinks):
    # funkce na vytvoření návštěvníků:
    id = 0
    id_tent = 0
    visitors = []
    visitors_groups = []
    
    while num_visitors > 0:       
        group = random.choice(list(source.Groups))
        
        if group == source.Groups.FAMILY and num_visitors < 5: #ošetření rozdělení posledních pár návštěvníků

            if num_visitors == 1:
                group = source.Groups.INDIVIDUAL
            else:
                group = source.Groups.GROUP

        if group == source.Groups.INDIVIDUAL or group == source.Groups.GROUP: #Vytvoření účastníků když jdou jednotlivě nebo jako skupina
            num_members = 1
            have_place_to_sleep = 0
            id_group_members = []
            group_members = []

            if group == source.Groups.GROUP:

                num_members = random.randint(2,6)
                
                if num_members == 1:
                    group = source.Groups.INDIVIDUAL

                elif num_members > num_visitors:
                    num_members = num_visitors

                for i in range(num_members):
                    id_group_members.append(id+i+1)

            for i in range(num_members):
                
                id += 1
                gender = random.choice(list(source.Gender))
                age_category = random.choice([source.Age_category.YOUTH, source.Age_category.ADULT, source.Age_category.SENIOR])

                match age_category:
                    case source.Age_category.YOUTH:
                        age = random.randint(15,25)
                    case source.Age_category.ADULT:
                        age = random.randint(26, 64)
                    case source.Age_category.SENIOR:
                        age = random.randint(65,80)

                if age >= 18:
                    preference = {"alcohol_consumer" : random.choice([True, False]), "smoker" : random.choice([True, False]), "favourite_food" : random.choice(available_foods), "favourite_soft_drink" : random.choice(available_soft_drinks)}
                else:
                    preference = {"alcohol_consumer" : False, "smoker" : False, "favourite_food" : random.choice(available_foods), "favourite_soft_drink" : random.choice(available_soft_drinks)}

                qualities = {"impatience": random.randint(1,10), "tendency_to_spend" : random.randint(1,10), "hunger_frequency" : random.randint(1,10), "alcohol_tolerance" : random.randint(1,10), "weather_tolerance" : random.randint(1, 10)}
                state = {"location" : source.Locations.SPAWN_ZONE, "money" : random.randint(on_site_ticket_price, 10000), "pre_sale_ticket" : random.choice([True, False]) , "entry_bracelet" : False ,"plastic_cup": False, "tiredness": 100, "mood": 100, "hunger" : 100, "thirst": 100, "drunkenness": 0, "wc": 100, "hygiene": 100, "sociability" : 100}                
                fellows = [id_group_members, group] # první parametr je seznam id lidi ze stejné skupiny, druhý parametr je v jakém uskupení je na festivalu (jednotlivec/skupina/rodina) 
                inventory = []

                if gender == source.Gender.MALE:
                    name = random.choice(list(source.names_male))
                    surname = random.choice(list(source.surnames_male))

                else:
                    name = random.choice(list(source.names_female))
                    surname = random.choice(list(source.surnames_female))

                if preference["smoker"] == True:
                    state["nicotine"] = 100
                    state["level_of_addiction"] = random.randint(1,10)
                    state["cigarettes"] = random.randint(1,60)
                
                if preference["alcohol_consumer"] == True:
                    preference["favourite_alcohol"] = random.choice(available_alcohol_drinks)

                if state["pre_sale_ticket"] == True:
                    income += pre_sale_ticket_price

                if num_members == 1:
                    id_tent += 1
                    accommodation = {"owner": True, "tent_id" : id_tent, "built" : False}  #První argument je zda návštěvník vlastní stan, druhý je id_tentu ve kterém bude bydlet, třetí jestli už je postavený.
                    tent = simpy.Resource(environment, capacity = random.randint(1,2))
                    inventory.append(tent)

                else:

                    if have_place_to_sleep > 0 and tent_capacity > 0:
                        accommodation = {"owner": False, "tent_id" : id_tent, "built" : False} #První argument je zda návštěvník vlastní stan, druhý je id_tentu ve kterém bude bydlet, třetí jestli už je postavený.
                        tent_capacity -= 1
                        
                    else:
                        id_tent += 1
                        accommodation = {"owner": True, "tent_id" : id_tent, "built" : False} #První argument je zda návštěvník vlastní stan, druhý je id_tentu ve kterém bude bydlet, třetí jestli už je postavený.
                        tent_capacity = random.randint(1,4)
                        tent = simpy.Resource(environment, capacity = tent_capacity)
                        tent_capacity -= 1
                        inventory.append(tent)
                        have_place_to_sleep += tent_capacity


                num_visitors -= 1
                
                nav = simulation_new.Visitor(environment, id, name=name, surname=surname, gender=gender, age_category = age_category, age = age, qualities = qualities, state = state, preference = preference, accommodation = accommodation, fellows = fellows, inventory = inventory)
                visitors.append(nav)                
                group_members.append(nav)

            if len(group_members) == 1:
                groups = simulation_new.Group(environment, group_members, source.Groups.INDIVIDUAL, source.Groups_modes.INDIVIDUALLY)
            else: 
                groups = simulation_new.Group(environment, group_members, source.Groups.GROUP, source.Groups_modes.IN_GROUP)

            visitors_groups.append(groups)
            group_members = []

        elif group == source.Groups.FAMILY: #Vytvoření rodiny
                
            num_parents = random.randint(1,2)
            num_childrens = random.randint(1,3)
            num_members = num_parents + num_childrens
            father = False
            mother = False

            if num_parents == 1:
                parent = random.choice(list(source.Parents))
                
                if parent == source.Parents.MOTHER:
                    father = True    #V případě, že rodič je jen jeden a bude jím matka, otec se nastaví na True což znamená že otec je nastavený (ikdyž žádný není)
                else:
                    mother = True

                          
            id_group_members = []
            group_members = []
            have_place_to_sleep = 0
            surname_male = random.choice(list(source.surnames_male))
            surname_female = source.surname_map[surname_male]

            for i in range(num_members):
                id_group_members.append(id+i+1)
            
            for i in range(num_members):
                id += 1
                fellows = [id_group_members, group]

                if num_parents > 0:

                    num_parents -= 1

                    if mother != True:
                        gender = source.Gender.FEMALE
                        mother = True

                    elif father != True:
                        gender = source.Gender.MALE
                        father = True
                                
                                #nedočkavost
                    qualities = {"impatience": random.randint(1,10), "tendency_to_spend" : random.randint(1,10), "hunger_frequency" : random.randint(1,10), "alcohol_tolerance" : random.randint(1,10), "weather_tolerance" : random.randint(1, 10)}
                    state = {"location" : source.Locations.SPAWN_ZONE, "money" : random.randint(on_site_ticket_price, 10000), "pre_sale_ticket" : random.choice([True, False]) , "entry_bracelet" : False , "plastic_cup": False, "tiredness": 100, "mood": 100, "hunger" : 100, "thirst": 100, "drunkenness": 0, "wc": 100, "hygiene": 100, "sociability" : 100}
                    preference = {"alcohol_consumer" : random.choice([True, False]), "smoker" : random.choice([True, False]), "favourite_food" : random.choice(available_foods), "favourite_soft_drink" : random.choice(available_soft_drinks)}
                    inventory = []
                    age_category = source.Age_category.ADULT
                    age = random.randint(26, 64)

                    if gender == source.Gender.MALE:
                        name = random.choice(list(source.names_male))
                        surname = surname_male

                    else:
                        name = random.choice(list(source.names_female))
                        surname = surname_female

                    if preference["smoker"] == True:
                        state["nicotine"] = 100
                        state["level_of_addiction"] = random.randint(1,10)
                        state["cigarettes"] = random.randint(1,60)
                
                    if preference["alcohol_consumer"] == True:
                        preference["favourite_alcohol"] = random.choice(available_alcohol_drinks)

                    if state["pre_sale_ticket"] == True:
                        income += pre_sale_ticket_price

                    if (have_place_to_sleep >= num_members):
                        accommodation = {"owner": False, "tent_id" : id_tent, "built" : False} #První argument je zda návštěvník vlastní stan, druhý je id_tentu ve kterém bude bydlet, třetí jestli už je postavený.

                    else:
                        id_tent += 1
                        accommodation = {"owner": True, "tent_id" : id_tent, "built" : False} #První argument je zda návštěvník vlastní stan, druhý je id_tentu ve kterém bude bydlet, třetí jestli už je postavený.
                        tent_capacity = num_members
                        tent = simpy.Resource(environment, capacity = tent_capacity)
                        inventory.append(tent)
                        have_place_to_sleep += tent_capacity

                    num_visitors -= 1

                    nav = simulation_new.Visitor(environment, id, name=name, surname=surname, gender=gender, age_category = age_category, age = age, qualities = qualities, state = state, preference = preference, accommodation = accommodation, fellows = fellows, inventory = inventory)    
                    visitors.append(nav)
                    group_members.append(nav)

                else:
                    gender = random.choice(list(source.Gender))
                    qualities = {"impatience": random.randint(1,10), "tendency_to_spend" : random.randint(1,10), "hunger_frequency" : random.randint(1,10), "alcohol_tolerance" : random.randint(1,10), "weather_tolerance" : random.randint(1, 10)}
                    state = {"location" : source.Locations.SPAWN_ZONE, "money" : random.randint(on_site_ticket_price, 10000), "pre_sale_ticket" : random.choice([True, False]) , "entry_bracelet" : False ,"plastic_cup": False, "tiredness": 100, "mood": 100, "hunger" : 100, "thirst": 100, "drunkenness": 0, "wc": 100, "hygiene": 100, "sociability" : 100}
                    preference = {"alcohol_consumer" : False, "smoker" : False, "favourite_food" : random.choice(available_foods), "favourite_soft_drink" : random.choice(available_soft_drinks)}
                    inventory = []
                    age_category = source.Age_category.CHILD
                    age = random.randint(6, 14)

                    if gender == source.Gender.MALE:
                        name = random.choice(list(source.names_male))
                        surname = surname_male

                    else:
                        name = random.choice(list(source.names_female))
                        surname = surname_female

                    if state["pre_sale_ticket"] == True:
                        income += pre_sale_ticket_price

                    accommodation = {"owner": False, "tent_id" : id_tent, "built" : False} #První argument je zda návštěvník vlastní stan, druhý je id_tentu ve kterém bude bydlet, třetí jestli už je postavený.
                    num_visitors -= 1

                    nav = simulation_new.Visitor(environment, id, name=name, surname=surname, gender=gender, age_category = age_category, age = age, qualities = qualities, state = state, preference = preference, accommodation = accommodation, fellows = fellows, inventory = inventory)    
                    visitors.append(nav)
                    group_members.append(nav)

            groups = simulation_new.Group(environment, group_members, source.Groups.FAMILY, source.Groups_modes.IN_GROUP)
            visitors_groups.append(groups)
            group_members = []

    return visitors, visitors_groups
    
def print_visitors(visitors):
    for n in visitors:
        print(f"ID: {n.id}, Jméno: {n.name} {n.surname}, Věk: {n.age} ({n.age_category.name}), Pohlaví: {n.gender.name}")
        print("Vlastnosti:")
        for k, v in n.qualities.items():
            print(f"  {k}: {v}")
        print("Stav:")
        for k, v in n.state.items():
            print(f"  {k}: {v}")
        print("Preference:")
        for k, v in n.preference.items():
            print(f"  {k}: {v}")
        print("Bydlení:")
        for k, v in n.accommodation.items():
            print(f"  {k}: {v}")
        print("Parta:")
        print(f"  ID členů: {n.fellows[0]}, Uskupení: {n.fellows[1].name}")
        print("Inventář:")
        print(f"  {n.inventory}")
        print("-" * 50)
