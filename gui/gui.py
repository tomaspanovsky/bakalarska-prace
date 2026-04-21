import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import textwrap
import copy
import simpy
from . import saving
from . import loading 
import source
import visitors
import bands
import resources
import simulation
import fest
import foods
import drinks
import random
import source
import times
import time
import simulation_controller
import threading
from outputs.code import logs

current_zone = None         
current_object = None
drawing = False
last_x, last_y = None, None
zone_rect = None
zone_label = None
zone_buttons = {}
object_buttons = {}
selected_zone_instance = None
selected_object = None
selected_connect_zone = None
selected_line = None
is_dragging_object = False
is_dragging_zone = False
connect_start_zone = None
object_id = 0

zones_data = {
    "Spawn zóna": {},
    "Vstupní zóna": {},
    "Festivalový areál": {},
    "Stanové městečko": {},
    "Chill zóna": {},
    "Zábavní zóna": {}
}

zones_data_default = copy.deepcopy(zones_data)

def run_app():
    settings = {}
    controller = None
    default_loaded = False
    loaded = False
    value = 1
    
    merch_data = None
    
    def start():
        nonlocal controller, value, loaded
        global current_mode

        if not loaded:
            show_message("Musí být načten nebo vytvořen a uložen festivalový areál!")
            return
        
        
        merch = get_merch(bands_entries)
        capacities = get_capacities()
        prices = get_prices()
        festival_times_data = get_times()

        settings["num_visitors"] = int(entry_visitors.get())
        settings["num_days"] = int(entry_days.get())
        settings["budget_for_bands"] = int(entry_budget.get())
        settings["num_bands"] = int(entry_num_bands.get())
        settings["simulation_start_time"] = simulation_start_time.get()
        settings["prices"] = prices
        settings["merch"] = merch
        settings["capacities"] = capacities
        
        editor_buttons_frame.pack_forget()
        frame_left.pack_forget()
        frame_right.pack_forget()
        simulation_buttons_frame.pack()
        left_simulation_container.pack(side="left", fill="y")
        create_zone_stats_labels()

        num_visitors = settings["num_visitors"]
        num_days = settings["num_days"]
        budget_for_bands = settings["budget_for_bands"]
        num_bands = settings["num_bands"]
        prices = settings["prices"]
        festival_times = {"simulation_start_time": times.format_time_string_to_mins(settings["simulation_start_time"]), "headliner_time" : int(festival_times_data["headliner_time"]), "band_time" : int(festival_times_data["band_time"]), "first_show_starts" : times.format_time_string_to_mins(festival_times_data["first_show_starts"]), "last_show_ends" : times.format_time_string_to_mins(festival_times_data["last_show_ends"]), "signing_time" : int((festival_times_data["signing_time"]))}

        festival_env = simpy.Environment()

        stalls = resources.create_resources(festival_env, capacities, num_visitors, festival_times["simulation_start_time"])
        logs.add_stalls_to_logs(stalls)

        food_stalls_names = resources.find_all_type_stall_at_festival(stalls, "foods")
        drink_stalls_names = resources.find_all_type_stall_at_festival(stalls, "drinks")
        available_foods = foods.find_all_foods_at_festival(food_stalls_names)
        available_soft_drinks, available_alcohol_drinks = drinks.find_all_drinks_at_festival(drink_stalls_names)

        people, groups_of_visitors = visitors.create_visitors(num_visitors, festival_env, available_foods, available_soft_drinks, available_alcohol_drinks, prices["on_site_price"], prices["pre_sale_price"], prices["camping_area_price"])
        lineup = bands.create_lineup(num_days, budget_for_bands, num_bands)
        people = bands.add_favorite_bands_to_visitor(people, lineup)
        festival = fest.Festival(festival_env, people, groups_of_visitors, num_days, lineup, stalls, prices, festival_times, random.choice(list(source.Weather)), merch)
        lineup = bands.create_schedule(lineup, festival)
        merch = bands.create_merch(festival)
        festival.set_merch(merch)

        stage = resources.find_stalls_in_zone(festival_env, festival, "stage")
        signing_stall = resources.find_stalls_in_zone(festival_env, festival, "signing_stall")
        bands.set_bands(festival_env, lineup, stage, signing_stall[0], festival)


        bands.print_lineup(lineup)
        visitors.print_visitors(people)

        controller = simulation_controller.SimulationController(festival_env, festival)

        festival_env.process(simulation.spawn_groups(festival_env, groups_of_visitors, festival))

        message = f"ČAS {times.get_real_time(festival_env, festival.get_start_time())}: START SIMULACE"
        print(message)
        logs.log_message(message)
        message = f"ČAS {times.get_real_time(festival_env, festival.get_start_time())}: 1. DEN"
        print(message)
        logs.log_message("1. DEN:")

        current_mode = "inspect"

        SIMULATION_MODE = "debug"
        SIMULATION_MODE = "hardcore"

        if SIMULATION_MODE == "debug":

            print("Simulace jede v debug režimu")
            festival_env.run(until=num_days * 1440)
            print("SIMULACE PROBĚHLA ÚSPĚŠNĚ")
        else:
            print("Simulace jede v krokovacím režimu")   

    def move_forward_by_time():
        nonlocal value

        if controller.get_auto_mode_state():
            print("Nelze krokovat během automatického režimu.")
            return

        controller.move_forward_by_time(value)
        move_forward_actions()

    def start_smooth_simulation():
        smooth_simulation_start_button.pack_forget()
        smooth_simulation_stop_button.pack(anchor="center", pady=10)
        controller.start_smooth_simulation()
        threading.Thread(target=smooth_loop, daemon=True).start()

    def stop_smooth_simulation():
        smooth_simulation_start_button.pack(anchor="center", pady=10)
        smooth_simulation_stop_button.pack_forget()
        controller.stop_smooth_simulation()
    
    def smooth_loop():

        while controller.get_auto_mode_state():
            controller.move_forward_by_time(1)

            root.after(0, lambda: move_forward_actions())
            time.sleep(1)
            

    def move_forward_actions():
        new_logs = get_new_logs()
        get_actual_state(controller)
        view_changes(controller)
        view_logs(new_logs)

    def exit_app():
        print("Uživatel ukončil program")
        root.quit()
        root.destroy()
    
    def stop_simulation():
        global current_mode

        controller.stop_smooth_simulation()
        festival = controller.get_festival()
        current_mode = "edit"

        delete_zone_stats_labels()
        stall_log_box.delete("0.0", "end")
        messages_log_box.delete("0.0", "end")
        
        simulation_buttons_frame.pack_forget()
        left_simulation_container.pack_forget()
        editor_buttons_frame.pack(pady=20)
        frame_left.pack(side="left", fill="y", padx=0, pady=0)
        frame_right.pack(side="left", fill="y", padx=0, pady=0)

        logs.log_message("SIMULACE UKONČENA")
        logs.save_logs(festival)

    def get_new_logs():
        all_logs = logs.all_messages
        new_logs = all_logs[controller.get_number_of_shown_logs():]
        controller.increase_shown_logs(len(new_logs))
        return new_logs

    def view_logs(new_logs):
        for log in new_logs:
            add_log(log)

    def add_log(log):
        MAX_LOG_LINES = 100
        WRAP_WIDTH = 55 

        if ": " in log:
            prefix, rest = log.split(": ", 1)
            prefix = prefix + ": "
        else:
            prefix = ""
            rest = log

        # odsazení pro další řádky
        indent = " " * (len(prefix) + 8)

        # ruční zalomení textu
        wrapped = textwrap.fill(
            rest,
            width=WRAP_WIDTH,
            initial_indent=prefix,
            subsequent_indent=indent,
            break_long_words=False,
            break_on_hyphens=False
        )

        # vložení do textboxu
        messages_log_box.configure(state="normal")
        messages_log_box.insert("end", wrapped + "\n")
        messages_log_box.see("end")

        # limit počtu řádků
        lines = int(messages_log_box.index("end-1c").split(".")[0])
        if lines > MAX_LOG_LINES:
            messages_log_box.delete("1.0", f"{lines - MAX_LOG_LINES}.0")

        messages_log_box.configure(state="disabled")

    def get_actual_state(controller):
        festival = controller.get_festival()
        stalls = festival.get_stalls()
        simulation_state = controller.get_simulation_state()
        num_people_in_zones = festival.get_num_people_in_zones()

        simulation_state["time"] = controller.get_actual_time()

        for zone in num_people_in_zones:
            simulation_state["zones"][zone]["num_people_in_zone"] = num_people_in_zones[zone]

        for zone, zone_stalls in stalls.items():
            for stall in zone_stalls:

                stall_name = stall.get_name()
                stall_id = stall.get_id()

                stall_list = simulation_state["zones"][zone]["stalls"][stall_name]

                for stall_data in stall_list:
                    if stall_data["id"] == stall_id:

                        if stall_name == "standing_at_stage":
                            resource = stall.get_resource()

                            stall_data["num_people_on_show"] = stall.get_num_using()
                            stall_data["num_people_in_first_lines"] = stall.get_num_using("first_lines")
                            stall_data["num_people_in_the_middle"] = stall.get_num_using("middle")
                            stall_data["num_people_in_back"] = stall.get_num_using("back")

                        elif stall_name == "meadow_for_living":
                            stall_data["num_tents"] = stall.get_num_tents()
                            stall_data["num_people_in_tents"] = stall.get_num_using()

                        else:
                            stall_data["num_people_served"] = stall.get_num_using()
                            stall_data["num_people_in_queue"] = stall.get_num_in_queue()
                            break 

    def open_editor():
        nonlocal default_loaded

        main_frame.pack_forget()
        editor_frame.pack(fill="both", expand=True)

        if not default_loaded:
            load_default()
            default_loaded = True
        
    def open_stalls_settings():
        main_frame.pack_forget()
        background_frame.pack(fill="both", expand=True)
        stall_settings_frame.place(relx=0.5, rely=0.5, anchor="center")

    def open_times_settings():
        main_frame.pack_forget()
        background_frame.pack(fill="both", expand=True)
        times_settings_frame.place(relx=0.5, rely=0.5, anchor="center")

    def open_prices_settings():
        main_frame.pack_forget()
        background_frame.pack(fill="both", expand=True)
        prices_settings_frame.place(relx=0.5, rely=0.5, anchor="center")

    def open_merch_settings():
        nonlocal merch_data
        main_frame.pack_forget()
        background_frame.pack(fill="both", expand=True)
        merch_frame.place(relx=0.5, rely=0.5, anchor="center")
        
    def open_settings():
        main_frame_middle.pack(anchor="center", expand=True)
        settings_open_button.pack_forget()
        settings_hide_button.pack(side="left", padx=10, pady=10)

    def hide_settings():
        main_frame_middle.pack_forget()
        settings_open_button.pack(side="left", padx=10, pady=10)
        settings_hide_button.pack_forget()
    
    def go_back():
        if stall_settings_frame.winfo_ismapped():
            stall_settings_frame.place_forget()
  
        elif prices_settings_frame.winfo_ismapped():
            prices_settings_frame.place_forget()

        elif times_settings_frame.winfo_ismapped():
            times_settings_frame.place_forget()
        
        elif merch_frame.winfo_ismapped():
            merch_frame.place_forget()

        elif editor_frame.winfo_ismapped():
            editor_frame.pack_forget()

        background_frame.pack_forget()
        main_frame.pack(fill="both", expand=True)

    def save_actual_state():
        logs.save_actual_state(controller)

    def save_merch():
        merch = get_merch(bands_entries)
        saving.save_merch_settings(merch)

    def save_capacities():
        capacities = get_capacities()
        saving.save_capacities_settings(capacities)

    def save_fest_prices():
        prices = get_prices()
        saving.save_fest_prices_settings(prices)

    def save_time_settings():
        festival_times = get_times()
        saving.save_time_settings(festival_times)

    def save():
        nonlocal loaded

        saving.save(zones_data)
        print("Rozložení úspěšně uloženo do festival_settings.json")
        loaded = True

    def print_zones_data():
        global zones_data
        print(zones_data)
    
    def load():
        nonlocal loaded

        delete()
        data = loading.load(auto=False)
        draw_load(data)
        loaded = True

    def load_default():
        nonlocal loaded

        data = loading.load(auto=True)
        draw_load(data)
        loaded = True

    def delete():
        global zones_data, selected_zone_instance, selected_object, selected_line
        global connect_start_zone, is_dragging_object, is_dragging_zone
        nonlocal loaded

        canvas.delete("all")
        zones_data = copy.deepcopy(zones_data_default)

        selected_zone_instance = None
        selected_object = None
        selected_line = None
        connect_start_zone = None
        is_dragging_object = False
        is_dragging_zone = False
        loaded = False
        
        print("Uživatel smazal canvas")

    # ---------- HLAVNÍ OKNO ----------
    
    root = tk.Tk()
    root.title("Nastavení festivalu")
    root.attributes("-fullscreen", True)
    root.configure(bg="black")

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

