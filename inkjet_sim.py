import numpy
import pygame
import matplotlib.pyplot as plt
import matplotlib.animation as animation

#Scaling factor
PIX_TO_M = 150000

def m_to_pix(m):
    return m*PIX_TO_M

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
paperWidth = 4*10**-3 #m
paperLength = 6*10**-3 #m
paperCoord = [1100, 210, 10, m_to_pix(paperLength)]

#Capacitor Parameters
capacitorWidth = 1*10**-3 #m
capacitorLength = 0.5*10**-3 #m
cap1Coord = [paperCoord[0]-(m_to_pix(capDistanceToPaper))-(m_to_pix(capacitorLength)), (paperCoord[1] + (paperCoord[3]/2)) - (m_to_pix(capacitorWidth/2)), m_to_pix(capacitorLength)]
cap2Coord = [paperCoord[0]-(m_to_pix(capDistanceToPaper))-(m_to_pix(capacitorLength)), cap1Coord[1] + m_to_pix(capacitorWidth)+10, m_to_pix(capacitorLength)]

#Bullet parameters


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
    pygame.draw.rect(screen, GRAY, (cap1Coord[0], cap1Coord[1], cap1Coord[2], 10))
    pygame.draw.rect(screen, GRAY, (cap2Coord[0], cap2Coord[1], cap2Coord[2], 10))
    # Draw droplet gun
    pygame.draw.rect(screen, BLACK, (cap1Coord[0] - m_to_pix(capDistanceToPaper)-170, cap1Coord[1] + (m_to_pix(capacitorWidth/2))-25, 120, 70))
    pygame.draw.rect(screen, BLACK, (cap1Coord[0] - m_to_pix(capDistanceToPaper)-50, cap1Coord[1] + (m_to_pix(capacitorWidth/2))-15, 50, 50))
    pygame.draw.rect(screen, BLACK, (cap1Coord[0] - m_to_pix(capDistanceToPaper), cap1Coord[1] + (m_to_pix(capacitorWidth/2)) - 10, 30, 40))
    # Draw paper display
    pygame.draw.rect(screen, BLACK, (paperCoord[0], paperCoord[1], m_to_pix(paperWidth), paperCoord[3]), width=3)
    pygame.display.flip()
    
pygame.quit()
