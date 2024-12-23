#infofunc.py
import pygame as pg
import constants as c
from agents import Agent
import random
import time
screen = pg.display.set_mode((c.screen_width, c.screen_height))
import neat
import pickle
import matplotlib.pyplot as plt
import numpy as np


def prnt(text, percentage):
    screen.blit(text, (c.screen_width*percentage, 5))


def prnt1(text, percentage):
    screen.blit(text, (c.screen_width*percentage, c.screen_height-20))

def checkmouse(agent_group):
        mouse_pos = pg.mouse.get_pos()
        # Check if mouse is hovering over any agent and display its energy level, age, and generation number
        for agent in agent_group:

            if agent.rect.collidepoint(mouse_pos):
                font = pg.font.Font(None, 24)
                hover_text = f"Energy: {agent.energy_level} Age: {agent.age} Generation: {agent.generation_no}"
                text_surface = font.render(hover_text, True, c.WHITE)
                hover_text2 = agent.calculate_movement_direction()
                text_surface2 = font.render(hover_text2, True, c.WHITE)
                hover_text3 = agent.state
                text_surface3 = font.render(hover_text3, True, c.WHITE)


                hover_text9 = f"Left Wheel speed: {agent.left_wheel_speed}"
                text_surface9 = font.render(hover_text9, True, c.WHITE)
                hover_text10 = f"Right Wheel Speed: {agent.right_wheel_speed}"
                text_surface10 = font.render(hover_text10, True, c.WHITE)
                screen.blit(text_surface, (mouse_pos[0] + 10, mouse_pos[1] + 10))
                screen.blit(text_surface2, (mouse_pos[0] + 10, mouse_pos[1] + 30))
                screen.blit(text_surface3, (mouse_pos[0] + 10, mouse_pos[1] + 50))
                screen.blit(text_surface9, (mouse_pos[0] + 10, mouse_pos[1] + 70))
                screen.blit(text_surface10, (mouse_pos[0] + 10, mouse_pos[1] + 90))


def envtime(clock_time):

    sec=int(clock_time)
    sec=sec%60
    min=int(clock_time/60)
    min=min%60
    hour=int(clock_time/60)
    hour=int(hour/60)

    return sec,min,hour
    

def createAgent( genome,time):
    initial_position = (random.randint(0, c.screen_width), random.randint(0, c.screen_height))
    # age = random.randint(5, 6)
    # age=1
    # gender = random.choice(["m", "f"])
    generation_no = 1
    # energy_level = random.randint(10, 12)
    energy_level = 100
    body_size = 6 
    agent = Agent(initial_position, generation_no, energy_level, body_size,genome,time)

    return agent

def agent_fitness(agent,time):
     energy=agent.energy_level*agent.energy_weight
     age=(time-agent.birth_time)*agent.servival_time_weight
     reproduction_success=agent.reproductive_success*agent.reproductive_success_weight
     return energy+age+reproduction_success



def cloneAgent(agent):

    new_pos_x = (agent.rect.x ) 
    new_pos_y = (agent.rect.y ) 
    new_pos = (new_pos_x, new_pos_y)

    new_age=agent.age
    new_generation_no = agent.generation_no
    new_energy_level =  agent.energy_level
    new_body_size = agent.body_size
    child_genome=agent.genome
    new_agent = Agent(new_pos, new_age, new_generation_no, new_energy_level, new_body_size,child_genome,time.time())
    return new_agent

def inter_genome(genome,agent_group):
            
    agent = createAgent(genome,time.time())
    agent.left_wheel_speed=0
    agent.right_wheel_speed=0
    c.dead_agent_bucket_list.append(agent)
    # genome.fitness = 0
    agent_group.add(agent) #sprite class of agents
    c.update_agents(agent)
    c.update_ge(genome)
    # print(genome.fitness)
    # c.genomes_archive [genome_id]=genome
    # c.add_genomes_archive(genome.id,genome)
    # print("genome: ",genome)

       

def best_fitness_genome(config):
         
    genomeid_new = []
    genomes_new = []
    genomeFitness_new = []
    agents_new = []
    # net_group=[]

    # Iterating over the original lists and appending to new lists
    for genome, gid, agent, genfit in zip(c.ge2, c.genome_id, c.agents2, c.fitness):
        genomeid_new.append(gid)
        genomes_new.append(genome)
        genomeFitness_new.append(genfit)
        agents_new.append(agent)
        # net_group.append(neat.nn.FeedForwardNetwork.create(genome, config))

    # Print the length of the new lists
    print(f"genomeid list has {len(genomeid_new)} elements.")
    print(f"genomes list has {len(genomes_new)} elements.")
    print(f"genomeFitness list has {len(genomeFitness_new)} elements.")
    print(f"agents list has {len(agents_new)} elements.")

    # zipped_list=list(zip(genomes_new,genomeFitness_new,genomeid_new,agents_new,net_group)) 
    zipped_list=list(zip(genomes_new,genomeFitness_new,genomeid_new,agents_new)) 

    zipped_list.sort(key=lambda x: x[1], reverse=True)
    print(f"Zipped list has {len(zipped_list)} elements.")

    top_100_zipped = zipped_list[:100]  # Slicing to get the first 100 items
    print(f"top_100_zipped list has {len(top_100_zipped)} elements.")

    # genomes,genomeFitness,genomeid,agents,net_group=zip(*top_100_zipped)
    genomes,genomeFitness,genomeid,agents=zip(*top_100_zipped)

    # c.ge2=[]
    # c.fitness=[]
    # c.genome_id=[]

    c.update_ge2(list(genomes))
    c.update_fitness(list(genomeFitness))
    c.update_genome_id(list(genomeid))
    c.update_agents2(list(agents))
    c.add_genome_to_offspring(list(genomes),list(genomeid))
    # c.dead_agent_genome_bucket_dict.clear()
    # c.dead_agent_genome_bucket_dict=list(agents)
    # for n in net_group:
    #     c.update_nets(n)

