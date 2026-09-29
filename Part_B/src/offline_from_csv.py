# Import the required library
import os 
import genome
import sys
import creature
import pybullet as p
import numpy as np

def main(csv_file):
    # check if the csv exist first
    assert os.path.exists(csv_file), "Tried to load " + csv_file + " but it does not exists"

    # pybullet with GUI 
    p.connect(p.DIRECT)
    p.setPhysicsEngineParameter(enableFileCaching=0)
    p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0)
    # Plane floor
    plane_shape = p.createCollisionShape(p.GEOM_PLANE)
    floor = p.createMultiBody(plane_shape, plane_shape)
    p.setGravity(0, 0, -10)

    # generate a random creature
    cr = creature.Creature(gene_count=1)
    dna = genome.Genome.from_csv(csv_file)
    cr.update_dna(dna)
    # save it to XML
    with open('test.urdf', 'w') as f:
        f.write(cr.to_xml())
    # load it into the sim
    rob1 = p.loadURDF('test.urdf')
    
    # air drop it
    p.resetBasePositionAndOrientation(rob1, [0, 0, 2.5], [0, 0, 0, 1])
    start_pos, orn = p.getBasePositionAndOrientation(rob1)

    # iterate 
    elapsed_time = 0
    wait_time = 1.0/240 # seconds
    total_time = 30 # seconds
    step = 0
    while True:
        # simulation forward by 1 step
        p.stepSimulation()
        step += 1
        # updated motors every 24 steps
        if step % 24 == 0:
            motors = cr.get_motors()
            # number of joints equal to number of motors
            assert len(motors) == p.getNumJoints(rob1), "Something went wrong"
            # apply velocity control to the joints
            for jid in range(p.getNumJoints(rob1)):
                mode = p.VELOCITY_CONTROL
                vel = motors[jid].get_output()
                p.setJointMotorControl2(rob1, 
                            jid,  
                            controlMode=mode, 
                            targetVelocity=vel)
            # the creature new position
            new_pos, orn = p.getBasePositionAndOrientation(rob1)

            # straight line distance 
            dist_moved = np.linalg.norm(np.asarray(start_pos) - np.asarray(new_pos))
            print(dist_moved)

        # stop after total_time seconds
        elapsed_time += wait_time
        if elapsed_time > total_time:
            break

    # print the last distance moved
    print("TOTAL DISTANCE MOVED:", dist_moved)

if __name__ == "__main__":
    # need to pass csv file name
    assert len(sys.argv) == 2, "Usage: python playback_test.py csv_filename"
    main(sys.argv[1])