#------------------------------------------------------------------STYLY----------------------------------------------------------------------------------------------------
    
    pizza = ImageTk.PhotoImage(Image.open("data/emojis/pizza.png").resize((23, 23)))
    ticket_booth = ImageTk.PhotoImage(Image.open("data/emojis/dollar.png").resize((23, 23)))
    beer = ImageTk.PhotoImage(Image.open("data/emojis/beer.png").resize((23, 23)))
    hamburger = ImageTk.PhotoImage(Image.open("data/emojis/hamburger.png").resize((23, 23)))
    grill = ImageTk.PhotoImage(Image.open("data/emojis/cut_of_meat.png").resize((23, 23)))
    gyros = ImageTk.PhotoImage(Image.open("data/emojis/burrito.png").resize((23, 23)))
    langos = ImageTk.PhotoImage(Image.open("data/emojis/flatbread.png").resize((23, 23)))
    fries = ImageTk.PhotoImage(Image.open("data/emojis/fries.png").resize((23, 23)))
    sweet = ImageTk.PhotoImage(Image.open("data/emojis/doughnut.png").resize((23, 23)))
    atm = ImageTk.PhotoImage(Image.open("data/emojis/atm.png").resize((23, 23)))
    battery = ImageTk.PhotoImage(Image.open("data/emojis/battery.png").resize((23, 23)))
    tables = ImageTk.PhotoImage(Image.open("data/emojis/table.png").resize((23, 23)))
    soft_drinks = ImageTk.PhotoImage(Image.open("data/emojis/cup_with_straw.png").resize((23, 23)))
    wc = ImageTk.PhotoImage(Image.open("data/emojis/restroom.png").resize((23, 23)))
    shower = ImageTk.PhotoImage(Image.open("data/emojis/shower.png").resize((23, 23)))
    cigars = ImageTk.PhotoImage(Image.open("data/emojis/smoking.png").resize((23, 23)))
    washing = ImageTk.PhotoImage(Image.open("data/emojis/soap.png").resize((23, 23)))
    cocktails = ImageTk.PhotoImage(Image.open("data/emojis/tropical_drink.png").resize((23, 23)))
    water_pipe = ImageTk.PhotoImage(Image.open("data/emojis/bubbles.png").resize((23, 23)))
    stage = ImageTk.PhotoImage(Image.open("data/emojis/guitar.png").resize((23, 23)))
    signing = ImageTk.PhotoImage(Image.open("data/emojis/writing_hand.png").resize((23, 23)))
    merch = ImageTk.PhotoImage(Image.open("data/emojis/shirt.png").resize((23, 23)))
    shot = ImageTk.PhotoImage(Image.open("data/emojis/shot.png").resize((23, 23)))
    chill = ImageTk.PhotoImage(Image.open("data/emojis/beach.png").resize((23, 23)))
    rollercoaster = ImageTk.PhotoImage(Image.open("data/emojis/roller_coaster.png").resize((23, 23)))
    jumping_castle = ImageTk.PhotoImage(Image.open("data/emojis/jumping_castle.png").resize((23, 23)))
    hammer = ImageTk.PhotoImage(Image.open("data/emojis/hammer.png").resize((23, 23)))
    carousel = ImageTk.PhotoImage(Image.open("data/emojis/carousel.png").resize((23, 23)))
    bungeejumping = ImageTk.PhotoImage(Image.open("data/emojis/bungeejumping.png").resize((23, 23)))
    bench = ImageTk.PhotoImage(Image.open("data/emojis/bench.png").resize((23, 23)))
    cup_return = ImageTk.PhotoImage(Image.open("data/emojis/back.png").resize((23, 23)))
    tent = ImageTk.PhotoImage(Image.open("data/emojis/tent.png").resize((22, 22)))
    door = ImageTk.PhotoImage(Image.open("data/emojis/door.png").resize((22, 22)))

    OBJECT_IMAGES = {"Louka na stanování": [tent, "Louka na stanování"],
                    "Chill stánek": [chill, "Chill stánek"],
                    "Skákací hrad": [jumping_castle, "Skákací hrad"],
                    "Horská dráha": [rollercoaster, "Horská dráha"],
                    "Kladivo": [hammer, "Kladivo"],
                    "Řetizkáč": [carousel, "Řetizkáč"],
                    "Bungee-jumping": [bungeejumping, "Bungee-jumping"],
                    "Lavice": [bench, "Lavice"],
                    "Výkup kelímků": [cup_return, "Výkup kelímků"],
                    "Pizza stánek": [pizza, "Pizza"],
                    "Pokladna": [ticket_booth, "Pokladna"],
                    "Burger stánek": [hamburger, "Burgery"],
                    "Gyros stánek": [gyros, "Gyros"],
                    "Grill stánek": [grill, "Grill"],
                    "Bel hranolky stánek": [fries, "Belgické hranolky"],
                    "Langoš stánek": [langos, "Langoše"],
                    "Sladký stánek": [sweet, "Sladké"],
                    "Pivní stánek": [beer, "Pivo"],
                    "Nealko stánek": [soft_drinks, "Nealko"],
                    "Red Bull stánek": [shot, "RedBull"],
                    "Stánek s míchanými drinky": [cocktails, "Míchané drinky"],
                    "Bankomat": [atm, "Bankomat"],
                    "Dobíjecí stan": [battery, "Nabíjení telefonů"],
                    "Stoly": [tables, "Stoly"],
                    "Toitoiky": [wc, "Toitoiky"],
                    "Umývárna": [washing, "Umývárna"],
                    "Sprchy": [shower, "Sprchy"],
                    "Cigaretový stánek": [cigars, "Cigarety"],
                    "Stánek s vodníma dýmkama": [water_pipe, "Vodní dýmka"],
                    "Podium": [stage, "Pódium"],
                    "Stan na autogramiády": [signing, "Autogramiády"],
                    "Merch stan": [merch, "Merch"],
                    "Vstup": [door, "Vstup"]}


    label_style = {"bg": "black", "fg": "white", "font": ("Arial", 20)}
    entry_style = {"font": ("Arial", 18), "bg": "#222", "fg": "white", "insertbackground": "white", "width": 10}
    entry_style2 = {"font": ("Arial", 18),  "bg": "#222", "fg": "white", "insertbackground": "white", "width": 5}

    def blue_button(parent, text, command, text_size = None):
        if text_size:
            size = text_size
        else:
            size = 25

        return ctk.CTkButton(parent, text=text, command=command, corner_radius=20, fg_color="blue", hover_color="#2f4dfa", text_color="white", width=150, height=65, font=("Arial", size))

    def blue_button_small(parent, text, command, text_size = None, bold = None):
        
        if text_size:
            size = text_size
        else:
            size = 25

        if bold:
            font = ("Arial", size, "bold")
        else:
            font = ("Arial", size)

        return ctk.CTkButton(parent, text=text, command=command, corner_radius=20, fg_color="blue", hover_color="#2f4dfa", text_color="white", width=90, height=50, font=font)
        
    def red_button(parent, text, command):
        return ctk.CTkButton(parent, text=text, command=command, corner_radius=20, fg_color="red", hover_color="#fc4437", text_color="white", width=150, height=65, font=("Arial", 25))
    
    def red_button_small(parent, text, command):
        return ctk.CTkButton(parent, text=text, command=command, corner_radius=20, fg_color="red", hover_color="#fc4437", text_color="white", width=90, height=50, font=("Arial", 18))
    
    def green_button(parent, text, command):
        return ctk.CTkButton(parent, text=text, command=command, corner_radius=20, fg_color="green", hover_color="#4ef35c", text_color="white", width=150, height=65, font=("Arial", 25))
    
    def green_button_small(parent, text, command):
        return ctk.CTkButton(parent, text=text, command=command, corner_radius=20, fg_color="green", hover_color="#4ef35c", text_color="white", width=90, height=50, font=("Arial", 25, "bold"))

    def object_button(parent, text, obj, img):       
        return ctk.CTkButton(parent, text=text, image=img, compound="left", anchor="w", corner_radius=10, fg_color="white", hover_color="#c3c3c5",  text_color="black", border_width=2, border_color="black", width=170, height=28, font=("Arial", 12.5, "bold"), command=lambda o=obj: select_object(o))
    
    def zone_button(parent, zone_name):
        return ctk.CTkButton(parent, text=zone_name, corner_radius=10, fg_color="white", hover_color="#c3c3c5",  text_color="black", border_width=2, border_color="black", width=170, height=50, font=("Arial", 15, "bold"), command=lambda z=zone_name: select_zone(z))
    
    def mode_button(parent, text):
        return ctk.CTkButton(parent, text=text, corner_radius=10, fg_color="white", hover_color="#c3c3c5",  text_color="black", border_width=2, border_color="black",  width=55, height=55, font=("Arial", 14, "bold"), command=lambda m=mode_name: select_mode(m))

    def choose_emoji(stall_name, OBJECT_IMAGE=OBJECT_IMAGES):
        img = OBJECT_IMAGE[stall_name][0]
        text = OBJECT_IMAGE[stall_name][1]

        return img, text
    
    def show_message(message, automatic_close = None):
        warning = ctk.CTkFrame(root, corner_radius=20, fg_color="black")
        warning.place(relx=0.5, rely=0.5, anchor="center")

        label = tk.Label(warning, text=message, fg="white", bg="black", font=("Arial", 18, "bold"))
        label.pack(padx=30, pady=(20, 10))

        def close_message():
            warning.destroy()

        close_btn = red_button_small(warning, "Zavřít", close_message)
        close_btn.pack_forget()

        if not automatic_close:
            close_btn.pack(pady=(0, 15))


    # ---------- OBRAZOVKA 1: Úvodní menu ----------
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    background_frame = ctk.CTkFrame(root, fg_color="transparent", corner_radius=30)
    background_frame.pack_forget()

    main_frame = ctk.CTkFrame(root, fg_color="transparent", corner_radius=30)
    main_frame.pack(fill="both", expand=True)

    bg_image = ctk.CTkImage(Image.open("data/images/main_page2.png"), size=(screen_width, screen_height))
    
    background_label = ctk.CTkLabel(background_frame, image=bg_image, text="")
    background_label.place(relx=0.5, rely=0.5, anchor="center")

    background_label_main_frame = ctk.CTkLabel(main_frame, image=bg_image, text="")
    background_label_main_frame.place(relx=0.5, rely=0.5, anchor="center")

    title_label = ctk.CTkLabel(main_frame, text=" Simulace hudebního festivalu ", font=("Segoe UI", 60, "bold"), fg_color="black", text_color="white")
    title_label.pack(padx=30, pady=30)

    main_frame_middle = ctk.CTkFrame(main_frame, fg_color="black", corner_radius=30)
    main_frame_middle.pack_forget()

    basic_settings_frame_title = ctk.CTkFrame(main_frame_middle, fg_color="black")
    basic_settings_frame_title.pack()

    ctk.CTkLabel(basic_settings_frame_title, text="Nastavení", font=("Arial", 32,"bold"), fg_color="black", text_color="white").pack(padx=20, pady=10)
    
    basic_settings_frame = ctk.CTkFrame(main_frame_middle, fg_color="transparent", corner_radius=30)
    basic_settings_frame.pack(padx=10)

    tk.Label(basic_settings_frame, text="Počet návštěvníků:", **label_style).grid(row=0, column=0, pady=10, sticky="w")
    entry_visitors = tk.Entry(basic_settings_frame, **entry_style)
    entry_visitors.grid(row=0, column=1, pady=10)
    entry_visitors.insert(0, "50")

    tk.Label(basic_settings_frame, text="Počet dní:", **label_style).grid(row=1, column=0, pady=10, sticky="w")
    entry_days = tk.Entry(basic_settings_frame, **entry_style)
    entry_days.grid(row=1, column=1, pady=10)
    entry_days.insert(0, "2")

    tk.Label(basic_settings_frame, text="Rozpočet pro kapely:", **label_style).grid(row=2, column=0, pady=10, sticky="w")
    entry_budget = tk.Entry(basic_settings_frame, **entry_style)
    entry_budget.grid(row=2, column=1, pady=10)
    entry_budget.insert(0, "10000000")

    tk.Label(basic_settings_frame, text="Počet kapel na den:", **label_style).grid(row=3, column=0, pady=10, sticky="w")
    entry_num_bands = tk.Entry(basic_settings_frame, **entry_style)
    entry_num_bands.grid(row=3, column=1, pady=10)
    entry_num_bands.insert(0, "8")

    tk.Label(basic_settings_frame, text="Čas začátku simulace:", **label_style).grid(row=4, column=0, pady=10, sticky="w")
    simulation_start_time = tk.Entry(basic_settings_frame, **entry_style)
    simulation_start_time.grid(row=4, column=1, pady=10)
    simulation_start_time.insert(0, "09:00")

    advanced_settings_buttons_frame = tk.Frame(main_frame_middle, bg="black")
    advanced_settings_buttons_frame.pack()

    stall_settings_button = blue_button_small(advanced_settings_buttons_frame, "Kapacity\nobjektů", open_stalls_settings, 14, bold=True)
    stall_settings_button.pack(side="left", padx=10, pady=20)

    prices_settings_button = blue_button_small(advanced_settings_buttons_frame, "Ceny\nfestivalu", open_prices_settings, 14, bold=True)
    prices_settings_button.pack(side="left", padx=10, pady=20) 

    merch_settings_button = blue_button_small(advanced_settings_buttons_frame, "Ceny\nmerche", open_merch_settings, 14, bold=True)
    merch_settings_button.pack(side="left", padx=10, pady=20) 

    times_settings_button = blue_button_small(advanced_settings_buttons_frame, "Časy", open_times_settings, 14, bold=True)
    times_settings_button.pack(side="left", padx=10, pady=20) 

    bottom_frame = ctk.CTkFrame(main_frame, fg_color="black", corner_radius=30)
    bottom_frame.pack(side="bottom", pady=30)

    settings_open_button = blue_button(bottom_frame, "Nastavení", open_settings)
    settings_open_button.pack(side="left", padx=10, pady=10)

    settings_hide_button = blue_button(bottom_frame, "Zavřít\nnastavení", hide_settings)
    settings_hide_button.pack_forget()

    exit_button = red_button(bottom_frame, "Zavřít", exit_app)
    exit_button.pack(side="right", padx=10, pady=10)

    editor_button = blue_button(bottom_frame, "Pokračovat", open_editor)
    editor_button.pack(side="right", padx=10, pady=10)
    

    # ---------- OBRAZOVKA3: Stall capacities settings

    stall_settings_frame = tk.Frame(root, bg="black")
    stall_settings_frame.pack_forget()

    capacities = loading.load_capacities_settings()

    tk.Label(stall_settings_frame, text="Kapacity", font=("Arial", 32, "bold"), bg="black", fg="white").grid(row=0, column=0, columnspan=7, pady=(20, 20))

    left_fields = [
        (1, "pizza_stall", "Pizza stánek:", 2),
        (2, "burger_stall", "Burger stánek:", 2),
        (3, "gyros_stall", "Gyros stánek:", 2),
        (4, "grill_stall", "Grill stánek:", 2),
        (5, "belgian_fries_stall", "Bel hranolky stánek:", 2),
        (6, "langos_stall", "Langoš stánek:", 2),
        (7, "sweet_stall", "Sladký stánek:", 2),
        (8, "nonalcohol_stall", "Nealko stánek:", 2),
        (9, "beer_stall", "Pivní stánek:", 2),
        (10, "redbull_stall", "Red Bull stánek:", 2),
        (11, "cocktail_stall", "Stánek s míchanými drinky:", 2),
        (12, "showers", "Sprchy:", 5),
        (13, "meadow_for_living", "Stany ve stanovém městečku:", 200),
        (14, "cigaret_stall", "Stánek s cigaretama:", 1),
        (15, "water_pipe_stall", "Stánek s vodníma dýmkama:", 20),
        (16, "entrance", "Počet turniketů u vstupu:", 4),
        (17, "cup_return", "Výkup kelímků:", 4),
    ]   

    left_entries = {}

    for row, key, label, default in left_fields:
        tk.Label(stall_settings_frame, text=label, **label_style).grid(
            row=row, column=1, pady=5, sticky="w", padx=20
        )

        entry = tk.Entry(stall_settings_frame, **entry_style2)
        entry.grid(row=row, column=2, padx=20)
        entry.insert(0, capacities.get(key, default))

        left_entries[key] = entry

    right_fields = [
        (1, "chill_stall", "Chill stánek", 20),
        (2, "ticket_booth", "Pokladna:", 2),
        (3, "toitoi", "Toitoiky:", 20),
        (4, "handwashing_station", "Umývárna:", 20),
        (5, "tables", "Stoly:", 20),
        (6, "standing", "Plocha na stání u pódia:", 1000),
        (7, "merch_stall", "Merch stan:", 3),
        (8, "signing_stall", "Fronta na autogramiády", 200),
        (9, "charging_stall", "Dobíjecí stan:", 2),
        (10, "charging_stall_mobile", "Dobíjecí stan - max počet telefonů:", 20),
        (11, "bungee_jumping", "Bungee-jumping:", 1),
        (12, "rollercoaster", "Horská dráha:", 24),
        (13, "bench", "Lavice (atrakce):", 20),
        (14, "hammer", "Kladivo (atrakce):", 32),
        (15, "carousel", "Řetizkáč:", 32),
        (16, "jumping_castle", "Skákací hrad:", 8),
    ]

    right_entries = {}

    for row, key, label, default in right_fields:
        tk.Label(stall_settings_frame, text=label, **label_style).grid(
            row=row, column=4, pady=5, sticky="w", padx=20
        )

        entry = tk.Entry(stall_settings_frame, **entry_style2)
        entry.grid(row=row, column=5, padx=20)
        entry.insert(0, capacities.get(key, default))

        right_entries[key] = entry

    bottom_settings_stalls_frame = tk.Frame(stall_settings_frame, bg="black") 
    bottom_settings_stalls_frame.grid(row=20, column=0, columnspan=6, pady=20)

    save_default_capacities = blue_button(bottom_settings_stalls_frame, "Uložit\nnastavení", save_capacities)
    save_default_capacities.pack(side="left", padx=10) 

    back_button = blue_button(bottom_settings_stalls_frame,"Zpět", go_back) 
    back_button.pack(side="left", padx=10)

    def get_capacities():
        capacities = {}

        for key, entry in left_entries.items():
            capacities[key] = int(entry.get())

        for key, entry in right_entries.items():
            capacities[key] = int(entry.get())

        capacities["atm"] = 1

        return capacities
    
    # ---------- OBRAZOVKA4: Prices settings

    prices_settings_frame = tk.Frame(root, bg="black")
    prices_settings_frame.pack_forget()

    prices = loading.load_fest_prices_settings()

    tk.Label(prices_settings_frame, text="Ceny", font=("Arial", 32, "bold"), bg="black", fg="white").grid(row=0, column=0, columnspan=7, pady=(10, 10))

    price_fields = [
        (2, "on_site_price", "Cena vstupenky na místě:", 1500),
        (3, "pre_sale_price", "Cena vstupenky v předprodeji:", 1300),
        (4, "camping_area_price", "Cena stanového městečka:", 200),
        (5, "plastic_cup_price", "Cena za kelímek na pití:", 50),
        (6, "charging_phone_price", "Cena za nabití telefonu:", 80),
        (7, "shower_price", "Cena sprch:", 50),
        (8, "cigars_price", "Cena za krabičku cigaret:", 140),
        (9, "water_pipe_price", "Cena za vodní dýmku:", 200),
        (10, "bungee_jumping", "Bungee jumping:", 200),
        (11, "rollercoaster", "Horská dráha:", 200),
        (12, "bench", "Lavice:", 200),
        (13, "hammer", "Kladivo:", 200),
        (14, "carousel", "Řetízkový kolotoč:", 200),
        (15, "jumping_castle", "Skákací hrad:", 200),
    ]

    price_entries = {}

    for row, key, label, default in price_fields:

        tk.Label(prices_settings_frame, text=label, **label_style).grid(
            row=row, column=0, padx=20, pady=10, sticky="w"
        )

        entry = tk.Entry(prices_settings_frame, **entry_style)
        entry.grid(row=row, column=1, pady=10)

        entry.insert(0, prices.get(key, default))

        price_entries[key] = entry

        tk.Label(prices_settings_frame, text="Kč  ", **label_style).grid(
            row=row, column=2, pady=10, sticky="w"
        )


    bottom_settings_prices_frame = tk.Frame(prices_settings_frame, bg="black") 
    bottom_settings_prices_frame.grid(row=16, column=0, columnspan=6, pady=20)

    save_default_prices = blue_button(bottom_settings_prices_frame, "Uložit\nnastavení", save_fest_prices)
    save_default_prices.pack(side="left", padx=10) 

    back_button = blue_button(bottom_settings_prices_frame, "Zpět", go_back) 
    back_button.pack(side="left", padx=10)

    def get_prices():
        prices = {}

        for key, entry in price_entries.items():
            prices[key] = int(entry.get())

        return prices
        
    # ---------- OBRAZOVKA5: Merch settings
    
    bands_merch, festival_merch = loading.load_merch_settings()

    merch_frame = tk.Frame(root, bg="black")
    merch_frame.pack_forget()

    tk.Label(merch_frame,text="Ceny v merch stánku", font=("Arial", 32, "bold"), bg="black", fg="white").grid(row=0, column=0, columnspan=6, pady=(40, 40))

    tk.Label(merch_frame, text="Merch kapel", **label_style).grid(row=1, column=0, columnspan=3, pady=10)
    tk.Label(merch_frame, text="Merch", **label_style).grid(row=2, column=0, padx=50)
    tk.Label(merch_frame, text="Cena", **label_style).grid(row=2, column=1)
    tk.Label(merch_frame, text="Kusů", **label_style).grid(row=2, column=2, padx=(10,0))

    bands_entries = {}
    row_index = 3

    for item in bands_merch:

        tk.Label(merch_frame, text=item, **label_style).grid(
            row=row_index, column=0, sticky="w", padx=50, pady=5
        )

        price_entry = tk.Entry(merch_frame, **entry_style2)
        price_entry.grid(row=row_index, column=1)

        quantity_entry = tk.Entry(merch_frame, **entry_style2)
        quantity_entry.grid(row=row_index, column=2, padx=(10,0))


        if "price" in bands_merch[item]:
            price_entry.insert(0, str(bands_merch[item]["price"]))
            quantity_entry.insert(0, str(bands_merch[item]["quantity"]))

        else:
            price_entry.insert(0, str(bands_merch[item].get("default_price", 0)))
            quantity_entry.insert(0, str(bands_merch[item].get("default_quantity", 0)))

        bands_entries[item] = {"price": price_entry, "quantity": quantity_entry}
        row_index += 1


    tk.Label(merch_frame, text="Festivalový merch", **label_style).grid(row=1, column=3, columnspan=3, pady=10)
    tk.Label(merch_frame, text="Merch", **label_style).grid(row=2, column=3)
    tk.Label(merch_frame, text="Cena", **label_style).grid(row=2, column=4)
    tk.Label(merch_frame, text="Kusů", **label_style).grid(row=2, column=5, padx=(10,0))

    festival_entries = {}
    row_index = 3

    for item in festival_merch:

        tk.Label(merch_frame, text=item, **label_style).grid(
            row=row_index, column=3, sticky="w", padx=50, pady=5
        )

        price_entry = tk.Entry(merch_frame, **entry_style2)
        price_entry.grid(row=row_index, column=4)

        quantity_entry = tk.Entry(merch_frame, **entry_style2)
        quantity_entry.grid(row=row_index, column=5, padx=(10,30))

  
        if "price" in festival_merch[item]:
            price_entry.insert(0, str(festival_merch[item]["price"]))
            quantity_entry.insert(0, str(festival_merch[item]["quantity"]))

        else:
            price_entry.insert(0, str(festival_merch[item].get("default_price", 0)))
            quantity_entry.insert(0, str(festival_merch[item].get("default_quantity", 0)))

        festival_entries[item] = {"price": price_entry, "quantity": quantity_entry}
        row_index += 1

        bottom_merch_frame = tk.Frame(merch_frame, bg="black")
        bottom_merch_frame.grid(row=50, column=0, columnspan=6, pady=40)

        save_default_merch_prices = blue_button(bottom_merch_frame, "Uložit\nnastavení", save_merch)
        save_default_merch_prices.pack(side="left", padx=10)

        back_button = blue_button(bottom_merch_frame, "Zpět", go_back)
        back_button.pack(side="left", padx=10)

    def get_merch(bands_entries):

        merch = {
            "bands_merch": {},
            "festival_merch": {}
        }

        for item, entries in bands_entries.items():

            try:
                price = int(entries["price"].get())
            except ValueError:
                price = 0

            try:
                quantity = int(entries["quantity"].get())
            except ValueError:
                quantity = 0

            merch["bands_merch"][item] = {
                "price": price,
                "quantity": quantity
            }

        for item, entries in festival_entries.items():

            try:
                price = int(entries["price"].get())
            except ValueError:
                price = 0

            try:
                quantity = int(entries["quantity"].get())
            except ValueError:
                quantity = 0

            merch["festival_merch"][item] = {
                "price": price,
                "quantity": quantity
            }

        return merch

    # ---------- OBRAZOVKA6: Times settings
    times_settings_frame = tk.Frame(root, bg="black")
    times_settings_frame.pack_forget()

    tk.Label(times_settings_frame, text="Časy", font=("Arial", 32, "bold"), bg="black", fg="white").grid(row=0, column=0, columnspan=7, pady=(40, 40))
    
    festival_times = loading.load_time_settings()

    time_fields = [
        (2, "band_time", "  Délka vystoupení kapely:", 60, " min."),
        (3, "headliner_time", "  Délka vystoupení headlinera:", 90, " min."),
        (4, "signing_time", "  Délka trvání autogramiád:", 30, " min."),
        (5, "first_show_starts", "  Čas prvního koncertu dne:", "12:00", ""),
        (6, "last_show_ends", "  Konec posledního koncertu dne:", "23:00", "")
    ]  


    for row, key, label, default, unit in time_fields:

        tk.Label(times_settings_frame, text=label, **label_style).grid(
            row=row, column=0, pady=10, sticky="w"
        )

        entry = tk.Entry(times_settings_frame, **entry_style2)
        entry.grid(row=row, column=1, pady=10)

        entry.insert(0, festival_times.get(key, default))

        festival_times[key] = entry

        if unit:
            tk.Label(times_settings_frame, text=f"{unit}  ", **label_style).grid(
                row=row, column=2, pady=10, sticky="w"
            )

    def get_times():
        result = {}

        for key, entry in festival_times.items():
            result[key] = entry.get()

        return result

    bottom_settings_times_frame = tk.Frame(times_settings_frame, bg="black") 
    bottom_settings_times_frame.grid(row=7, column=0, columnspan=6, pady=40) 

    save_default_times = blue_button(bottom_settings_times_frame, "Uložit\nnastavení", save_time_settings)
    save_default_times.pack(side="left", padx=10)

    back_button = blue_button(bottom_settings_times_frame, "Zpět", go_back) 
    back_button.pack(side="left", padx=10)


