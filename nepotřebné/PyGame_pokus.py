import pygame
import random

# Inicializace PyGame
pygame.init()

# Nastavení okna
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulace pohybu")

# Barvy
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

# Parametry návštěvníků
poc_navstevniku = 5
navstevnici = [{"x": random.randint(50, WIDTH - 50), "y": random.randint(50, HEIGHT - 50)} for _ in range(poc_navstevniku)]

# Hlavní smyčka
running = True
while running:
    screen.fill(WHITE)  # Vyčistí obrazovku

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Pohyb návštěvníků
    for v in navstevnici:
        v["x"] += random.choice([-5, 0, 5])
        v["y"] += random.choice([-5, 0, 5])
        pygame.draw.circle(screen, BLUE, (v["x"], v["y"]), 10)

    pygame.display.flip()
    pygame.time.delay(100)

pygame.quit()