# Import the required library 
import unittest
import population
import simulation 
import genome 
import creature 
import numpy as np
import os
from datetime import datetime
import glob

# expriment mode to run can change to motor_only, motor_only_blend also
EXPERIMENT = "baseline"

class TestGA(unittest.TestCase):
    def testBasicGA(self):
        # population of creatures
        pop = population.Population(pop_size=10, gene_count=3)
        # simulation, motor blend happens only on motor_only_blend mode
        sim = simulation.Simulation(motor_blend=(EXPERIMENT == "motor_only_blend"))
        # if mode is motor only or motor only blend, start with the same elite body
        if EXPERIMENT in ["motor_only", "motor_only_blend"]:
            path = "archive/Fitness_baseline/2026-01-01_20-41-50/elite_250.csv"
            # if the path exists
            if os.path.exists(path):
                basebody = genome.Genome.from_csv(path)
                # Give all creatures the same starting body
                for cr in pop.creatures:
                    cr.update_dna(basebody)
            else:
                # latest elite_250.csv under archieve
                latest = glob.glob(os.path.join("archive", "**", "elite_250.csv"), recursive=True)
                if latest:
                    # most recent added
                    path = max(latest, key=os.path.getmtime)
                    basebody = genome.Genome.from_csv(path)
                    # Give all creatures the same starting body
                    for cr in pop.creatures:
                        cr.update_dna(basebody)


        # new folder to save the csv with the timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        archive = os.path.join("archive", timestamp)
        os.makedirs(archive, exist_ok=True)

        # store best and mean fitness
        bestfitness = []
        meanfitness = []

        # run ga for 300 iterations
        for iteration in range(300):
            # look at each creature
            for cr in pop.creatures:
                sim.run_creature(cr, 2400)   
            # collect the gitness and links         
            fits = [cr.get_distance_travelled() 
                    for cr in pop.creatures]
            links = [len(cr.get_expanded_links()) 
                    for cr in pop.creatures]
            # save the best and mean fitness
            bestfitness.append(np.max(fits))
            meanfitness.append(np.mean(fits))
            # print statement
            print(iteration, "fittest:", np.round(np.max(fits), 3), 
                  "mean:", np.round(np.mean(fits), 3), "mean links", np.round(np.mean(links)), "max links", np.round(np.max(links)))       
            # fit map for roulette-wheel parent selection
            fit_map = population.Population.get_fitness_map(fits)
            # create the next generation
            new_creatures = []
            for i in range(len(pop.creatures)):
                # select 2 parents base on the fitness
                p1_ind = population.Population.select_parent(fit_map)
                p2_ind = population.Population.select_parent(fit_map)
                p1 = pop.creatures[p1_ind]
                p2 = pop.creatures[p2_ind]
                # child dna using crossover
                dna = genome.Genome.crossover(p1.dna, p2.dna)
                # point mutate motor only modes only motor genes change
                dna = genome.Genome.point_mutate(dna, rate=0.1, amount=0.25, motor_only=EXPERIMENT in ["motor_only", "motor_only_blend"])
                # if not in motor mode than allow shrink and grow mutate
                if not EXPERIMENT in ["motor_only", "motor_only_blend"]:
                    dna = genome.Genome.shrink_mutate(dna, rate=0.25)
                    dna = genome.Genome.grow_mutate(dna, rate=0.1)
                
                # new creature with the new dna
                cr = creature.Creature(1)
                cr.update_dna(dna)
                new_creatures.append(cr)
            
            # elitism
            max_fit = np.max(fits)
            for cr in pop.creatures:
                if cr.get_distance_travelled() == max_fit:
                    new_cr = creature.Creature(1)
                    new_cr.update_dna(cr.dna)
                    new_creatures[0] = new_cr
                    # save the csv for the generations
                    filename = os.path.join(archive, f"elite_{iteration}.csv")
                    genome.Genome.to_csv(cr.dna, filename)
                    break
            # replace old one to new generation
            pop.creatures = new_creatures

        # overall best fitness and mean fitness
        final_bestfitness = float(np.max(bestfitness)) if bestfitness else 0
        final_meanfitness = float(np.mean(meanfitness)) if meanfitness else 0
        # print statemetns
        print("Overall best fitness:", round(final_bestfitness, 3))
        print("Overall mean fitness:", round(final_meanfitness, 3))
        # fitness not equal to 0                       
        self.assertNotEqual(fits[0], 0)

unittest.main()