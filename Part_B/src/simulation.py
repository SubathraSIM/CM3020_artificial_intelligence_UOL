# Import the required library
import pybullet as p
from multiprocessing import Pool
import cw_envt

class Simulation: 
    def __init__(self, sim_id=0, motor_blend=False):
        # pybullet simulation in direct mode
        self.physicsClientId = p.connect(p.DIRECT)
        # sim id
        self.sim_id = sim_id
        # if true, creature will use the blended motor mode the advanced part
        self.motor_blend = motor_blend

    def run_creature(self, cr, iterations=2400):
        # one creature run for 2400 iterations
        pid = self.physicsClientId
        # reset the simulation
        p.resetSimulation(physicsClientId=pid)
        p.setPhysicsEngineParameter(enableFileCaching=0, physicsClientId=pid)
        # set gravity
        p.setGravity(0, 0, -10, physicsClientId=pid)
        # Integrate the mountain arena instead of the floor
        arena_size = 20
        cw_envt.make_arena(arena_size=arena_size)

        mountain_position = [0, 0, -1]
        mountain_orientation = p.getQuaternionFromEuler([0, 0, 0])
        p.setAdditionalSearchPath("shapes", physicsClientId=pid)
        p.loadURDF("gaussian_pyramid.urdf",  mountain_position,
            mountain_orientation,
            useFixedBase=1,
            physicsClientId=pid)

        # use this codes if running in the hills or valleys environment
        # p.loadURDF("hills.urdf",  mountain_position,
        #     mountain_orientation,
        #     useFixedBase=1,
        #     physicsClientId=pid)

        # p.loadURDF("valleys.urdf",  mountain_position,
        #     mountain_orientation,
        #     useFixedBase=1,
        #     physicsClientId=pid)

        # save creature urdf to urdf file
        xml_file = 'temp' + str(self.sim_id) + '.urdf'
        xml_str = cr.to_xml()
        with open(xml_file, 'w') as f:
            f.write(xml_str)

        # load the creature urdf
        try:
            cid = p.loadURDF(xml_file, physicsClientId=pid)
        except Exception:
            cr.cheated = True
            return
        # pybullet invalid id, failed creature
        if cid < 0:
            cr.cheated = True
            return
        # spawn creature near the mountain if not consider as cheated
        try:
            p.resetBasePositionAndOrientation(cid, [6.0, 0.0, 2.5], [0, 0, 0, 1], physicsClientId=pid)
            spawn_pos, _ = p.getBasePositionAndOrientation(cid, physicsClientId=pid)
        except Exception:
            cr.cheated = True
            return
        # position track
        cr.update_position(spawn_pos)
        # see if creature out of arena
        half = arena_size / 2

        for step in range(iterations):
            p.stepSimulation(physicsClientId=pid)
            # update every 24 steps
            if step % 24 == 0:
                self.update_motors(cid=cid, cr=cr)
            # current position store for fitness
            pos, orn = p.getBasePositionAndOrientation(cid, physicsClientId=pid)
            cr.update_position(pos)

            # anti-cheat function to stop if creature leaves the arena
            if abs(pos[0]) > half or abs(pos[1]) > half:
                cr.out_of_bounds = True
                cr.cheated = True
                break

            # anti-cheat function is creature flying in the air
            flyingair = p.getContactPoints(bodyA=cid, physicsClientId=pid)
            airborne = True
            for check in flyingair:
                # id of the other body in contact
                body = check[2]
                # ignore the self contact
                if body != cid:
                    airborne = False
                    break

            # aiborne steps count
            if airborne:
                cr.airbornenumber += 1
            else:
                cr.airbornenumber = 0
            # if airborne too long, creature cheat
            if cr.airbornenumber > 480:
                cr.cheated = True
                break
    
    def update_motors(self, cid, cr):
        """
        cid is the id in the physics engine
        cr is a creature object
        """
        # loop all joint and apply force and velocity
        for jid in range(p.getNumJoints(cid,
                                        physicsClientId=self.physicsClientId)):
            m = cr.get_motors(blend=self.motor_blend)[jid]
            p.setJointMotorControl2(cid, jid, 
                    controlMode=p.VELOCITY_CONTROL, 
                    targetVelocity=m.get_output(), 
                    force = 50, 
                    physicsClientId=self.physicsClientId)
        
    def eval_population(self, pop, iterations):
        # evaluate every creature
        for cr in pop.creatures:
            self.run_creature(cr, 2400) 


class ThreadedSim():
    def __init__(self, pool_size):
        # multiple simulation objects 
        self.sims = [Simulation(i) for i in range(pool_size)]

    @staticmethod
    def static_run_creature(sim, cr, iterations):
        # static run creature to call run_creature helper funciton
        sim.run_creature(cr, iterations)
        return cr
    
    def eval_population(self, pop, iterations):
        """
        pop is a Population object
        iterations is frames in pybullet to run for at 240fps
        """
        pool_args = [] 
        start_ind = 0
        pool_size = len(self.sims)
        # split population into batch
        while start_ind < len(pop.creatures):
            this_pool_args = []
            for i in range(start_ind, start_ind + pool_size):
                if i == len(pop.creatures):
                    break
                # pic simulation instance to use
                sim_ind = i % len(self.sims)
                # store arguments needed to run creature
                this_pool_args.append([
                            self.sims[sim_ind], 
                            pop.creatures[i], 
                            iterations]   
                )
            pool_args.append(this_pool_args)
            start_ind = start_ind + pool_size

        new_creatures = []
        # run each multiprocessing pool
        for pool_argset in pool_args:
            with Pool(pool_size) as p:
                # it works on a copy of the creatures, so receive them
                creatures = p.starmap(ThreadedSim.static_run_creature, pool_argset)
                # and now put those creatures back into the main 
                # self.creatures array
                new_creatures.extend(creatures)
        pop.creatures = new_creatures
