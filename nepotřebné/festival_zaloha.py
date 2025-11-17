import simpy
import random
import zdroje

global prijem


#promene, ktere budou vstupní parametry
poc_navstevniku = 10
poc_vstupu = 5
poc_pokladen = 3
poc_toitoi_areal = 5 # (x pro každé pohlaví)
poc_toitoi_stan_mestecko = 5 # (x pro každé pohlaví)
obsazeno = [0] * poc_vstupu
obsazeno_pokladny = [0] * poc_pokladen
max_kapacita_navstevniku = 3000
max_stanu = 100
cena_listku_predprodej = 1000
cena_listku_na_miste = cena_listku_predprodej + 200
cena_stanoveho_mestecka = 200
prijem = 0


class Navstevnik:
    id = 0

    def __init__(self, festival):
        Navstevnik.id += 1

        self.festival = festival
        self.id = Navstevnik.id 
        self.pohlavi = random.choice(list(zdroje.Pohlavi))
        self.vek_kategorie = random.choice(list(zdroje.Vek_kategorie))
        self.vlastnosti = {"nedockavost": random.randint(1,10), "chut_utracet" : random.randint(1,10), "hladovost" : random.randint(1,10),"pije_alkohol" : random.choice(list(zdroje.Ano_ne)) ,"alko_tolerance" : random.randint(1,10), "bod_opilosti" : random.randint(1,10), "pocasi_odolnost" : random.randint(1, 10)}
        self.stav = {"lokace" : zdroje.Lokace.NADRAZI, "predchozi_lokace" : zdroje.Lokace.NADRAZI, "penize" : random.randint(cena_listku_na_miste, 10000), "listek_v_predprodeji" : random.choice(list(zdroje.Ano_ne)) , "pasek" : zdroje.Ano_ne.NE ,"kelimek": zdroje.Ano_ne.NE, "unava": 100, "nalada": 100, "hlad" : 100, "zizen": 100, "opilost": 0, "wc": 100, "hygiena": 100, "spolecenskost" : 100}
        self.preference = {"oblibene_jidlo" : random.choice(list(zdroje.Jidlo)).name, "oblibene_piti" : random.choice(list(zdroje.Piti)).name}
        self.bydleni = [random.choice(list(zdroje.Ano_ne)), 0] # první parametr je zda návštěvník vlastní stan, druhý jestli je stan postavený a návštěvník má kde bydlet
        self.partaci = []
        self.batoh = []

        match self.vek_kategorie:
            case zdroje.Vek_kategorie.DITE:
                self.vek = random.randint(6, 14)
            case zdroje.Vek_kategorie.MLADISTVI:
                self.vek = random.randint(15,25)
            case zdroje.Vek_kategorie.DOSPELY:
                self.vek = random.randint(26, 64)
            case zdroje.Vek_kategorie.DUCHODCE:
                self.vek = random.randint(65,80)

        if self.pohlavi == zdroje.Pohlavi.MUZ:
            self.jmeno = random.choice(list(zdroje.Jmena_muz))
            self.prijmeni = random.choice(list(zdroje.Prijmeni_muz))
        else:
            self.jmeno = random.choice(list(zdroje.Jmena_zen))
            self.prijmeni = random.choice(list(zdroje.Prijemi_zen))
        
        if self.vek >= 18:
            self.preference["alkoholik"] = random.choice(list(zdroje.Ano_ne))
            self.preference["kurak"] = random.choice(list(zdroje.Ano_ne))

            if self.preference["kurak"] == zdroje.Ano_ne.ANO:
                self.stav["nikotin"] = 100
                self.stav["uroven_zavislosti"] = random.randint(1,10)
                self.stav["cigaret"] = random.randint(1,60)

        if self.stav["listek_v_predprodeji"] == zdroje.Ano_ne.ANO and self.vek > 14:
            global prijem
            prijem += cena_listku_predprodej

        if self.bydleni[0] == zdroje.Ano_ne.ANO:
            self.stan = [simpy.Resource(festival, capacity = random.randint(2,4))]

        self.proces = festival.process(self.co_ted())

    def co_ted(self):
        #funkce, která rozhodne následující krok návštěvníka
        moznosti = {"vymena_pasku" : self.vymena_pasku, 
                    "vstup_do_arealu" : self.vstup_do_arealu,
                    "zapalit_si" : self.zapalit_si
                    }

        if self.vek >= 18 and self.preference["kurak"] == zdroje.Ano_ne.ANO:
            chut_na_cigaretu = random.randint(0, 12 - self.stav["uroven_zavislosti"])

            if chut_na_cigaretu <= 2:
                yield self.festival.process(moznosti["zapalit_si"]())   

            elif self.stav["nikotin"] < 30 or self.stav["nalada"] < 50:
                yield self.festival.process(moznosti["zapalit_si"]())

        #hajzly in progress
        #wc_faktor = random.randint(0, 100 - self.stav["wc"])
        
        #if wc_faktor > 50:
        #    yield self.festival.process(moznosti["jdi_na_zachod"])

        if self.stav["lokace"] == zdroje.Lokace.NADRAZI:

            if self.stav["pasek"] == zdroje.Ano_ne.NE:
                yield self.festival.process(moznosti["vymena_pasku"](pokladny))
            
            if self.stav["pasek"] == zdroje.Ano_ne.ANO:
                yield self.festival.process(moznosti["vstup_do_arealu"](vstupy))

    def stanove_mestecko(self, stanove_mestecko):
        pass

    def vymena_pasku(self, pokladny):
        yield self.festival.timeout(random.expovariate(1/2))

        pokladna_id = obsazeno_pokladny.index(min(obsazeno_pokladny))
        pokladna = pokladny[pokladna_id]
        obsazeno_pokladny[pokladna_id] += 1
        
        with pokladna.request() as req:

            if self.stav["listek_v_predprodeji"] == zdroje.Ano_ne.ANO:
                vymena_pasku_time = random.uniform(2,5)
            else:
                vymena_pasku_time = random.uniform(4, 8)

            yield self.festival.timeout(vymena_pasku_time)
            
            self.stav["pasek"] = zdroje.Ano_ne.ANO

            if self.stav["listek_v_predprodeji"] == zdroje.Ano_ne.NE and self.vek > 14:
                self.stav["penize"] = self.stav["penize"] - cena_listku_na_miste
                global prijem
                prijem += cena_listku_na_miste
                print(f"{self.jmeno.value} {self.prijmeni.value} si byl pro pásek, a odešel z pokladen v čase {self.festival.now:.2f} a kupoval lístek na místě")
            
            else:
                print(f"{self.jmeno.value} {self.prijmeni.value} si byl pro pásek, a odešel z pokladen v čase {self.festival.now:.2f} a měl lístek z předprodeje")

        obsazeno_pokladny[pokladna_id] -= 1

    def vstup_do_arealu(self, vstupy):
        # Návštěvník přichází s určitou náhodnou prodlevou
        yield self.festival.timeout(random.expovariate(1/2))  # Průměrná mezera mezi příchody = 2s
        prichod_time = self.festival.now

        # Návštěvník si vybere vstup s nejmenším počtem lidí
        vstup_id = obsazeno.index(min(obsazeno))
        vstup = vstupy[vstup_id]
        obsazeno[vstup_id] += 1

        print(f"{self.jmeno.value} {self.prijmeni.value}, přišel ke vstupu {vstup_id + 1} v čase {prichod_time:.2f}")
        print(obsazeno)

        # Počká ve frontě na bezpečnostní kontrolu
        with vstup.request() as req:
            fronta_start = self.festival.now  
            yield req  # Čekání na uvolnění kontroly

            fronta_cekani_time = self.festival.now - fronta_start  # Doba čekání ve frontě
            vstup_time = random.uniform(1, 3)  # Náhodná doba kontroly
            yield self.festival.timeout(vstup_time)

            print(f"{self.jmeno.value} {self.prijmeni.value} prošel kontrolou {vstup_id + 1} v čase {self.festival.now:.2f}, čekal {fronta_cekani_time:.2f}s, kontrola trvala {vstup_time:.2f}s, návtěvníkovo oblíbené jídlo je {zdroje.Jidlo[self.preference['oblibene_jidlo']].value}")

        obsazeno[vstup_id] -= 1
        print(obsazeno)

        #Funkce která obsluhuje návštěvníkovo kouření cigaret 
    def zapalit_si(self):
           
        yield self.festival.timeout(random.uniform(5, 10))

        self.stav["cigaret"] -= 1
        self.stav["nikotin"] = min(self.stav["nikotin"] + 30, 100)
        self.stav["nalada"] += min(self.stav["nalada"] + 30, 100)
        print(f"{self.jmeno.value} {self.prijmeni.value} si zapálil cigaretu.")

        #Funkce která obsluje průběh toho, když jde návštěvník na záchod

        def jit_na_wc(self, toitoiky):

            #jak dlouho budou na wc
            if self.stav["wc"] > 50:
                wc_faktor = random.randint(1, 5)
                
                if wc_faktor == 1 and self.pohlavi == zdroje.pohlavi.ZENA:
                    pass

                elif wc_faktor == 1 and self.pohlavi == zdroje.pohlavi.MUZ:
                    pass


# Vytvoření prostředí
festival = simpy.Environment()

# Resources
stanove_mestecko = [simpy.Resource(festival, capacity = max_kapacita_navstevniku / 3) for _ in range(1)]
pokladny = [simpy.Resource(festival, capacity=1) for _ in range(poc_pokladen)]
vstupy = [simpy.Resource(festival, capacity=1) for _ in range(poc_vstupu)]
toitoiky_areal_m = [simpy.Resource(festival, capacity=1) for _ in range(poc_toitoi_areal)]
toitoiky_areal_z = [simpy.Resource(festival, capacity=1) for _ in range(poc_toitoi_areal)]
toitoiky_stan_mestecko_m = [simpy.Resource(festival, capacity=1) for _ in range(poc_toitoi_stan_mestecko)]
toitoiky_stan_mestecko_z = [simpy.Resource(festival, capacity=1) for _ in range(poc_toitoi_stan_mestecko)]

# Postupné vytváření návštěvníků
for i in range(poc_navstevniku):
    Navstevnik(festival)
    
# Spuštění simulace
festival.run()
