import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
from . import saving
from . import loading 
import os
import copy
import source

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

zones_data = {
    "Spawn zóna": {"multiple": False, "instances": []},
    "Vstupní zóna": {"multiple": False, "instances": []},
    "Festivalový areál": {"multiple": False, "instances": []},
    "Stanové městečko": {"multiple": False, "instances": []},
    "Chill zóna": {"multiple": False, "instances": []},
    "Zábavní zóna": {"multiple": False, "instances": []}
}

zones_data_default = copy.deepcopy(zones_data)

def get_user_settings():
    settings = {}
    
    def start():
        merch = get_merch(bands_entries)
        capacities = get_capacities()
        prices = get_prices()

        settings['num_visitors'] = int(entry_visitors.get())
        settings['num_days'] = int(entry_days.get())
        settings['budget_for_bands'] = int(entry_budget.get())
        settings['num_bands'] = int(entry_num_bands.get())
        settings['simulation_start_time'] = simulation_start_time.get()
        settings['headliner_time'] = int(headliner_time.get())
        settings['band_time'] = int(band_time.get())
        settings['first_show_starts'] = first_show_starts.get()
        settings['last_show_ends'] = last_show_ends.get()
        settings['signing_time'] = signing_time.get()
        settings['prices'] = prices
        settings['merch'] = merch
        settings['capacities'] = capacities
        
        editor_buttons_frame.pack_forget()
        frame_left.pack_forget()
        frame_right.pack_forget()
        simulation_buttons_frame.pack(pady=5)
        left_simulation_container.pack(side="left", fill="y")

        #root.destroy()

    def exit_app():
        root.quit()
        root.destroy()

    default_loaded = False

    def open_editor():
        nonlocal default_loaded

        main_frame.pack_forget()
        editor_frame.pack(fill="both", expand=True)

        if not default_loaded:
            load_default()
            default_loaded = True
        
    def open_stalls_settings():
        main_frame.pack_forget()
        settings_frame.pack_forget()
        stall_settings_frame.place(relx=0.5, rely=0.5, anchor="center")

    def open_times_settings():
        main_frame.pack_forget()
        settings_frame.pack_forget()
        times_settings_frame.place(relx=0.5, rely=0.5, anchor="center")

    def open_prices_settings():
        main_frame.pack_forget()
        settings_frame.pack_forget()
        prices_settings_frame.place(relx=0.5, rely=0.5, anchor="center")

    def open_merch_settings():
        main_frame.pack_forget()
        settings_frame.pack_forget()
        merch_frame.place(relx=0.5, rely=0.5, anchor="center")
    
    def open_settings():
        main_frame.pack_forget()
        settings_frame.pack(fill="both", expand=True)

    def go_back():
        if stall_settings_frame.winfo_ismapped():
            stall_settings_frame.place_forget()
            settings_frame.pack(fill="both", expand=True)
        
        elif prices_settings_frame.winfo_ismapped():
            prices_settings_frame.place_forget()
            settings_frame.pack(fill="both", expand=True) 

        elif settings_frame.winfo_ismapped():
            settings_frame.pack_forget()
            main_frame.pack(fill="both", expand=True)

        elif times_settings_frame.winfo_ismapped():
            times_settings_frame.place_forget()
            settings_frame.pack(fill="both", expand=True)
        
        elif merch_frame.winfo_ismapped():
            merch_frame.place_forget()
            settings_frame.pack(fill="both", expand=True)

        elif editor_frame.winfo_ismapped():
            editor_frame.pack_forget()
            main_frame.pack(fill="both", expand=True)
    
    def stop_simulation():
        simulation_buttons_frame.pack_forget()
        left_simulation_container.pack_forget()
        editor_buttons_frame.pack(pady=20)
        frame_left.pack(side="left", fill="y", padx=0, pady=0)
        frame_right.pack(side="left", fill="y", padx=0, pady=0)

    def simulation_step():
        pass
    # ---------- HLAVNÍ OKNO ----------
    
    root = tk.Tk()
    root.title("Nastavení festivalu")
    root.attributes("-fullscreen", True)
    root.configure(bg='black')


