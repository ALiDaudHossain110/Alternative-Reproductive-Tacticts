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

    def reproduce(self, male_genome, female_genome):
        
        g1,g2=self.CrossOver(male_genome,female_genome)
        offspring_gene1,offspring_gene2=self.Mutate(g1,g2, mutation_rate=0.1, standard_deviation=0.1)
        return offspring_gene1,offspring_gene2

    def CrossOver(self, male_genome, female_genome,crossover_rate=0.1):


        offspring_1=male_genome
        offspring_2=female_genome

        if np.random.rand() < crossover_rate:  # Check if crossover occurs


            male_genome_flat = np.array(male_genome).flatten()
            female_genome_flat = np.array(female_genome).flatten()
            # Select a random crossover point (between 1 and length - 1)
            crossover_point = np.random.randint(1, len(male_genome_flat))

            # Perform the crossover
            offspring_flat_1 = np.concatenate([
                male_genome_flat[:crossover_point],  # Take first part from male
                female_genome_flat[crossover_point:]  # Take second part from female
            ])

            offspring_flat_2 = np.concatenate([
                female_genome_flat[:crossover_point],  # Take first part from male
                male_genome_flat[crossover_point:]  # Take second part from female
            ])

            # Reshaping the genom back to the original 2D shape
            offspring_1 = offspring_flat_1.reshape(len(male_genome), len(male_genome[0]))
            offspring_2 = offspring_flat_2.reshape(len(male_genome), len(male_genome[0]))
            print("cross over has been done on the offspring")
            return offspring_1 ,offspring_2






        
        
        return offspring_1,offspring_2



    def Mutate(self, offspring_gene1,offspring_gene2, mutation_rate=0.1,standard_deviation=0.1):

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
                        offspring_gene1[i][j] += mutation  # Apply mutation
                        # Ensure the mutated value is within bounds (e.g., 0 to 1)
                        # offspring_gene[i][j] = np.clip(offspring_gene[i][j], -1, 1)
            for i in range(6):
                for j in range(4):
                        # mutation = np.random.uniform(-mutation_amount, mutation_amount)  # Random change
                        mutation = np.random.normal(0, standard_deviation)  # Gaussian mutation
                        offspring_gene2[i][j] += mutation  # Apply mutation
                        # Ensure the mutated value is within bounds (e.g., 0 to 1)
                        # offspring_gene[i][j] = np.clip(offspring_gene[i][j], -1, 1)




            print("Mutation has been done on child")

        return offspring_gene1,offspring_gene2

    

