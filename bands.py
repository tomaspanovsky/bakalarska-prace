import random
import source
import math
import operator
import times
from outputs.code import logs

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

def create_lineup(num_days, budget_for_bands, num_of_bands):
    #funkce, která vytvoří program na všechny dny festivalu

    budget_for_day = budget_for_bands / num_days
    num_of_bands 
    total_price_for_bands = 0
    lineup = []

    for i in range(num_days):

        if i == 0:
            bands, price, remaining_money, reduced_bands = choose_bands(budget_for_day, num_of_bands)
        else:
            bands, price, remaining_money, reduced_bands = choose_bands(budget_for_day, num_of_bands, remaining_money, reduced_bands)
        
        total_price_for_bands += price
        lineup.append(bands)

    return lineup, total_price_for_bands  

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

    bands_list = []

    for day in lineup:

        for band in day:
            bands_list.append(band)

    bands_list = sorted(bands_list, key=operator.itemgetter("popularity"))

    return bands_list

def create_schedule(line_up, festival):
    headliner_time = festival.get_time("headliner_time")
    band_time = festival.get_time("band_time")
    signing_time = int(festival.get_time("signing_time"))
    first_show_starts = festival.get_time("first_show_starts")
    last_show_ends = festival.get_time("last_show_ends")
    start_time = festival.get_start_time()

    time_to_play = last_show_ends - first_show_starts
    pause_time = time_to_play - (band_time * (len(line_up[0]) - 1) + headliner_time)
    pause_time /= len(line_up[0]) - 1
    rounded = (pause_time // 10) * 10
    remainder = pause_time - rounded
    pause_time = rounded
    festival.set_pause_between_shows(pause_time)
    start_show = first_show_starts - start_time
    starting_index = start_show
    headliner_time += (len(line_up[0]) - 1) * remainder
    headliner_time = round(headliner_time)
    num_day = 0

    for day in line_up:
        i = 0
        num_day += 1 
        
        if num_day > 1:
            start_show = starting_index + 1440
    
        for band in day:
            i += 1

            if i == 1:
                band["start_playing_time"] = start_show
                
            else:
                start_show = end_show + pause_time
                band["start_playing_time"] = start_show
 
            if i == (len(day)):
                end_show = start_show + headliner_time
            else:
                end_show = start_show + band_time

            band["end_playing_time"] = end_show

            offset = max(band_time, signing_time) + 30

            if i % 2 == 0:
                start_signing = start_show - offset
            else:
                start_signing = start_show + offset

            end_signing = start_signing + signing_time
            band["start_signing_session"] = start_signing
            band["end_signing_session"] = end_signing

    return line_up

def create_merch(festival):
    """Čím slavnější kapela, tím víc si vozí merche -> nejméně známé kapely 1/3 možných položek merche,
    středně známé kapely 2/3 merche,
    a nejslavnější kapely všechny možné položky merche"""

    line_up = festival.get_lineup()
    merch = festival.get_merch()
    bands_merch_type = merch["bands_merch"]
    festival_merch = merch["festival_merch"]
    number_of_merch = len(bands_merch_type)
    number_of_merch_factor = number_of_merch // 3
    number_of_merch = [number_of_merch_factor, number_of_merch_factor * 2, number_of_merch]
    
    merch = {}
    merch["festival_merch"] = festival_merch
    bands_merch = {}

    for bands_day in line_up:
        for band in bands_day:
            if band["popularity"] <= 40:
                band_merch = dict(list(bands_merch_type.items())[:number_of_merch[0]])
            elif band["popularity"] <= 80:
                band_merch = dict(list(bands_merch_type.items())[:number_of_merch[1]])
            else:
                band_merch = dict(list(bands_merch_type.items())[:number_of_merch[2]])

            bands_merch[band["band_name"]] = band_merch
    
    merch["bands_merch"] = bands_merch
    return merch

def band_play(env, band, stage, festival, i):

    start_show = band["start_playing_time"]
    end_show = band["end_playing_time"]
    duration = end_show - start_show
    pause_time = festival.get_pause()
    start_time = festival.get_start_time()
    num_bands = len(festival.get_lineup()[0])
    yield env.timeout(start_show - env.now)

    if len(stage) == 1:
        stage = stage[0]
    
    with stage.resource.request() as req:
        
            yield req
            
            message = f"ČAS {times.get_real_time(env, start_time)}: Kapela {band['band_name']} právě začala hrát a bude hrát do {times.get_real_time(env, start_time, end_show)}."            
            print(message)
            logs.log_message(message)

            yield env.timeout(duration)
            
            if num_bands == i:

                message = f"ČAS {times.get_real_time(env, start_time)}: Kapela {band['band_name']} právě dohrála. Další kapela hraje až zítra v {times.format_time_minutes_to_hours(festival.get_time("first_show_starts"))}."
                print(message)
                logs.log_message(message)            
            else:

                message = f"ČAS {times.get_real_time(env, start_time)}: Kapela {band['band_name']} právě dohrála a náseduje pauza, další kapela hraje za {int(pause_time)} minut."
                print(message)
                logs.log_message(message)

def band_go_to_signing_session(env, band, signing_stall, festival, signing_order):
    start_signign = band["start_signing_session"]
    end_signing = band["end_signing_session"]
    signign_time = int(festival.get_time("signing_time"))
    start_time = festival.get_start_time()

    if band == signing_order[0]:
        signing_stall.resource[3] = band

    yield env.timeout(start_signign - env.now)

    with signing_stall.resource[0].request() as req:

        yield req

        message = f"ČAS {times.get_real_time(env, start_time)}: Právě začala autogramiáda kapely {band['band_name']} a bude trvat do {times.get_real_time(env, start_time, end_signing)}."
        print(message)
        logs.log_message(message)

        yield env.timeout(signign_time)

        message = f"ČAS {times.get_real_time(env, start_time)}: Skončila autogramiáda kapely {band['band_name']}. "
        print(message)
        logs.log_message

        next = False
        for ordered_band in signing_order:

            if ordered_band == band:
                next = True
                continue

            if next:
                signing_stall.resource[3] = ordered_band
                break

def get_order_of_signing_sessions(festival):
    lineup = festival.get_lineup()
    sorted_days = []
    all_bands = []

    for day in lineup:
        sorted_day = sorted(day, key=lambda band: band["start_signing_session"])
        sorted_days.append(sorted_day)

    for day in sorted_days:
        for band in day:
            all_bands.append(band)

    return all_bands

def set_bands(env, lineup, stage, signign_stall, festival):

    signing_order = get_order_of_signing_sessions(festival)

    for day in lineup:
        i = 0
        for band in day:
            i += 1
            env.process(band_play(env, band, stage, festival, i))
            env.process(band_go_to_signing_session(env, band, signign_stall, festival, signing_order))
