import enum
import json
import os

here = os.path.dirname(__file__)
file_path_foods = os.path.join(here, "data", "foods.json")
file_path_drinks = os.path.join(here, "data", "drinks.json")
file_path_names = os.path.join(here, "data", "names.json")
file_path_surnames = os.path.join(here, "data", "surnames.json")
file_path_bands = os.path.join(here, "data", "bands.json")

class Groups(enum.Enum):
    GROUP = "skupina"
    FAMILY = "rodina"
    INDIVIDUAL = "jednotlivec"

class Groups_modes(enum.Enum):
    IN_GROUP = "skupinově"
    INDIVIDUALLY = "individuálně"

class Locations(enum.Enum):
    SPAWN_AREA = "spawn zóna"
    TENT_AREA = "stanové městečko"
    ENTRANCE_ZONE = "vstupní zóna"
    FESTIVAL_AREA = "festivalý areál"
    CHILL_ZONE = "chill zóna"
    STAGE_STANDING = "Stání u podia"
    ATRACTION_ZONE = "atrakce zóna"

class Actions_onetime(enum.Enum):
    PITCH_TENT = "pitch_tent"
    BRACELET_EXCHANGE = "bracelet_exchange"

class Actions_moves(enum.Enum):
    GO_TO_TRAIN_STATION = "go_to_train_station"
    GO_TO_PARKING_LOT = "go_to_parking_lot"
    GO_TO_ENTRANCE_ZONE = "go_to_entrance_zone"
    GO_TO_TENT_AREA = "go_to_tent_area"
    GO_TO_FESTIVAL_AREA = "go_to_festival_area"

class Actions_departure(enum.Enum):
    GO_TO_TRAIN_STATION = "go_to_train_station"
    GO_TO_PARKING_LOT = "go_to_parking_lot"

class Actions_entrance_zone(enum.Enum):
    GO_TO_TOILET = "go_to_the_toilet"
    GO_FOR_DRINK = "go_for_drink"
    GO_FOR_FOOD = "go_for_food"

class Actions_tent_area(enum.Enum):
    GO_TO_TOILET = "go_to_toilet"
    GO_TO_SCHOWER = "go_to_shower"
    GO_FOR_DRINK = "go_for_drink"
    GO_TO_TENT = "go_to_tent"
    
ACTIONS_BY_LOCATIONS = {
    Locations.ENTRANCE_ZONE: {
        "hunger": Actions_entrance_zone.GO_FOR_FOOD.value, #ok
        #"thirst": Actions_entrance_zone.GO_FOR_DRINK.value,
        "wc": Actions_entrance_zone.GO_TO_TOILET.value, #ok
        "bracelet_exchange": Actions_onetime.BRACELET_EXCHANGE.value, #ok
        "go_to_festival_area": Actions_moves.GO_TO_FESTIVAL_AREA.value #ok
    },
    Locations.TENT_AREA: {
        "wc": Actions_tent_area.GO_TO_TOILET.value,   #ok
        "hygiene": Actions_tent_area.GO_TO_SCHOWER.value, #ok
        #"thirst": Actions_tent_area.GO_FOR_DRINK.value,
        #"tiredness": Actions_tent_area.GO_TO_TENT.value,
        "pitch_tent": Actions_onetime.PITCH_TENT.value #ok
    }
}

with open(file_path_foods, "r", encoding="utf-8") as f:
    foods_data = json.load(f)

foods = foods_data["foods"]
stalls = foods_data["stalls"]

with open(file_path_drinks, "r", encoding="utf-8") as f:
    drinks_data = json.load(f)

soft_drinks = drinks_data["soft_drinks"]
alcohol = drinks_data["alcohol"]

SELECTIONS_OF_STALLS = {
    Locations.ENTRANCE_ZONE : {
        "stall_entrance_zone_pizza",
        "stall_entrance_zone_burger",
        "stall_entrance_zone_gyros",
        "stall_entrance_zone_grill",
        "stall_entrance_zone_fries",
        "stall_entrance_zone_langos",
        "stall_entrance_zone_sweet"
        }
    }

class Gender(enum.Enum):
    MALE = "muž"
    FEMALE = "žena"

class Age_category(enum.Enum):
    CHILD = "dítě"
    YOUTH = "mladiství"
    ADULT = "dospělý"
    SENIOR = "důchodce"

class Parents(enum.Enum):
    FATHER = "otec"
    MOTHER = "matka"

with open(file_path_names, "r", encoding="utf-8") as f:
    names_data = json.load(f)

names_male = names_data["names_male"]
names_female = names_data["names_female"]

with open(file_path_surnames, "r", encoding="utf-8") as f:
    surnames_data = json.load(f)

surnames_male = surnames_data["surnames_male"]
surnames_female = surnames_data["surnames_female"]
surname_map = surnames_data["surname_map"]

with open(file_path_bands, "r", encoding="utf-8") as f:
    BANDS = json.load(f)