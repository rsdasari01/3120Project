import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

I_TRUE = False
H_TRUE = False
while not I_TRUE and not H_TRUE:
    IorH = input("Select I or H. ")
    if IorH == "I":
        I_TRUE = True
    if IorH == "H":
        H_TRUE = True

# DROPLET CONSTANTS
droplet_diameter = input("Enter droplet diameter in um (default = 84): ")
droplet_diameter = float(droplet_diameter) * 10**-6
r = droplet_diameter / 2
q = input("Enter droplet charge in nC (default = 0.19): ")
q = float(q) * 10**-9
droplet_density = 1000
droplet_volume = (4/3)*(np.pi * r**3)
m = droplet_density * droplet_volume

# SETUP
L0 = 1.25/1000                                          # distance from gun to capacitor
L1 = input("Enter L1 in mm (default = 0.5): ")          # length of capacitor
L1 = float(L1)/1000
L2 = input("Enter L2 in mm (default = 1.25): ")         # distance capacitor to wall
L2 = float(L2)/1000
D = L0 + L1 + L2                                        # total distance
w = 1/1000                                              # width between plates
dpm = 300/0.0254                                        # 300 dpi to dpm

# KINEMATIC CONSTANTS
v_z = float(input("Enter speed  in m/s (default = 20): "))
Tc = L1 / v_z                                           # time spent inside capacitor
T1 = L0 / v_z                                           # time at capacitor entry
T2 = T1 + Tc                                            # time at capacitor exit
T3 = D / v_z                                            # time at wall contact
# 1/Tc is the fastest possible firing rate. anything faster would result in multiple droplets being in the capacitor at the same time.
firing_period = Tc
# necessary voltage step for 300 dpi
V_step = ( ( (q*Tc)/(m*w) ) * (Tc/2 + (T3 - T2)) * dpm ) ** -1

# calculate the largest possible line in both directions
V_max = (w/2 * 2 * m * w) / (q*Tc**2)                               # maximum possible voltage
v_exit = (q * V_max * Tc) / (w*m)                                   # exit velocity
cruise_distance = v_exit * (L2/v_z)                                 # displacement after capacitor
max_length = 2*(cruise_distance + w/2)                              # Largest possible line
max_width = max_length                                              # Same in both directions because capacitors are symmetrical
N1 = 2 * (np.floor(dpm * max_length).astype(int) + 1)               # number of dots required for vertical stroke
N2 = np.floor(dpm * max_width).astype(int) + 1                      # number of dots required for horizontal stroke

if I_TRUE:
    N_TOTAL = N1 // 2
else:
    N_TOTAL = N1 + N2
T_TOTAL = (T3 + (N_TOTAL - 1) * firing_period)                      # total time for all droplets to finish
NUM_POINTS = 5000                                                   # resolution
# time vector containing all t values from 0 to T_TOTAL
t_global = np.linspace(0, T_TOTAL, NUM_POINTS)

# converts t values to appropriate array index
def get_index(time):
    index = np.floor(time * NUM_POINTS/T_TOTAL).astype(int)
    return index

# matrix to hold all positions for each droplet
# rows will be accessed and updated in for loop below
# initialize arrays to starting position (0, 0, D)
x_array = np.zeros((N_TOTAL, NUM_POINTS))
y_array = np.zeros((N_TOTAL, NUM_POINTS))
z_array = np.zeros((N_TOTAL, NUM_POINTS)) + D

# Initialize array to hold voltage values
Vx_array = np.zeros(N_TOTAL)
Vy_array = np.zeros(N_TOTAL)

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
    z_vector = z_array[i]
    z_vector[index0:index3] = -v_z * t_local0 + D             # t_local0 used because the z motion is governed by one equation the entire time
    z_vector[index3:] = 0                                     # set resting position
    z_array[i] = z_vector                                     # update row i of z_array

    if i < N1:                                                                  # first N1 iterations draws the two vertical strokes
        # x kinematic values
        if I_TRUE:
            Vx = 0
        else:
            # necessary x voltage to deflect in x direction for H
            Vx = sign * (0.5 * max_width * m * w) / ((q * Tc) * (0.5 * Tc + T3 - T2))

        Vx_array[i] = Vx
        Ex = Vx / w
        vx_exit = (q * Ex * Tc) / m                                             # x velocity after exiting capacitor
        x_exit = (q * Ex * Tc ** 2) / (2 * m)                                   # x position after exiting capacitor

        # y kinematic values
        Vy = V_step * (i - shift - np.floor(N1 / 4))                            # updates the y voltage each iteration
        Vy_array[i] = Vy
        Ey = Vy / w
        vy_exit = (q * Ey * Tc) / m                                             # y velocity after exiting capacitor
        y_exit = (q * Ey * Tc ** 2) / (2 * m)                                   # y velocity after exiting capacitor

        #  X POSITIONS
        x_vector = x_array[i]
        x_vector[index1: index2] = (q * Ex) / (2 * m) * t_local1 ** 2           # different t_local used for piecewise function
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
        Vx_array[i] = Vx
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

# Axis labels in mm
ax.set_xlabel("X (mm)")
ax.set_ylabel("Y (mm)")
ax.set_zlabel("Z (mm)")

