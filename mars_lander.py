import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# 1. CONFIGURATION
MARS_RADIUS = 3389500.0
MARS_GRAVITY_PARAM = 4.2828e13
ATMOS_DENSITY_0 = 0.02
ATMOS_SCALE_HEIGHT = 11100.0 

# Lander Specs
START_MASS, DRY_MASS = 992.0, 600.0
SHIELD_MASS = 150.0      
FUEL_BURN_RATE = 12.0  
MAX_THRUST = 8000   
DRAG_COEFF = 1.7
SHIELD_AREA = 9.6        # Surface area for shield
LANDER_AREA = 2.0        # Small area after shield is ejected

BURN_START_ALTITUDE = 2200.0 

# 2. PHYSICS FUNCTIONS

def get_air_density(altitude):
    return ATMOS_DENSITY_0 * math.exp(-altitude / ATMOS_SCALE_HEIGHT) if altitude < 120000 else 0.0

def get_net_acceleration(px, py, vx, vy, current_mass, thrust, density, current_area):
    v_mag = math.sqrt(vx**2 + vy**2)
    r_mag = math.sqrt(px**2 + py**2)
    
    # Directions
    angle_v = math.atan2(vy, vx)
    angle_p = math.atan2(py, px)
    
    # Forces
    grav_force = (MARS_GRAVITY_PARAM / (r_mag**2)) * current_mass
    drag_force = 0.5 * density * (v_mag**2) * DRAG_COEFF * current_area
    
    # Net acceleration components (Thrust opposite to velocity)
    ax = (-(drag_force + thrust) * math.cos(angle_v) - grav_force * math.cos(angle_p)) / current_mass
    ay = (-(drag_force + thrust) * math.sin(angle_v) - grav_force * math.sin(angle_p)) / current_mass
    
    return ax, ay

# 3. MISSION SIMULATION

def run_suicide_burn_mission():
    px, py = 0.0, MARS_RADIUS + 120000.0
    v_start, entry_angle = 3600.0, math.radians(-8)
    vx, vy = v_start * math.cos(entry_angle), v_start * math.sin(entry_angle)
    
    dt, time = 0.1, 0.0
    current_fuel = START_MASS - DRY_MASS
    history = {
    'dist': [], 'alt': [], 'v': [], 'q': [], 
    'g': [], 'theta': [], 'r': [], 'mass': [], 'engine': []}

    while True:
        r_mag = math.sqrt(px**2 + py**2)
        alt = r_mag - MARS_RADIUS
        if alt <= 0: break
        
        # JETTISON & BURN LOGIC
        engine_on = (alt < BURN_START_ALTITUDE) and (current_fuel > 0)
        
        if engine_on:
            current_area = LANDER_AREA
            current_dry_mass = DRY_MASS - SHIELD_MASS
            thrust = MAX_THRUST
            current_fuel -= FUEL_BURN_RATE * dt
        else:
            current_area = SHIELD_AREA
            current_dry_mass = DRY_MASS
            thrust = 0.0
            
        current_mass = current_dry_mass + max(0, current_fuel)
        rho = get_air_density(alt)
        v_mag = math.sqrt(vx**2 + vy**2)
        
        ax, ay = get_net_acceleration(px, py, vx, vy, current_mass, thrust, rho, current_area)
        
        # Log data
        history['dist'].append(MARS_RADIUS * math.atan2(px, py))
        history['alt'].append(alt)
        history['v'].append(v_mag)
        history['q'].append(0.5 * rho * v_mag**2)
        history['g'].append(math.sqrt(ax**2 + ay**2) / 3.71) # Shown in Mars Gs
        history['theta'].append(math.atan2(px, py))
        history['r'].append(r_mag)
        history['mass'].append(current_mass)
        history['engine'].append(engine_on)

        vx += ax * dt; vy += ay * dt
        px += vx * dt; py += vy * dt
        time += dt
        
    return history

# 4. DASHBOARD

data = run_suicide_burn_mission()
fig = plt.figure(figsize=(16, 10), facecolor='#fdfdfd')

