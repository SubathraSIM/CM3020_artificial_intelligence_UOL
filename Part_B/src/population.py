# import required library
import creature 
import numpy as np

class Population:
    def __init__(self, pop_size, gene_count):
        # creates list of creatures for the population
        self.creatures = [creature.Creature(
                          gene_count=gene_count) 
                          for i in range(pop_size)]

    @staticmethod
    def get_fitness_map(fits):
        # total the fitness values
        total = sum(fits)
        # roulette-wheel selection cumulative fitness list
        fitmap = []
        total = 0
        for f in fits:
            total = total + f
            fitmap.append(total)
        return fitmap
    
    @staticmethod
    def select_parent(fitmap):
        # random number 0 to 1
        r = np.random.rand()
        r = r * fitmap[-1]
        # return the first index random numbers fits in the cumulative map
        for i in range(len(fitmap)):
            if r <= fitmap[i]:
                return i