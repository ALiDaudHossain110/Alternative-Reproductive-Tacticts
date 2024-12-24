#genome.py
import numpy as np
import constants as c
import random

class Genome():
    def __init__(self, shape=(6, 4), mean=0, std_dev=0.1):

        self.gene = np.random.normal(loc=mean, scale=std_dev, size=shape)
        # self.gene=np.clip(self.gene,0,1)
        self.id=c.geneCounter
        c.update_geneCounter(c.geneCounter+1)

    def reproduce(self, genome,male_genome, female_genome,g):
        
        
        offspring_gene=self.Mutate(self.CrossOver(genome,male_genome,female_genome,g), mutation_rate=0.1, standard_deviation=0.1)
        return offspring_gene

    def CrossOver(self, offspring_gene, male_genome, female_genome,g,crossover_rate=0.1):

        if np.random.rand() < crossover_rate:  # Check if crossover occurs
            # Take the first half from the male genome
            crossover_point=random.randint(1,4)
            for i in range(4):
                for j in range(crossover_point):  # First half (columns 0 to 3)
                    offspring_gene[i][j] = male_genome[i][j]

            # Take the second half from the female genome
            for i in range(4):
                for j in range(crossover_point, 4):  # Second half (columns 4 to 6)
                    offspring_gene[i][j] = female_genome[i][j]
            print("cross_Over has been done on",g)
        
        else:

            if g=="m":
                offspring_gene=male_genome
            if g=="f":
                offspring_gene=female_genome
        
        
        return offspring_gene



    def Mutate(self, offspring_gene, mutation_rate=0.1,standard_deviation=0.1):

        if np.random.rand() < mutation_rate:  # Check if mutation occurs
            # random_row=random.randint(0,5)
            # random_col=random.randint(0,3)
            # mutation = np.random.normal(0, standard_deviation)  # Gaussian mutation
            # gene=offspring_gene[random_row][random_col]
            # offspring_gene[random_row][random_col]=gene+mutation
            for i in range(6):
                for j in range(4):
                        # mutation = np.random.uniform(-mutation_amount, mutation_amount)  # Random change
                        mutation = np.random.normal(0, standard_deviation)  # Gaussian mutation
                        offspring_gene[i][j] += mutation  # Apply mutation
                        # Ensure the mutated value is within bounds (e.g., 0 to 1)
                        offspring_gene[i][j] = np.clip(offspring_gene[i][j], 0, 1)
            print("Mutation has been done on child")

        return offspring_gene

    