#-------------------------------------------------------------------------OBRAZOVKA7: Editor-----------------------------------------------------------

    editor_frame = tk.Frame(root, bg="black")

    background_label = ctk.CTkLabel(editor_frame, image=bg_image, text="")
    background_label.place(relx=0.5, rely=0.5, anchor="center")

    title = ctk.CTkLabel(editor_frame, text="Editor festivalového areálu",font=("Arial", 40, "bold"),text_color="#ffffff")
    title.pack(pady=20)


    content_frame = tk.Frame(editor_frame, bg="black")
    content_frame.pack(fill="both", padx=50, pady=10)

    frame_left = tk.Frame(content_frame, width=200, height=860, bg="white", bd=2, relief="ridge")
    frame_left.pack(side="left", fill="y", padx=0, pady=0)
    frame_left.pack_propagate(False)

    tk.Label(frame_left, text="Zóny", font=("Arial", 15, "bold"), bg="white", fg="black").pack(pady=5)

    frame_right = tk.Frame(content_frame, width=200, height=860, bg="white", bd=2, relief="ridge")
    frame_right.pack(side="left", fill="y", padx=0, pady=0)
    frame_right.pack_propagate(False)

    tk.Label(frame_right, text="Objekty", font=("Arial", 15, "bold"), bg="white", fg="black").pack(pady=5)

    canvas = tk.Canvas(content_frame, bg="lightgray", width=1200, height=860, highlightthickness=0)

    canvas.pack(side="right", fill="both", expand=True)
    canvas.pack_propagate(False)


    #EDITOR BUTTONS
    editor_buttons_frame = tk.Frame(editor_frame, bg="black")
    editor_buttons_frame.pack(pady=20)

    back_button = blue_button(editor_buttons_frame, "Zpět", go_back)
    back_button.pack(side="left", padx=10, pady=10)

    save_button = blue_button(editor_buttons_frame, "Uložit", save)
    save_button.pack(side="left", padx=10, pady=10)

    save_button = blue_button(editor_buttons_frame, "Načíst", load)
    save_button.pack(side="left", padx=10, pady=10)

    delete_button = red_button(editor_buttons_frame, "Smazat", delete)
    delete_button.pack(side="left", padx=10, pady=10)

    start_button = green_button(editor_buttons_frame, "Start", start)
    start_button.pack(side="left", padx=10, pady=10)


    objects_for_zone = {
        "Spawn bod": [],
        "Vstupní zóna": ["Pokladna", "Pizza stánek", "Burger stánek", "Gyros stánek", "Grill stánek", "Bel hranolky stánek", "Langoš stánek", "Sladký stánek", "Nealko stánek", "Pivní stánek", "Red Bull stánek","Stánek s míchanými drinky", "Toitoiky", "Umývárna", "Stoly", "Bankomat", "Výkup kelímků"],
        "Festivalový areál": ["Vstup", "Podium", "Pizza stánek", "Burger stánek", "Gyros stánek", "Grill stánek", "Bel hranolky stánek", "Langoš stánek", "Sladký stánek", "Nealko stánek", "Pivní stánek", "Red Bull stánek","Stánek s míchanými drinky", "Toitoiky","Umývárna", "Stoly", "Bankomat", "Merch stan", "Stan na autogramiády", "Dobíjecí stan", "Výkup kelímků"],
        "Stanové městečko": ["Nealko stánek", "Pivní stánek", "Red Bull stánek","Stánek s míchanými drinky", "Toitoiky", "Sprchy", "Umývárna", "Dobíjecí stan", "Louka na stanování"],
        "Chill zóna": ["Stánek s vodníma dýmkama", "Cigaretový stánek", "Chill stánek", "Nealko stánek","Stánek s míchanými drinky", "Pivní stánek", "Red Bull stánek", "Toitoiky", "Umývárna", "Dobíjecí stan"],
        "Zábavní zóna": ["Bungee-jumping", "Horská dráha", "Lavice", "Kladivo", "Řetizkáč", "Skákací hrad", "Nealko stánek", "Pivní stánek","Stánek s míchanými drinky", "Red Bull stánek", "Bankomat"]
    }

    # Funkce pro výběr objektu
    def select_object(obj_name):
        global current_object, object_buttons

        if current_object == obj_name:
            current_object = None

            for btn in object_buttons.values():
                btn.configure(fg_color="white", text_color="black")

            print(f"Objekt {obj_name} odvybrán")
            return

        current_object = obj_name
        print(f"Vybrán objekt: {current_object}")

        for name, btn in object_buttons.items():
            btn.configure(fg_color="white", text_color="black")

        if obj_name in object_buttons:
            object_buttons[obj_name].configure(fg_color="yellow", text_color="black")
                                    
    # Funkce pro výběr zóny (typ)
    def select_zone(zone_name):

        global current_zone, object_buttons, current_object
        current_zone = zone_name
        print(f"Vybrána zóna: {current_zone}")

        current_object = None
        for name, btn in zone_buttons.items():
            btn.configure(fg_color="white", text_color="black")

        zone_buttons[zone_name].configure(fg_color="yellow", text_color="black")

        # Vyčistí pravý panel a naplní objekty pro tento typ zóny
        for widget in frame_right.winfo_children():
            widget.destroy()

        tk.Label(frame_right, text="Objekty", font=("Arial", 15, "bold"), bg="white", fg="black").pack(pady=5)

        object_buttons.clear()
        for obj in objects_for_zone.get(zone_name, []):

            img, text = choose_emoji(obj)
        
            btn = object_button(frame_right, text, obj, img)
            btn.pack(pady=3)
            object_buttons[obj] = btn

    # Vytvoření tlačítek pro zóny
    for zone_name in zones_data.keys():
        btn = zone_button(frame_left, zone_name)
        btn.pack(pady=5)
        zone_buttons[zone_name] = btn

    tk.Label(frame_left, text="Režimy", font=("Arial", 20, "bold"), bg="white", fg="black").pack(pady=(30,10))

    modes_frame = tk.Frame(frame_left, bg="white")
    modes_frame.pack(pady=5)

    # Funkce pro výběr režimu
    current_mode = None

    def select_mode(mode_name):
        global current_mode
        current_mode = mode_name

        print(f"Režim vybrán: {current_mode}")

        # Reset barvy všech tlačítek
        for btn in mode_buttons.values():
            btn.configure(fg_color="white", text_color="black")

        # Zvýraznit vybraný
        mode_buttons[mode_name].configure(fg_color="yellow", text_color="black")

    # Tlačítka pro režimy
    mode_buttons = {}
    mode_icons = {"add": "➕", "edit": "➤", "connect": "🔗"}
    mode_labels_text = {"add": "Přidat", "edit": "Editovat", "connect": "Spojit"}

    for i, (mode_name, symbol) in enumerate(mode_icons.items()):

        # rámec pro label + tlačítko
        btn_frame = tk.Frame(modes_frame)
        btn_frame.pack(side="left", padx=5)

        # label nad tlačítkem
        lbl = tk.Label(btn_frame, text=mode_labels_text.get(mode_name, ""), font=("Arial", 10))
        lbl.pack()

        # tlačítko
        btn = mode_button(btn_frame, symbol)
        btn.pack()
        mode_buttons[mode_name] = btn
    
    select_mode("add")

    # Pomocná funkce, která najde instanci zóny, do které patří bod x,y
    def find_zone_instance_for_point(zone_type, x, y):
        inst = zones_data.get(zone_type)
        if not inst:
            return None

        # kontrola hlavní oblasti zóny
        if inst["left"] <= x <= inst["right"] and inst["top"] <= y <= inst["bottom"]:
            return inst

        # kontrola objektů v zóně
        for obj in inst.get("objects", []):
            coords_list = []

            # hlavní tvar objektu
            main_id = obj["canvas_ids"][1]
            coords_list.append(canvas.coords(main_id))

            # extra objekty (např. stání u podia)
            for extra in obj.get("extra", []):
                extra_id = extra["canvas_ids"][1]
                coords_list.append(canvas.coords(extra_id))

            # projdeme všechny bounding boxy
            for coords in coords_list:
                left, top, right, bottom = coords
                if left <= x <= right and top <= y <= bottom:
                    return inst

        return None