def save_genomes(filename, data):
    """Saves the genomes to a file."""
    with open(filename, 'wb') as f:
        pickle.dump(data, f)

def visualize_genome(genome, config):
    # Create a mapping for nodes and their positions
    node_positions = {}
    edges = []

    # Define positions based on the number of inputs and outputs
    num_inputs = config.num_inputs  # Assuming you have num_inputs defined in config
    num_outputs = config.num_outputs  # Assuming you have num_outputs defined in config

    # Get nodes and their types
    for node in genome.nodes.values():
        if node.key < num_inputs:  # Input nodes are indexed from 0 to num_inputs-1
            node_positions[node.key] = (node.key * 2, 1)  # Place input nodes in one row
        elif node.key < num_inputs + num_outputs:  # Output nodes follow input nodes
            node_positions[node.key] = (node.key * 2, 3)  # Place output nodes in a different row
        else:
            node_positions[node.key] = (node.key * 2, 2)  # Place hidden nodes in the middle row

    # Get connections
    for conn in genome.connections.values():
        if conn.enabled:  # Only draw enabled connections
            edges.append((conn.key[0], conn.key[1]))

    # Set up the plot
    plt.figure(figsize=(10, 6))
    ax = plt.gca()

    # Draw edges
    for start, end in edges:
        ax.plot(
            [node_positions[start][0], node_positions[end][0]],
            [node_positions[start][1], node_positions[end][1]],
            'k-'
        )

    # Draw nodes
    for node, pos in node_positions.items():
        circle = plt.Circle(pos, 0.1, color='b' if node.key < num_inputs + num_outputs else 'g')
        ax.add_artist(circle)
        ax.text(pos[0], pos[1], str(node.key), fontsize=12, ha='center', va='center', color='w')

    # Set limits and labels
    ax.set_xlim(-1, max(node_positions.keys()) * 2 + 1)
    ax.set_ylim(0, 4)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("NEAT Neural Network Visualization")
    plt.grid(False)
    plt.show()

def make_gen_agent_property_dict():
    # print(c.dead_agent_bucket_list)
    agent_dict={}

    for i,agent in enumerate(c.dead_agent_bucket_list):
        age=agent.age
        generation_no=agent.generation_no
        energy_level=agent.energy_level
        body_size=agent.body_size
        reproductive_success=agent.reproductive_success
        # reproductive_success_weight=agent.reproductive_success_weight
        # servival_time_weight=agent.servival_time_weight
        # energy_weight=agent.energy_weight
        no_of_matings_as_female=agent.no_of_matings_as_female
        no_of_matings_as_male=agent.no_of_matings_as_male
        pos=agent.pos
        genome=agent.genome.gene
        state_counter_dict=agent.state_counter_dict

        agent_dict[i]={
            "pos":pos,
            "age":age,
            "generation_no":generation_no,
            "energy_level":energy_level,
            "body_size":body_size,
            "reproductive_success":reproductive_success,
            # "reproductive_success_weight":reproductive_success_weight,
            # "servival_time_weight":servival_time_weight,
            # "energy_weight":energy_weight,
            "no_of_matings_as_female":no_of_matings_as_female,
            "no_of_matings_as_male":no_of_matings_as_male,
            # "genome id":genome.id,
            "genome":genome,
            "state_counter_dict":state_counter_dict
            }
    
    return agent_dict

def load_genomes(filename):
    """Loads genomes from a file."""
    with open(filename, 'rb') as f:
        return pickle.load(f)



def extract_species_info(species_set):
    """Extracts species information from the DefaultSpeciesSet."""
    species_info = []
    
    # Iterate over the species in the species_set
    for species_id, species in species_set.species.items():
        # Each species has a `members` dictionary where keys are genome IDs
        members = list(species.members.keys())  # Get genome IDs in the species
        # Append the species info
        species_info.append({'species_id': species_id, 'members': members})
    
    return species_info


def upload_gen_info():
    agent_dict = make_gen_agent_property_dict()

    # Use the length of dead_agent_genome_bucket_dict to determine the current generation
    current_generation = c.pop_set_num

    if current_generation not in c.dead_agent_genome_bucket_dict:
        c.dead_agent_genome_bucket_dict[current_generation] = {
            "agents": [],
            "genomes": []
        }
    # print("2",type(c.dead_agent_genome_bucket_dict))

    # Store the agent information
    c.dead_agent_genome_bucket_dict[current_generation]["agents"].extend(agent_dict.values())
    # print("3",type(c.dead_agent_genome_bucket_dict))

    for agent in c.dead_agent_bucket_list:
        c.dead_agent_genome_bucket_dict[current_generation]["genomes"].append(agent.genome.gene)
    # Save the updated dictionary
    save_genomes('dead_agents_info.pkl', c.dead_agent_genome_bucket_dict)

def get_gen_info():
    return c.dead_agent_genome_bucket_dict