#------------------------------------------------------------------STYLY----------------------------------------------------------------------------------------------------
  
  
    label_style = {"bg": "black", "fg": "white", "font": ("Arial", 20)}
    entry_style = {"font": ("Arial", 18), "bg": "#222", "fg": "white", "insertbackground": "white", "width": 10}
    entry_style2 = {"font": ("Arial", 18), "bg": "#222", "fg": "white", "insertbackground": "white", "width": 5}

    def blue_button(parent, text, command):
        return ctk.CTkButton(parent, text=text, command=command, corner_radius=20, fg_color="blue", hover_color="#2f4dfa", text_color="white", width=150, height=65, font=("Arial", 25))

    def blue_button_small(parent, text, command):
        return ctk.CTkButton(parent, text=text, command=command, corner_radius=20, fg_color="blue", hover_color="#2f4dfa", text_color="white", width=90, height=50, font=("Arial", 25))
        
    def red_button(parent, text, command):
        return ctk.CTkButton(parent, text=text, command=command, corner_radius=20, fg_color="red", hover_color="#fc4437", text_color="white", width=150, height=65, font=("Arial", 25))
    
    def red_button_small(parent, text, command):
        return ctk.CTkButton(parent, text=text, command=command, corner_radius=20, fg_color="red", hover_color="#fc4437", text_color="white", width=90, height=50, font=("Arial", 25))
    
    def green_button(parent, text, command):
        return ctk.CTkButton(parent, text=text, command=command, corner_radius=20, fg_color="green", hover_color="#4ef35c", text_color="white", width=150, height=65, font=("Arial", 25))
    
    def green_button_small(parent, text, command):
        return ctk.CTkButton(parent, text=text, command=command, corner_radius=20, fg_color="green", hover_color="#4ef35c", text_color="white", width=90, height=50, font=("Arial", 25))

    def object_button(parent, text, obj, img):       
        return ctk.CTkButton(parent, text=text, image=img, compound="left", anchor="w", corner_radius=10, fg_color="white", hover_color="#c3c3c5",  text_color="black", border_width=2, border_color="black", width=170, height=28, font=("Arial", 12.5, "bold"), command=lambda o=obj: select_object(o))
    
    def zone_button(parent, zone_name):
        return ctk.CTkButton(parent, text=zone_name, corner_radius=10, fg_color="white", hover_color="#c3c3c5",  text_color="black", border_width=2, border_color="black", width=170, height=50, font=("Arial", 15, "bold"), command=lambda z=zone_name: select_zone(z))
    
    def mode_button(parent, text):
        return ctk.CTkButton(parent, text=text, corner_radius=10, fg_color="white", hover_color="#c3c3c5",  text_color="black", border_width=2, border_color="black",  width=55, height=55, font=("Arial", 14, "bold"), command=lambda m=mode_name: select_mode(m))

    # ---------- OBRAZOVKA 1: Úvodní menu ----------

    main_frame = tk.Frame(root, bg='black')
    main_frame.pack(fill="both", expand=True)

    title_label = tk.Label(main_frame, text="Simulace hudebního festivalu", font=("Arial", 36, "bold"), bg="black", fg="yellow")
    title_label.pack(pady=30)

    frame = tk.Frame(main_frame, bg='black')
    frame.pack(pady=30)

    tk.Label(frame, text="Počet návštěvníků:", **label_style).grid(row=0, column=0, pady=10, sticky="w")
    entry_visitors = tk.Entry(frame, **entry_style)
    entry_visitors.grid(row=0, column=1, pady=10)
    entry_visitors.insert(0, "50")

    tk.Label(frame, text="Počet dní:", **label_style).grid(row=1, column=0, pady=10, sticky="w")
    entry_days = tk.Entry(frame, **entry_style)
    entry_days.grid(row=1, column=1, pady=10)
    entry_days.insert(0, "2")

    tk.Label(frame, text="Rozpočet pro kapely:", **label_style).grid(row=2, column=0, pady=10, sticky="w")
    entry_budget = tk.Entry(frame, **entry_style)
    entry_budget.grid(row=2, column=1, pady=10)
    entry_budget.insert(0, "10000000")

    tk.Label(frame, text="Počet kapel na den:", **label_style).grid(row=3, column=0, pady=10, sticky="w")
    entry_num_bands = tk.Entry(frame, **entry_style)
    entry_num_bands.grid(row=3, column=1, pady=10)
    entry_num_bands.insert(0, "8")

    tk.Label(frame, text="Čas začátku simulace:", **label_style).grid(row=4, column=0, pady=10, sticky="w")
    simulation_start_time = tk.Entry(frame, **entry_style)
    simulation_start_time.grid(row=4, column=1, pady=10)
    simulation_start_time.insert(0, "09:00")

    bottom_frame = tk.Frame(main_frame, bg='black')
    bottom_frame.pack(side="bottom", pady=30)

    editor_button = blue_button(bottom_frame, "Dále", open_editor)
    editor_button.pack(side="left", padx=10)
 
    settings_button = blue_button(bottom_frame, "Nastavení", open_settings)
    settings_button.pack(side="left", padx=10)

    exit_button = red_button(bottom_frame, "Zavřít", exit_app)
    exit_button.pack(side="left", padx=10)


    # ---------- OBRAZOVKA2: Settings

    settings_frame = tk.Frame(root, bg="black")
    settings_frame.pack_forget()

    tk.Label(settings_frame, text="Nastavení", font=("Arial", 32,"bold"), bg="black", fg="yellow").pack(padx=20, pady=20)

    stall_settings_button = blue_button(settings_frame, "Kapacity objektů", open_stalls_settings)
    stall_settings_button.pack() 

    prices_settings_button = blue_button(settings_frame, "Festivalové ceny", open_prices_settings)
    prices_settings_button.pack() 

    merch_settings_button = blue_button(settings_frame, "Ceny merche", open_merch_settings)
    merch_settings_button.pack() 

    times_settings_button = blue_button(settings_frame, "Časy", open_times_settings)
    times_settings_button.pack() 

    settings_bottom_frame = tk.Frame(settings_frame, bg='black')
    settings_bottom_frame.pack(side="bottom", pady=30, fill="x")

    back_button = blue_button(settings_bottom_frame, "Zpět", go_back)
    back_button.pack()

    # ---------- OBRAZOVKA3: Stall capacities settings

    stall_settings_frame = tk.Frame(root, bg="black")
    stall_settings_frame.pack_forget()
    

    tk.Label(stall_settings_frame, text="Kapacity", font=("Arial", 32, "bold"), bg="black", fg="yellow").grid(row=0, column=0, columnspan=7, pady=(40, 40))

    tk.Label(stall_settings_frame, text="Pizza stánek:", **label_style).grid(row=1, column=1, pady=5, sticky="w", padx=50)
    cap_pizza_stall = tk.Entry(stall_settings_frame, **entry_style2)
    cap_pizza_stall.grid(row=1, column=2, padx=20)
    cap_pizza_stall.insert(0, "2")

    tk.Label(stall_settings_frame, text="Burger stánek:", **label_style).grid(row=2, column=1, pady=5, sticky="w", padx=50)
    cap_burger_stall = tk.Entry(stall_settings_frame, **entry_style2)
    cap_burger_stall.grid(row=2, column=2, padx=20)
    cap_burger_stall.insert(0, "2")

    tk.Label(stall_settings_frame, text="Gyros stánek:", **label_style).grid(row=3, column=1, pady=5, sticky="w", padx=50)
    cap_gyros_stall = tk.Entry(stall_settings_frame, **entry_style2)
    cap_gyros_stall.grid(row=3, column=2, padx=20)
    cap_gyros_stall.insert(0, "2")

    tk.Label(stall_settings_frame, text="Grill stánek:", **label_style).grid(row=4, column=1, pady=5, sticky="w", padx=50)
    cap_grill_stall = tk.Entry(stall_settings_frame, **entry_style2)
    cap_grill_stall.grid(row=4, column=2, padx=20)
    cap_grill_stall.insert(0, "2")

    tk.Label(stall_settings_frame, text="Bel hranolky stánek:", **label_style).grid(row=5, column=1, pady=5, sticky="w", padx=50)
    cap_fries_stall = tk.Entry(stall_settings_frame, **entry_style2)
    cap_fries_stall.grid(row=5, column=2, padx=20)
    cap_fries_stall.insert(0, "2")

    tk.Label(stall_settings_frame, text="Langoš stánek:", **label_style).grid(row=6, column=1, pady=5, sticky="w", padx=50)
    cap_langos_stall = tk.Entry(stall_settings_frame, **entry_style2)
    cap_langos_stall.grid(row=6, column=2, padx=20)
    cap_langos_stall.insert(0, "2")

    tk.Label(stall_settings_frame, text="Sladký stánek:", **label_style).grid(row=7, column=1, pady=5, sticky="w", padx=50)
    cap_sweet_stall = tk.Entry(stall_settings_frame, **entry_style2)
    cap_sweet_stall.grid(row=7, column=2, padx=20)
    cap_sweet_stall.insert(0, "2")

    tk.Label(stall_settings_frame, text="Nealko stánek:", **label_style).grid(row=8, column=1, pady=5, sticky="w", padx=50)
    cap_nonalcohol_stall = tk.Entry(stall_settings_frame, **entry_style2)
    cap_nonalcohol_stall.grid(row=8, column=2, padx=20)
    cap_nonalcohol_stall.insert(0, "2")

    tk.Label(stall_settings_frame, text="Pivní stánek:", **label_style).grid(row=9, column=1, pady=5, sticky="w", padx=50)
    cap_beer_stall = tk.Entry(stall_settings_frame, **entry_style2)
    cap_beer_stall.grid(row=9, column=2, padx=20)
    cap_beer_stall.insert(0, "2")

    tk.Label(stall_settings_frame, text="Red Bull stánek:", **label_style).grid(row=10, column=1, pady=5, sticky="w", padx=50)
    cap_redbull_stall = tk.Entry(stall_settings_frame, **entry_style2)
    cap_redbull_stall.grid(row=10, column=2, padx=20)
    cap_redbull_stall.insert(0, "2")

    tk.Label(stall_settings_frame, text="Stánek s míchanými drinky:", **label_style).grid(row=11, column=1, pady=5, sticky="w", padx=50)
    cap_cocktail_stall = tk.Entry(stall_settings_frame, **entry_style2)
    cap_cocktail_stall.grid(row=11, column=2, padx=20)
    cap_cocktail_stall.insert(0, "2")

    tk.Label(stall_settings_frame, text="Sprchy:", **label_style).grid(row=12, column=1, pady=5, sticky="w", padx=50)
    cap_showers = tk.Entry(stall_settings_frame, **entry_style2)
    cap_showers.grid(row=12, column=2, padx=20)
    cap_showers.insert(0, "5")

    tk.Label(stall_settings_frame, text="Stany ve stanovém městečku:", **label_style).grid(row=13, column=1, pady=5, sticky="w", padx=50)
    cap_tents = tk.Entry(stall_settings_frame, **entry_style2)
    cap_tents.grid(row=13, column=2, padx=20)
    cap_tents.insert(0, "500")

    tk.Label(stall_settings_frame, text="Stánek s cigaretama:", **label_style).grid(row=14, column=1, pady=5, sticky="w", padx=50)
    cap_cigars_tent = tk.Entry(stall_settings_frame, **entry_style2)
    cap_cigars_tent.grid(row=14, column=2, padx=20)
    cap_cigars_tent.insert(0, "1")

    tk.Label(stall_settings_frame, text="Stánek s vodníma dýmkama", **label_style).grid(row=15, column=1, pady=5, sticky="w", padx=50)
    cap_water_pipe_stall = tk.Entry(stall_settings_frame, **entry_style2)
    cap_water_pipe_stall.grid(row=15, column=2, padx=20)
    cap_water_pipe_stall.insert(0, "20")

    tk.Label(stall_settings_frame, text="Počet turniketů u vstupu:", **label_style).grid(row=16, column=1, pady=5, sticky="w", padx=50)
    num_entrance_gate = tk.Entry(stall_settings_frame, **entry_style2)
    num_entrance_gate.grid(row=16, column=2, padx=20)
    num_entrance_gate.insert(0, "4")

    tk.Label(stall_settings_frame, text="Výkup kelímků:", **label_style).grid(row=17, column=1, pady=5, sticky="w", padx=50)
    cap_cup_return = tk.Entry(stall_settings_frame, **entry_style2)
    cap_cup_return.grid(row=17, column=2, padx=20)
    cap_cup_return.insert(0, "4")    

    tk.Label(stall_settings_frame, text="Chill stánek", **label_style).grid(row=1, column=4, pady=5, sticky="w", padx=50)
    cap_chill_stall = tk.Entry(stall_settings_frame, **entry_style2)
    cap_chill_stall.grid(row=1, column=5, padx=20)
    cap_chill_stall.insert(0, "20")  

    tk.Label(stall_settings_frame, text="Pokladna:", **label_style).grid(row=2, column=4, pady=5, sticky="w", padx=50)
    cap_ticket_booth = tk.Entry(stall_settings_frame, **entry_style2)
    cap_ticket_booth.grid(row=2, column=5, padx=20)
    cap_ticket_booth.insert(0, "2")
    
    tk.Label(stall_settings_frame, text="Toitoiky:", **label_style).grid(row=3, column=4, pady=5, sticky="w", padx=50)
    cap_toitoi = tk.Entry(stall_settings_frame, **entry_style2)
    cap_toitoi.grid(row=3, column=5, padx=20)
    cap_toitoi.insert(0, "20")

    tk.Label(stall_settings_frame, text="Umývárna:", **label_style).grid(row=4, column=4, pady=5, sticky="w", padx=50)
    cap_handwashing_station = tk.Entry(stall_settings_frame, **entry_style2)
    cap_handwashing_station.grid(row=4, column=5, padx=20)
    cap_handwashing_station.insert(0, "20")

    tk.Label(stall_settings_frame, text="Stoly:", **label_style).grid(row=5, column=4, pady=5, sticky="w", padx=50)
    cap_tables = tk.Entry(stall_settings_frame, **entry_style2)
    cap_tables.grid(row=5, column=5, padx=20)
    cap_tables.insert(0, "20")

    tk.Label(stall_settings_frame, text="Plocha na stání u pódia:", **label_style).grid(row=6, column=4, pady=5, sticky="w", padx=50)
    cap_standing = tk.Entry(stall_settings_frame, **entry_style2)
    cap_standing.grid(row=6, column=5, padx=20)
    cap_standing.insert(0, "1000")

    tk.Label(stall_settings_frame, text="Merch stan:", **label_style).grid(row=7, column=4, pady=5, sticky="w", padx=50)
    cap_merch_stall = tk.Entry(stall_settings_frame, **entry_style2)
    cap_merch_stall.grid(row=7, column=5, padx=20)
    cap_merch_stall.insert(0, "3")

    tk.Label(stall_settings_frame, text="Fronta na autogramiády", **label_style).grid(row=8, column=4, pady=5, sticky="w", padx=50)
    cap_signing_stall = tk.Entry(stall_settings_frame, **entry_style2)
    cap_signing_stall.grid(row=8, column=5, padx=20)
    cap_signing_stall.insert(0, "500")

    tk.Label(stall_settings_frame, text="Dobíjecí stan:", **label_style).grid(row=9, column=4, pady=5, sticky="w", padx=50)
    cap_charging_stall = tk.Entry(stall_settings_frame, **entry_style2)
    cap_charging_stall.grid(row=9, column=5, padx=20)
    cap_charging_stall.insert(0, "2")

    tk.Label(stall_settings_frame, text="Dobíjecí stan - max počet telefonů:", **label_style).grid(row=10, column=4, pady=5, sticky="w", padx=50)
    cap_charging_stall_mobile = tk.Entry(stall_settings_frame, **entry_style2)
    cap_charging_stall_mobile.grid(row=10, column=5, padx=20)
    cap_charging_stall_mobile.insert(0, "20")

    tk.Label(stall_settings_frame, text="Bungee-jumping:", **label_style).grid(row=11, column=4, pady=5, sticky="w", padx=50)
    cap_bungee_jumping = tk.Entry(stall_settings_frame, **entry_style2)
    cap_bungee_jumping.grid(row=11, column=5, padx=20)
    cap_bungee_jumping.insert(0, "1")

    tk.Label(stall_settings_frame, text="Horská dráze:", **label_style).grid(row=12, column=4, pady=5, sticky="w", padx=50)
    cap_rollercoaster = tk.Entry(stall_settings_frame, **entry_style2)
    cap_rollercoaster.grid(row=12, column=5, padx=20)
    cap_rollercoaster.insert(0, "24")

    tk.Label(stall_settings_frame, text="Lavice (atrakce):", **label_style).grid(row=13, column=4, pady=5, sticky="w", padx=50)
    cap_bench_attraction = tk.Entry(stall_settings_frame, **entry_style2)
    cap_bench_attraction.grid(row=13, column=5, padx=20)
    cap_bench_attraction.insert(0, "20")

    tk.Label(stall_settings_frame, text="Kladivo (atrakce):", **label_style).grid(row=14, column=4, pady=5, sticky="w", padx=50)
    cap_hammer_attraction = tk.Entry(stall_settings_frame, **entry_style2)
    cap_hammer_attraction.grid(row=14, column=5, padx=20)
    cap_hammer_attraction.insert(0, "32")

    tk.Label(stall_settings_frame, text="Řetizkáč:", **label_style).grid(row=15, column=4, pady=5, sticky="w", padx=50)
    cap_carousel = tk.Entry(stall_settings_frame, **entry_style2)
    cap_carousel.grid(row=15, column=5, padx=20)
    cap_carousel.insert(0, "32")

    tk.Label(stall_settings_frame, text="Skákací hrad:", **label_style).grid(row=16, column=4, pady=5, sticky="w", padx=50)
    cap_jumping_castle = tk.Entry(stall_settings_frame, **entry_style2)
    cap_jumping_castle.grid(row=16, column=5, padx=20)
    cap_jumping_castle.insert(0, "8")


    bottom_settings_stalls_frame = tk.Frame(stall_settings_frame, bg="black") 
    bottom_settings_stalls_frame.grid(row=20, column=0, columnspan=6, pady=40) 
    back_button = blue_button(bottom_settings_stalls_frame,"Zpět", go_back) 
    back_button.pack()

    def get_capacities():
        capacities = {}
        capacities["pizza_stall"] = int(cap_pizza_stall.get())
        capacities["burger_stall"] = int(cap_burger_stall.get())
        capacities["gyros_stall"] = int(cap_gyros_stall.get())
        capacities["grill_stall"] = int(cap_grill_stall.get())
        capacities["belgian_fries_stall"] = int(cap_fries_stall.get())
        capacities["langos_stall"] = int(cap_langos_stall.get())
        capacities["sweet_stall"] = int(cap_sweet_stall.get())
        capacities["ticket_booth"] = int(cap_ticket_booth.get())
        capacities["toitoi"] = int(cap_toitoi.get())
        capacities["handwashing_station"] = int(cap_handwashing_station.get())
        capacities["tables"] = int(cap_tables.get())
        capacities["standing"] = int(cap_standing.get())
        capacities["merch_stall"] = int(cap_merch_stall.get())
        capacities["signing_stall"] = int(cap_signing_stall.get())
        capacities["charging_stall"] = int(cap_charging_stall.get())
        capacities["charging_stall_mobile"] = int(cap_charging_stall_mobile.get())
        capacities["showers"] = int(cap_showers.get())
        capacities["cigaret_stall"] = int(cap_cigars_tent.get())
        capacities["water_pipe_stall"] = int(cap_water_pipe_stall.get())
        capacities["chill_stall"] = int(cap_charging_stall.get())
        capacities["bungee_jumping"] = int(cap_bungee_jumping.get())
        capacities["rollercoaster"] = int(cap_rollercoaster.get())
        capacities["bench"] = int(cap_bench_attraction.get())
        capacities["hammer"] = int(cap_hammer_attraction.get())
        capacities["nonalcohol_stall"] = int(cap_nonalcohol_stall.get())
        capacities["beer_stall"] = int(cap_beer_stall.get())
        capacities["redbull_stall"] = int(cap_redbull_stall.get())
        capacities["cocktail_stall"] = int(cap_cocktail_stall.get())
        capacities["entry"] = int(num_entrance_gate.get())
        capacities["signing_stall"] = int(cap_signing_stall.get())
        capacities["meadow_for_living"] = int(cap_tents.get())
        capacities["atm"] = 1
        capacities["cup_return"] = int(cap_cup_return.get())
        capacities["carousel"] = int(cap_carousel.get())
        capacities["jumping_castle"] = int(cap_jumping_castle.get())

        return capacities
    
    # ---------- OBRAZOVKA4: Prices settings

    prices_settings_frame = tk.Frame(root, bg="black")
    prices_settings_frame.pack_forget()

    tk.Label(prices_settings_frame, text="Ceny", font=("Arial", 32, "bold"), bg="black", fg="yellow").grid(row=0, column=0, columnspan=7, pady=(40, 40))

    tk.Label(prices_settings_frame, text="Cena vstupenky na místě:", **label_style).grid(row=2, column=0, pady=10, sticky="w")
    tk.Label(prices_settings_frame, text=" Kč", **label_style).grid(row=2, column=2, pady=10, sticky="w")
    on_site_price = tk.Entry(prices_settings_frame, **entry_style)
    on_site_price.grid(row=2, column=1, pady=10)
    on_site_price.insert(0, "1500")

    tk.Label(prices_settings_frame, text="Cena vstupenky v předprodeji:  ", **label_style).grid(row=3, column=0, pady=10, sticky="w")
    tk.Label(prices_settings_frame, text=" Kč", **label_style).grid(row=3, column=2, pady=10, sticky="w")
    pre_sale_price = tk.Entry(prices_settings_frame, **entry_style)
    pre_sale_price.grid(row=3, column=1, pady=10)
    pre_sale_price.insert(0, "1300")

    tk.Label(prices_settings_frame, text="Cena stanového městečka:", **label_style).grid(row=4, column=0, pady=10, sticky="w")
    tk.Label(prices_settings_frame, text=" Kč", **label_style).grid(row=4, column=2, pady=10, sticky="w")
    camping_area_price = tk.Entry(prices_settings_frame, **entry_style)
    camping_area_price.grid(row=4, column=1, pady=10)
    camping_area_price.insert(0, "200")

    tk.Label(prices_settings_frame, text="Cena za kelímek na pití:", **label_style).grid(row=5, column=0, pady=10, sticky="w")
    tk.Label(prices_settings_frame, text=" Kč", **label_style).grid(row=5, column=2, pady=10, sticky="w")
    plastic_cup_price = tk.Entry(prices_settings_frame, **entry_style)
    plastic_cup_price.grid(row=5, column=1, pady=10)
    plastic_cup_price.insert(0, "50")

    tk.Label(prices_settings_frame, text="Cena za nabití telefonu:", **label_style).grid(row=6, column=0, pady=10, sticky="w")
    tk.Label(prices_settings_frame, text=" Kč", **label_style).grid(row=6, column=2, pady=10, sticky="w")
    charging_phone_price = tk.Entry(prices_settings_frame, **entry_style)
    charging_phone_price.grid(row=6, column=1, pady=10)
    charging_phone_price.insert(0, "80")

    tk.Label(prices_settings_frame, text="Cena sprch:", **label_style).grid(row=7, column=0, pady=10, sticky="w")
    tk.Label(prices_settings_frame, text=" Kč", **label_style).grid(row=7, column=2, pady=10, sticky="w")
    shower_price = tk.Entry(prices_settings_frame, **entry_style)
    shower_price.grid(row=7, column=1, pady=10)
    shower_price.insert(0, "50")

    tk.Label(prices_settings_frame, text="Cena za krabičku cigaret:", **label_style).grid(row=8, column=0, pady=10, sticky="w")
    tk.Label(prices_settings_frame, text=" Kč", **label_style).grid(row=8, column=2, pady=10, sticky="w")
    cigars_price = tk.Entry(prices_settings_frame, **entry_style)
    cigars_price.grid(row=8, column=1, pady=10)
    cigars_price.insert(0, "140")

    tk.Label(prices_settings_frame, text="Cena za vodní dýmku:", **label_style).grid(row=9, column=0, pady=10, sticky="w")
    tk.Label(prices_settings_frame, text=" Kč", **label_style).grid(row=9, column=2, pady=10, sticky="w")
    water_pipe_price = tk.Entry(prices_settings_frame, **entry_style)
    water_pipe_price.grid(row=9, column=1, pady=10)
    water_pipe_price.insert(0, "200")

    tk.Label(prices_settings_frame, text="Bungee jumping:", **label_style).grid(row=10, column=0, pady=10, sticky="w")
    tk.Label(prices_settings_frame, text=" Kč", **label_style).grid(row=10, column=2, pady=10, sticky="w")
    bungee_jumping_price = tk.Entry(prices_settings_frame, **entry_style)
    bungee_jumping_price.grid(row=10, column=1, pady=10)
    bungee_jumping_price.insert(0, "200")

    tk.Label(prices_settings_frame, text="Horská dráha:", **label_style).grid(row=11, column=0, pady=10, sticky="w")
    tk.Label(prices_settings_frame, text=" Kč", **label_style).grid(row=11, column=2, pady=10, sticky="w")
    rollercoaster_price = tk.Entry(prices_settings_frame, **entry_style)
    rollercoaster_price.grid(row=11, column=1, pady=10)
    rollercoaster_price.insert(0, "200")

    tk.Label(prices_settings_frame, text="Lavice:", **label_style).grid(row=12, column=0, pady=10, sticky="w")
    tk.Label(prices_settings_frame, text=" Kč", **label_style).grid(row=12, column=2, pady=10, sticky="w")
    bench_price = tk.Entry(prices_settings_frame, **entry_style)
    bench_price.grid(row=12, column=1, pady=10)
    bench_price.insert(0, "200")

    tk.Label(prices_settings_frame, text="Kladivo:", **label_style).grid(row=13, column=0, pady=10, sticky="w")
    tk.Label(prices_settings_frame, text=" Kč", **label_style).grid(row=13, column=2, pady=10, sticky="w")
    hammer_price = tk.Entry(prices_settings_frame, **entry_style)
    hammer_price.grid(row=13, column=1, pady=10)
    hammer_price.insert(0, "200")

    tk.Label(prices_settings_frame, text="Řetízkový kolotoč:", **label_style).grid(row=14, column=0, pady=10, sticky="w")
    tk.Label(prices_settings_frame, text=" Kč", **label_style).grid(row=14, column=2, pady=10, sticky="w")
    carousel_price = tk.Entry(prices_settings_frame, **entry_style)
    carousel_price.grid(row=14, column=1, pady=10)
    carousel_price.insert(0, "200")

    tk.Label(prices_settings_frame, text="Skákací hrad:", **label_style).grid(row=15, column=0, pady=10, sticky="w")
    tk.Label(prices_settings_frame, text=" Kč", **label_style).grid(row=15, column=2, pady=10, sticky="w")
    jumping_castle_price = tk.Entry(prices_settings_frame, **entry_style)
    jumping_castle_price.grid(row=15, column=1, pady=10)
    jumping_castle_price.insert(0, "200")

    bottom_settings_prices_frame = tk.Frame(prices_settings_frame, bg="black") 
    bottom_settings_prices_frame.grid(row=16, column=0, columnspan=6, pady=40) 
    back_button = blue_button(bottom_settings_prices_frame, "Zpět", go_back) 
    back_button.pack()

    def get_prices():
        prices = {}
        prices['pre_sale_price'] = int(pre_sale_price.get())
        prices['on_site_price'] = int(on_site_price.get())
        prices['camping_area_price'] = int(camping_area_price.get())
        prices['plastic_cup_price'] = int(plastic_cup_price.get())
        prices['charging_phone_price'] = int(plastic_cup_price.get())
        prices['shower_price'] = int(shower_price.get())
        prices['cigars_price'] = int(cigars_price.get())
        prices['water_pipe_price'] = int(water_pipe_price.get())
        prices['bungee_jumping'] = int(bungee_jumping_price.get())
        prices['rollercoaster'] = int(rollercoaster_price.get())
        prices['bench'] = int(bench_price.get())
        prices['hammer'] = int(hammer_price.get())
        prices['carousel'] = int(carousel_price.get())
        prices['jumping_castle'] = int(jumping_castle_price.get())
        
        return prices

    # ---------- OBRAZOVKA5: Merch settings

    bands_merch = source.bands_merch
    festival_merch = source.festival_merch

    merch_frame = tk.Frame(root, bg="black")
    merch_frame.pack_forget()

    tk.Label(merch_frame,text="Ceny v merch stánku", font=("Arial", 32, "bold"), bg="black", fg="yellow").grid(row=0, column=0, columnspan=6, pady=(40, 40))

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

        default_price = bands_merch[item].get("default_price", 0)
        default_quantity = bands_merch[item].get("default_quantity", 0)

        price_entry.insert(0, str(default_price))
        quantity_entry.insert(0, str(default_quantity))

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
        quantity_entry.grid(row=row_index, column=5, padx=(10,0))

        default_price = festival_merch[item].get("default_price", 0)
        default_quantity = festival_merch[item].get("default_quantity", 0)

        price_entry.insert(0, str(default_price))
        quantity_entry.insert(0, str(default_quantity))

        festival_entries[item] = {"price": price_entry, "quantity": quantity_entry}

        row_index += 1

        bottom_merch_frame = tk.Frame(merch_frame, bg="black")
        bottom_merch_frame.grid(row=50, column=0, columnspan=6, pady=40)

        back_button = blue_button(bottom_merch_frame, "Zpět", go_back)
        back_button.pack()

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

    tk.Label(times_settings_frame, text="Časy", font=("Arial", 32, "bold"), bg="black", fg="yellow").grid(row=0, column=0, columnspan=7, pady=(40, 40))

    tk.Label(times_settings_frame, text="Délka vystoupení kapely: ", **label_style).grid(row=2, column=0, pady=10, sticky="w")
    tk.Label(times_settings_frame, text=" min.", **label_style).grid(row=2, column=2, pady=10, sticky="w")
    band_time = tk.Entry(times_settings_frame, **entry_style2)
    band_time.grid(row=2, column=1, pady=10)
    band_time.insert(0, "60")

    tk.Label(times_settings_frame, text="Délka vystoupení headlinera: ", **label_style).grid(row=3, column=0, pady=10, sticky="w")
    tk.Label(times_settings_frame, text=" min.", **label_style).grid(row=3, column=2, pady=10, sticky="w")
    headliner_time = tk.Entry(times_settings_frame, **entry_style2)
    headliner_time.grid(row=3, column=1, pady=10)
    headliner_time.insert(0, "90")

    tk.Label(times_settings_frame, text="Délka trvání autogramiád: ", **label_style).grid(row=4, column=0, pady=10, sticky="w")
    tk.Label(times_settings_frame, text=" min.", **label_style).grid(row=4, column=2, pady=10, sticky="w")
    signing_time = tk.Entry(times_settings_frame, **entry_style2)
    signing_time.grid(row=4, column=1, pady=10)
    signing_time.insert(0, "30")

    tk.Label(times_settings_frame, text="Čas prvního koncertu dne: ", **label_style).grid(row=5, column=0, pady=10, sticky="w")
    first_show_starts = tk.Entry(times_settings_frame, **entry_style2)
    first_show_starts.grid(row=5, column=1, pady=10)
    first_show_starts.insert(0, "12:00")

    tk.Label(times_settings_frame, text="Konec posledního koncertu dne: ", **label_style).grid(row=6, column=0, pady=10, sticky="w")
    last_show_ends = tk.Entry(times_settings_frame, **entry_style2)
    last_show_ends.grid(row=6, column=1, pady=10)
    last_show_ends.insert(0, "23:00")

    bottom_settings_times_frame = tk.Frame(times_settings_frame, bg="black") 
    bottom_settings_times_frame.grid(row=7, column=0, columnspan=6, pady=40) 

    back_button = blue_button(bottom_settings_times_frame, "Zpět", go_back) 
    back_button.pack()


