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
Tc = L1 / v_z                                           # time in capacitor
T1 = L0 / v_z                                           # time to enter capacitor
T2 = T1 + Tc                                            # time to exit capacitor
T3 = D / v_z                                            # time to hit wall
firing_period = Tc
V_step = ( ( (q*Tc)/(m*w) ) * (Tc/2 + (T3 - T2)) * dpm ) ** -1          # necessary voltage step for 300 dpi



length_to_draw = .006                                                   # length of line
N = np.floor(dpm * length_to_draw).astype(int) + 1                                # number of dots required
T_TOTAL = (T3 + (N - 1) * firing_period)                                  # total time for all droplets to finish

NUM_POINTS = 1000
t_global = np.linspace(0, T_TOTAL, NUM_POINTS)

def get_index(time):
    index = np.floor(time * NUM_POINTS/T_TOTAL).astype(int)
    return index

x_array = np.zeros((N, NUM_POINTS))
y_array = np.zeros((N, NUM_POINTS))
z_array = np.zeros((N, NUM_POINTS)) + D

for i in range(N):
    # Time
    index0 = get_index(firing_period * i)
    index1 = get_index(firing_period * i + T1)
    index2 = get_index(firing_period * i + T2)
    index3 = get_index(firing_period * i + T3)
    t_local0 = t_global[index0:index3] - t_global[index0]
    t_local1 = t_global[index1:index2] - t_global[index1]
    t_local2 = t_global[index2:index3] - t_global[index2]

    # Kinematics
    Vx = (0.001 * m * w) / ((q * Tc) * (0.5 * Tc + T3 - T2))
    Ex = Vx / w
    vx_exit = (q * Ex * Tc) / m
    x_exit = (q * Ex * Tc ** 2) / (2 * m)

    Vy = V_step * (i - np.floor(N / 2))
    Ey = Vy / w
    vy_exit = (q * Ey * Tc) / m
    y_exit = (q * Ey * Tc ** 2) / (2 * m)

    # z positions
    z_vector = z_array[i]
    z_vector[index0:index3] = -v_z * t_local0 + D
    z_vector[index3:] = 0
    z_array[i] = z_vector

    # y positions
    y_vector = y_array[i]
    y_vector[index1: index2] = (q * Ey) / (2 * m) * t_local1 ** 2
    y_vector[index2: index3] = vy_exit * t_local2 + y_exit
    y_vector[index3:] = y_vector[index3 - 1]
    y_array[i] = y_vector

    # x positions
    x_vector = x_array[i]
    x_vector[index1: index2] = (q * Ex) / (2 * m) * t_local1 ** 2
    x_vector[index2: index3] = vx_exit * t_local2 + x_exit
    x_vector[index3:] = x_vector[index3 - 1]
    x_array[i] = x_vector

dt = t_global[1] - t_global[0]
N_drops = x_array.shape[0]

fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')
ax.view_init(elev=-20, azim=70, roll=-180)

scat = ax.scatter(
    x_array[:, 0] * 1000,
    y_array[:, 0] * 1000,
    z_array[:, 0] * 1000,
    s=5
)

# Axis labels in mm
ax.set_xlabel("X (mm)")
ax.set_ylabel("Y (mm)")
ax.set_zlabel("Z (mm)")

# Axis limits (mm)
ax.set_xlim(-3, 3)
ax.set_ylim(np.min(y_array) * 1000,
            np.max(y_array) * 1000)
ax.set_zlim(D * 1000, 0)   # change once you have real z data

# Time tracker text (upper-left)
time_text = ax.text2D(0.05, 0.95, "", transform=ax.transAxes)

# ------------------------------------------------------------
# UPDATE FUNCTION FOR ANIMATION
# ------------------------------------------------------------
def update(frame):
    x = x_array[:, frame] * 1000  # convert to mm
    y = y_array[:, frame] * 1000
    z = z_array[:, frame] * 1000

    scat._offsets3d = (x, y, z)

    # Update time (ms)
    time_text.set_text(f"t = {frame * dt * 1000:.2f} ms")

    return scat, time_text

# ------------------------------------------------------------
# ANIMATION DRIVER
# ------------------------------------------------------------
anim = FuncAnimation(
    fig,
    update,
    frames=NUM_POINTS,
    interval=1,   # 1 ms per frame (adjust if needed)
    blit=False
)

plt.show()
