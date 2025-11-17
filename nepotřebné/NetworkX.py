import networkx as nx
import matplotlib.pyplot as plt
import random

# Počet návštěvníků
NUM_VISITORS = 10

# Vytvoření prázdného grafu
G = nx.Graph()

# Přidání návštěvníků jako uzlů
for i in range(NUM_VISITORS):
    G.add_node(f"Návštěvník {i+1}")

# Vytvoření náhodných propojení mezi návštěvníky
for _ in range(NUM_VISITORS * 2):  # Každý má průměrně 2 přátele
    a, b = random.sample(list(G.nodes), 2)
    G.add_edge(a, b)

# Vykreslení grafu
plt.figure(figsize=(6, 6))
nx.draw(G, with_labels=True, node_color="lightblue", edge_color="gray", node_size=2000, font_size=10)
plt.show()