#-------------------------------------------------------------------------OBRAZOVKA7: Editor-----------------------------------------------------------

    editor_frame = tk.Frame(root, bg="black")

    title = ctk.CTkLabel(editor_frame, text="Editor festivalového areálu",font=("Arial", 40, "bold"),text_color="#ffffff")
    title.pack(pady=20)

    # Hlavní obsahový rám
    content_frame = tk.Frame(editor_frame, bg="black")
    content_frame.pack(fill="both", padx=50, pady=10)

    # Levý panel – Zóny
    frame_left = tk.Frame(content_frame, width=200, height=860, bg="white", bd=2, relief="ridge")
    frame_left.pack(side="left", fill="y", padx=0, pady=0)
    frame_left.pack_propagate(False)

    tk.Label(frame_left, text="Zóny", font=("Arial", 15, "bold"), bg="white", fg="black").pack(pady=5)

    # Pravý panel – Objekty 
    frame_right = tk.Frame(content_frame, width=200, height=860, bg="white", bd=2, relief="ridge")
    frame_right.pack(side="left", fill="y", padx=0, pady=0)
    frame_right.pack_propagate(False)

    tk.Label(frame_right, text="Objekty", font=("Arial", 15, "bold"), bg="white", fg="black").pack(pady=5)

    canvas = tk.Canvas(content_frame, bg="lightgray", width=1200, height=860, highlightthickness=0)

    canvas.pack(side="right", fill="both", expand=True)
    canvas.pack_propagate(False)

    def save():
        saving.save(zones_data)
        print("Rozložení úspěšně uloženo do festival_settings.json")

    def print_zones_data():
        global zones_data
        print(zones_data)
    
    def load():
        delete()
        data = loading.load(auto=False)
        draw_load(data)

    def load_default():
        data = loading.load(auto=True)
        draw_load(data)


    def delete():
        
        global zones_data, selected_zone_instance, selected_object, selected_line
        global connect_start_zone, is_dragging_object, is_dragging_zone

        canvas.delete("all")
        zones_data = copy.deepcopy(zones_data_default)

        selected_zone_instance = None
        selected_object = None
        selected_line = None
        connect_start_zone = None
        is_dragging_object = False
        is_dragging_zone = False

        print("Uživatel smazal canvas")

    #EDITOR BUTTONS
    editor_buttons_frame = tk.Frame(editor_frame, bg="black")
    editor_buttons_frame.pack(pady=20)

    back_button = blue_button(editor_buttons_frame, "Zpět", go_back)
    back_button.pack(side="left", padx=10)

    save_button = blue_button(editor_buttons_frame, "Uložit", save)
    save_button.pack(side="left", padx=10)

    save_button = blue_button(editor_buttons_frame, "Načíst", load)
    save_button.pack(side="left", padx=10)

    delete_button = red_button(editor_buttons_frame, "Smazat", delete)
    delete_button.pack(side="left", padx=10)

    print_button = blue_button(editor_buttons_frame, "Print Zones data", print_zones_data)
    print_button.pack(side="left", padx=10)

    start_button = green_button(editor_buttons_frame, "Start", start)
    start_button.pack(side="left", padx=10)


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

        pizza = ctk.CTkImage(light_image=Image.open("data/emojis/pizza.png"), size=(23, 23))
        ticket_booth = ctk.CTkImage(light_image=Image.open("data/emojis/dollar.png"), size=(23, 23))
        beer = ctk.CTkImage(light_image=Image.open("data/emojis/beer.png"), size=(23, 23))
        hamburger = ctk.CTkImage(light_image=Image.open("data/emojis/hamburger.png"), size=(23, 23))
        grill = ctk.CTkImage(light_image=Image.open("data/emojis/cut_of_meat.png"), size=(23, 23))
        gyros = ctk.CTkImage(light_image=Image.open("data/emojis/burrito.png"), size=(23, 23))
        langos = ctk.CTkImage(light_image=Image.open("data/emojis/flatbread.png"), size=(23, 23))
        fries = ctk.CTkImage(light_image=Image.open("data/emojis/fries.png"), size=(23, 23))
        sweet = ctk.CTkImage(light_image=Image.open("data/emojis/doughnut.png"), size=(23, 23))
        atm = ctk.CTkImage(light_image=Image.open("data/emojis/atm.png"), size=(23, 23))
        battery = ctk.CTkImage(light_image=Image.open("data/emojis/battery.png"), size=(23, 23))
        tables = ctk.CTkImage(light_image=Image.open("data/emojis/chair.png"), size=(23, 23))
        soft_drinks = ctk.CTkImage(light_image=Image.open("data/emojis/cup_with_straw.png"), size=(23, 23))
        wc = ctk.CTkImage(light_image=Image.open("data/emojis/restroom.png"), size=(23, 23))
        shower = ctk.CTkImage(light_image=Image.open("data/emojis/shower.png"), size=(23, 23))
        cigars = ctk.CTkImage(light_image=Image.open("data/emojis/smoking.png"), size=(23, 23))
        washing = ctk.CTkImage(light_image=Image.open("data/emojis/soap.png"), size=(23, 23))
        cocktails = ctk.CTkImage(light_image=Image.open("data/emojis/tropical_drink.png"), size=(23, 23))
        water_pipe = ctk.CTkImage(light_image=Image.open("data/emojis/bubbles.png"), size=(23, 23))
        stage = ctk.CTkImage(light_image=Image.open("data/emojis/guitar.png"), size=(23, 23))
        signing = ctk.CTkImage(light_image=Image.open("data/emojis/writing_hand.png"), size=(23, 23))
        merch = ctk.CTkImage(light_image=Image.open("data/emojis/shirt.png"), size=(23, 23))
        shot = ctk.CTkImage(light_image=Image.open("data/emojis/shot.png"), size=(23, 23))
        chill = ctk.CTkImage(light_image=Image.open("data/emojis/beach.png"), size=(23, 23))
        rollercoaster = ctk.CTkImage(light_image=Image.open("data/emojis/roller_coaster.png"), size=(23, 23))
        jumping_castle = ctk.CTkImage(light_image=Image.open("data/emojis/jumping_castle.png"), size=(23, 23))
        hammer = ctk.CTkImage(light_image=Image.open("data/emojis/hammer.png"), size=(23, 23))
        carousel = ctk.CTkImage(light_image=Image.open("data/emojis/carousel.png"), size=(23, 23))
        bungeejumping = ctk.CTkImage(light_image=Image.open("data/emojis/bungeejumping.png"), size=(23, 23))
        bench = ctk.CTkImage(light_image=Image.open("data/emojis/bench.png"), size=(23, 23))
        cup_return = ctk.CTkImage(light_image=Image.open("data/emojis/back.png"), size=(23, 23))
        tent = ctk.CTkImage(light_image=Image.open("data/emojis/tent.png"), size=(22, 22))
        door = ctk.CTkImage(light_image=Image.open("data/emojis/door.png"), size=(22, 22))

        object_buttons.clear()
        for obj in objects_for_zone.get(zone_name, []):

            match obj:

                case "Louka na stanování":
                    img = tent
                    text = "Louka na stanování"

                case "Chill stánek":
                    img = chill
                    text = "Chill stánek"

                case "Skákací hrad":
                    img = jumping_castle
                    text = "Skákací hrad"

                case "Horská dráha":
                    img = rollercoaster
                    text = "Horská dráha"

                case "Kladivo":
                    img = hammer
                    text = "Kladivo"
                case "Řetizkáč":
                    img = carousel
                    text = "Řetizkáč"

                case "Bungee-jumping":
                    img = bungeejumping
                    text = "Bungee Jumping"

                case "Lavice":
                    img = bench
                    text = "Lavice"

                case "Výkup kelímků":
                    img = cup_return
                    text = "Výkup kelímků"

                case "Pizza stánek":
                    img = pizza
                    text = "Pizza"

                case "Pokladna":
                    img = ticket_booth
                    text = "Pokladna"

                case "Burger stánek":
                    img = hamburger
                    text = "Burgery"

                case "Gyros stánek":
                    img = gyros
                    text = "Gyros"
                
                case "Grill stánek":
                    img = grill
                    text = "Grill"
                
                case "Bel hranolky stánek":
                    img = fries
                    text = "Belgické hranolky"

                case "Langoš stánek":
                    img = langos
                    text = "Langoše"

                case "Pivní stánek":
                    img = beer
                    text = "Pivo"

                case "Sladký stánek":
                    img = sweet
                    text = "Sladké"
                
                case "Bankomat":
                    img = atm    
                    text = "Bankomat"

                case "Dobíjecí stan":
                    img = battery
                    text = "Nabíjení telefonů"

                case "Stoly":
                    img = tables
                    text = "Stoly"

                case "Nealko stánek":
                    img = soft_drinks
                    text = "Nealko"

                case "Toitoiky":
                    img = wc
                    text = "Toitoiky"

                case "Umývárna":
                    img = washing
                    text = "Umývárna"

                case "Sprchy":
                    img = shower
                    text = "Sprchy"

                case "Cigaretový stánek":
                    img = cigars
                    text = "Cigarety"
                
                case "Stánek s míchanými drinky":
                    img = cocktails
                    text = "Míchané drinky"

                case "Stánek s vodníma dýmkama":
                    img = water_pipe
                    text = "Vodní dýmka"

                case "Podium":
                    img = stage
                    text = "Pódium"

                case "Stan na autogramiády":
                    img = signing
                    text = "Autogramiády"

                case "Merch stan":
                    img = merch
                    text = "Merch"
                case "Red Bull stánek":
                    img = shot
                    text = "RedBull"

                case "Vstup":
                    img = door
                    text = "Vstup"

                case _:
                    img = None
                    text = obj

        
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
        insts = zones_data[zone_type]["instances"]
        for inst in insts:
            # nejdřív zkontrola hlavní oblasti zóny
            if inst["left"] <= x <= inst["right"] and inst["top"] <= y <= inst["bottom"]:
                return inst
        
            # teď zkontroluju objekty v této zóně
            for obj in inst.get("objects", []):
                
                coords_list = []
                main_id = obj["canvas_ids"][1]  
                coords_list.append(canvas.coords(main_id))

                # extra objekty (stání u podia)
                for extra in obj.get("extra", []):
                    extra_id = extra["canvas_ids"][1]
                    coords_list.append(canvas.coords(extra_id))

                # projdem souřadnice
                for coords in coords_list:
                    left, top, right, bottom = coords[0], coords[1], coords[2], coords[3]
                    if left <= x <= right and top <= y <= bottom:
                        return inst

        return None

