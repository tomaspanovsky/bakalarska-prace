import enum
import json
import os

here = os.path.dirname(__file__)
file_path_foods = os.path.join(here, "data", "foods.json")
file_path_drinks = os.path.join(here, "data", "drinks.json")
file_path_names = os.path.join(here, "data", "names.json")
file_path_surnames = os.path.join(here, "data", "surnames.json")
file_path_bands = os.path.join(here, "data", "bands.json")
file_path_merch = os.path.join(here, "data", "merch.json")
file_path_attraction = os.path.join(here, "data", "attractions.json")

class Groups(enum.Enum):
    GROUP = "skupina"
    FAMILY = "rodina"
    INDIVIDUAL = "jednotlivec"

class Groups_modes(enum.Enum):
    IN_GROUP = "skupinově"
    INDIVIDUALLY = "individuálně"

class Locations(enum.Enum):
    SPAWN_ZONE= "spawn zóna"
    TENT_AREA = "stanové městečko"
    ENTRANCE_ZONE = "vstupní zóna"
    FESTIVAL_AREA = "festivalý areál"
    CHILL_ZONE = "chill zóna"
    STAGE_STANDING = "stání u podia"
    FUN_ZONE = "zábavní zóna"
    SIGNING_STALL = "autogramiády stánek"

with open(file_path_merch, "r", encoding="utf-8") as f:
    merch_data = json.load(f)

bands_merch = merch_data["bands_merch"]
festival_merch = merch_data["festival_merch"]

with open(file_path_foods, "r", encoding="utf-8") as f:
    foods_data = json.load(f)

foods = foods_data["foods"]
food_stalls = foods_data["stalls"]

with open(file_path_drinks, "r", encoding="utf-8") as f:
    drinks_data = json.load(f)

soft_drinks = drinks_data["soft_drinks"]
alcohol = drinks_data["alcohol"]
beers = drinks_data["beers"]
hard_alcohol = drinks_data["hard_alcohol"]
cocktails = drinks_data["cocktails"]
drink_stalls = drinks_data["stalls"]
drinks = drinks_data["drinks"]
cup_requirement = drinks_data["cup_requirement"]

class Weather(enum.Enum):
    RAINING = "déšť"
    HOT = "horko"
    COLD = "chladno"
    STORM = "bouřka"
    PARTLY_CLOUDY = "polojasno"
    SUNNY = "slunečno"
    
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

with open(file_path_attraction, "r", encoding="utf-8") as f:
    ATTRACTIONS = json.load(f)
