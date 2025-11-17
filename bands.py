import random
import source
import math
import operator
global income

def choose_bands(budget, num, remaining_money = 0, bands = source.BANDS.copy()):
    #Vybere kapely do programu jednoho dne podle budgetu
    random.shuffle(bands)  # zamícháme pořadí

    budget += remaining_money
    deposit = budget / 4
    chosen = []
    total_price = 0
    order_of_band = 0

    for band in bands[:]:
        
        if len(chosen) >= num:
            #seřazení kapel od nejméně známé po headlinera

            chosen = sorted(chosen, key=operator.itemgetter("popularity"))
            break

        if num - order_of_band != 1:
            
            if total_price + band["price"] <= budget and band["price"] <= budget - deposit:
                chosen.append(band)
                bands.remove(band)
                total_price += band["price"]
                order_of_band += 1

        else:
            left = budget - total_price
            possibilities = [k for k in bands if k["price"] <= left and k not in chosen]

            headliner = possibilities[0]
            for k in possibilities[1:]:
                if k["price"] > headliner["price"]:
                    headliner = k

            chosen.append(headliner)
            bands.remove(headliner)
            total_price += headliner["price"]

    remaining_money = budget - total_price

    return chosen, total_price, remaining_money, bands

def create_lineup(num_days, budget_for_bands, total_num_of_bands):
    #funkce, která vytvoří program na všechny dny festivalu

    budget_for_day = budget_for_bands / num_days
    num_bands_per_day = total_num_of_bands / num_days
    total_price_za_kapely = 0
    lineup = []

    for i in range(num_days):

        if i == 0:
            bands, price, remaining_money, redukovane_kapely = choose_bands(budget_for_day, num_bands_per_day)
        else:
            bands, price, remaining_money, redukovane_kapely = choose_bands(budget_for_day, num_bands_per_day, remaining_money, redukovane_kapely)
        
        total_price_za_kapely += price
        lineup.append(bands)

    return lineup, total_price_za_kapely  

def print_lineup(lineup):
    #vypis kapel
    i = 1

    for day in lineup:
        print("DEN", i)
        i += 1

        for band in day:     
            print(band["band_name"])

        print()

def add_favorite_bands_to_visitor(visitors, bands):
    #přidá každému návštěvníkovi z kapel na line-upu nějaké jeho oblíbené kapely, polovina kapel je vybrána náhodně, 
    #druhá polovina jsou headlineři.
    bands = merge_bands(bands)

    for visitor in visitors:
        bands_to_choose = bands.copy()
        favourite_bands = []
        num_favourite = random.randint(1, math.floor(len(bands) * 0.75))
        random_half = num_favourite // 2
        headliner_half = num_favourite - random_half

        for i in range(headliner_half):
            choosen_band = bands_to_choose[len(bands_to_choose)-1]
            favourite_bands.append(choosen_band)
            bands_to_choose.remove(choosen_band)

        for j in range(random_half):
            random.shuffle(bands_to_choose)
            choosen_band = bands_to_choose[0]
            favourite_bands.append(choosen_band)
            bands_to_choose.remove(choosen_band)

        visitor.preference["favourite_bands"] = favourite_bands
        
    return visitors

def merge_bands(lineup):
    #funkce, která z vícedenního lineupu udělá jeden seznam se všema kapelama

    bands_list = []

    for day in lineup:

        for band in day:
            bands_list.append(band)

    bands_list = sorted(bands_list, key=operator.itemgetter("popularity"))

    return bands_list