#-------------------------------------------------------------------------------EDITOR - SIMULATION MODE---------------------------------------------------------------------------------------------------

    left_simulation_container = left_simulation_container = tk.Frame(content_frame, bg="black")
    left_simulation_container.pack_forget()

    frame_up_simulation = tk.Frame(left_simulation_container, width=400, height=430, bg="white", bd=2, relief="ridge")
    frame_up_simulation.pack_propagate(False)
    frame_up_simulation.pack(fill="x")

    tk.Label(frame_up_simulation, text="Detaily o stánku: ", font=("Arial", 15, "bold"), bg="white", fg="black").pack(pady=5)
    
    
    frame_down_simulation = tk.Frame(left_simulation_container, width=400, height=430, bg="white", bd=2, relief="ridge")
    frame_down_simulation.pack_propagate(False)
    frame_down_simulation.pack(fill="x")

    tk.Label(frame_down_simulation, text="Aktuální výpisy:", font=("Arial", 15, "bold"), bg="white", fg="black").pack(pady=5)

    #SIMULATION BUTTONS

    simulation_buttons_frame = tk.Frame(editor_frame, bg="black")
    simulation_buttons_frame.pack_forget()

    # COUNTER ČÁST
    value = 1

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

    jump_label_text = ctk.CTkLabel(simulation_counter_frame, text="Posunout simulaci o čas",font=("Arial", 20, "bold"), width=50)
    jump_label_text.pack(side="top", pady=8)

    minus_button = blue_button_small(simulation_counter_frame, "-", decrease)
    minus_button.pack(side="left")

    jump_label = ctk.CTkLabel(simulation_counter_frame, text=str(value), font=("Arial", 20, "bold"), width=50)
    jump_label.pack(side="left")

    plus_button = blue_button_small(simulation_counter_frame, "+", increase)
    plus_button.pack(side="left")

    back_button = green_button_small(simulation_counter_frame, "▶", "next_step")
    back_button.pack(side="left", padx=10)


    # DO DALŠÍ UDÁLOSTI

    simulation_next_event_buttons_frame = tk.Frame(simulation_buttons_frame, bg="black")
    simulation_next_event_buttons_frame.pack(side="left", padx=30)

    next_event_label = ctk.CTkLabel(simulation_next_event_buttons_frame, text="Posunout simulaci do další události", font=("Arial", 20, "bold"), width=50)
    next_event_label.pack(side="top", pady=8)

    back_button = green_button_small(simulation_next_event_buttons_frame, "▶", "next_step")
    back_button.pack(anchor="center")

    stop_simulation_frame = tk.Frame(simulation_buttons_frame, bg="black")
    stop_simulation_frame.pack(side="left", padx=30)

    empty_label = ctk.CTkLabel(stop_simulation_frame, text=" ", font=("Arial", 20, "bold"))
    empty_label.pack(side="top", pady=8)

    stop_simulation_button = red_button_small(stop_simulation_frame, "Ukončit", stop_simulation)
    stop_simulation_button.pack(side="left", padx=30)

    #stop_simulation_button = red_button(simulation_buttons_frame, "Ukončit", stop_simulation)
    #stop_simulation_button.pack(side="left", padx=30)

