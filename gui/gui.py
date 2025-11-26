import tkinter as tk
from PIL import Image, ImageTk
from . import saving 
import os

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
is_dragging_object = False
is_dragging_zone = False
connect_start_zone = None

zones_data = {
    "Spawn bod": {"multiple": True, "instances": []},
    "Vstupní zóna": {"multiple": True, "instances": []},
    "Festivalový areál": {"multiple": False, "instances": []},
    "Stanové městečko": {"multiple": True, "instances": []},
    "Chill zóna": {"multiple": True, "instances": []},
    "Zábavní zóna": {"multiple": False, "instances": []}
}

def get_user_settings():
    settings = {}

    def start():
        settings['num_visitors'] = int(entry_visitors.get())
        settings['num_days'] = int(entry_days.get())
        settings['budget_for_bands'] = int(entry_budget.get())
        settings['num_bands'] = int(entry_num_bands.get())
        root.destroy()

    def exit_app():
        root.quit()
        root.destroy()

    def open_editor():
        main_frame.pack_forget()
        editor_frame.pack(fill="both", expand=True)

    def go_back():
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

    title_label = tk.Label(main_frame, text="Simulace hudebního festivalu",
                           font=("Arial", 36, "bold"), bg="black", fg="yellow")
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

    start_button = tk.Button(bottom_frame, text="Start", command=start, font=("Arial", 20), bg="green", fg="white", padx=40, pady=15)
    start_button.pack(side="left", padx=10)

    editor_button = tk.Button(bottom_frame, text="Dále", command=open_editor, font=("Arial", 20), bg="blue", fg="white", padx=40, pady=15)
    editor_button.pack(side="left", padx=10)

    exit_button = tk.Button(bottom_frame, text="Zavřít", command=exit_app, font=("Arial", 20), bg="red", fg="white", padx=40, pady=15)
    exit_button.pack(side="left", padx=10)

    # ---------- OBRAZOVKA 2: Editor ----------
    
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

    print_button = tk.Button(buttons_frame, text="Print Zones data", command=print_zones_data, font=("Arial", 20), bg="blue", fg="white", padx=20, pady=10, width=10, height=1)
    print_button.pack(side="left", padx=10)

    # Výčet objektů podle zóny
    objects_for_zone = {
        "Spawn bod": ["Spawn bod"],
        "Vstupní zóna": ["Pokladna", "Pizza stánek", "Burger stánek", "Gyros stánek", "Grill stánek", "Bel hranolky stánek", "Langoš stánek", "Sladký stánek", "Nealko stánek", "Pivní stánek", "Red Bull stánek", "Toitoiky"],
        "Festivalový areál": ["Podium", "Pizza stánek", "Burger stánek", "Gyros stánek", "Grill stánek", "Bel hranolky stánek", "Langoš stánek", "Sladký stánek", "Nealko stánek", "Pivní stánek", "Red Bull stánek", "Toitoiky"],
        "Stanové městečko": ["Nealko stánek", "Pivní stánek", "Red Bull stánek", "Toitoiky", "Sprchy"],
        "Chill zóna": [],
        "Zábavní zóna": ["Bungee-jumping", "Horská dráha", "Lavice", "Kladivo", "Nealko stánek", "Pivní stánek"]
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
            btn = tk.Button(frame_right, text=obj, font=("Arial", 13), width=15, command=lambda o=obj: select_object(o))
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

        foods = ["Pizza stánek", "Burger stánek", "Gyros stánek", "Grill stánek", "Bel hranolky stánek", "Langoš stánek", "Sladký stánek"]
        drinks = ["Nealko stánek", "Pivní stánek", "Red Bull stánek"]

        if current_zone is None or current_object is None:
            print("chyba: není vybrána zóna nebo objekt")
            return

        x, y = event.x, event.y
        r = 13

        if current_zone != "Spawn bod":
            instance = find_zone_instance_for_point(current_zone, x, y)
            if instance is None:
                print("chyba: objekt musí být uvnitř existující zóny")
                return
        else:
            # speciál pro Spawn body 
            instance = {"type": "Global", "objects": []}
            zones_data.setdefault("Global", {"multiple": True, "instances": []})
            zones_data["Global"]["instances"].append(instance)

        EDGE_TOLERANCE = 15 

        if current_object == "Vstup":
            left, top, right, bottom = instance["left"], instance["top"], instance["right"], instance["bottom"]
            on_edge = (abs(x - left) <= EDGE_TOLERANCE or abs(x - right) <= EDGE_TOLERANCE or abs(y - top) <= EDGE_TOLERANCE or abs(y - bottom) <= EDGE_TOLERANCE)

            if not on_edge:
                print("Objekt 'Vstup' musí být umístěn na okraji zóny!")
                return
    
        text_id = canvas.create_text(x, y-20, text=current_object, fill="black", font=("Arial", 8, "bold"), anchor="center")

        if current_object in foods:
            obj_id = canvas.create_oval(x-r, y-r, x+r, y+r, fill="green", outline="black")

        elif current_object in drinks:
            obj_id = canvas.create_oval(x-r, y-r, x+r, y+r, fill="blue", outline="black")

        elif current_object == "Spawn bod":
            obj_id = canvas.create_rectangle(x-50, y, x+50, y+50, fill="black")

        elif current_object == "Toitoiky":
            obj_id = canvas.create_rectangle(x-50, y, x+50, y+50, fill="black")

        elif current_object == "Podium":

            # Podium
            obj_id = canvas.create_rectangle(x-80, y, x+80, y+50, fill="black")

            # Stání u podia
            stand_top = y + 55
            stand_bottom = y + 50 + 150
            stand_left = x - 110
            stand_right = x + 110

            stand_id = canvas.create_rectangle(stand_left, stand_top, stand_right, stand_bottom, fill="grey", outline="black")
    
            # Popis stání u podia
            stand_text_id = canvas.create_text((stand_left + stand_right)/2,(stand_top + stand_bottom)/2,text="Stání u podia",fill="black", font=("Arial", 8, "bold"), anchor="center")

            # Přidání do obj_data obojího
            obj_data = {"object": current_object,"x": x,"y": y,"canvas_ids": [text_id, obj_id], "extra": [{"object": "Stání u podia", "canvas_ids": [stand_text_id, stand_id]}]}
            instance.setdefault("objects", []).append(obj_data)
           
            return
        
        else:
            obj_id = canvas.create_oval(x-r, y-r, x+r, y+r, fill="gray", outline="black")

        obj_data = {"object": current_object, "x": x, "y": y, "canvas_ids": [text_id, obj_id], "extra": []}

        instance.setdefault("objects", []).append(obj_data)
            
    def on_click(event):
        """Začátek kreslení zóny (pokud není vybraný objekt)."""
        global drawing, last_x, last_y, zone_rect, zone_label, current_object, current_zone, current_mode, selected_zone_instance, selected_object, is_dragging_object, is_dragging_zone, connect_start_zone


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

                is_dragging_object = True
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
        if not drawing or current_object is not None or current_zone == "Spawn bod":
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
            bbox = canvas.coords(zone_rect)
            left, top, right, bottom = bbox

            permanent_rect = canvas.create_rectangle(left, top, right, bottom, outline="blue", fill="white", width=3)
            text_x = (left + right) / 2
            text_y = top - 12
            permanent_label = canvas.create_text(text_x, text_y, text=current_zone or "", fill="black", font=("Arial", 12, "bold"), anchor="s")

            zone_instance = { "type": current_zone, "left": left, "top": top, "right": right, "bottom": bottom, "label_id": permanent_label, "rect_id": permanent_rect,"canvas_ids":[permanent_rect, permanent_label], "objects": [], "lines": []}

            zones_data[current_zone]["instances"].append(zone_instance)
            print(f"Uložená zóna {current_zone}: {left, top, right, bottom}")

            # smaž dočasné objekty
            canvas.delete(zone_rect)
            if zone_label:
                canvas.delete(zone_label)

        zone_rect = None
        zone_label = None

    def delete_selected(event=None):
        global selected_zone_instance, selected_object

        if selected_object:

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
            return  # tady ukonči, aby se dál nesmazala celá zóna

        if selected_zone_instance:
            # smažeme všechny canvas objekty spojené se zónou
            for cid in selected_zone_instance.get("canvas_ids", []):
                canvas.delete(cid)
            for obj in selected_zone_instance.get("objects", []):
                for cid in obj.get("canvas_ids", []):
                    canvas.delete(cid)
            for line_id in selected_zone_instance.get("lines", []):
                canvas.delete(line_id)

            # odstraníme z dat
            zone_type = selected_zone_instance["type"]
            zones_data[zone_type]["instances"].remove(selected_zone_instance)
            selected_zone_instance = None
            print("Zóna smazána")

    RESIZE_TOLERANCE = 20 

    def get_resize_direction(zone, x, y):
        """Vrátí tuple (dx, dy), který říká, které hrany/rohy se mají měnit"""
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
            # jednoduchá AABB kolize
            if (zone["left"] < other["right"] and zone["right"] > other["left"] and
                zone["top"] < other["bottom"] and zone["bottom"] > other["top"]):
                return True
        return False

    canvas.bind("<Button-1>", on_click)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)
    root.bind("<Delete>", delete_selected)

    root.mainloop()
    return settings
