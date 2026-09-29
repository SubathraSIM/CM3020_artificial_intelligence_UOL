# Import the required library
import os 
import genome
import sys
import creature
import pybullet as p
import time 
import numpy as np
import cw_envt


def main(csv_file):
    # check if the csv exist first
    assert os.path.exists(csv_file), "Tried to load " + csv_file + " but it does not exists"

    # pybullet with GUI 
    p.connect(p.GUI)
    p.setPhysicsEngineParameter(enableFileCaching=0)
    p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0)
    p.setGravity(0, 0, -10)

    # Mountain arena was integrated by me
    arena_size = 20
    cw_envt.make_arena(arena_size=arena_size)
    mountain_position = [0, 0, -1]
    mountain_orientation = p.getQuaternionFromEuler([0, 0, 0])
    p.setAdditionalSearchPath("shapes")
    # can change and load the different landscapes here 
    p.loadURDF(
        "gaussian_pyramid.urdf",
        # "hills.urdf",
        # "valleys.urdf",
        mountain_position,
        mountain_orientation,
        useFixedBase=1
    )

    # generate a random creature
    cr = creature.Creature(gene_count=1)
    dna = genome.Genome.from_csv(csv_file)
    cr.update_dna(dna)
    # save it to XML
    with open('test.urdf', 'w') as f:
        f.write(cr.to_xml())
    # load it into the sim
    rob1 = p.loadURDF('test.urdf')

    # start position changed by me no more air drop 
    p.resetBasePositionAndOrientation(rob1, [6.0, 0.0, 2.5], [0, 0, 0, 1])
    start_pos, orn = p.getBasePositionAndOrientation(rob1)
    cr.update_position(start_pos)

    # iterate
    elapsed_time = 0
    wait_time = 1.0/240 # seconds
    total_time = 30 # seconds
    step = 0

    # Anti-cheat checking if the creature leaves the arena
    half = arena_size / 2
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
                # velocity and force has been increased just for visual purpose only
                p.setJointMotorControl2(rob1, 
                            jid,  
                            controlMode=mode, 
                            targetVelocity=vel * 5,
                            force=50)
            # the creature new position
            new_pos, orn = p.getBasePositionAndOrientation(rob1)
            cr.update_position(new_pos)

            # Anti cheat functions to stop if creatures leaves arena
            if abs(new_pos[0]) > half or abs(new_pos[1]) > half:
                cr.out_of_bounds = True
                cr.cheated = True
                print("Out of bounds", new_pos)
                break

            # Anti cheat funciton to stop the creature flying 
            flyingair = p.getContactPoints(bodyA=rob1)
            airborne = True
            for check in flyingair:
                body = check[2]
                if body != rob1:
                    airborne = False
                    break
            # count the number of steps for airborne
            if airborne:
                cr.airbornenumber += 1
            else:
                cr.airbornenumber = 0
            # stops is flying for too long
            if cr.airbornenumber > 480:
                cr.cheated = True
                print("CHEAT: airborne too long", cr.airbornenumber, new_pos)
                break
            
            # straight line distance 
            dist_moved = np.linalg.norm(np.asarray(start_pos) - np.asarray(new_pos))
            print(dist_moved)
        
        # slow down the replay
        time.sleep(wait_time)
        elapsed_time += wait_time

        # stop after total_time seconds
        if elapsed_time > total_time:
            break
    
    # print the last distance moved
    print("TOTAL DISTANCE MOVED:", dist_moved)

if __name__ == "__main__":
    # need to pass csv file name 
    assert len(sys.argv) == 2, "Usage: python playback_test.py csv_filename"
    main(sys.argv[1])