#-------------------------------------------------------------------------------EDITOR - SIMULATION MODE---------------------------------------------------------------------------------------------------

    left_simulation_container = tk.Frame(content_frame, bg="black")
    left_simulation_container.pack_forget()

    frame_up_simulation = tk.Frame(left_simulation_container, width=400, height=430, bg="white", bd=2, relief="ridge")
    frame_up_simulation.pack_propagate(False)
    frame_up_simulation.pack(fill="x")

    tk.Label(frame_up_simulation, text="Detaily o stánku: ", font=("Arial", 15, "bold"), bg="white", fg="black").pack(pady=5)
    
    stall_log_box = ctk.CTkTextbox(frame_up_simulation, width=380, height=370, text_color="black", fg_color="#C0C0C0", font=("Arial", 20))
    stall_log_box.pack()
    stall_log_box.configure(state="disabled")

    frame_down_simulation = tk.Frame(left_simulation_container, width=400, height=430, bg="white", bd=2, relief="ridge")
    frame_down_simulation.pack_propagate(False)
    frame_down_simulation.pack(fill="x")

    tk.Label(frame_down_simulation, text="Průběh festivalu:", font=("Arial", 15, "bold"), bg="white", fg="black").pack(pady=5)
    
    messages_log_box = ctk.CTkTextbox(frame_down_simulation, width=380, height=370, text_color="black", fg_color="#C0C0C0", font=("Arial", 14))
    messages_log_box.pack()
    messages_log_box.configure(state="disabled")

    #SIMULATION BUTTONS

    simulation_buttons_frame = tk.Frame(editor_frame, bg="black")
    simulation_buttons_frame.pack_forget()


    # ČÁST PLYNULÉ SIMULACE

    smooth_simulation_buttons_frame = tk.Frame(simulation_buttons_frame, bg="black")
    smooth_simulation_buttons_frame.pack(side="left", padx=30)

    smooth_simulation_label = ctk.CTkLabel(smooth_simulation_buttons_frame, text="Automatická simulace", font=("Arial", 20, "bold"), text_color="white", width=50)
    smooth_simulation_label.pack(side="top", pady=8)

    smooth_simulation_start_button = green_button_small(smooth_simulation_buttons_frame, "▶", start_smooth_simulation)
    smooth_simulation_start_button.pack(anchor="center", pady=10)

    smooth_simulation_stop_button = blue_button_small(smooth_simulation_buttons_frame, "⏸", stop_smooth_simulation)
    smooth_simulation_stop_button.pack_forget()

    # COUNTER ČÁST

    def increase():
        nonlocal value
        value += 1
        jump_label.configure(text=str(value))

    def decrease():
        nonlocal value

        if value > 1:
            value -= 1
            jump_label.configure(text=str(value))

    simulation_counter_frame = tk.Frame(simulation_buttons_frame, bg="black")
    simulation_counter_frame.pack(side="left")

    jump_label_text = ctk.CTkLabel(simulation_counter_frame, text="Posunout simulaci o čas", font=("Arial", 20, "bold"), text_color="white", width=50)
    jump_label_text.pack(side="top", pady=8)

    minus_button = blue_button_small(simulation_counter_frame, "-", decrease)
    minus_button.pack(side="left", pady=10)

    jump_label = ctk.CTkLabel(simulation_counter_frame, text=str(value), font=("Arial", 20, "bold"), text_color="white", width=50)
    jump_label.pack(side="left")

    plus_button = blue_button_small(simulation_counter_frame, "+", increase)
    plus_button.pack(side="left", pady=10)

    move_forward_by_time_button = green_button_small(simulation_counter_frame, "▶", move_forward_by_time)
    move_forward_by_time_button.pack(side="left", padx=10, pady=10)

    #stop_simulation_button = red_button_small(stop_simulation_frame, "Ukončit", stop_simulation)
    #stop_simulation_button.pack(side="left", padx=30)

    save_simulation_state_button = blue_button(simulation_buttons_frame, "Uložit stav\nsimulace", save_actual_state, 20)
    save_simulation_state_button.pack(side="left", padx=[50,0])

    stop_simulation_button = red_button(simulation_buttons_frame, "Ukončit", stop_simulation)
    stop_simulation_button.pack(side="left", padx=30)


    def create_zone_stats_labels():

        for zone in zones_data.values():
            text = "Návštěvníků v zóně: 0"
            x_center = zone["left"]
            y_label = zone["top"] - 8

            label_id = canvas.create_text(x_center, y_label, text=text, fill="black", anchor="w", font=("Arial", 8, "bold"))
            zone["num_visitors_label_id"] = label_id

    def delete_zone_stats_labels():

        for zone in zones_data.values():
            if "num_visitors_label_id" in zone:
                canvas.delete(zone["num_visitors_label_id"])
                del zone["num_visitors_label_id"]

