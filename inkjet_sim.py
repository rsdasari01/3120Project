import numpy
import pygame
import matplotlib.pyplot as plt
import matplotlib.animation as animation

clock = pygame.time.Clock()
#Scaling factor
PIX_TO_M = 160000

def m_to_pix(m):
    return m*PIX_TO_M

#Droplet Gun Parameters
printResolution = 300 #dpi

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

#Droplet parameters
dropDiameter = 84*10**-6 #micrometers
q = -1.9*10**-10 #C
dropRadius = dropDiameter/2
dropDensity = 1000 #kg/m^3
dropVol = 4*(numpy.pi)*(dropRadius**3)/3
dropMass = dropDensity*dropVol

#Initial and Constant Kinematic Values
ax = 0 #This always a constant
ay = 0 #gravity is ignored
vx = 20 #m/s -> This is always a constant
vy = 0 #Inside the capacior will be q*E/m
x = cap1Coord[0] - m_to_pix(capDistanceToPaper) + m_to_pix(dropRadius) + 30 # Initial x-posn of dot
y = cap1Coord[1] + (m_to_pix(capacitorWidth/2)) + 10 # Initial y-posn of dot

#Voltage
V_max = 2610
num = int((V_max + V_max)/71)
v = numpy.linspace(-V_max, V_max, num, (V_max/71))

imapcts = []

pygame.init()

#Window Setup
WIDTH, HEIGHT = 2000, 1200
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Inkjet Printer Simulation")

clock = pygame.time.Clock()

#Color Definitions
WHITE = (255, 255, 255) #RGB for white
BLACK = (0, 0, 0) #RGB for black 
GRAY = (128, 128, 128) #RGB for gray
BLUE = (0, 0, 255) #RGB for blue

i = 0
running = True
while running:
    dt = clock.tick(60) / 1000 #Time step in miliseconds
    firing = True

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



    #starting animation
    if firing:
        x += (vx*dt*10)
        if cap1Coord[0] < x : #Checks if it is inside the capacitor
            ay = q*(v[i]*10**3)/dropMass
            y += (ay*(dt**2)/2)/100
        else:
            ay = 0
            y += (vy*dt)*100
    else:
        dot = pygame.draw.circle(screen, BLUE, (x*100,y), m_to_pix(dropRadius))
    
    #Draw droplet
    pygame.draw.circle(screen, BLUE, (x,y), m_to_pix(dropRadius))

    #Showing impact on paper
    if x >= paperCoord[0] + (m_to_pix(paperWidth)/2):
        firing = False
        i += 1
        imapcts.append(y)
        x = cap1Coord[0] - m_to_pix(capDistanceToPaper) + m_to_pix(dropRadius) + 30 # Initial x-posn of dot
        y = cap1Coord[1] + (m_to_pix(capacitorWidth/2)) + 10 # Initial y-posn of dot

    for y_paper in imapcts:
        dot = pygame.draw.circle(screen, BLUE, (paperCoord[0] + (m_to_pix(paperWidth)/2),y_paper), m_to_pix(dropRadius))

    pygame.display.update()
    
pygame.quit()
