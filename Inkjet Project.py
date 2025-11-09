import numpy
import pygame
import matplotlib.pyplot as plt
import matplotlib.animation as animation

#Simulation Parameters
dropletDiameter = 84*10**-6 #micrometers
dropletCharge = -1.9*10**-10 #C
gunVelocity = 20 #m/s
dropletDensity = 1000 #kg/m^3
printResolution = 300 #dpi
clock = pygame.time.Clock()

#Paper Parameters
distanceToPaper = 3*10**-3 #m
capDistanceToPaper = 1.25*10**-3 #m
paperWidth = 215.9*10**-3 #m
paperLength = 279.4*10**-3 #m

#Capacitor Parameters
capacitorWidth = 1*10**-3 #m
capacitorLength = 0.5*10**-3 #m

pygame.init()

#Window Setup
WIDTH, HEIGHT = 2000, 1200
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Electrostatic Inkjet Simulation")

clock = pygame.time.Clock()

#Color Definitions
WHITE = (255, 255, 255) #RGB for white
BLACK = (0, 0, 0) #RGB for black 
GRAY = (128, 128, 128) #RGB for gray
BLUE = (0, 0, 255) #RGB for blue

#paperX = 
running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(WHITE)
    # Draw capacitor plates
    pygame.draw.rect(screen, GRAY, (340, 250, 10, 150))
    pygame.draw.rect(screen, GRAY, (550, 250, 10, 150))
    # Draw droplet gun
    pygame.draw.rect(screen, BLACK, (400, 10, 100, 120))
    pygame.draw.rect(screen, BLACK, (420, 130, 60, 20))
    pygame.draw.rect(screen, BLACK, (430, 150, 40, 20))
    # Draw table
    pygame.draw.rect(screen, BLACK, (50, 1125, 800, 25))
    # Draw paper display
    pygame.draw.rect(screen, BLACK, (1100, 50, 870, 1120))
    pygame.draw.rect(screen, WHITE, (1110, 60, 850, 1100))
    pygame.display.flip()
    
pygame.quit()
