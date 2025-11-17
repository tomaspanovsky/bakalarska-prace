import tkinter as tk
from PIL import Image, ImageTk
from . import saving 

# Stav aplikace
current_zone = None         
current_object = None
drawing = False
last_x, last_y = None, None
zone_rect = None
zone_label = None
zone_buttons = {}
object_buttons = {}
history = []
selected_object_for_line = None

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


    image = Image.open("data/simpy-logo.webp")
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

    def undo():
        global history, zones_data
        nonlocal canvas
        
        print(history)
        if not history:
            print("Žádná akce k vrácení")
            return

        last_action = history.pop()
        action_type = last_action[0]

        if action_type == "object":

            zone, zone_type, instance, obj_data = last_action

            for cid in obj_data.get("canvas_ids", []):
                canvas.delete(cid)

            if instance and "objects" in instance and obj_data in instance["objects"]:
                instance["objects"].remove(obj_data)
                
            print(f"Vrácen objekt '{obj_data.get('object')}' ze zóny '{zone_type}'")

        elif action_type == "zone":
            
            zone, zone_type, instance = last_action

            print("Smazat rect_id:", instance["rect_id"])
            print("Smazat label_id:", instance["label_id"])
            canvas.delete(instance["rect_id"])
            canvas.delete(instance["label_id"])

            if instance in zones_data[zone_type]["instances"]:
                zones_data[zone_type]["instances"].remove(instance)

            print(f"Vrácena zóna {zone_type}")

        elif action_type == "line":
            obj1, obj2, line_id = last_action
            canvas.delete(line_id)
            print(f"Vrácena čára mezi {obj1['object']} a {obj2['object']}")

    def save():
        saving.save(zones_data)
        print("Rozložení úspěšně uloženo do festival_layout.json")

    # Pravý sloupec
    frame_right = tk.Frame(content_frame, width=200, height=800, bg="white")
    frame_right.pack(side="left", fill="y", padx=(20,0), pady=5)
    frame_right.pack_propagate(False)
    tk.Label(frame_right, text="Objekty", font=("Arial", 25, "bold"), bg="white", fg="black").pack(pady=10)

    buttons_frame = tk.Frame(editor_frame, bg="black")
    buttons_frame.pack(pady=20)

    back_button = tk.Button(buttons_frame, text="Zpět", command=go_back, font=("Arial", 20), bg="blue", fg="white", padx=20, pady=10, width=10, height=1)
    back_button.pack(side="left", padx=10)

    undo_button = tk.Button(buttons_frame, text="Vrátit akci", command=undo, font=("Arial", 20), bg="red", fg="white", padx=20, pady=10, width=10, height=1)
    undo_button.pack(side="left", padx=10)

    save_button = tk.Button(buttons_frame, text="Uložit do JSONu", command=save, font=("Arial", 20), bg="blue", fg="white", padx=20, pady=10, width=10, height=1)
    save_button.pack(side="left", padx=10)

    # Výčet objektů podle zóny
    objects_for_zone = {
        "Spawn bod": ["Spawn bod"],
        "Vstupní zóna": ["Pokladna", "Jídelní prostor", "Pizza stánek", "Burger stánek", "Gyros stánek", "Grill stánek", "Bel hranolky stánek", "Langoš stánek", "Sladký stánek", "Nealko stánek", "Pivní stánek", "Red Bull stánek", "Toitoiky", "Vstup"],
        "Festivalový areál": ["Podium", "Stání u podia", "Jídelní prostor", "Pizza stánek", "Burger stánek", "Gyros stánek", "Grill stánek", "Bel hranolky stánek", "Langoš stánek", "Sladký stánek", "Nealko stánek", "Pivní stánek", "Red Bull stánek", "Toitoiky", "Vstup"],
        "Stanové městečko": ["Nealko stánek","Jídelní prostor", "Pivní stánek", "Red Bull stánek", "Toitoiky", "Sprchy", "Vstup"],
        "Chill zóna": ["Jídelní prostor"],
        "Zábavní zóna": ["Vstup", "Bungee-jumping", "Horská dráha", "Lavice", "Kladivo", "Nealko stánek", "Pivní stánek"]
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

        global current_zone, object_buttons
        current_zone = zone_name
        print(f"Vybrána zóna: {current_zone}")

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

    # Pomocná funkce: najde instanci (slovník) zóny, do které patří bod x,y
    def find_zone_instance_for_point(zone_type, x, y):
        insts = zones_data[zone_type]["instances"]
        for inst in insts:
            if inst["left"] <= x <= inst["right"] and inst["top"] <= y <= inst["bottom"]:
                return inst
        return None

    # Funkce pro vkládání objektů
    def place_object(event):
        global current_object, current_zone, history, zones_data

        foods = ["Pizza stánek", "Burger stánek", "Gyros stánek", "Grill stánek", "Bel hranolky stánek", "Langoš stánek", "Sladký stánek"]
        drinks = ["Nealko stánek", "Pivní stánek", "Red Bull stánek"]

        if current_zone is None or current_object is None:
            print("chyba: není vybrána zóna nebo objekt")
            return

        x, y = event.x, event.y
        r = 13
        text_id = canvas.create_text(x, y-20, text=current_object, fill="black", font=("Arial", 8), anchor="center")

        if current_object in foods:
            obj_id = canvas.create_oval(x-r, y-r, x+r, y+r, fill="red", outline="black")

        elif current_object in drinks:
            obj_id = canvas.create_oval(x-r, y-r, x+r, y+r, fill="blue", outline="black")

        elif current_object == "Spawn bod":
            obj_id = canvas.create_rectangle(x-50, y, x+50, y+50, fill="black")

        elif current_object == "Toitoiky":
            obj_id = canvas.create_rectangle(x-50, y, x+50, y+50, fill="black")

        elif current_object == "Podium":
            obj_id = canvas.create_rectangle(x-80, y, x+80, y+50, fill="black")

        elif current_object == "Stání u podia":
            obj_id = canvas.create_rectangle(x-80, y, x+80, y+150, fill="grey")

        else:
            obj_id = canvas.create_oval(x-r, y-r, x+r, y+r, fill="gray", outline="black")

        obj_data = {"object": current_object, "x": x, "y": y, "canvas_ids": [text_id, obj_id]}

        EDGE_TOLERANCE = 15 

        if current_zone != "Spawn bod":
            instance = find_zone_instance_for_point(current_zone, x, y)

            if instance is None:
                print("chyba: objekt musí být uvnitř existující zóny")
                canvas.delete(text_id)
                canvas.delete(obj_id)
                return

        else:
            instance = {"type": "Global", "objects": []}
            zones_data.setdefault("Global", {"multiple": True, "instances": []})
            zones_data["Global"]["instances"].append(instance)

        if current_object == "Vstup":
            left, top, right, bottom = instance["left"], instance["top"], instance["right"], instance["bottom"]
            on_edge = (abs(x - left) <= EDGE_TOLERANCE or abs(x - right) <= EDGE_TOLERANCE or abs(y - top) <= EDGE_TOLERANCE or abs(y - bottom) <= EDGE_TOLERANCE)

            if not on_edge:
                print("Objekt 'Vstup' musí být umístěn na okraji zóny!")
                canvas.delete(text_id)
                canvas.delete(obj_id)
                return

        instance.setdefault("objects", []).append(obj_data)
        history.append(("object", current_zone, instance, obj_data))

    
    def select_object_for_line(event):
        global selected_object_for_line
    
        x, y = event.x, event.y
        clicked_obj = None

        for zone_type, zone_info in zones_data.items():
            for instance in zone_info["instances"]:
                for obj in instance.get("objects", []):
                   
                    geom_id = obj["canvas_ids"][1] 
                    coords = canvas.coords(geom_id)
                
                    if canvas.type(geom_id) in ("oval", "rectangle"):
                        ox = (coords[0] + coords[2]) / 2
                        oy = (coords[1] + coords[3]) / 2
                    else:
                        ox, oy = coords  
                
                    r = max((coords[2]-coords[0])/2, (coords[3]-coords[1])/2) + 3
                    if (ox - r) <= x <= (ox + r) and (oy - r) <= y <= (oy + r):
                        clicked_obj = obj
                        break
                if clicked_obj:
                    break
            if clicked_obj:
                break

        if clicked_obj is None:
            print("Kliknuto mimo objekt")
            return

        if selected_object_for_line is None:
            selected_object_for_line = clicked_obj
            print(f"První objekt vybrán: {clicked_obj['object']}")
        else:
        
            id1 = selected_object_for_line["canvas_ids"][1]
            id2 = clicked_obj["canvas_ids"][1]
            x1, y1 = (canvas.coords(id1)[0] + canvas.coords(id1)[2]) / 2, (canvas.coords(id1)[1] + canvas.coords(id1)[3]) / 2
            x2, y2 = (canvas.coords(id2)[0] + canvas.coords(id2)[2]) / 2, (canvas.coords(id2)[1] + canvas.coords(id2)[3]) / 2
        
            line_id = canvas.create_line(x1, y1, x2, y2, fill="black", width=2)
            history.append(("line", selected_object_for_line, clicked_obj, line_id))
        
            print(f"Propojeno: {selected_object_for_line['object']} → {clicked_obj['object']}")
            selected_object_for_line = None

    def on_click(event):
        """Začátek kreslení zóny (pokud není vybraný objekt)."""
        global drawing, last_x, last_y, zone_rect, zone_label, current_object, current_zone

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

    def on_drag(event):
        """Aktualizace obdélníku + textu při tažení myší."""
        global drawing, last_x, last_y, zone_rect, zone_label, current_object, current_zone

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
        global drawing, zone_rect, zone_label, last_x, last_y, current_zone, zones_data

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

            zone_instance = { "type": current_zone, "left": left, "top": top, "right": right, "bottom": bottom, "label_id": permanent_label, "rect_id": permanent_rect, "objects": []}

            zones_data[current_zone]["instances"].append(zone_instance)
            history.append(("zone", current_zone, zone_instance))

            print(f"Uložená zóna {current_zone}: {left, top, right, bottom}")

        zone_rect = None
        zone_label = None

    canvas.bind("<Button-1>", on_click)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)
    canvas.bind("<Shift-Button-1>", select_object_for_line)

    root.mainloop()
    return settings