#--------------------------------------------------------------------------------KÓDY EDITORU-------------------------------------------------------------
    
    
    entrance_id = 0

    # Funkce pro vkládání objektů
    def place_object(event):
        global current_object, current_zone, zones_data, current_mode
        nonlocal entrance_id

        if current_mode != "add":
            print("Zony a objekty lze přidávat pouze v režimu +")
            return


        if current_zone is None or current_object is None:
            print("chyba: není vybrána zóna nebo objekt")
            return
        
        
        x, y = event.x, event.y

        instance = find_zone_instance_for_point(current_zone, x, y)

        if current_object == "Vstup":
            # najdeme festivalový areál
            fest_zone = None
            for inst in zones_data["Festivalový areál"]["instances"]:
                fest_zone = inst
                break

            if fest_zone is None:
                print("Chyba: festivalový areál neexistuje.")
                return

            # vstup musí být na hraně festivalového areálu
            if not is_on_edge(fest_zone, x, y):
                print("Vstup musí být umístěn na hranu festivalového areálu.")
                return

            # vstup se ukládá do festivalové zóny
            instance = fest_zone

        elif instance is None:
            print("chyba: objekt musí být uvnitř existující zóny")
            return
        
        obj_data = create_object(instance, current_object, x, y)

        if current_object == "Vstup":
            entrance_id += 1
            obj_data["id"] = entrance_id
            

        instance.setdefault("objects", []).append(obj_data)

    def create_object(instance, current_object, x, y, x1=None, y1=None, x2=None, y2=None):
        foods = ["Pizza stánek", "Burger stánek", "Gyros stánek", "Grill stánek", "Bel hranolky stánek", "Langoš stánek", "Sladký stánek"]
        drinks = ["Nealko stánek", "Pivní stánek", "Red Bull stánek"]
        extra = []

        r = 13
        if x1 is not None and y1 is not None and x2 is not None and y2 is not None:
            coords_oval = (x1, y1, x2, y2)
            coords_toiky = (x1, y1, x2, y2)
            coords_camping = (x1, y1, x2, y2)
            coords_stage = (x1, y1, x2, y2)
            coords_stage_standing = (x1, y1, x2, y2)
        else:
            coords_oval = (x-r, y-r, x+r, y+r)
            coords_toiky = (x-50, y, x+50, y+50)
            coords_camping = (x-100, y, x+100, y+100)
            coords_stage = (x-80, y, x+80, y+50)
            coords_stage_standing = (x - 110, y + 55, x + 110, y + 200)

        text_id = canvas.create_text(x, y-20, text=current_object, fill="black", font=("Arial", 8, "bold"), anchor="center")

        if current_object in foods:
            x1, y1, x2, y2 = coords_oval
            obj_id = canvas.create_oval(*coords_oval, fill="green", outline="black")

        elif current_object in drinks:
            x1, y1, x2, y2 = coords_oval
            obj_id = canvas.create_oval(*coords_oval, fill="blue", outline="black")

        elif current_object == "Toitoiky":
            x1, y1, x2, y2 = coords_toiky
            obj_id = canvas.create_rectangle(*coords_toiky, fill="black")

        elif current_object == "Louka na stanování":
            x1, y1, x2, y2 = coords_camping
            obj_id = canvas.create_rectangle(*coords_camping, fill="black")

        elif current_object == "Podium":
            x1, y1, x2, y2 = coords_stage_standing

            # Podium
            obj_id = canvas.create_rectangle(*coords_stage, fill="black")
            stand_id = canvas.create_rectangle(*coords_stage_standing, fill="grey", outline="black")
    
            # Popis stání u podia
            
            stand_text_id = canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text="Stání u podia",fill="black", font=("Arial", 8, "bold"), anchor="center")
            
            extra.append({"object": "Stání u podia", "canvas_ids": [stand_text_id, stand_id]})
        
        else:
            obj_id = canvas.create_oval(*coords_oval, fill="gray", outline="black")

        return { "object": current_object, "x": x, "y": y, "x1": x1, "y1": y1, "x2": x2, "y2": y2, "canvas_ids": [text_id, obj_id], "extra": extra}   
    

    def on_click(event):
        """Začátek kreslení zóny (pokud není vybraný objekt)."""
        global drawing, last_x, last_y, zone_rect, zone_label, current_object, current_zone, current_mode, selected_zone_instance, selected_object, is_dragging_object, is_dragging_zone, connect_start_zone, selected_line


        print("\n[CLICK] at", event.x, event.y, "mode:", current_mode)

        if current_mode == "add":
            if current_zone is None:
                print("Není vybrána žádná zóna.")
                return

            if current_object is not None:
                # umisťování objektů
                place_object(event)
                return

            zone_info = zones_data[current_zone]
            if not zone_info["multiple"] and len(zone_info["instances"]) >= 1:
                print(f"Zóna '{current_zone}' může být pouze jedna — nelze přidat další.")
                return

            # začínáme kreslit
            drawing = True
            last_x, last_y = event.x, event.y

            if zone_rect is not None:
                canvas.delete(zone_rect)
                zone_rect = None
            if zone_label is not None:
                canvas.delete(zone_label)
                zone_label = None

        elif current_mode == "edit":
            # nejdřív hledáme objekt
            clicked_obj = None
            clicked_zone = None
            clicked_line = None

            for zone_type, zone_info in zones_data.items():
                for zone in zone_info["instances"]:
                    for line in zone.get("lines", []):
                        coords = canvas.coords(line["id"])
                        if not coords:
                            continue

                        x1, y1, x2, y2 = coords
                        # jednoduchá tolerance kliknutí
                        if is_near_line(event.x, event.y, x1, y1, x2, y2, tol=5):
                            clicked_line = line

                    if clicked_line:
                        break
                if clicked_line:
                    break

            if clicked_line:
                if selected_line:
                    canvas.itemconfig(selected_line["id"], width=2)

                selected_line = clicked_line
                canvas.itemconfig(clicked_line["id"], width=4)
                print("Vybrána čára")
                return

            for zone_type, zone_info in zones_data.items():
                for inst in zone_info["instances"]:
                    for obj in inst.get("objects", []):
                        geom_id = obj["canvas_ids"][1]
                        coords = canvas.coords(geom_id)
                        x1, y1, x2, y2 = coords
                        if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                            clicked_obj = obj
                            break
                    if clicked_obj: break
                if clicked_obj: break

            if clicked_obj:

                print("[CLICK] Objekt nalezen:", clicked_obj.get("object", "?"))

                last_x, last_y = event.x, event.y

                # odznačí případně starý výběr
                if selected_object and selected_object != clicked_obj:
                    canvas.itemconfig(selected_object["canvas_ids"][1], outline="black", width=1)
                    
                if selected_zone_instance:
                    canvas.itemconfig(selected_zone_instance["rect_id"], outline="blue", width=3)
                    selected_zone_instance = None

                # vždy nastaví nový výběr ikdyž je to ten samý objekt
                if selected_object and selected_object != clicked_obj:
                    canvas.itemconfig(selected_object["canvas_ids"][1], outline="black", width=1)

                selected_object = clicked_obj
                selected_zone_instance = None
                canvas.itemconfig(clicked_obj["canvas_ids"][1], outline="red", width=3)

                print(f"[SELECT]Označený objekt: {clicked_obj['object']}")

                
                is_dragging_object = True

                print("[SELECT] Dragging aktivován")

                # střed objektu pro konzistentní posun
                coords = canvas.coords(clicked_obj["canvas_ids"][1])
                cx = (coords[0] + coords[2]) / 2
                cy = (coords[1] + coords[3]) / 2
                clicked_obj["x"] = cx
                clicked_obj["y"] = cy

                return

            # pokud nenajdem objekt, hledáme zónu
            for zone_type, zone_info in zones_data.items():
                for inst in zone_info["instances"]:
                    left, top, right, bottom = inst["left"], inst["top"], inst["right"], inst["bottom"]
                    if left <= event.x <= right and top <= event.y <= bottom:
                        clicked_zone = inst
                        break
                if clicked_zone: break

            if clicked_zone:

                if selected_object:
                    canvas.itemconfig(selected_object["canvas_ids"][1], outline="black", width=1)
                    selected_object = None

                if selected_zone_instance and selected_zone_instance != clicked_zone:
                    canvas.itemconfig(selected_zone_instance["rect_id"], outline="blue", width=3)

                if selected_zone_instance != clicked_zone:
                    selected_zone_instance = clicked_zone
                    canvas.itemconfig(clicked_zone["rect_id"], outline="red", width=4)
                    print(f"Označená zóna: {clicked_zone['type']}")
                
                resize_info = get_resize_direction(clicked_zone, event.x, event.y)
                print("Resize info:", resize_info)

                if resize_info:

                    if selected_zone_instance["type"] == "Festivalový areál":
                        for obj in selected_zone_instance.get("objects", []):
                            if obj.get("object") == "Vstup":
                                return
                              
                    selected_zone_instance["resize_info"] = resize_info
                    is_dragging_zone = True
                    last_x, last_y = event.x, event.y                                                              
                    return

            # pokud se nenašel ani objekt ani zóna tak se odznačí vše
            if not clicked_obj and not clicked_zone and not clicked_line:
                if selected_object:
                    canvas.itemconfig(selected_object["canvas_ids"][1], outline="black", width=1)
                    selected_object = None
                if selected_zone_instance:
                    canvas.itemconfig(selected_zone_instance["rect_id"], outline="blue", width=3)
                    selected_zone_instance = None
                if selected_line:
                    canvas.itemconfig(selected_line["id"], width=2)  # reset tloušťky
                    selected_line = None
                print("Výběr zrušen")

        elif current_mode == "connect":
            
            handle_connect_click(event)

    def handle_connect_click(event):
        """Obslouží connect mód."""
        global connect_start_zone

        clicked_obj, obj_zone = find_clicked_object(event)

        # zjistíme, jestli jsme klikli na zónu
        clicked_zone = None
        for zone_type, zone_info in zones_data.items():
            for inst in zone_info["instances"]:
                if inst["left"] <= event.x <= inst["right"] and inst["top"] <= event.y <= inst["bottom"]:
                    clicked_zone = inst
                    break
            if clicked_zone:
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

        # nakonec reset
        connect_start_zone = None
        print("CONNECT DONE")


    def connect_entry_to_zone(vstup_obj, target_zone):
        """Vstup → zóna."""
        vstup_zone = None
        for zt, zi in zones_data.items():
            for inst in zi["instances"]:
                if vstup_obj in inst.get("objects", []):
                    vstup_zone = inst
                    break
            if vstup_zone:
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
            "other_zone": {"type": target_zone["type"], "entry": {"id": vstup_obj["id"], "x": x1, "y": y1}}
        })
        target_zone.setdefault("lines", []).append({
            "id": line_id,
            "other_zone": {"type": vstup_zone["type"], "entry": {"id": vstup_obj["id"], "x": x1, "y": y1}}
        })


    def connect_zone_to_entry(start_zone, vstup_obj):
        """Zóna → vstup."""
        vstup_zone = None
        for zt, zi in zones_data.items():
            for inst in zi["instances"]:
                if vstup_obj in inst.get("objects", []):
                    vstup_zone = inst
                    break
            if vstup_zone:
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
            "other_zone": {"type": vstup_zone["type"], "entry": {"id": vstup_obj["id"], "x": x2, "y": y2}}
        })
        vstup_zone.setdefault("lines", []).append({
            "id": line_id,
            "other_zone": {"type": start_zone["type"], "entry": {"id": vstup_obj["id"], "x": x2, "y": y2}}
        })


    def connect_zone_to_zone(z1, z2):
        """Zóna → zóna."""
        for line in z1.get("lines", []):
            if line["other_zone"]["type"] == z2["type"]:
                return

        x1, y1 = closest_point_on_zone(z1, z2)
        x2, y2 = closest_point_on_zone(z2, z1)
        line_id = canvas.create_line(x1, y1, x2, y2, fill="black", width=2)

        z1.setdefault("lines", []).append({"id": line_id, "other_zone": z2})
        z2.setdefault("lines", []).append({"id": line_id, "other_zone": z1})
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

    def on_drag(event):
        """Aktualizace při tažení myší – kreslení zóny nebo přesun objektu."""
        global drawing, last_x, last_y, zone_rect, zone_label, current_object, current_zone, selected_object, is_dragging_object, is_dragging_zone, current_mode

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
            for zone_type, zone_info in zones_data.items():
                for inst in zone_info["instances"]:
                    if selected_object in inst.get("objects", []):
                        parent_zone = inst
                        break
                if parent_zone:
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
                for zone_type, zone_info in zones_data.items():
                    other_zones.extend(zone_info["instances"])

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
        text_x = (left + right) / 2
        text_y = top - 12
        zone_label = canvas.create_text(text_x, text_y, text=current_zone or "", fill="black", font=("Arial", 12, "bold"), anchor="s")



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
    
            zones_data[current_zone]["instances"].append(zone_instance)

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
            for zone_type, zone_info in zones_data.items():
                for inst in zone_info["instances"]:
                    if "objects" in inst and selected_object in inst["objects"]:
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
        for zone_type, zone_info in zones_data.items():
            if zone in zone_info["instances"]:
                zone_info["instances"].remove(zone)
                break

    def delete_line(line_id):
        global zones_data

        # 1) Smazat z canvasu
        canvas.delete(line_id)

        # 2) Smazat ze všech zón
        for zone_type, zone_info in zones_data.items():
            for zone in zone_info["instances"]:
                zone["lines"] = [ln for ln in zone.get("lines", []) if ln["id"] != line_id]

                # 3) Smazat z objektů (hlavně Vstup)
                for obj in zone.get("objects", []):
                    if obj.get("object") == "Vstup":
                        obj["lines"] = [ln for ln in obj.get("lines", []) if ln["id"] != line_id]

                        # odemknout vstup, pokud už nemá žádné linky
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
                for zt, zi in zones_data.items():
                    for inst in zi["instances"]:
                        if inst["type"] == other["type"]:
                            other_zone = inst
                            break
                    if other_zone:
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

    
    def find_clicked_object(event):
        for zone_type, zone_info in zones_data.items():
            for inst in zone_info["instances"]:
                for obj in inst.get("objects", []):
                    x1, y1, x2, y2 = canvas.coords(obj["canvas_ids"][1])
                    if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                        return obj, inst
        return None, None


    def draw_load(data):
        global zones_data
        zones_data = data

        # 1) vykreslit zóny
        for zone_type, zone_info in zones_data.items():
            for zone_instance in zone_info["instances"]:
                draw_zone(zone_instance)

                # 2) vykreslit objekty ve zónách
                for obj in zone_instance.get("objects", []):
                    new_obj = create_object(zone_instance, obj["object"], obj["x"], obj["y"])
                    obj["canvas_ids"] = new_obj["canvas_ids"]
                    obj["extra"] = new_obj.get("extra", [])
                    if obj["object"] == "Vstup":
                        obj["locked"] = True

        print("Všechny zóny a objekty vykresleny.")

        all_lines = []

        for zone_type, zone_info in zones_data.items():
            for zona1 in zone_info["instances"]:
                for line in zona1.get("lines", []):

                    # najdeme cílovou zónu
                    target_name = line["other_zone"]["zone"]
                    zona2 = next(
                        (inst for zt, zi in zones_data.items() for inst in zi["instances"]
                        if inst.get("type") == target_name),
                        None
                    )

                    # najdeme vstup (pokud existuje)
                    vstup = None
                    if "entry" in line:
                        entry_id = line["entry"]["id"]
                        vstup = next(
                            (obj for obj in zona1["objects"]
                            if obj.get("object") == "Vstup" and obj.get("id") == entry_id),
                            None
                        )

                    # uložíme do seznamu
                    all_lines.append({
                        "zona1": zona1,
                        "zona2": zona2,
                        "vstup": vstup,
                        "line": line
                    })
        
        for zone_type, zone_info in zones_data.items():
            for inst in zone_info["instances"]:
                inst["lines"] = []
        
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
    
    return settings
                    