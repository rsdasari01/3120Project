import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# DROPLET CONSTANTS
droplet_diameter = 8.4e-5
r = droplet_diameter / 2
q = -1.9e-10
droplet_density = 1000
droplet_volume = (4/3)*(np.pi * r**3)
m = droplet_density * droplet_volume

# SETUP
w = 0.001
D = 0.003
L1 = 0.0005
L2 = 0.00125
L0 = D - (L1 + L2)                                      # distance from gun to capacitor
dpm = 300/0.0254                                        # 300 dpi to dpm

# KINEMATIC CONSTANTS
v_z = 20.0
Tc = L1 / v_z                                           # time spent inside capacitor
T1 = L0 / v_z                                           # time at capacitor entry
T2 = T1 + Tc                                            # time at capacitor exit
T3 = D / v_z                                            # time at wall contact
# 1/Tc is the fastest possible firing rate. anything faster would result in multiple droplets being in the capacitor at the same time.
firing_period = Tc
# necessary voltage step for 300 dpi. around 73.8 V per dot.
V_step = ( ( (q*Tc)/(m*w) ) * (Tc/2 + (T3 - T2)) * dpm ) ** -1

line_height = .006                                                  # length of vertical line
line_width = .006                                                   # length of horizontal line
N1 = 2 * (np.floor(dpm * line_height).astype(int) + 1)              # number of dots required for vertical
N2 = np.floor(dpm * line_width).astype(int) + 1                     # number of dots required for horizontal
N_TOTAL = N1 + N2
T_TOTAL = (T3 + (N_TOTAL - 1) * firing_period)                      # total time for all droplets to finish
NUM_POINTS = 2000                                                   # resolution
# time vector containing all t values from 0 to T_TOTAL
t_global = np.linspace(0, T_TOTAL, NUM_POINTS)

# converts t values to appropriate array index
def get_index(time):
    index = np.floor(time * NUM_POINTS/T_TOTAL).astype(int)
    return index

# matrix to hold all positions for each droplet
# rows will be accessed and updated in for loop
# initialize arrays to starting position (0, 0, D)
x_array = np.zeros((N_TOTAL, NUM_POINTS))
y_array = np.zeros((N_TOTAL, NUM_POINTS))
z_array = np.zeros((N_TOTAL, NUM_POINTS)) + D

for i in range(N_TOTAL):
    if i < N1//2:
        sign = -1                   # sets the sign for the x voltage
        shift = 0                   # shift resets i so that voltage can update properly when transitioning between strokes
    else:
        sign = 1
        shift = N1 // 2

    # these are the global t values for each dot, i.
    # represents the actual time of occurrence, e.g. dot 1 is fired at t = 0, while dot 2 is fired at t = Tc.
    index0 = get_index(firing_period * i)               # time when fired
    index1 = get_index(firing_period * i + T1)          # time when enters capacitor
    index2 = get_index(firing_period * i + T2)          # time when exits capacitor
    index3 = get_index(firing_period * i + T3)          # time when hits wall

    # these are the local time vectors for each dot. this is what is actually plugged in for t depending on equation.
    # the subtraction ensures each vector is identical between iterations.
    t_local0 = t_global[index0:index3] - t_global[index0]     # full lifespan of each dot, ranges from t = 0 to T3
    t_local1 = t_global[index1:index2] - t_global[index1]     # T1 to T2, used for trajectory inside capacitor
    t_local2 = t_global[index2:index3] - t_global[index2]     # T2 to T3, used for trajectory after capacitor

    # Z POSITIONS                                             # all dots have the same z motion
    z_vector = z_array[i]                                     # access row i of array
    z_vector[index0:index3] = -v_z * t_local0 + D             # t_local0 used because the z motion is governed by one equation the entire time
    z_vector[index3:] = 0                                     # sets resting position
    z_array[i] = z_vector

    if i < N1:                                                                  # first N1 iterations draws the two vertical strokes
        # x kinematic values
        Vx = sign * (0.003 * m * w) / ((q * Tc) * (0.5 * Tc + T3 - T2))         # necessary x voltage to deflect drop by 3 mm
        Ex = Vx / w
        vx_exit = (q * Ex * Tc) / m                                             # x velocity after exiting capacitor
        x_exit = (q * Ex * Tc ** 2) / (2 * m)                                   # x position after exiting capacitor

        # y kinematic values
        Vy = V_step * (i - shift - np.floor(N1 / 4))                            # updates the y voltage each iteration
        Ey = Vy / w
        vy_exit = (q * Ey * Tc) / m                                             # y velocity after exiting capacitor
        y_exit = (q * Ey * Tc ** 2) / (2 * m)                                   # y velocity after exiting capacitor

        #  X POSITIONS
        x_vector = x_array[i]
        x_vector[index1: index2] = (q * Ex) / (2 * m) * t_local1 ** 2
        x_vector[index2: index3] = vx_exit * t_local2 + x_exit
        x_vector[index3:] = x_vector[index3 - 1]
        x_array[i] = x_vector

        # Y POSITIONS
        y_vector = y_array[i]
        y_vector[index1: index2] = (q * Ey) / (2 * m) * t_local1 ** 2
        y_vector[index2: index3] = vy_exit * t_local2 + y_exit
        y_vector[index3:] = y_vector[index3 - 1]
        y_array[i] = y_vector

    else:                   # last N2 iterations to draw horizontal stroke
        shift = N1
        Vx = V_step * (i - shift - np.floor(N2 / 2))            # updates the x voltage each iteration
        Ex = Vx / w
        vx_exit = (q * Ex * Tc) / m
        x_exit = (q * Ex * Tc ** 2) / (2 * m)

        # X POSITIONS
        x_vector = x_array[i]
        x_vector[index1: index2] = (q * Ex) / (2 * m) * t_local1 ** 2
        x_vector[index2: index3] = vx_exit * t_local2 + x_exit
        x_vector[index3:] = x_vector[index3 - 1]
        x_array[i] = x_vector



# PLOTTING SECTION
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')
ax.view_init(elev=-20, azim=70, roll=-180)

scat = ax.scatter(
    x_array[:, 0] * 1000,   # convert to mm
    y_array[:, 0] * 1000,
    z_array[:, 0] * 1000,
    s=5
)

# Axis labels in mm
ax.set_xlabel("X (mm)")
ax.set_ylabel("Y (mm)")
ax.set_zlabel("Z (mm)")

# Axis limits
ax.set_xlim(-3, 3)
ax.set_ylim(-3, 3)
ax.set_zlim(D * 1000, 0)   # change once you have real z data

# Time tracker text
time_text = ax.text2D(0.05, 0.95, "", transform=ax.transAxes)

# update function for animation
def update(frame):
    x = x_array[:, frame] * 1000  # convert to mm
    y = y_array[:, frame] * 1000
    z = z_array[:, frame] * 1000

    scat._offsets3d = (x, y, z)

    # Update time (ms)
    dt = t_global[1] - t_global[0]  # time step
    time_text.set_text(f"t = {frame * dt * 1000:.2f} ms")

    return scat, time_text

anim = FuncAnimation(
    fig,
    update,
    repeat=False,
    frames=NUM_POINTS,
    interval=1,
)

plt.show()
