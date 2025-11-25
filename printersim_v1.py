import math
import numpy as np

# DROPLET CONSTANTS
droplet_diameter = 8.4e-5                               # meters
r = droplet_diameter / 2                                # meters
q = -1.9e-10                                            # coulombs
droplet_density = 1000                                  # kg/m3
droplet_volume = (4/3)*(np.pi * r**3)                   # m3
m = droplet_density * droplet_volume                    # kg

# SETUP
w = 0.001                                               # meters
D = 0.003                                               # meters
L1 = 0.0005                                             # meters
L2 = 0.00125                                            # meters
L0 = D - (L1 + L2)                                      # meters
v_x = 20.0                                              # m/s
dpm = 300/0.0254                                        # dots per meter

# KINEMATIC CONSTANTS
Tc = L1 / v_x                                           # seconds
T1 = L0 / v_x                                           # seconds
T2 = T1 + Tc                                            # seconds
T3 = D / v_x                                            # seconds
firing_period = Tc                                     # seconds

length_to_draw = 0.006
N = math.floor(dpm * length_to_draw) + 1
a = q*Tc
b = m*w
V_step = ( (a/b) * (Tc/2 + (T3 - T2)) * dpm ) ** -1
T_TOTAL = T3 + (N - 1) * firing_period
NUM_POINTS = 1000
time = np.linspace(0, T_TOTAL, NUM_POINTS)
def get_index(time):
    index = math.floor(time * NUM_POINTS/T_TOTAL)
    return index

all_x_positions = np.zeros((N, NUM_POINTS))
all_y_positions = np.zeros((N, NUM_POINTS))

T3_index = get_index(T3)

for i in range(N):
    start_index = get_index(firing_period * i)
    end_index = get_index(firing_period * i + T3)
    diff_index = end_index - start_index
    x_vector = all_x_positions[i]

    try:
        x_vector[start_index: end_index + 1] = v_x * time[: T3_index + 1]
        x_vector[end_index + 1:] = D

    except ValueError:
        x_vector[start_index: end_index] = v_x * time[: T3_index + 1]
        x_vector[end_index:] = D

    all_x_positions[i, :] = x_vector



# FROM GOOGLE GEMINI
# FOR VISUALIZATION PURPOSES
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# 1. Initialize plot
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_xlim(-0.0001, D + 0.0005) # Add a small buffer
ax.set_ylim(-0.003, 0.003)       # Adjust Y limits based on max deflection
ax.set_title("Electrostatic Droplet Deflection")
ax.set_xlabel("X Position (m)")
ax.set_ylabel("Y Position (m)")
ax.grid(True)

# 2. Create an artist (Line2D object) for *each* droplet
# These will be updated in the animation loop.
droplets_artists = []
for i in range(N):
    # 'o' marker style, ms=5 (marker size), color can be changed
    line, = ax.plot([], [], 'o', ms=3, color=plt.cm.viridis(i / N))
    droplets_artists.append(line)

# 3. Initialization function (required by FuncAnimation)
def init():
    """Sets up the initial state of the plot."""
    for line in droplets_artists:
        line.set_data([], [])
    return droplets_artists


NUM_POINTS = all_x_positions.shape[1]


def update_frame(frame):
    """
    Updates the position of all N droplets for the current frame index.
    """

    # Loop over all N droplets
    for i in range(N):
        # The current position for particle 'i' is the data at column 'frame'

        # Get the X and Y coordinates at the current time step (frame)
        x_current = all_x_positions[i, frame]
        y_current = all_y_positions[i, frame]

        # Update the data for the specific droplet's artist
        # The artist is a Line2D object; we set its data to the current point.
        droplets_artists[i].set_data([x_current], [y_current])

    # Update the title to show physical time elapsed
    current_time_phys = T_TOTAL * (frame / (NUM_POINTS - 1))
    ax.set_title(f"Time: {current_time_phys * 1000:.2f} ms")

    return droplets_artists

TOTAL_PLAYBACK_MS = 1000
INTERVAL_MS = TOTAL_PLAYBACK_MS / NUM_POINTS

anim = FuncAnimation(
    fig,
    update_frame,
    frames=NUM_POINTS,
    init_func=init,
    interval=INTERVAL_MS, # Controls the speed (delay between frames)
    blit=True # Optimize drawing for speed
)

# Use one of the following commands to display the animation:
# 1. To display in a live plot window (standard desktop environment):
plt.show()