#--------------------------------------------------------------------------------KÓDY EDITORU-------------------------------------------------------------
    
    def view_changes(controller):

        simulation_state = controller.get_simulation_state()
        stalls = controller.get_festival().get_stalls()
        location_map = {
            "Vstupní zóna": "ENTRANCE_ZONE",
            "Festivalový areál": "FESTIVAL_AREA",
            "Stanové městečko": "TENT_AREA",
            "Chill zóna": "CHILL_ZONE",
            "Zábavní zóna": "FUN_ZONE",
            "Spawn zóna": "SPAWN_ZONE"
        }

        # aktualizace počtu lidí v zónách
        for zone, zone_data in zones_data.items():
            count = simulation_state["zones"][location_map[zone]]["num_people_in_zone"]
            update_zone_visitor_count(zone_data, count)

        # aktualizace stánků
        for zone_name, zone_stalls in stalls.items():
            for stall in zone_stalls:

                stall_name = stall.get_name()
                stall_id = stall.get_id()

                # seznam stánků stejného typu
                stall_list = simulation_state["zones"][zone_name]["stalls"][stall_name]

                # najdeme správný stánek podle ID
                stall_stats = None
                for s in stall_list:
                    if s["id"] == stall_id:
                        stall_stats = s
                        break

                if stall_stats is None:
                    print(f"ERROR: Nenalezen stánek ID {stall_id} v zone {zone_name}")
                    continue

                canvas_ids = stall.get_canvas_ids()
                item = canvas_ids[1]

                # barvení podle typu stánku
                if stall_name == "standing_at_stage":
                    capacity = stall.get_capacity()

                    if stall_stats["num_people_served"] < capacity / 3:
                        canvas.itemconfig(item, fill="")

                    elif stall_stats["num_people_served"] < capacity / 2:
                        canvas.itemconfig(item, fill="#CDDC39")

                    elif stall_stats["num_people_served"] <= capacity / 1.2:
                        canvas.itemconfig(item, fill="#FF9800")

                    else:
                        canvas.itemconfig(item, fill="red")

                elif stall_name != "stage":
                    if stall_stats["num_people_in_queue"] < 1:
                        canvas.itemconfig(item, fill="")

                    elif stall_stats["num_people_in_queue"] < 5:
                        canvas.itemconfig(item, fill="#CDDC39")

                    elif stall_stats["num_people_in_queue"] <= 10:
                        canvas.itemconfig(item, fill="#FF9800")

                    else:
                        canvas.itemconfig(item, fill="red")


    def update_zone_visitor_count(zone, count):
        label_id = zone.get("num_visitors_label_id")
        canvas.itemconfig(label_id, text=f"Počet návštěvníků v zóně: {count}")

    # Funkce pro vkládání objektů
    def place_object(event):
        global current_object, current_zone, zones_data, current_mode

        if current_mode != "add":
            print("Zony a objekty lze přidávat pouze v režimu +")
            return

        if current_zone is None or current_object is None:
            print("chyba: není vybrána zóna nebo objekt")
            return

        x, y = event.x, event.y

        instance = find_zone_instance_for_point(current_zone, x, y)

        # speciální logika pro vstup
        if current_object == "Vstup":
            fest_zone = zones_data.get("Festivalový areál")

            if not fest_zone:
                print("Chyba: festivalový areál neexistuje.")
                return

            if not is_on_edge(fest_zone, x, y):
                print("Vstup musí být umístěn na hranu festivalového areálu.")
                return

            instance = fest_zone

        elif instance is None:
            print("chyba: objekt musí být uvnitř existující zóny")
            return

        # vytvoření objektu
        obj_data = create_object(instance, current_object, x, y)
        instance.setdefault("objects", []).append(obj_data)

    def create_object(instance, current_object, x, y, x1=None, y1=None, x2=None, y2=None, saved_object_id=None):
        global object_id

        extra = []
        img, text = choose_emoji(current_object)

        r = 13
        if x1 is not None and y1 is not None and x2 is not None and y2 is not None:
            coords_oval = (x1, y1, x2, y2)
            coords_toiky = (x1, y1, x2, y2)
            coords_camping = (x1, y1, x2, y2)
            coords_stage = (x1, y1, x2, y2)
            coords_stage_standing = (x1, y1, x2, y2)

        else:
            w, h = 100, 50
            coords_toiky = (x - w//2, y - h//2, x + w//2, y + h//2)

            w, h = 200, 100
            coords_camping = (x - w//2, y - h//2, x + w//2, y + h//2)

            w, h = 160, 50
            coords_stage = (x - w//2, y - h//2, x + w//2, y + h//2)

            w, h = 220, 145
            offset = 100
            coords_stage_standing = (x - w//2, y - h//2 + offset, x + w//2, y + h//2 + offset)


        if saved_object_id:
            object_id_backup = object_id
            object_id = saved_object_id

        else:
            object_id += 1

        if current_object == "Toitoiky":
            x1, y1, x2, y2 = coords_toiky
            text_id = canvas.create_text(x, y - 40, text=current_object, fill="black", font=("Arial", 8, "bold"), anchor="center")
            shape_id = canvas.create_rectangle(*coords_toiky, fill="")
            img_id = canvas.create_image((x1 + x2) / 2, (y1 + y2) / 2, image=img)


        elif current_object == "Louka na stanování":
            x1, y1, x2, y2 = coords_camping
            text_id = canvas.create_text(x, y - 65, text=current_object, fill="black", font=("Arial", 8, "bold"), anchor="center")
            shape_id = canvas.create_rectangle(*coords_camping, fill="")
            img_id = canvas.create_image((x1 + x2) / 2, (y1 + y2) / 2, image=img)

        elif current_object == "Podium":
            x1s, y1s, x2s, y2s = coords_stage
            x1p, y1p, x2p, y2p = coords_stage_standing

            stand_id = canvas.create_rectangle(*coords_stage_standing, fill="", outline="black")

            stand_text_id = canvas.create_text((x1p + x2p) / 2, (y1p + y2p) / 2, text="Stání u podia", fill="black", font=("Arial", 8, "bold"), anchor="center")

            stage_id = canvas.create_rectangle(*coords_stage, fill="black")

            img_id = canvas.create_image((x1s + x2s) / 2, (y1s + y2s) / 2, image=img)

            text_id = canvas.create_text((x1s + x2s) / 2, y1s - 20, text=current_object, fill="black", font=("Arial", 8, "bold"), anchor="center")
            
            id_standing = object_id + 1
            extra.append({"id": id_standing, "object": "Stání u podia", "canvas_ids": [stand_text_id, stand_id]})
           
            
            shape_id = stage_id
            x1, y1, x2, y2 = coords_stage

        
        else:

            size = 16
            x1 = x - size
            y1 = y - size
            x2 = x + size
            y2 = y + size

            text_id = canvas.create_text(x, y - 20, text=current_object, fill="black", font=("Arial", 8, "bold"), anchor="center")
            shape_id = canvas.create_oval(x1, y1, x2, y2, outline="", fill="")
            img_id = canvas.create_image(x, y, image=img)

        new_object = { "object": current_object, "id": object_id, "x": x, "y": y, "x1": x1, "y1": y1, "x2": x2, "y2": y2, "canvas_ids": [text_id, shape_id, img_id], "extra": extra}   

        if saved_object_id:
            object_id = object_id_backup

        if current_object == "Podium":
            object_id += 1

        return new_object

    def on_click(event):
        """Začátek kreslení zóny (pokud není vybraný objekt)."""
        global drawing, last_x, last_y, zone_rect, zone_label, current_object, current_zone, current_mode, selected_zone_instance, selected_object, is_dragging_object, is_dragging_zone, connect_start_zone, selected_line


        print("\n[CLICK] at", event.x, event.y, "mode:", current_mode)

        if current_mode == "add":
            handle_add_click(event)

        elif current_mode == "edit":
            handle_edit_click(event)

        elif current_mode == "connect": 
            handle_connect_click(event)

        elif current_mode == "inspect":
            handle_inspect_click(event, controller)
    
    def handle_add_click(event):
        global drawing, last_x, last_y, zone_rect, zone_label, current_object, current_zone, selected_zone_instance, selected_object, selected_line

        # 1) musí být vybraná zóna
        if current_zone is None:
            print("Není vybrána žádná zóna.")
            return

        # 2) pokud je vybraný objekt → umisťujeme objekt
        if current_object is not None:
            place_object(event)
            return

        # 3) kontrola, zda zóna už existuje (jen jedna instance)
        zone_info = zones_data[current_zone]
        if zone_info:
            print(f"Zóna '{current_zone}' může být pouze jedna — nelze přidat další.")
            return

        # 4) začínáme kreslit novou zónu
        drawing = True
        last_x, last_y = event.x, event.y

        # smazat staré náhledy
        if zone_rect is not None:
            canvas.delete(zone_rect)
            zone_rect = None

        if zone_label is not None:
            canvas.delete(zone_label)
            zone_label = None

    def handle_edit_click(event):
        global selected_object, selected_zone_instance, selected_line, is_dragging_object, is_dragging_zone, last_x, last_y

        # 1) čára
        line = find_clicked_line(event)
        if line:
            if selected_line:
                canvas.itemconfig(selected_line["id"], width=2)
            selected_line = line
            canvas.itemconfig(line["id"], width=4)
            return

        # 2) objekt
        obj = find_clicked_object(event)
        if obj:
            if selected_object and selected_object != obj:
                unhighlight_object(selected_object)

            selected_object = obj
            highlight_object(obj)

            if selected_object and selected_zone_instance:
                unhighlight_zone(selected_zone_instance)

            is_dragging_object = True
            last_x, last_y = event.x, event.y
            return

        # 3) zóna
        zone = find_clicked_zone(event)
        if zone:
            # stejné jako teď, jen v samostatné funkci
            handle_zone_selection(zone, event)
            return

        # 4) nic → odznačit vše
        clear_selection()

    def clear_selection():
        global selected_object, selected_zone_instance, selected_line
        
        # odznačit objekt
        if selected_object:
            unhighlight_object(selected_object)
            selected_object = None

        # odznačit zónu
        if selected_zone_instance:
            unhighlight_zone(selected_zone_instance)
            selected_zone_instance = None

        # odznačit čáru
        if selected_line:
            canvas.itemconfig(selected_line["id"], width=2)
            selected_line = None

        print("Výběr zrušen")
    
    def handle_zone_selection(zone, event):
        global selected_zone_instance, selected_object, selected_line
        global is_dragging_zone, last_x, last_y

        # odznačit objekt
        if selected_object:
            canvas.itemconfig(selected_object["canvas_ids"][1], outline="", width=1)
            selected_object = None

        # odznačit čáru
        if selected_line:
            canvas.itemconfig(selected_line["id"], width=2)
            selected_line = None

        # pokud klikám na jinou zónu, odznačím starou
        if selected_zone_instance and selected_zone_instance != zone:
            canvas.itemconfig(selected_zone_instance["rect_id"], outline="blue", width=3)

        # označit novou zónu
        if selected_zone_instance != zone:
            selected_zone_instance = zone
            canvas.itemconfig(zone["rect_id"], outline="red", width=4)
            print(f"Označená zóna: {zone["type"]}")

        # zjištění resize směru
        resize_info = get_resize_direction(zone, event.x, event.y)
        print("Resize info:", resize_info)

        if resize_info:

            # speciální pravidlo pro Festivalový areál
            if zone["type"] == "Festivalový areál":
                for obj in zone.get("objects", []):
                    if obj.get("object") == "Vstup":
                        return

            zone["resize_info"] = resize_info
            is_dragging_zone = True
            last_x, last_y = event.x, event.y

    def find_clicked_object(event):
        for zone_type, inst in zones_data.items():
            if not inst:
                continue

            for obj in inst.get("objects", []):
            
                geom_id = obj["canvas_ids"][1]
                coords = canvas.coords(geom_id)

                x1, y1, x2, y2 = coords
                if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                    return obj

                if obj["object"] == "Podium":
                    obj = obj["extra"]

                    geom_id = obj[0]["canvas_ids"][1]
                    coords = canvas.coords(geom_id)

                    x1, y1, x2, y2 = coords
                    if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                        return obj

        return None
    
    def find_clicked_line(event):
        for zone_type, inst in zones_data.items():
            if not inst:
                continue

            for line in inst.get("lines", []):
                coords = canvas.coords(line["id"])
                if not coords:
                    continue

                x1, y1, x2, y2 = coords
                if is_near_line(event.x, event.y, x1, y1, x2, y2, tol=5):
                    return line

        return None
    
    def find_clicked_zone(event):
        for zone_type, inst in zones_data.items():
            if not inst:
                continue

            if inst["left"] <= event.x <= inst["right"] and inst["top"] <= event.y <= inst["bottom"]:
                return inst

        return None
    
    def highlight_object(obj):
        if isinstance(obj, list):
            obj = obj[0]

        canvas.itemconfig(obj["canvas_ids"][1], outline="red", width=3)

    def unhighlight_object(obj):
        if isinstance(obj, list):
            obj = obj[0]

        border_objects = ["Louka na stanování", "Toitoiky", "Stání u podia"]

        # odznačit objekt
        if obj["object"] not in border_objects:
            canvas.itemconfig(obj["canvas_ids"][1], outline="", width=1)
        else:
            canvas.itemconfig(obj["canvas_ids"][1], outline="black", width=1)

    def highlight_zone(zone):
        canvas.itemconfig(zone["react_id"], outline="red", width=3)

    def unhighlight_zone(zone):
        canvas.itemconfig(zone["rect_id"], outline="blue", width=3)

    def handle_connect_click(event):
        """Obslouží connect mód."""
        global connect_start_zone

        clicked_obj = find_clicked_object(event)

        # zjistíme, jestli jsme klikli na zónu
        clicked_zone = None
        for zone_type, inst in zones_data.items():
            if not inst:
                continue

            if inst["left"] <= event.x <= inst["right"] and inst["top"] <= event.y <= inst["bottom"]:
                clicked_zone = inst
                break

        # nic nekliknuto → reset
        if not clicked_zone and not clicked_obj:
            if connect_start_zone and "rect_id" in connect_start_zone:
                canvas.itemconfig(connect_start_zone["rect_id"], outline="blue", width=3)
            connect_start_zone = None
            return

        # pokud ještě není start
        if connect_start_zone is None:
            if clicked_obj and clicked_obj.get("object") == "Vstup":
                if "id" not in clicked_obj:
                    clicked_obj["id"] = canvas.create_oval(0,0,0,0)
                connect_start_zone = clicked_obj
                print("CONNECT START = vstup", clicked_obj.get("id"))

            elif clicked_zone:
                connect_start_zone = clicked_zone
                canvas.itemconfig(clicked_zone["rect_id"], outline="green", width=4)
                print("CONNECT START = zone", clicked_zone["type"])

            return

        # máme první klik → teď spojujeme
        first = connect_start_zone
        second_zone = clicked_zone
        second_obj = clicked_obj

        # -------- start = vstup --------
        if isinstance(first, dict) and first.get("object") == "Vstup":
            if second_zone:  # klik na zónu
                connect_entry_to_zone(first, second_zone)
            else:
                print("Špatný klik, vstup → něco nekliknutého")

        # -------- start = zóna --------
        elif isinstance(first, dict) and "type" in first:
            if second_obj and second_obj.get("object") == "Vstup":  # klik na vstup
                connect_zone_to_entry(first, second_obj)
            elif second_zone:  # klik na jinou zónu
                connect_zone_to_zone(first, second_zone)
            else:
                print("Špatný klik, zóna → něco nekliknutého")

        # nakonec reset + odznačení start zóny
        if isinstance(first, dict) and "rect_id" in first:
            canvas.itemconfig(first["rect_id"], outline="blue", width=3)

        connect_start_zone = None
        print("CONNECT DONE")


    def connect_entry_to_zone(vstup_obj, target_zone):
        """Vstup → zóna."""
        vstup_zone = None

        # najdeme zónu, ve které je tento vstup umístěný
        for zt, inst in zones_data.items():
            if not inst:
                continue

            if vstup_obj in inst.get("objects", []):
                vstup_zone = inst
                break

        if not target_zone or not vstup_zone:
            print("Špatný klik, vstup → zóna selhalo")
            return

        x1, y1 = vstup_obj["x"], vstup_obj["y"]
        x2, y2 = center_of_closest_edge(target_zone, x1, y1)

        line_id = canvas.create_line(x1, y1, x2, y2, fill="black", width=2)
        vstup_obj["locked"] = True

        # uložíme do lines
        vstup_zone.setdefault("lines", []).append({
            "id": line_id,
            "other_zone": {
                "type": target_zone["type"],
                "entry": {"id": vstup_obj["id"], "x": x1, "y": y1}
            }
        })

        target_zone.setdefault("lines", []).append({
            "id": line_id,
            "other_zone": {
                "type": vstup_zone["type"],
                "entry": {"id": vstup_obj["id"], "x": x1, "y": y1}
            }
        })


    def connect_zone_to_entry(start_zone, vstup_obj):
        """Zóna → vstup."""
        vstup_zone = None

        # najdeme zónu, ve které je tento vstup umístěný
        for zt, inst in zones_data.items():
            if not inst:
                continue

            if vstup_obj in inst.get("objects", []):
                vstup_zone = inst
                break

        if not vstup_zone:
            print("Špatný klik, zóna → vstup selhalo")
            return

        x2, y2 = vstup_obj["x"], vstup_obj["y"]
        x1, y1 = center_of_closest_edge(start_zone, x2, y2)

        line_id = canvas.create_line(x1, y1, x2, y2, fill="black", width=2)
        vstup_obj["locked"] = True

        start_zone.setdefault("lines", []).append({
            "id": line_id,
            "other_zone": {
                "type": vstup_zone["type"],
                "entry": {"id": vstup_obj["id"], "x": x2, "y": y2}
            }
        })

        vstup_zone.setdefault("lines", []).append({
            "id": line_id,
            "other_zone": {
                "type": start_zone["type"],
                "entry": {"id": vstup_obj["id"], "x": x2, "y": y2}
            }
        })


    def connect_zone_to_zone(z1, z2):
        """Zóna → zóna."""
        # pokud už existuje spojení, nic nedělej
        for line in z1.get("lines", []):
            if line["other_zone"]["type"] == z2["type"]:
                return

        x1, y1 = closest_point_on_zone(z1, z2)
        x2, y2 = closest_point_on_zone(z2, z1)

        line_id = canvas.create_line(x1, y1, x2, y2, fill="black", width=2)

        z1.setdefault("lines", []).append({
            "id": line_id,
            "other_zone": {"type": z2["type"]}
        })

        z2.setdefault("lines", []).append({
            "id": line_id,
            "other_zone": {"type": z1["type"]}
        })

        canvas.itemconfig(z1["rect_id"], outline="blue", width=3)



    def center_of_closest_edge(zone, x, y):
        left, top, right, bottom = zone["left"], zone["top"], zone["right"], zone["bottom"]

        centers = [
            ((left + right) / 2, top),          # horní hrana
            ((left + right) / 2, bottom),       # dolní hrana
            (left, (top + bottom) / 2),         # levá hrana
            (right, (top + bottom) / 2),        # pravá hrana
        ]

        best = min(centers, key=lambda p: (p[0] - x)**2 + (p[1] - y)**2)
        return best

    def is_on_edge(zone, x, y, tolerance=5):
        left, top, right, bottom = zone["left"], zone["top"], zone["right"], zone["bottom"]

        if abs(y - top) <= tolerance and left <= x <= right:
            return True

        if abs(y - bottom) <= tolerance and left <= x <= right:
            return True

        if abs(x - left) <= tolerance and top <= y <= bottom:
            return True
        
        if abs(x - right) <= tolerance and top <= y <= bottom:
            return True

        return False
    
    def is_near_line(x, y, x1, y1, x2, y2, tol=5):
        """Vrátí True, pokud je bod (x, y) blízko úsečky (x1, y1, x2, y2) do tolerance tol."""
        # pokud je čára vertikální/ horizontální zvlášť
        if x1 == x2 and y1 == y2:
            return abs(x - x1) <= tol and abs(y - y1) <= tol
        
        # vzdálenost bodu od čáry (úsečky) podle vektorové projekce
        # parametr t pro projekci bodu na čáru
        dx, dy = x2 - x1, y2 - y1
        t = ((x - x1) * dx + (y - y1) * dy) / (dx*dx + dy*dy)
        t = max(0, min(1, t))  # omezení na úsečku
        nearest_x = x1 + t * dx
        nearest_y = y1 + t * dy
        dist = ((x - nearest_x)**2 + (y - nearest_y)**2)**0.5
        return dist <= tol
    

    def handle_inspect_click(event, controller):
        global current_object

        obj = find_clicked_object(event)
        zone = find_clicked_zone(event)
        zone = zone["type"].lower()
        zone = source.Locations(zone).name

        if not obj:
            return
        
        if isinstance(obj, list):
            obj = obj[0]

        if current_object != obj:       
            highlight_object(obj)

            if current_object:
                unhighlight_object(current_object)

            current_object = obj

        sim_state = controller.get_simulation_state()
        stalls_data = sim_state["zones"][zone]["stalls"]

        data = None

        for stall_name, stall_list in stalls_data.items():

            for stall_data in stall_list:
                if stall_data["id"] == obj["id"]:
                    data = stall_data
                    break

            if data:
                break
        
        if not data:
            add_log("ERROR: Nenalezen objekt na který se kliklo v inspect režimu!")
            return
        
        cz_name = data["cz_name"][0].upper() + data["cz_name"][1:]

        stall_log_box.configure(state="normal")
        stall_log_box.delete("1.0", "end")
        stall_log_box.insert("end", f"ID stánku: {data['id']}\n")
        stall_log_box.insert("end", f"Název stánku: {cz_name}\n")

        if stall_name == "stage":

            band = controller.get_festival().get_playing_band()
            if band:
                band = band["band_name"]
                stall_log_box.insert("end", f"Právě hraje kapela: {band}\n")
            else:
                stall_log_box.insert("end", f"V tuto chvíli žádná kapela nehraje\n")

            stall_log_box.configure(state="disabled")
            return 

        elif stall_name == "standing_at_stage":
            stall_log_box.insert("end", f"Počet návštěvníků na koncertě: {data["num_people_served"]}\n")
            stall_log_box.insert("end", f"Počet návštěvníků v prvních řádách: {data["num_people_in_first_lines"]} \n")
            stall_log_box.insert("end", f"Počet návštěvníků uprostřed plochy: {data["num_people_in_the_middle"]} \n")
            stall_log_box.insert("end", f"Počet návštěvníků vzadu: {data["num_people_in_back"]} \n")
            stall_log_box.insert("end", f"Kapacita stánku: {data['capacity']}\n")
            stall_log_box.configure(state="disabled")
            return 
        
        elif stall_name == "signing_stall":
            band = controller.get_festival().get_signing_band()

            if band:
                band = band["band_name"]
                stall_log_box.insert("end", f"Právě má autogramiádu kapela: {band}\n")

            else:
                stall_log_box.insert("end", f"V tuto chvíli žádná kapela nemá autogramiádu\n")

        elif stall_name == "meadow_for_living":
            stall_log_box.insert("end", f"Počet stanů: {data["num_tents"]}\n")
            stall_log_box.insert("end", f"Počet návštěvníků ve stanu: {data["num_people_in_tents"]}\n")
        
        stall_log_box.insert("end", f"Návštěvníků obsluhováno: {data["num_people_served"]}\n")
        stall_log_box.insert("end", f"Návštěvníků ve frontě: {data["num_people_in_queue"]}\n")
        stall_log_box.insert("end", f"Kapacita stánku: {data["capacity"]}\n")

        
        stall_log_box.configure(state="disabled")

    def on_drag(event):
        """Aktualizace při tažení myší – kreslení zóny nebo přesun objektu."""
        global drawing, last_x, last_y, zone_rect, zone_label, current_object, current_zone, selected_object, is_dragging_object, is_dragging_zone, current_mode
        
        if current_mode == "inspect":
            return
        
        print("[DRAG EVENT] at", event.x, event.y)

        # pokud není startovní souřadnice, nic se nestane
        if last_x is None or last_y is None:
            print("nemáme startovací souřadnice")
            return

        dx = event.x - last_x
        dy = event.y - last_y

        # pokud je vybraný objekt, posunem ho
        if selected_object and current_mode == "edit" and is_dragging_object:
            if selected_object.get("locked"):
                return

            # najdeme zónu, do které objekt patří
            parent_zone = None
            for zone_type, inst in zones_data.items():
                if not inst:
                    continue

                if selected_object in inst.get("objects", []):
                    parent_zone = inst
                    break

            # --- SPECIÁLNÍ LOGIKA PRO VSTUP ---
            if selected_object["object"] == "Vstup":

                # vypočítáme nové souřadnice středu po posunu
                new_x = selected_object["x"] + dx
                new_y = selected_object["y"] + dy

                # vstup smí být jen na festivalovém areálu
                if parent_zone["type"] != "Festivalový areál":
                    print("Vstup lze přesouvat pouze na festivalovém areálu.")
                    return

                # musí zůstat na hraně
                if not is_on_edge(parent_zone, new_x, new_y):
                    print("Vstup lze přesouvat pouze po hraně festivalového areálu.")
                    return

                # pokud prošel kontrolou → posuneme ho
                for cid in selected_object.get("canvas_ids", []):
                    canvas.move(cid, dx, dy)

                for extra in selected_object.get("extra", []):
                    for cid in extra.get("canvas_ids", []):
                        canvas.move(cid, dx, dy)

                selected_object["x"] += dx
                selected_object["y"] += dy

                last_x, last_y = event.x, event.y
                return
            # --- KONEC SPECIÁLNÍ LOGIKY PRO VSTUP ---

            # --- BĚŽNÉ OBJEKTY ---
            if parent_zone:
                zone_left = parent_zone["left"]
                zone_top = parent_zone["top"]
                zone_right = parent_zone["right"]
                zone_bottom = parent_zone["bottom"]

                obj_left, obj_top, obj_right, obj_bottom = canvas.bbox(selected_object["canvas_ids"][1])

                # omezení dx, dy, aby objekt nevyskočil z hranic zóny
                if obj_left + dx < zone_left:
                    dx = zone_left - obj_left
                if obj_right + dx > zone_right:
                    dx = zone_right - obj_right
                if obj_top + dy < zone_top:
                    dy = zone_top - obj_top
                if obj_bottom + dy > zone_bottom:
                    dy = zone_bottom - obj_bottom

            # posun běžného objektu
            for cid in selected_object.get("canvas_ids", []):
                canvas.move(cid, dx, dy)

            for extra in selected_object.get("extra", []):
                for cid in extra.get("canvas_ids", []):
                    canvas.move(cid, dx, dy)

            selected_object["x"] += dx
            selected_object["y"] += dy

            last_x, last_y = event.x, event.y
            return

        # pokud budeme měnit velikost zony
        if selected_zone_instance and current_mode == "edit" and is_dragging_zone:
            
            RESIZE_TOLERANCE_OBJ = 50

            resize_info = selected_zone_instance.get("resize_info")
            print("Resize info:" , resize_info)
            if resize_info:
                old_left = selected_zone_instance["left"]
                old_right = selected_zone_instance["right"]
                old_top = selected_zone_instance["top"]
                old_bottom = selected_zone_instance["bottom"]
                old_coords = old_left, old_top, old_right, old_bottom

                # upravíme souřadnice
                if resize_info["left"]:
                    selected_zone_instance["left"] += dx
                if resize_info["right"]:
                    selected_zone_instance["right"] += dx
                if resize_info["top"]:
                    selected_zone_instance["top"] += dy
                if resize_info["bottom"]:
                    selected_zone_instance["bottom"] += dy

                l = selected_zone_instance["left"]
                t = selected_zone_instance["top"]
                r = selected_zone_instance["right"]
                b = selected_zone_instance["bottom"]

                selected_zone_instance["left"] = min(l, r)
                selected_zone_instance["right"] = max(l, r)
                selected_zone_instance["top"] = min(t, b)
                selected_zone_instance["bottom"] = max(t, b)

                other_zones = []
                for zone_type, inst in zones_data.items():
                    if inst:
                        other_zones.append(inst)

                # pokud je překrytí, vrátíme staré souřadnice
                if zone_overlaps(selected_zone_instance, other_zones):
                    selected_zone_instance["left"], selected_zone_instance["top"], selected_zone_instance["right"], selected_zone_instance["bottom"] = old_coords

                # omezíme posun, aby objekty zůstaly uvnitř
                for obj in selected_zone_instance.get("objects", []):
                    obj_x, obj_y = obj["x"], obj["y"]
                    # pokud objekt vyjde mimo, vrátíme souřadnici zóny zpět
                    if obj_x - RESIZE_TOLERANCE_OBJ < selected_zone_instance["left"]:
                        selected_zone_instance["left"] = old_left
                    if obj_x + RESIZE_TOLERANCE_OBJ > selected_zone_instance["right"]:
                        selected_zone_instance["right"] = old_right
                    if obj_y - RESIZE_TOLERANCE_OBJ < selected_zone_instance["top"]:
                        selected_zone_instance["top"] = old_top
                    if obj_y + RESIZE_TOLERANCE_OBJ > selected_zone_instance["bottom"]:
                        selected_zone_instance["bottom"] = old_bottom

                # aktualizujeme canvas
                canvas.coords(
                    selected_zone_instance["rect_id"],
                    selected_zone_instance["left"],
                    selected_zone_instance["top"],
                    selected_zone_instance["right"],
                    selected_zone_instance["bottom"]
                )

                # nadpis uprostřed nahoře
                label_x = (selected_zone_instance["left"] + selected_zone_instance["right"]) / 2
                label_y = selected_zone_instance["top"] - 12
                canvas.coords(selected_zone_instance["label_id"], label_x, label_y)

                update_zone_lines(selected_zone_instance)

                last_x, last_y = event.x, event.y

        # pokud kreslíme novou zónu
        if not drawing or current_object is not None:
            return

        if zone_rect is not None:
            canvas.delete(zone_rect)
            zone_rect = None
        if zone_label is not None:
            canvas.delete(zone_label)
            zone_label = None

        x1, y1 = last_x, last_y
        x2, y2 = event.x, event.y
        left, right = min(x1, x2), max(x1, x2)
        top, bottom = min(y1, y2), max(y1, y2)

        zone_rect = canvas.create_rectangle(left, top, right, bottom, outline="blue", fill="white", width=3)
        zone_label_x = (left + right) / 2
        zone_label_y = top - 12
        zone_label = canvas.create_text(zone_label_x, zone_label_y, text=current_zone, fill="black", font=("Arial", 12, "bold"), anchor="s")


    def on_release(event):
        """Ukončení kreslení"""
        global drawing, zone_rect, zone_label, last_x, last_y, current_zone, zones_data, is_dragging_object

        print("[RELEASE] at", event.x, event.y)
        print("    is_dragging_object =", is_dragging_object)

        is_dragging_object = False
        print("[RELEASE] Dragging deaktivován")
        last_x, last_y = None, None

        if not drawing:
            return

        drawing = False

        if zone_rect is not None:
            left, top, right, bottom = canvas.coords(zone_rect)

            zone_instance = {"type": current_zone, "left": left, "top": top, "right": right, "bottom": bottom, "objects": [], "lines": [] }

            draw_zone(zone_instance)
    
            zones_data[current_zone] = zone_instance

            print(f"Uložená zóna {current_zone}: {left, top, right, bottom}")

            canvas.delete(zone_rect)
            if zone_label:
                canvas.delete(zone_label)

        zone_rect = None
        zone_label = None

    def draw_zone(zone_instance):
        zone_instance["resize_info"] = {
            "left": False,
            "right": False,
            "top": False,
            "bottom": False
        }

        left = zone_instance["left"]
        top = zone_instance["top"]
        right = zone_instance["right"]
        bottom = zone_instance["bottom"]
        zone_type = zone_instance["type"]

        rect_id = canvas.create_rectangle(left, top, right, bottom, outline="blue", fill="white", width=3)
        label_id = canvas.create_text((left + right)/2, top-12, text=zone_type, fill="black", font=("Arial", 12, "bold"), anchor="s")

        zone_instance["rect_id"] = rect_id
        zone_instance["label_id"] = label_id
        zone_instance["canvas_ids"] = [rect_id, label_id]

        return {
        "rect_id": rect_id,
        "label_id": label_id,
        "canvas_ids": [rect_id, label_id]
        }


    def delete_selected(event=None):
        global selected_zone_instance, selected_object, selected_line

        if selected_object:
            
            # smažeme z canvasu
            extra = selected_object.get("extra", [])
            for e in extra:
                for cid in e.get("canvas_ids", []):
                    canvas.delete(cid)
            for cid in selected_object.get("canvas_ids", []):
                canvas.delete(cid)

            # odstraní z instance
            for zone_type, inst in zones_data.items():
                if inst and selected_object in inst.get("objects", []):
                    inst["objects"].remove(selected_object)
            selected_object = None
            print("Objekt smazán")

        if selected_line:
            delete_line(selected_line["id"])

        if selected_zone_instance:
            delete_zone(selected_zone_instance)
            selected_zone_instance = None
            return

    RESIZE_TOLERANCE = 20 

    def delete_zone(zone):
        # 1) Smazat grafiku z canvasu
        canvas.delete(zone["rect_id"])
        canvas.delete(zone["label_id"])

        # 2) Smazat všechny objekty v zóně
        for obj in zone.get("objects", []):
            for cid in obj.get("canvas_ids", []):
                canvas.delete(cid)
            for extra in obj.get("extra", []):
                for cid in extra.get("canvas_ids", []):
                    canvas.delete(cid)

        # 3) Smazat všechny linky této zóny
        for line in zone.get("lines", []):
            canvas.delete(line["id"])

        # 4) Odstranit zónu z dat
        for zone_type, inst in zones_data.items():
            if inst is zone:
                zones_data[zone_type] = None
                break

    def delete_line(line_id):
        global zones_data

        # 1) Smazat z canvasu
        canvas.delete(line_id)

        # 2) Smazat ze všech zón
        for zone_type, zone in zones_data.items():
            if not zone:
                continue

            zone["lines"] = [ln for ln in zone.get("lines", []) if ln["id"] != line_id]

            for obj in zone.get("objects", []):
                if obj.get("object") == "Vstup":
                    obj["lines"] = [ln for ln in obj.get("lines", []) if ln["id"] != line_id]
                    if len(obj["lines"]) == 0:
                        obj["locked"] = False


    def get_resize_direction(zone, x, y):
        """Vrátí (dx, dy) který říká, které hrany/rohy se mají měnit"""

        left, top, right, bottom = zone["left"], zone["top"], zone["right"], zone["bottom"]

        resize_dir = {"left": False, "right": False, "top": False, "bottom": False}

        if abs(x - left) <= RESIZE_TOLERANCE:
            resize_dir["left"] = True
        if abs(x - right) <= RESIZE_TOLERANCE:
            resize_dir["right"] = True
        if abs(y - top) <= RESIZE_TOLERANCE:
            resize_dir["top"] = True
        if abs(y - bottom) <= RESIZE_TOLERANCE:
            resize_dir["bottom"] = True

        # pokud žádná hrana, tak vrátí None → znamená přesouvání
        if not any(resize_dir.values()):
            return None
        return resize_dir



    def closest_point_on_zone(zone_from, zone_to):
        """Vrátí bod (x, y) na hraně zone_from nejbližší k zone_to"""

        fx1, fy1, fx2, fy2 = zone_from["left"], zone_from["top"], zone_from["right"], zone_from["bottom"]
        tx1, ty1, tx2, ty2 = zone_to["left"], zone_to["top"], zone_to["right"], zone_to["bottom"]

        # střed zóny 2
        cx2 = (tx1 + tx2) / 2
        cy2 = (ty1 + ty2) / 2

        # středy hran zóny 1
        top_center = ((fx1 + fx2) / 2, fy1)
        bottom_center = ((fx1 + fx2) / 2, fy2)
        left_center = (fx1, (fy1 + fy2) / 2)
        right_center = (fx2, (fy1 + fy2) / 2)

        edges = [top_center, bottom_center, left_center, right_center]

        # najdeme nejbližší bod
        closest = min(edges, key=lambda p: (p[0] - cx2)**2 + (p[1] - cy2)**2)
        return closest

    def update_zone_lines(zone):
        for line in zone.get("lines", []):
            other = line["other_zone"]

            # rozlišení spojení přes vstup
            if "entry" in other:
                # pevný bod je vstup
                x2, y2 = other["entry"]["x"], other["entry"]["y"]
                # zóna – střed hrany nejblíže vstupu
                x1, y1 = center_of_closest_edge(zone, x2, y2)
            else:
                # normální zóna ↔ zóna
                other_zone = None
                for zt, inst in zones_data.items():
                    if inst and inst["type"] == other["type"]:
                        other_zone = inst
                        break

                if not other_zone:
                    continue
                x1, y1 = closest_point_on_zone(zone, other_zone)
                x2, y2 = closest_point_on_zone(other_zone, zone)

            canvas.coords(line["id"], x1, y1, x2, y2)
    
    def zone_overlaps(zone, other_zones):
        """Vrátí True, pokud zóna překrývá některou z ostatních zón."""

        for other in other_zones:
            if other == zone:
                continue
            
            if (zone["left"] < other["right"] and zone["right"] > other["left"] and zone["top"] < other["bottom"] and zone["bottom"] > other["top"]):
                return True
        return False


    def draw_load(data):
        global zones_data
        zones_data = data

        # 1) vykreslit zóny
        for zone_type, inst in zones_data.items():
            if not inst:
                continue

            draw_zone(inst)

            # 2) vykreslit objekty
            for obj in inst.get("objects", []):
                new_obj = create_object(inst, obj["object"], obj["x"], obj["y"], saved_object_id=obj["id"])
                obj["canvas_ids"] = new_obj["canvas_ids"]
                obj["extra"] = new_obj.get("extra", [])
                if obj["object"] == "Vstup":
                    obj["locked"] = True

        print("Všechny zóny a objekty vykresleny.")

        # 3) znovu vytvořit linky
        all_lines = []

        for zone_type, inst in zones_data.items():
            if not inst:
                continue

            for line in inst.get("lines", []):
                target_name = line["other_zone"]["zone"]

                zona2 = next(
                    (z for z in zones_data.values() if z and z.get("type") == target_name),
                    None
                )

                vstup = None
                if "entry" in line:
                    entry_id = line["entry"]["id"]
                    vstup = next(
                        (obj for obj in inst["objects"]
                        if obj.get("object") == "Vstup" and obj.get("id") == entry_id),
                        None
                    )

                all_lines.append({
                    "zona1": inst,
                    "zona2": zona2,
                    "vstup": vstup,
                    "line": line
                })

        # reset lines
        for inst in zones_data.values():
            if inst:
                inst["lines"] = []

        # znovu nakreslit
        for item in all_lines:
            zona1 = item["zona1"]
            zona2 = item["zona2"]
            vstup = item["vstup"]

            if not zona1 or not zona2:
                continue

            if vstup:
                connect_entry_to_zone(vstup, zona2)
            else:
                connect_zone_to_zone(zona1, zona2)

    print("Všechny linky vykresleny.")

    print("Všechny čáry vykresleny.")

    canvas.bind("<Button-1>", on_click)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)
    root.bind("<Delete>", delete_selected)
    root.mainloop()
                    