# Creating a 2x3 grid layout
ax_traj = plt.subplot2grid((2, 3), (0, 0))
ax_vel  = plt.subplot2grid((2, 3), (0, 1))
ax_q    = plt.subplot2grid((2, 3), (0, 2))
ax_g    = plt.subplot2grid((2, 3), (1, 0))
ax_pol  = plt.subplot2grid((2, 3), (1, 1), projection='polar')
ax_empty = plt.subplot2grid((2, 3), (1, 2)) # Extra slot for mass/stats later
ax_empty.axis('off')

# Plot list for easy updating
plots = [ax_traj, ax_vel, ax_q, ax_g]

# Initial setup for all altitude-based plots
for ax in plots:
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-5000, 130000)
    ax.set_ylabel("Altitude (m)")

# Specific axis limits and titles
ax_traj.set_xlim(-5000, max(data['dist']) * 1.05)
ax_traj.set_title("Ground Track")
ax_traj.set_xlabel("Downrange (m)")

ax_vel.set_xlim(0, max(data['v']) * 1.1)
ax_vel.set_title("Velocity vs Altitude")
ax_vel.set_xlabel("Velocity (m/s)")

ax_q.set_xlim(0, max(data['q']) * 1.1)
ax_q.set_title("Dynamic Pressure")
ax_q.set_xlabel("Pressure (Pa)")

ax_g.set_xlim(0, max(data['g']) * 1.1)
ax_g.set_title("Deceleration (Mars G's)")
ax_g.set_xlabel("G-Force")

# Polar setup
ax_pol.set_theta_zero_location('N'); ax_pol.set_theta_direction(-1)
ax_pol.plot(np.linspace(0, 2*np.pi, 100), [MARS_RADIUS]*100, color='#c0392b', lw=2)
line_pol, = ax_pol.plot([], [], color='teal', lw=2)
point_pol, = ax_pol.plot([], [], 'ro', markersize=4)
ax_pol.set_ylim(0, MARS_RADIUS + 130000); ax_pol.set_yticklabels([])
ax_pol.set_title("Global View", pad=20)

# HUD text
hud = ax_traj.text(0.05, 0.65, '', transform=ax_traj.transAxes, fontfamily='monospace', weight='bold', fontsize=9)

# Create line objects for all graphs
line_objects = [ax.plot([], [], lw=2)[0] for ax in plots]
# Set specific colors
line_objects[0].set_color('teal')   # Trajectory
line_objects[1].set_color('orange') # Velocity
line_objects[2].set_color('purple') # Max Q
line_objects[3].set_color('red')    # G-force
# Add points for the current position
points = [ax.plot([], [], 'ro', markersize=5)[0] for ax in plots]

plt.tight_layout()

def update(frame):
    idx = frame * 20 
    if idx >= len(data['dist']): idx = len(data['dist']) - 1
    
    # Update all 1D plots
    line_objects[0].set_data(data['dist'][:idx], data['alt'][:idx])
    line_objects[1].set_data(data['v'][:idx], data['alt'][:idx])
    line_objects[2].set_data(data['q'][:idx], data['alt'][:idx])
    line_objects[3].set_data(data['g'][:idx], data['alt'][:idx])
    
    # Update red dots
    points[0].set_data([data['dist'][idx]], [data['alt'][idx]])
    points[1].set_data([data['v'][idx]], [data['alt'][idx]])
    points[2].set_data([data['q'][idx]], [data['alt'][idx]])
    points[3].set_data([data['g'][idx]], [data['alt'][idx]])
    
    # Update Polar
    line_pol.set_data(data['theta'][:idx], data['r'][:idx])
    point_pol.set_data([data['theta'][idx]], [data['r'][idx]])
    
    eng = "ON (SHIELD EJECTED)" if data['engine'][idx] else "OFF (AEROSHELL ON)"
    hud.set_text(f"ALT: {data['alt'][idx]/1000:5.1f}km\nVEL: {data['v'][idx]:5.0f}m/s\n"
                 f"MASS: {data['mass'][idx]:4.0f}kg\nENGINE: {eng}")
    
    return line_objects + points + [line_pol, point_pol, hud]

ani = FuncAnimation(fig, update, frames=len(data['dist']) // 20, blit=True, interval=40, repeat=True)

plt.show()
