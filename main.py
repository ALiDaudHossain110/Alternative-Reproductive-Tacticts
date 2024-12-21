# main.py
import pygame as pg
import pymunk
import constants as c
# from agents import Agent
from food import Food
import random
import time
import matplotlib.pyplot as plt
import neat
import os
import sys
from infofunc import screen, prnt, checkmouse, envtime, createAgent,agent_fitness,inter_genome,best_fitness_genome,save_genomes,upload_gen_info,load_genomes,extract_species_info
#from nn import run
# Initialize pygame
import visualize as v
pg.init()
space = pymunk.Space()

# Create a clock
clock = pg.time.Clock()

# Create game window
pg.display.set_caption("Alternative reproductive tactics (ARTs)")

# Create groups
agent_group = pg.sprite.Group()
food_group = pg.sprite.Group()
agent_group2 = pg.sprite.Group()

total_population= 100
# pop_set_num = 1

# Initial food population
initial_food = c.food_population
for _ in range(initial_food):
    food = Food()
    food_group.add(food)

#------------------------------------start of Eval_genomes()-----------------------------------

run = True  # Initialize the `run` variable to control the game loop
def eval_genomes(genomes, configg):
    # for gid1, gen2 in genomes:
    #     print(f"genomes id: {gid1} ")
    global agents, ge, nets, run, startGen,total_population

    start_time = time.time()
    startGen = False

    # Initialize the population only in the first generation
    if c.pop_set_num < 2:

        inter_genome(genomes,agent_group,configg)

    if c.pop_set_num >=2:

        # Clear previous generation's agents
        agent_group.empty()
        c.clear_agents()
        c.clear_ge()
        c.clear_nets()

        inter_genome(genomes,agent_group,configg)


        # # for i,genome_id, genome in enumerate(c.genomes_offspring):
        # for (gid, genome), agent, in zip(genomes, c.agents2):
        #     # for gid, ge in genome:
        #     # print("genomes type: ", type(genome))
        #     # print(f"genomes id: {gid} ")
        #     # agid=agent.genome.key
        #     # print(f"genomes id through agent: {gid} ")

        #     # print("c.agent in loop type: ", type(c.agents2[i]))
        #     # print("c.agent in loop : ", c.agents2[i])
        #     agent.left_wheel_speed=0
        #     agent.right_wheel_speed=0
        #     agent_group.add(agent) #sprite class of agents
        #     c.update_ge(genome)
        #     net = neat.nn.FeedForwardNetwork.create(agent.genome, configg)
        #     c.update_nets(net)
        #     c.update_agents(agent)



        # print("net: ",len(c.nets))
        # print("population len in hahahaha: ",len(agent_group))
        # print("population len in c,agent2: ",len(c.agents2))
        # print("genome len in hahahaha: ",len(genomes))

        # Now last_100_population contains the last 100 agents
        # print("the size of POP in: ",len(pop.population))
        agent_group2.empty()
        c.clear_agents2()
        c.clear_fitness()
        c.clear_ge2()
        c.clear_genome_id()
        c.clear_genomes_offspring()


        # c.agents2.clear()
        # print("the size of POP in before run: ",len(c.ge2))

  #--------------------------------RUN LOOP--------------------------------------------------

    while run:
        clock.tick(c.fps)
        screen.fill(c.BLACK)
        num_agent_on_screen = len(agent_group)

        if num_agent_on_screen > 0:
            agent_group.update(agent_group, agent_group2, food_group, configg)  # Updating groups
            agent_group.draw(screen)  # Drawing agents

        else:
            # print("pop.species: ",pop.species)
            # print("pop.population: ",pop.population)
            # print("pop.species: ",pop.generation)
            # Agents are all dead, move to next generation
            c.pop_set_num += 1
            
            # for p, g in pop.population:
            #     print("population: ", g )

            upload_gen_info(pop,genomes, pop.species.species)
 
            # Clear previous generation's agents
            agent_group.empty()
            c.clear_agents()
            c.clear_ge()
            c.clear_nets()
            # genomes.clear()
            # c.clear_fitness()
            # c.clear_ge2()
            # c.clear_genome_id()
            best_fitness_genome(configg)

            # print("population of offsprings: ", len(c.genomes_offspring))

            # Clear agent_group2 to avoid duplication
            # c.clear_agents2()
            # c.clear_fitness()
            # c.clear_ge2()
            # c.clear_genome_id()

         #   c.nets2.clear()
            # Set the flag to indicate the next generation can start
            startGen = True
            
            if startGen:
                break


        checkmouse(agent_group,configg,time.time())

        # Draw and update the food circles
        food_group.update(food_group)
        food_group.draw(screen)

        # Clock calculation
        clock_time = time.time() - start_time
        sec, min, hour = envtime(clock_time)

        # Print the number of agents on the screen
        population = len(agent_group)
        if population > 0:
            highest_generation = max(agent.generation_no for agent in agent_group)
            font = pg.font.Font(None, 20)
            text = font.render(f"Population: {population} Highest Generation: {highest_generation}", True, c.WHITE)
        text2 = font.render(f"CLOCK : {hour} hr: {min} min: {sec} sec", True, c.WHITE)
        text4 = font.render(f"Population set number: {c.pop_set_num}", True, c.WHITE)
        text3 = font.render(f"Agents children length: {len(agent_group2)}", True, c.WHITE)
        text5 = font.render(f"No. of food: {len(food_group)}", True, c.WHITE)
        prnt(text5, 0.7)
        prnt(text3, 0.5)
        prnt(text2, 0.8)
        prnt(text4, 0.3)
        prnt(text, 0.01)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                # upload_gen_info()
                run = False
                
        # Update agent states and fitness
        for i, agent in enumerate(c.agents):

            # c.ge[i].fitness = agent_fitness(agent,time.time())
            c.update_genome_fitness(i, agent_fitness(agent,time.time()))
            
            output = c.nets[i].activate(agent.data())
            output=c.softmax(output)
            # print(f"output: {output}")
            # if output[0] > 0.7:
            #     agent.state = 'moving_to_food'
            # if output[1] > 0.7:
            #     agent.state = 'searching_for_food'
            # if output[2] > 0.7:
            #     agent.state = 'mating as male'
            # if output[3] > 0.7:
            #     agent.state = 'mating as female'
            # if output[4] > 0.7:
            #     agent.state = 'wandering'
            output_0=output[0]
            output_1=output[1]
            output_2=output[2]
            output_3=output[3]
            output_4=output[4]

            # Map the outputs to a dictionary
            outputs = {
                'output_0': output_0,
                'output_1': output_1,
                'output_2': output_2,
                'output_3': output_3,
                'output_4': output_4
            }

            # Find the maximum value and the corresponding key
            max_output_key = max(outputs, key=outputs.get)
            max_output_value = outputs[max_output_key]

            # Output the result
            # print(f"The maximum value is {max_output_value} from {max_output_key}")

            if max_output_key == "output_0":
                agent.state = 'moving_to_food'
            if max_output_key == "output_1":
                agent.state = 'searching_for_food'
            if max_output_key == "output_2": 
                agent.state = 'mating as male'
            if max_output_key == "output_3":
                agent.state = 'mating as female'
            if max_output_key == "output_4":
                agent.state = 'wandering'

            c.update_agent_info(i, output[5], output[6], output[7],output[8],output[9]) 
        
            # agent.servival_time_weight=output[4]
            # agent.energy_weight=output[5]
            # agent.reproductive_success_weight=output[6]

        # Update display
        pg.display.flip()


