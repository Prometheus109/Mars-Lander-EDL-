# Mars-Lander-EDL-
Physics-based Mars lander simulation. Models atmospheric drag, variable vehicle mass, and suicide burn trajectories.

About this project

I wanted to see if I could recreate the "7 Minutes of Terror" using Python. This simulation follows a lander from the moment it hits the Martian atmosphere until it (hopefully) touches down safely.

The program doesn't just treat the lander like a point in space. It accounts for the way the air gets thicker as you drop, and it handles the high-stakes moment where the heat shield gets kicked away to make room for the landing rockets. I spent a lot of time tweaking the "Suicide Burn" logic to make sure the engine fires at just the right altitude to kill our velocity before we hit the dirt.

Engineering Assumptions & Design Basis

I based the vehicle specs on "Discovery-class" landers (like Phoenix or InSight), which are designed for direct-descent powered landings rather than the complex SkyCrane used by the larger rovers.

    Starting Altitude (120km): I chose 120km because that is the "Entry Interface." It’s the point where the Martian atmosphere finally becomes thick enough to actually exert force on a spacecraft traveling at orbital speeds.

    Mass (992kg Entry / 600kg Dry): These numbers reflect a mid-sized lander. The ~400kg difference accounts for the propellant needed for the final descent and the heavy structural weight of the aeroshell/heat shield.

    Mass Flow Rate (12 kg/s): This is based on the fuel consumption of high-thrust hydrazine thrusters. To kill thousands of kilometers of velocity in just a few seconds, you have to throw a lot of mass out of the engine very quickly.

    Surface Density (0.02 kg/m³): I purposely set the atmospheric density slightly higher than the "average" Martian day. I wanted to simulate a "thick" atmosphere day (like during a dust storm) to see how the drag profile handles higher structural loads.

    The "Suicide Burn" Trigger: I set the engine ignition to 2,500m. In a real mission, this is usually triggered by a radar altimeter once the lander has slowed down enough for the heat shield to be safely jettisoned without the air ripping the internal components apart.
    
What I modeled

    Atmospheric Entry: I used an exponential decay model for the air density. Even though Mars has a thin atmosphere, hitting it at 3,600 m/s still generates a massive amount of drag.

    Jettison Sequence: At 2,500 meters, the ship changes. It loses the 150kg heat shield, which changes its weight and its aerodynamics instantly.

    Powered Landing: The lander uses a 8,000N retro-rocket. The mass of the ship actually goes down as the fuel burns away, which makes the physics a little more complicated but much more realistic.

    Live Telemetry: I built a dashboard that shows the G-forces, the "Max Q" (dynamic pressure), and the velocity profile so you can see exactly where the ship is under the most stress.

Dependencies:

    NumPy: To handle the maths for the planet's curvature.

    Matplotlib: This is what powers the dashboard and the live animations.
    
    

    Feel free to reach out if you have ideas on how to make the more accurate!
