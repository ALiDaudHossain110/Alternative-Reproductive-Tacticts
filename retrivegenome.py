import pickle
from genome import Genome
from infofunc import inter_genome

def retrivegenome(filename, agent_group):
    with open(filename, 'rb') as file:  # Fixed: load from file object
        data = pickle.load(file)

    lastgen = max(data.keys())  # Assumes that the keys are generation numbers
    gen = data[lastgen]  # Get the list of agents for the latest generation

    for agent in gen["agents"]:
        genome = agent["genome"]
        gene=Genome()
        gene.gene=genome

        # print(genome)
        inter_genome(gene, agent_group, agent["generation_no"])  # Pass lastgen instead of hardcoded 1

def retriveselectedgenome(filename, agent_group,generation):
    with open(filename, 'rb') as file:  # Fixed: load from file object
        data = pickle.load(file)

    lastgen = generation  # Assumes that the keys are generation numbers
    print(lastgen)
    gen = data[lastgen]  # Get the list of agents for the latest generation

    for agent in gen["agents"]:
        genome = agent["genome"]
        gene=Genome()
        gene.gene=genome

        # print(genome)
        inter_genome(gene, agent_group, agent["generation_no"])  # Pass lastgen instead of hardcoded 1