axis_max = max_length*1000 + 1

# Axis limits
ax.set_xlim(-axis_max, axis_max)
ax.set_ylim(-axis_max, axis_max)
ax.set_zlim(1000*D, 0)

#Capacitor Plates
# Adjustable small corner gap (mm) so plate edges don't meet at corners
gap_mm = 0.2  # change this to increase/decrease the corner gap (mm)

# Plate center positions (mm)
y_min = (-w * 1000)/2
y_max = (w * 1000)/2

# Z bounds for the capacitor (mm), lifted by L2
z_plane = np.array([L2 * 1000, (L1 + L2) * 1000])

# Left/Right plates: keep x positions at +/- w but shorten their y-extent
y_lr_min = y_min + gap_mm/2
y_lr_max = y_max - gap_mm/2
y_plane_lr = np.array([y_lr_min, y_lr_max])
Y_left, Z_left = np.meshgrid(y_plane_lr, z_plane)
X_left = np.full_like(Y_left, (-w * 1000)/2)  # left plate at x = -w (mm)
ax.plot_surface(X_left, Y_left, Z_left, alpha=0.5, color='blue')

X_right = np.full_like(Y_left, (w * 1000)/2)  # right plate at x = +w (mm)
ax.plot_surface(X_right, Y_left, Z_left, alpha=0.5, color='blue')

# Front/Backplates: keep y positions at +/- w but shorten their x-extent
x_fb_min = y_min + gap_mm/2
x_fb_max = y_max - gap_mm/2
x_plane_fb = np.array([x_fb_min, x_fb_max])
X_front, Z_front = np.meshgrid(x_plane_fb, z_plane)
Y_front = np.full_like(X_front, (-w * 1000)/2)  # front plate at y = -w (mm)
ax.plot_surface(X_front, Y_front, Z_front, alpha=0.5, color='green')

# Backplate at y = +w (mm)
Y_back = np.full_like(X_front, (w * 1000)/2)
ax.plot_surface(X_front, Y_back, Z_front, alpha=0.5, color='green')

# Draw droplet gun (cylindrical nozzle with conical tip)
# All dimensions here are in mm for plotting; the tip end is located at z = D (paper distance)
gun_radius_mm = 0.5      # cylinder main radius (mm)
tip_radius_mm = 0.1      # tip end radius (mm)
tip_length_mm = 0.5      # length of the conical tip (mm)
body_length_mm = 1.0     # length of the cylindrical body above the tip (mm)

# Z positions (mm)
tip_end_z_mm = D * 1000
tip_start_z_mm = tip_end_z_mm + tip_length_mm
body_end_z_mm = tip_start_z_mm + body_length_mm

# Mesh for tip (cone)
theta = np.linspace(0, 2 * np.pi, 40)
z_tip = np.linspace(tip_end_z_mm, tip_start_z_mm, 20)
Theta_tip, Z_tip = np.meshgrid(theta, z_tip)
R_tip = tip_radius_mm + (Z_tip - tip_end_z_mm) / tip_length_mm * (gun_radius_mm - tip_radius_mm)
X_tip = R_tip * np.cos(Theta_tip)
Y_tip = R_tip * np.sin(Theta_tip)
ax.plot_surface(X_tip, Y_tip, Z_tip, color='gray', alpha=0.8, linewidth=0, shade=True)

# Mesh for body (cylinder)
z_body = np.linspace(tip_start_z_mm, body_end_z_mm, 20)
Theta_body, Z_body = np.meshgrid(theta, z_body)
R_body = np.full_like(Z_body, gun_radius_mm)
X_body = R_body * np.cos(Theta_body)
Y_body = R_body * np.sin(Theta_body)
ax.plot_surface(X_body, Y_body, Z_body, color='dimgray', alpha=0.8, linewidth=0, shade=True)

scat = ax.scatter(
    x_array[:, 0] * 1000,   # convert to mm
    y_array[:, 0] * 1000,
    z_array[:, 0] * 1000,
    s=5
)

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

FRAME_STEP = 20
anim = FuncAnimation(
    fig,
    update,
    repeat=False,
    frames=range(0, NUM_POINTS, FRAME_STEP),
    interval=1,
)

firing_times_ms = np.arange(N_TOTAL) * firing_period * 1000

fig_volt, (ax_vx, ax_vy) = plt.subplots(2, 1, figsize=(8, 8), sharex=True)
fig_volt.suptitle(f'Deflection Voltages vs Time (Shape: {"I" if I_TRUE else "H"})')

# Plot X Voltage
ax_vx.step(firing_times_ms, Vx_array, where='post', color='red', label='Vx (Horizontal)')
ax_vx.set_ylabel('Voltage X (V)')
ax_vx.grid(True, linestyle='--', alpha=0.6)
ax_vx.legend(loc='upper right')

# Plot Y Voltage
ax_vy.step(firing_times_ms, Vy_array, where='post', color='blue', label='Vy (Vertical)')
ax_vy.set_xlabel('Firing Time (ms)')
ax_vy.set_ylabel('Voltage Y (V)')
ax_vy.grid(True, linestyle='--', alpha=0.6)
ax_vy.legend(loc='upper right')

plt.tight_layout()
plt.show()
