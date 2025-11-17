import simpy
import random

# Počet návštěvníků a počet kontrolních bodů
poc_navstevniku = 20
poc_vstupu = 5
obsazeno = [0] * poc_vstupu

def vstup(prostredi, navstevnik, vstupy):
    
    # Návštěvník přichází s určitou náhodnou prodlevou
    yield prostredi.timeout(random.expovariate(1/2))  # Průměrná mezera mezi příchody = 2s
    
    prichod_time = prostredi.now

    # Návštěvník si vybere vstup s nejmenším počtem lidí
    vstup_id = obsazeno.index(min(obsazeno))
    vstup = vstupy[vstup_id]
    obsazeno[vstup_id] += 1

    print(f"{navstevnik}, přišel ke vstupu {vstup_id + 1} v čase {prichod_time:.2f}")
    print(obsazeno)

    # Počká ve frontě na bezpečnostní kontrolu
    with vstup.request() as req:

        fronta_start = prostredi.now  
        yield req  # Čekání na uvolnění kontroly

        fronta_cekani_time = prostredi.now - fronta_start  # Doba čekání ve frontě
        vstup_time = random.uniform(1, 5)  # Náhodná doba kontroly
        yield prostredi.timeout(vstup_time)

        print(f"{navstevnik} prošel kontrolou {vstup_id + 1} v čase {prostredi.now:.2f}, čekal {fronta_cekani_time:.2f}s, kontrola trvala {vstup_time:.2f}s")

        obsazeno[vstup_id] -= 1
        print(obsazeno)

# Hlavní simulace
prostredi = simpy.Environment()
vstupy = [simpy.Resource(prostredi, capacity=1) for _ in range(poc_vstupu)]  

# Postupné vytváření návštěvníků
for i in range(poc_navstevniku):
    prostredi.process(vstup(prostredi, f"Návštěvník {i+1}", vstupy))

prostredi.run()