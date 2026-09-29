# Import the required library
import unittest
import simulation
import creature
import population

class TestSim(unittest.TestCase):
    # checks that we can create the simulation
    def testSimExists(self):
        sim = simulation.Simulation()
        self.assertIsNotNone(sim)

    # checks that simulation has client id
    def testSimId(self):
        sim = simulation.Simulation()
        self.assertIsNotNone(sim.physicsClientId)

    # run_creature method exist
    def testRun(self):
        sim = simulation.Simulation()
        self.assertIsNotNone(sim.run_creature)

    # check that the creature move
    def testPos(self):
        sim = simulation.Simulation()
        cr = creature.Creature(gene_count = 3)
        sim.run_creature(cr)
        self.assertNotEqual(cr.start_position, cr.last_position)
    
    # run all creatures and get distance travelled
    def testPop(self):
        pop = population.Population(pop_size=5, gene_count=3)
        sim = simulation.Simulation()
        for cr in pop.creatures:
            sim.run_creature(cr)
        dists = [cr.get_distance_travelled() for cr in pop.creatures]
        print(dists)
        self.assertIsNotNone(dists)

    # checks eval_population runs
    def testProcNoThread(self):
        pop = population.Population(pop_size=20, gene_count=3)
        sim = simulation.Simulation()
        sim.eval_population(pop, 2400)
        dists = [cr.get_distance_travelled() for cr in pop.creatures]
        print(dists)
        self.assertIsNotNone(dists)

unittest.main()