def run(config_path):
    #print("Config path:", config_path)  # Debugging line
    global pop
    configg = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )
    #print("genome_config.single_structural_mutation",configg.genome_config.single_structural_mutation)
    # print(dir(configg.genome_config))
    # print(configg.genome_config.num_outputs)
    # print(configg.genome_config.output_keys)

    # if os.path.exists('dead_agents_info.pkl'):
    #     print("Loading saved genomes...")
    #     genomes = load_genomes('dead_agents_info.pkl')
    #     print("genomes", genomes.keys())

    #     if len(genomes) > 0:
    #         size = len(genomes)-1 # Last generation index
    #         print("Attempting to access generation:", size)

    #         agents = genomes[size]["agents"]  # Retrieve the saved agents
    #         genome = genomes[size]["genomes"]  # Retrieve the saved genomes
    #         species = genomes[size]["species"]  # Retrieve the saved genomes
    #         # print("genomes hhaaha", genome)
    #         # for g in genome:
    #         #     print("genome type: ",type(g))
    #         #     print("genome : ",g)
    #     # Recreate the population from the saved genomes
    #     # population, species, generation = genome  # Unpack the saved state
    #     # print("genomes", genome)
    #     pop = neat.Population(configg, initial_state=(genome,species,0))
    #     # for sid, sp in pop.species.species.items():
    #     #     print("Species ID: ", sid)
    #     #     print("Representative Genome ID: ", sp.representative.key)
    #     #     print("Members: ", list(sp.members.values()))
    #     #     print("Fitness: ", sp.fitness)
    #     #     print("Adjusted Fitness: ", sp.adjusted_fitness)
    # else:
    pop = neat.Population(configg)
        # for sid, sp in pop.species.species.items():
        #     print("Species ID: ", sid)
        #     print("Representative Genome ID: ", sp.representative.key)
        #     print("Members: ", list(sp.members.values()))
        #     print("Fitness: ", sp.fitness)
        #     print("Adjusted Fitness: ", sp.adjusted_fitness)
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
   # print(dir(configg))  # To list all attributes of the config object
    #print(configg.__dict__)  # To print out the actual configuration values
    winner=pop.run(eval_genomes, 100)
    print("winner genome: ", winner)

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config2.txt')
   # Setup NEAT Neural Network 
    run(config_path)
