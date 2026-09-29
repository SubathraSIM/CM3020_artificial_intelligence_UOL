# Import the required library
import pybullet as p
import pybullet_data as pd
import time

# Connect to PyBullet
p.connect(p.GUI)

# Configuration of the engine
p.setPhysicsEngineParameter(enableFileCaching=0)
p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0)

# Create the floor
plane_shape = p.createCollisionShape(p.GEOM_PLANE)
floor = p.createMultiBody(plane_shape, plane_shape)

# Set gravity
p.setGravity(0, 0, -10)

# Start the simulation loop
while True:
    p.stepSimulation()  # This keeps the simulation running
    time.sleep(1./240.)  # Adjust time step for realism (optional)
