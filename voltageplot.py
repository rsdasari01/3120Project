import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# --- Physical Parameters (Used only for Time Scale) ---
L1 = 0.0005  # Length of capacitor plates
v_x = 20  # Constant horizontal velocity
T_TOTAL = 0.012  # Total simulation duration (12ms)

# Calculated time spent in the capacitor
T_inCap = L1 / v_x
# T_wall (Time from firing to impact) = 1.5e-4 s
FIRING_INTERVAL = 2.5e-5

# --- SIMULATION CONTROL PARAMETERS (6mm line @ 300 DPI) ---
DROPLETS_TO_SIMULATE = 71  # Total dots required (70 + 1 center dot)
V_START = 2610.11  # Starting voltage for droplet 1
V_END = -2610.11  # Ending voltage for droplet 71

# Calculated voltage step per droplet interval
V_RANGE = V_START - V_END
V_STEP = V_RANGE / (DROPLETS_TO_SIMULATE - 1)  # 70 intervals

# --- 1. Generate Staircase Data ---

# 71 discrete voltage levels
discrete_voltages = np.array([V_START - j * V_STEP for j in range(DROPLETS_TO_SIMULATE)])

# 71 firing start times
start_times = np.array([j * FIRING_INTERVAL for j in range(DROPLETS_TO_SIMULATE)])

# Create the full staircase arrays (2 * 71 = 142 points)
# Voltage array: [V0, V0, V1, V1, V2, V2, ...]
V_staircase = np.repeat(discrete_voltages, 2)

# Time array: [t0, t1, t1, t2, t2, t3, ...]
t_staircase = np.empty(len(V_staircase))
t_staircase[0::2] = start_times  # Start of each step
# End of each step is the start of the next one. We must add the final time point.
t_staircase[1::2] = np.append(start_times[1:], start_times[-1] + FIRING_INTERVAL)

# --- 2. Setup Plot and Animation ---

fig, ax = plt.subplots(figsize=(10, 6))
ax.set_title(f'Animated Voltage Signal: {V_START:.2f} V to {V_END:.2f} V', fontsize=14)
ax.set_xlabel('Time (s)')
ax.set_ylabel('Applied Voltage (V)')
ax.grid(True, linestyle='--', alpha=0.7)

# Set the limits slightly wider than the data
ax.set_xlim(-0.0005, t_staircase[-1] + 0.0005)
ax.set_ylim(V_END * 1.1, V_START * 1.1)

# Initialize the plot line (removed the markers plot object)
line, = ax.plot([], [], drawstyle='steps-post', color='#3b82f6', linewidth=2)


# Function to initialize the background of the animation
def init():
    line.set_data([], [])
    return line,


# Function called at each frame of the animation
def update(frame):
    # 'frame' is the index of the current point in the staircase array (0 to 141)

    # Update the staircase line up to the current frame index
    line.set_data(t_staircase[:frame], V_staircase[:frame])

    # Return only the updated line object
    return line,


# Create the animation
# frames=len(t_staircase) gives us 142 frames (one for each point in the staircase)
# interval=50 means 50ms per frame
ani = animation.FuncAnimation(fig, update, frames=len(t_staircase),
                              init_func=init, blit=True, interval=50)

# Save the animation as an MP4 file
print("Saving animation to 'animated_voltage_plot.mp4'...")
try:
    # Save with a high enough frame rate for smooth visualization
    ani.save('animated_voltage_plot.mp4', writer='ffmpeg', fps=20)
    print("Animation successfully saved.")
except Exception as e:
    print(f"Could not save animation (FFmpeg might be missing): {e}")

# Display the final plot (non-animated) after saving the file
plt.show()