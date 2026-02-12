import tkinter as tk
from PIL import Image, ImageTk
from . import saving
from . import loading 
import os
import copy

# Stav aplikace
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
capacities = {}

zones_data = {
    "Spawn zóna": {"multiple": True, "instances": []},
    "Vstupní zóna": {"multiple": True, "instances": []},
    "Festivalový areál": {"multiple": False, "instances": []},
    "Stanové městečko": {"multiple": True, "instances": []},
    "Chill zóna": {"multiple": True, "instances": []},
    "Zábavní zóna": {"multiple": False, "instances": []}
}

zones_data_default = copy.deepcopy(zones_data)

def get_user_settings():
    settings = {}

    def start():
        settings['num_visitors'] = int(entry_visitors.get())
        settings['num_days'] = int(entry_days.get())
        settings['budget_for_bands'] = int(entry_budget.get())
        settings['num_bands'] = int(entry_num_bands.get())
        get_capacities()
        root.destroy()

    def exit_app():
        root.quit()
        root.destroy()

    def open_editor():
        main_frame.pack_forget()
        editor_frame.pack(fill="both", expand=True)

    def open_stalls_settings():
        main_frame.pack_forget()
        settings_frame.pack_forget()
        stall_settings_frame.place(relx=0.5, rely=0.5, anchor="center")

    def open_settings():
        main_frame.pack_forget()
        settings_frame.pack(fill="both", expand=True)

    def go_back():
        if stall_settings_frame.winfo_ismapped():
            get_capacities()
            stall_settings_frame.place_forget()
            settings_frame.pack(fill="both", expand=True)
        
        if settings_frame.winfo_ismapped():
            settings_frame.pack_forget()
            main_frame.pack(fill="both", expand=True)
        
        if editor_frame.winfo_ismapped():
            editor_frame.pack_forget()
            main_frame.pack(fill="both", expand=True)



    # ---------- HLAVNÍ OKNO ----------

    root = tk.Tk()
    root.title("Nastavení festivalu")
    root.attributes('-fullscreen', True)
    root.configure(bg='black')


    # ---------- OBRAZOVKA 1: Úvodní menu ----------

    main_frame = tk.Frame(root, bg='black')
    main_frame.pack(fill="both", expand=True)

    title_label = tk.Label(main_frame, text="Simulace hudebního festivalu", font=("Arial", 36, "bold"), bg="black", fg="yellow")
    title_label.pack(pady=30)


    here = os.path.dirname(os.path.dirname(__file__))
    file_path = os.path.join(here, "data", "simpy-logo.webp")

    image = Image.open(file_path)
    image = image.resize((300, 150))
    photo = ImageTk.PhotoImage(image)
    image_label = tk.Label(main_frame, image=photo, bg="black")
    image_label.image = photo
    image_label.pack(pady=20)

    label_style = {"bg": "black", "fg": "white", "font": ("Arial", 20)}
    entry_style = {"font": ("Arial", 18), "bg": "#222", "fg": "white", "insertbackground": "white", "width": 10}
    entry_style2 = {"font": ("Arial", 18), "bg": "#222", "fg": "white", "insertbackground": "white", "width": 5}

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

    tk.Label(frame, text="Počet vystupujících kapel:", **label_style).grid(row=3, column=0, pady=10, sticky="w")
    entry_num_bands = tk.Entry(frame, **entry_style)
    entry_num_bands.grid(row=3, column=1, pady=10)
    entry_num_bands.insert(0, "8")

    bottom_frame = tk.Frame(main_frame, bg='black')
    bottom_frame.pack(side="bottom", pady=30)

    editor_button = tk.Button(bottom_frame, text="Dále", command=open_editor, font=("Arial", 20), bg="blue", fg="white", padx=40, pady=15)
    editor_button.pack(side="left", padx=10)

    settings_button = tk.Button(bottom_frame, text="Nastavení", command=open_settings, font=("Arial", 20), bg="blue", fg="white", padx=40, pady=15)
    settings_button.pack(side="left", padx=10)

    exit_button = tk.Button(bottom_frame, text="Zavřít", command=exit_app, font=("Arial", 20), bg="red", fg="white", padx=40, pady=15)
    exit_button.pack(side="left", padx=10)

    # ---------- OBRAZOVKA2: Settings

    settings_frame = tk.Frame(root, bg="black")
    settings_frame.pack_forget()

    tk.Label(settings_frame, text="Nastavení", font=("Arial", 32,"bold"), bg="black", fg="yellow").pack(padx=20, pady=20)

    stall_settings_button = tk.Button(settings_frame, text="Kapacity objektů", command=open_stalls_settings, font=("Arial", 20), bg="blue", fg="white", padx=40, pady=15)
    stall_settings_button.pack() 

    settings_bottom_frame = tk.Frame(settings_frame, bg='black')
    settings_bottom_frame.pack(side="bottom", pady=30, fill="x")

    back_button = tk.Button(settings_bottom_frame, text="Zpět", command=go_back, font=("Arial", 20), bg="blue", fg="white", padx=40, pady=15)
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

    tk.Label(stall_settings_frame, text="Sprchy:", **label_style).grid(row=11, column=1, pady=5, sticky="w", padx=50)
    cap_showers = tk.Entry(stall_settings_frame, **entry_style2)
    cap_showers.grid(row=11, column=2, padx=20)
    cap_showers.insert(0, "5")

    tk.Label(stall_settings_frame, text="Stany ve stanovém městečku:", **label_style).grid(row=12, column=1, pady=5, sticky="w", padx=50)
    cap_tents = tk.Entry(stall_settings_frame, **entry_style2)
    cap_tents.grid(row=12, column=2, padx=20)
    cap_tents.insert(0, "500")

    tk.Label(stall_settings_frame, text="Stánek s cigaretama:", **label_style).grid(row=13, column=1, pady=5, sticky="w", padx=50)
    cap_cigars_tent = tk.Entry(stall_settings_frame, **entry_style2)
    cap_cigars_tent.grid(row=13, column=2, padx=20)
    cap_cigars_tent.insert(0, "1")

    tk.Label(stall_settings_frame, text="Stánek s vodníma dýmkama", **label_style).grid(row=14, column=1, pady=5, sticky="w", padx=50)
    cap_water_pipe_stall = tk.Entry(stall_settings_frame, **entry_style2)
    cap_water_pipe_stall.grid(row=14, column=2, padx=20)
    cap_water_pipe_stall.insert(0, "20")    

    tk.Label(stall_settings_frame, text="Chill stánek", **label_style).grid(row=15, column=1, pady=5, sticky="w", padx=50)
    cap_chill_stall = tk.Entry(stall_settings_frame, **entry_style2)
    cap_chill_stall.grid(row=15, column=2, padx=20)
    cap_chill_stall.insert(0, "20")  

    tk.Label(stall_settings_frame, text="Pokladna:", **label_style).grid(row=1, column=4, pady=5, sticky="w", padx=50)
    cap_ticket_booth = tk.Entry(stall_settings_frame, **entry_style2)
    cap_ticket_booth.grid(row=1, column=5, padx=20)
    cap_ticket_booth.insert(0, "2")
    
    tk.Label(stall_settings_frame, text="Toitoiky:", **label_style).grid(row=2, column=4, pady=5, sticky="w", padx=50)
    cap_toitoi = tk.Entry(stall_settings_frame, **entry_style2)
    cap_toitoi.grid(row=2, column=5, padx=20)
    cap_toitoi.insert(0, "20")

    tk.Label(stall_settings_frame, text="Umývárna:", **label_style).grid(row=3, column=4, pady=5, sticky="w", padx=50)
    cap_handwashing_station = tk.Entry(stall_settings_frame, **entry_style2)
    cap_handwashing_station.grid(row=3, column=5, padx=20)
    cap_handwashing_station.insert(0, "20")

    tk.Label(stall_settings_frame, text="Stoly:", **label_style).grid(row=4, column=4, pady=5, sticky="w", padx=50)
    cap_tables = tk.Entry(stall_settings_frame, **entry_style2)
    cap_tables.grid(row=4, column=5, padx=20)
    cap_tables.insert(0, "20")

    tk.Label(stall_settings_frame, text="Plocha na stání u pódia:", **label_style).grid(row=5, column=4, pady=5, sticky="w", padx=50)
    cap_standing = tk.Entry(stall_settings_frame, **entry_style2)
    cap_standing.grid(row=5, column=5, padx=20)
    cap_standing.insert(0, "1000")

    tk.Label(stall_settings_frame, text="Merch stan:", **label_style).grid(row=6, column=4, pady=5, sticky="w", padx=50)
    cap_merch_stall = tk.Entry(stall_settings_frame, **entry_style2)
    cap_merch_stall.grid(row=6, column=5, padx=20)
    cap_merch_stall.insert(0, "3")

    tk.Label(stall_settings_frame, text="Fronta na autogramiády", **label_style).grid(row=7, column=4, pady=5, sticky="w", padx=50)
    cap_signing_stall = tk.Entry(stall_settings_frame, **entry_style2)
    cap_signing_stall.grid(row=7, column=5, padx=20)
    cap_signing_stall.insert(0, "500")

    tk.Label(stall_settings_frame, text="Dobíjecí stan:", **label_style).grid(row=8, column=4, pady=5, sticky="w", padx=50)
    cap_charging_stall = tk.Entry(stall_settings_frame, **entry_style2)
    cap_charging_stall.grid(row=8, column=5, padx=20)
    cap_charging_stall.insert(0, "2")

    tk.Label(stall_settings_frame, text="Dobíjecí stan - max počet telefonů:", **label_style).grid(row=9, column=4, pady=5, sticky="w", padx=50)
    cap_charging_stall_mobile = tk.Entry(stall_settings_frame, **entry_style2)
    cap_charging_stall_mobile.grid(row=9, column=5, padx=20)
    cap_charging_stall_mobile.insert(0, "20")

    tk.Label(stall_settings_frame, text="Lidí na Bungee-jumping:", **label_style).grid(row=10, column=4, pady=5, sticky="w", padx=50)
    cap_bungee_jumping = tk.Entry(stall_settings_frame, **entry_style2)
    cap_bungee_jumping.grid(row=10, column=5, padx=20)
    cap_bungee_jumping.insert(0, "1")

    tk.Label(stall_settings_frame, text="Lidí horské dráze:", **label_style).grid(row=11, column=4, pady=5, sticky="w", padx=50)
    cap_roallercoaster = tk.Entry(stall_settings_frame, **entry_style2)
    cap_roallercoaster.grid(row=11, column=5, padx=20)
    cap_roallercoaster.insert(0, "24")

    tk.Label(stall_settings_frame, text="Lidí na lavici:", **label_style).grid(row=12, column=4, pady=5, sticky="w", padx=50)
    cap_bench_attraction = tk.Entry(stall_settings_frame, **entry_style2)
    cap_bench_attraction.grid(row=12, column=5, padx=20)
    cap_bench_attraction.insert(0, "20")

    tk.Label(stall_settings_frame, text="Lidí na kladivu:", **label_style).grid(row=13, column=4, pady=5, sticky="w", padx=50)
    cap_hammer_attraction = tk.Entry(stall_settings_frame, **entry_style2)
    cap_hammer_attraction.grid(row=13, column=5, padx=20)
    cap_hammer_attraction.insert(0, "32")

    tk.Label(stall_settings_frame, text="Počet turniketů u vstupu:", **label_style).grid(row=14, column=4, pady=5, sticky="w", padx=50)
    num_entrance_gate = tk.Entry(stall_settings_frame, **entry_style2)
    num_entrance_gate.grid(row=14, column=5, padx=20)
    num_entrance_gate.insert(0, "4")


    bottom_settings_stalls_frame = tk.Frame(stall_settings_frame, bg="black") 
    bottom_settings_stalls_frame.grid(row=20, column=0, columnspan=6, pady=40) 
    back_button = tk.Button(bottom_settings_stalls_frame, text="Zpět", command=go_back, font=("Arial", 20), bg="blue", fg="white", width=10) 
    back_button.pack()

    def get_capacities():
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
        capacities["sigining_stall"] = int(cap_signing_stall.get())
        capacities["charging_stall"] = int(cap_charging_stall.get())
        capacities["charging_stall_mobile"] = int(cap_charging_stall_mobile.get())
        capacities["showers"] = int(cap_showers.get())
        capacities["tents"] = int(cap_tents.get())
        capacities["cigars_tent"] = int(cap_cigars_tent.get())
        capacities["water_pipe_stall"] = int(cap_water_pipe_stall.get())
        capacities["chill_stall"] = int(cap_charging_stall.get())
        capacities["bungee_jumping"] = int(cap_bungee_jumping.get())
        capacities["roallercoaster"] = int(cap_roallercoaster.get())
        capacities["bench_attraction"] = int(cap_bench_attraction.get())
        capacities["hammer_attraction"] = int(cap_hammer_attraction.get())
        capacities["nonalcohol_stall"] = int(cap_nonalcohol_stall.get())
        capacities["beer_stall"] = int(cap_beer_stall.get())
        capacities["redbull_stall"] = int(cap_redbull_stall.get())
        capacities["atm"] = 1


    # ---------- OBRAZOVKA5: Editor ----------

    editor_frame = tk.Frame(root, bg="black")

    tk.Label(editor_frame, text="Editor festivalového areálu", font=("Arial", 30, "bold"), bg="black", fg="yellow").pack(pady=20)
   
    content_frame = tk.Frame(editor_frame, bg="black")
    content_frame.pack(fill="both", padx=50, pady=20)

    # Levý sloupec
    frame_left = tk.Frame(content_frame, width=200, height=800, bg="white")
    frame_left.pack(side="left", fill="y", padx=(0,20), pady=5)
    frame_left.pack_propagate(False)
    tk.Label(frame_left, text="Zóny", font=("Arial", 25, "bold"), bg="white", fg="black").pack(pady=10)

    # Canvas uprostřed
    canvas = tk.Canvas(content_frame, bg="lightgray", width=1200, height=800)
    canvas.pack(side="left", fill="both", expand=True)
    canvas.pack_propagate(False)

    def save():
        saving.save(zones_data)
        print("Rozložení úspěšně uloženo do festival_settings.json")

    def print_zones_data():
        global zones_data
        print(zones_data)
    
    def load():
        delete()
        data = loading.load()
        draw_load(data)

    def delete():
        global zones_data

        canvas.delete("all")
        zones_data = copy.deepcopy(zones_data_default)
        print("Uživatel smazal canvas")

    # Pravý sloupec
    frame_right = tk.Frame(content_frame, width=200, height=800, bg="white")
    frame_right.pack(side="left", fill="y", padx=(20,0), pady=5)
    frame_right.pack_propagate(False)
    tk.Label(frame_right, text="Objekty", font=("Arial", 25, "bold"), bg="white", fg="black").pack(pady=10)

    buttons_frame = tk.Frame(editor_frame, bg="black")
    buttons_frame.pack(pady=20)

    back_button = tk.Button(buttons_frame, text="Zpět", command=go_back, font=("Arial", 20), bg="blue", fg="white", padx=20, pady=10, width=10, height=1)
    back_button.pack(side="left", padx=10)

    save_button = tk.Button(buttons_frame, text="Uložit", command=save, font=("Arial", 20), bg="blue", fg="white", padx=20, pady=10, width=10, height=1)
    save_button.pack(side="left", padx=10)

    save_button = tk.Button(buttons_frame, text="Načíst", command=load, font=("Arial", 20), bg="blue", fg="white", padx=20, pady=10, width=10, height=1)
    save_button.pack(side="left", padx=10)

    delete_button = tk.Button(buttons_frame, text="Smazat", command=delete, font=("Arial", 20), bg="blue", fg="white", padx=20, pady=10, width=10, height=1)
    delete_button.pack(side="left", padx=10)

    print_button = tk.Button(buttons_frame, text="Print Zones data", command=print_zones_data, font=("Arial", 20), bg="blue", fg="white", padx=20, pady=10, width=10, height=1)
    print_button.pack(side="left", padx=10)

    start_button = tk.Button(buttons_frame, text="Start", command=start, font=("Arial", 20), bg="green", fg="white", padx=20, pady=10, width=10, height=1)
    start_button.pack(side="left", padx=10)

    # Výčet objektů podle zóny
    objects_for_zone = {
        "Spawn bod": [],
        "Vstupní zóna": ["Pokladna", "Pizza stánek", "Burger stánek", "Gyros stánek", "Grill stánek", "Bel hranolky stánek", "Langoš stánek", "Sladký stánek", "Nealko stánek", "Pivní stánek", "Red Bull stánek", "Toitoiky", "Umývárna", "Stoly", "Bankomat"],
        "Festivalový areál": ["Podium", "Pizza stánek", "Burger stánek", "Gyros stánek", "Grill stánek", "Bel hranolky stánek", "Langoš stánek", "Sladký stánek", "Nealko stánek", "Pivní stánek", "Red Bull stánek", "Toitoiky","Umývárna", "Stoly", "Bankomat", "Merch stan", "Stan na autogramiády", "Dobíjecí stan"],
        "Stanové městečko": ["Nealko stánek", "Pivní stánek", "Red Bull stánek", "Toitoiky", "Sprchy", "Umývárna", "Dobíjecí stan", "Louka na stanování"],
        "Chill zóna": ["Stánek s vodníma dýmkama", "Cigaretový stánek", "Chill stánek", "Nealko stánek", "Pivní stánek", "Red Bull stánek", "Toitoiky", "Umývárna", "Dobíjecí stan"],
        "Zábavní zóna": ["Bungee-jumping", "Horská dráha", "Lavice", "Kladivo", "Nealko stánek", "Pivní stánek","Bankomat"]
    }

    # Funkce pro výběr objektu
    def select_object(obj_name):

        global current_object, object_buttons
        if current_object == obj_name:
            current_object = None

            for btn in object_buttons.values():
                btn.config(bg="SystemButtonFace", fg="black")

            print(f"Objekt {obj_name} odvybrán")
            return

        current_object = obj_name
        print(f"Vybrán objekt: {current_object}")

        for name, btn in object_buttons.items():
            btn.config(bg="SystemButtonFace", fg="black")

        if obj_name in object_buttons:
            object_buttons[obj_name].config(bg="lightblue", fg="black")

    # Funkce pro výběr zóny (typ)
    def select_zone(zone_name):

        global current_zone, object_buttons, current_object
        current_zone = zone_name
        print(f"Vybrána zóna: {current_zone}")

        current_object = None
        for name, btn in zone_buttons.items():
            btn.config(bg="SystemButtonFace", fg="black")

        zone_buttons[zone_name].config(bg="yellow", fg="black")

        # Vyčistit pravý panel a naplnit objekty pro tento typ zóny
        for widget in frame_right.winfo_children():
            widget.destroy()

        tk.Label(frame_right, text="Objekty", font=("Arial", 25, "bold"), bg="white", fg="black").pack(pady=10)

        object_buttons.clear()
        for obj in objects_for_zone.get(zone_name, []):
            btn = tk.Button(frame_right, text=obj, font=("Arial", 8), height=1, width=25, command=lambda o=obj: select_object(o))
            btn.pack(pady=5)
            object_buttons[obj] = btn

    # Vytvoření tlačítek pro zóny
    for zone_name in zones_data.keys():
        btn = tk.Button(frame_left, text=zone_name, font=("Arial", 13), width=15, command=lambda z=zone_name: select_zone(z))
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
            btn.config(bg="white", fg="black")
        # Zvýraznit vybraný
        mode_buttons[mode_name].config(bg="lightblue", fg="black")

    # Tlačítka pro režimy
    mode_buttons = {}
    mode_icons = {"add": "➕", "edit": "➤", "connect": "🔗"}
    mode_labels_text = {"add": "Přidat", "edit": "Editovat", "connect": "Spojit"}

    for i, (mode_name, symbol) in enumerate(mode_icons.items()):
        # vytvoříme rámec pro label + tlačítko
        btn_frame = tk.Frame(modes_frame)
        btn_frame.pack(side="left", padx=5)

        # label nad tlačítkem
        lbl = tk.Label(btn_frame, text=mode_labels_text.get(mode_name, ""), font=("Arial", 10))
        lbl.pack()

        # tlačítko
        btn = tk.Button(btn_frame, text=symbol, font=("Arial", 14, "bold"), width=3, height=2, command=lambda m=mode_name: select_mode(m))
        btn.pack()
        mode_buttons[mode_name] = btn
    
    select_mode("add")

    # Pomocná funkce: najde instanci zóny, do které patří bod x,y
    def find_zone_instance_for_point(zone_type, x, y):
        insts = zones_data[zone_type]["instances"]
        for inst in insts:
            # nejdřív zkontrolujeme hlavní oblast zóny
            if inst["left"] <= x <= inst["right"] and inst["top"] <= y <= inst["bottom"]:
                return inst
        
            # teď zkontrolujeme objekty v této zóně
            for obj in inst.get("objects", []):
                # hlavní geometrie objektu
                coords_list = []
                main_id = obj["canvas_ids"][1]  # geometrie objektu
                coords_list.append(canvas.coords(main_id))

                # extra objekty (např. stání u podia)
                for extra in obj.get("extra", []):
                    extra_id = extra["canvas_ids"][1]
                    coords_list.append(canvas.coords(extra_id))

                # projdeme všechny souřadnice
                for coords in coords_list:
                    left, top, right, bottom = coords[0], coords[1], coords[2], coords[3]
                    if left <= x <= right and top <= y <= bottom:
                        return inst

        return None

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

        if instance is None:
            print("chyba: objekt musí být uvnitř existující zóny")
            return

        obj_data = create_object(instance, current_object, x, y)
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
                        if abs(event.x - (x1 + x2) / 2) < 10 and abs(event.y - (y1 + y2) / 2) < 10:
                            clicked_line = line
                            break
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

                if clicked_obj["object"] == "vstup":
                    return

                print("[CLICK] Objekt nalezen:", clicked_obj.get("object", "?"))

                last_x, last_y = event.x, event.y

                # odznačíme případně starý výběr
                if selected_object and selected_object != clicked_obj:
                    canvas.itemconfig(selected_object["canvas_ids"][1], outline="black", width=1)
                    
                if selected_zone_instance:
                    canvas.itemconfig(selected_zone_instance["rect_id"], outline="blue", width=3)
                    selected_zone_instance = None

                # vždy nastavíme nový výběr (i když je to ten samý objekt)
                if selected_object and selected_object != clicked_obj:
                    canvas.itemconfig(selected_object["canvas_ids"][1], outline="black", width=1)

                selected_object = clicked_obj
                selected_zone_instance = None
                canvas.itemconfig(clicked_obj["canvas_ids"][1], outline="red", width=3)

                print(f"[SELECT]Označený objekt: {clicked_obj['object']}")

                if clicked_obj["object"] != "vstup":
                    is_dragging_object = True

                print("[SELECT] Dragging aktivován")

                # uložíme střed objektu pro konzistentní posun
                coords = canvas.coords(clicked_obj["canvas_ids"][1])
                cx = (coords[0] + coords[2]) / 2
                cy = (coords[1] + coords[3]) / 2
                clicked_obj["x"] = cx
                clicked_obj["y"] = cy

                return

            # pokud nenajdeme objekt, hledáme zónu
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
                            if obj.get("object") == "vstup":
                                return
                              
                    selected_zone_instance["resize_info"] = resize_info
                    is_dragging_zone = True
                    last_x, last_y = event.x, event.y                                                              
                    return

            # pokud jsme nenašli ani objekt ani zónu → odznačíme vše
            if not clicked_obj and not clicked_zone:
                if selected_object:
                    canvas.itemconfig(selected_object["canvas_ids"][1], outline="black", width=1)
                    selected_object = None
                if selected_zone_instance:
                    canvas.itemconfig(selected_zone_instance["rect_id"], outline="blue", width=3)
                    selected_zone_instance = None
                print("Výběr zrušen")

        elif current_mode == "connect":
            clicked_zone = None
            # najdeme zónu pod kliknutím
            for zone_type, zone_info in zones_data.items():
                for inst in zone_info["instances"]:
                    left, top, right, bottom = inst["left"], inst["top"], inst["right"], inst["bottom"]
                    if left <= event.x <= right and top <= event.y <= bottom:
                        clicked_zone = inst
                        break
                if clicked_zone: break

            if clicked_zone:
                if connect_start_zone is None:
                    # první zóna kliknuta
                    connect_start_zone = clicked_zone
                    canvas.itemconfig(clicked_zone["rect_id"], outline="green", width=4)
                    print(f"Connect start: {clicked_zone['type']}")
                else:
                    # druhá zóna kliknuta → nakreslíme čáru
                    z1 = connect_start_zone
                    z2 = clicked_zone

                    # nejbližší hrany (x, y) z1 → z2
                    x1, y1 = closest_point_on_zone(z1, z2)
                    x2, y2 = closest_point_on_zone(z2, z1)

                    for line in z1["lines"]:
                        if line["other_zone"] == z2:
                            return 

                    line_id = canvas.create_line(x1, y1, x2, y2, fill="black", width=2)
                                        
                    # uložíme čáru do obou zón
                    z1["lines"].append({"id": line_id, "other_zone": z2})
                    z2["lines"].append({"id": line_id, "other_zone": z1})

                    # reset
                    canvas.itemconfig(connect_start_zone["rect_id"], outline="blue", width=3)
                    connect_start_zone = None
                    print(f"Connect vytvořen mezi {z1['type']} a {z2['type']}")

                    if z1["type"] == "Festivalový areál":
                        objects = z1["objects"]
                        objects.append(create_object(z1, "vstup", x1, y1))
                    
                    if z2["type"] == "Festivalový areál":
                        objects = z2["objects"]
                        objects.append(create_object(z2, "vstup", x2, y2))
            return

        else:
            print("Objekty a zony lze přidat pouze v režimu +")
            return

        

    def on_drag(event):
        """Aktualizace při tažení myší – kreslení zóny nebo přesun objektu."""
        global drawing, last_x, last_y, zone_rect, zone_label, current_object, current_zone, selected_object, is_dragging_object, is_dragging_zone, current_mode

        print("[DRAG EVENT] at", event.x, event.y)
        # pokud nemáme startovní souřadnice, nic neděláme
        if last_x is None or last_y is None:
            print("nemáme startovací souřadnice")
            return

        dx = event.x - last_x
        dy = event.y - last_y

        # pokud je vybraný objekt, posouváme ho
        if selected_object and current_mode == "edit" and is_dragging_object:
            
             # zjistíme zónu, ve které je objekt
            parent_zone = None

            for zone_type, zone_info in zones_data.items():
                for inst in zone_info["instances"]:
                    if selected_object in inst.get("objects", []):
                        parent_zone = inst
                        break
                if parent_zone:
                    break

            if parent_zone:
                # souřadnice zóny
                zone_left = parent_zone["left"]
                zone_top = parent_zone["top"]
                zone_right = parent_zone["right"]
                zone_bottom = parent_zone["bottom"]

                # bbox objektu
                obj_bbox = canvas.bbox(selected_object["canvas_ids"][1])  # [x1, y1, x2, y2]
                obj_left, obj_top, obj_right, obj_bottom = obj_bbox

                # omezíme dx, dy, aby objekt nevyskočil z hranic zóny
                if obj_left + dx < zone_left:
                    dx = zone_left - obj_left
                if obj_right + dx > zone_right:
                    dx = zone_right - obj_right
                if obj_top + dy < zone_top:
                    dy = zone_top - obj_top
                if obj_bottom + dy > zone_bottom:
                    dy = zone_bottom - obj_bottom


            print("[DRAG] Tahám objekt:", selected_object.get("object"))
            print("    dx =", dx, "dy =", dy)

            for cid in selected_object.get("canvas_ids", []):
                canvas.move(cid, dx, dy)

            # posuneme i případné extra prvky (např. podium.extra)
            for extra in selected_object.get("extra", []):
                for cid in extra.get("canvas_ids", []):
                    canvas.move(cid, dx, dy)

            # aktualizujeme uložené souřadnice (střed)
            if "x" in selected_object and "y" in selected_object:
                selected_object["x"] += dx
                selected_object["y"] += dy
            else:
                geom = canvas.coords(selected_object["canvas_ids"][1])
                selected_object["x"] = (geom[0] + geom[2]) / 2
                selected_object["y"] = (geom[1] + geom[3]) / 2

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

            # smaž dočasné objekty
            canvas.delete(zone_rect)
            if zone_label:
                canvas.delete(zone_label)

        zone_rect = None
        zone_label = None



    def draw_zone(zone_instance):
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
    


    def delete_selected(event=None):
        global selected_zone_instance, selected_object, selected_line

        def delete_entry_from_festival(festival_zone):
            """Smaže objekt vstup v zóně festivalového areálu."""
            for obj in festival_zone.get("objects", []):
                if obj.get("object") == "vstup":
                    for cid in obj.get("canvas_ids", []):
                        canvas.delete(cid)
                    festival_zone["objects"].remove(obj)
                    print("Vstup smazán z festivalového areálu")
                    break

        if selected_object:
            if selected_object["object"] == "vstup":
                return 
            # smažeme z canvasu
            extra = selected_object.get("extra", [])
            for e in extra:
                for cid in e.get("canvas_ids", []):
                    canvas.delete(cid)
            for cid in selected_object.get("canvas_ids", []):
                canvas.delete(cid)
            # odstraníme z instance
            for zone_type, zone_info in zones_data.items():
                for inst in zone_info["instances"]:
                    if "objects" in inst and selected_object in inst["objects"]:
                        inst["objects"].remove(selected_object)
            selected_object = None
            print("Objekt smazán")
            return

        if selected_line:
            canvas.delete(selected_line["id"])

            for zone_type, zone_info in zones_data.items():
                for zone in zone_info["instances"]:
                    if selected_line in zone.get("lines", []):
                        zone["lines"].remove(selected_line)
                        # pokud je druhá zóna festivalový areál, smažeme vstup
                        other_zone = selected_line.get("other_zone")
                        if other_zone and other_zone.get("type") == "Festivalový areál":
                            delete_entry_from_festival(other_zone)

            selected_line = None
            print("Propojení smazáno")
            return

        if selected_zone_instance:
            # smažeme všechny canvas objekty spojené se zónou
            for cid in selected_zone_instance.get("canvas_ids", []):
                canvas.delete(cid)
            for obj in selected_zone_instance.get("objects", []):
                for cid in obj.get("canvas_ids", []):
                    canvas.delete(cid)
            for line in selected_zone_instance.get("lines", []):
                canvas.delete(line["id"])
                other_zone = line["other_zone"]
                if other_zone and "lines" in other_zone:
                    other_zone["lines"] = [l for l in other_zone["lines"] if l["id"] != line["id"]]
                    # pokud druhá zóna festivalový areál, smažeme vstup
                    if other_zone.get("type") == "Festivalový areál":
                        delete_entry_from_festival(other_zone)

            # odstraníme z dat
            zone_type = selected_zone_instance["type"]
            zones_data[zone_type]["instances"].remove(selected_zone_instance)
            selected_zone_instance = None
            print("Zóna smazána")

    RESIZE_TOLERANCE = 20 

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

        # pokud žádná hrana, vrátíme None → znamená přesouvání
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
            # zóna = zone
            x1, y1 = closest_point_on_zone(zone, other)
            x2, y2 = closest_point_on_zone(other, zone)
            canvas.coords(line["id"], x1, y1, x2, y2)
    


    def zone_overlaps(zone, other_zones):
        """Vrátí True, pokud zóna překrývá některou z ostatních zón."""
        for other in other_zones:
            if other == zone:
                continue
            
            if (zone["left"] < other["right"] and zone["right"] > other["left"] and zone["top"] < other["bottom"] and zone["bottom"] > other["top"]):
                return True
        return False

    def relink_zone_lines():
        global zones_data

        for zone_type, zone_info in zones_data.items():
            for zone in zone_info["instances"]:
                for line in zone.get("lines", []):
                    other_name = line.get("other_zone")

                    # už je relinknuté
                    if isinstance(other_name, dict):
                        continue

                    target = find_zone_instance_by_type(other_name)
                    line["other_zone"] = target

    def find_zone_instance_by_type(zone_type):
        for zt, zi in zones_data.items():
            if zt == zone_type:
                return zi["instances"][0] if zi["instances"] else None
        return None

    def draw_load(data):
        global zones_data
        zones_data = data
        
        for zone_type, zone_info in data.items():
            for zone_instance in zone_info["instances"]:
                draw_zone(zone_instance) 

                objects = zone_instance.get("objects")
                for obj in objects:
                    new_obj = create_object(zone_instance, obj["object"], obj["x"], obj["y"])
                    obj["canvas_ids"] = new_obj["canvas_ids"]
                    obj["extra"] = new_obj.get("extra", [])

        print("Všechny zóny a objekty vykresleny.")

        relink_zone_lines()

        for zone_type, zone_info in zones_data.items():
            for zone in zone_info["instances"]:
                for line in zone.get("lines", []):
                    other = line["other_zone"]
                    x1, y1 = closest_point_on_zone(zone, other)
                    x2, y2 = closest_point_on_zone(other, zone)

                    line_id = canvas.create_line(x1, y1, x2, y2, fill="black", width=2)
                    line["id"] = line_id


    canvas.bind("<Button-1>", on_click)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)
    root.bind("<Delete>", delete_selected)

    root.mainloop()
    return settings, capacities
            
                    