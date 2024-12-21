#constants.py
import pygame as pg
import numpy as np

clock = pg.time.Clock()


# Screen dimensions
screen_width = 1300
screen_height = 700

# screen_width = 250
# screen_height = 250

# Frames per second
# fps = 49
fps = 2400
life_timestep=5000
loop_counter=0
post_mating_state_timer_counter=4
mating_state_timer_counter=4
def update_loop_counter(x):
    global loop_counter
    loop_counter=x


# Body size range
min_body_size = 5
max_body_size = 20

# Initialize the screen and set display mode
screen = pg.display.set_mode((screen_width, screen_height))
pg.display.set_caption("Alternative Reproductive Tactics (ARTs)")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (0, 0, 255)  # Added for the marker color

# Time intervals
age_increment_interval = 25  # seconds
food_spawn_chance = 0.1  # Adjust the value as needed
energy_decrease_interval = 15  # Decrease energy level every 5 seconds

food_population=100
genomeid=100

geneCounter=0

def update_geneCounter(x):
    global geneCounter
    geneCounter=x


#using in min.py and other files
agents = []
ge = []
nets = []
genomes_offspring={}
genomes_archive={}

#using in agents.py
male_parent = []
female_parent = []
agents2 = []
ge2 = []
fitness = []
genome_id=[]

#config_id = []
# nets2 = []
# agent_pos=[]
# generation_num=[]



pop_set_num = 0


bestgenome=None

pop_prev_gen={}



def update_ge(input_genome):
    
    global ge
    ge.append(input_genome)

def clear_ge():
    global ge
    ge.clear()
    ge=[]



def update_agents(input_agent):
    global agents
    agents.append(input_agent)

def clear_agents():
    global agents
    agents.clear()
    agents=[]



def update_nets(input_net):
    global nets
    nets.append(input_net)

def clear_nets():
    global nets
    nets.clear()
    nets=[]


#----------best_fitness_genome()-----------
def update_ge2(new_list):
    """
    Updates or reassigns the global ge2 list.
    This function ensures changes are reflected globally.
    """
    global ge2
    ge2.clear()
    ge2 = new_list

def clear_ge2():
    global ge2
    ge2.clear()
    ge2=[]

def update_fitness(new_list):
    """
    Updates or reassigns the global ge2 list.
    This function ensures changes are reflected globally.
    """
    global fitness
    fitness.clear()
    fitness = new_list

def clear_fitness():
    global fitness
    fitness.clear()
    fitness=[]


def update_genome_id(new_list):
    """
    Updates or reassigns the global ge2 list.
    This function ensures changes are reflected globally.
    """
    global genome_id
    genome_id.clear()
    genome_id = new_list

def clear_genome_id():
    global genome_id
    genome_id.clear()
    genome_id=[]
 
def update_agents2(new_list):
    """
    Updates or reassigns the global ge2 list.
    This function ensures changes are reflected globally.
    """
    global agents2
    agents2.clear()
    agents2 = new_list

def clear_agents2():
    global agents2
    agents2.clear()
    agents2=[]


def clear_genomes_offspring():
    """
    Updates or reassigns the global ge2 list.
    This function ensures changes are reflected globally.
    """
    global genomes_offspring
    genomes_offspring.clear()


# def add_genome_to_offspring(genom_list,genomeid):
#     """Adds a genome to the genomes_offspring dictionary."""
#     global genomes_offspring

#     genomes_offspring.clear()
#       # Add or update the genome entry
#     for genome, gid in zip(genom_list,genomeid):
#         genomes_offspring [gid]=genome
#         add_genomes_archive(gid,genome)


# def add_genomes_archive(genome_id, genome_object):
#     """Adds a genome to the genomes_offspring dictionary."""
#     global genomes_archive
#     genomes_archive[genome_id] = genome_object  # Add or update the genome entry



def update_genome_fitness(iternum, fitness):
    
    global ge
    ge[iternum].fitness=fitness



# Softmax function
def softmax(x):
    exp_x = np.exp(x - np.max(x))  # Subtract max(x) for numerical stability
    return exp_x / np.sum(exp_x)

# def update_agent_info(agent,output4, output5,output6):
def update_agent_info(agent,output6):
    global agents

    if output6<=0.5:
        agent.dir_selec=0
    else:
        agent.dir_selec=1
    
    # value=softmax(np.array([output4, output5]))
    # # Scale to a maximum of 3
    # output4 = value[0] * 3
    # output5 = value[1] * 3

    # # Clamping the values to be within [-3, 3]
    # output4 = round(max(min(3, output4),-3),2)
    # output5 = round(max(min(3, output5),-3),2)

    # if output4 > 3:
    #     print(f"Warning: Left wheel speed exceeded 3: {output4}")
    # if output5 > 3:
    #     print(f"Warning: Right wheel speed exceeded 3: {output5}")

    # # Assign the calculated wheel speeds to the agent
    # agent.left_wheel_speed = output4
    # agent.right_wheel_speed = output5

    # # Debugging print statement in case values exceed 3
    # if output4 > 3:
    #     print(f"Warning: Left wheel speed exceeded 3: {output4}")
    # if output5 > 3:
    #     print(f"Warning: Right wheel speed exceeded 3: {output5}")


def add_agent_at_reproduction_file(agent):
    global agents2
    agents2= agent+agents2


def add_ge_at_reproduction_file(ge):
    global ge2
    ge2= ge+ge2


def add_geid_at_reproduction_file(geid):
    global genome_id
    genome_id= geid+genome_id

def add_gefitness_at_reproduction_file(geFitness):
    
    global fitness
    fitness= geFitness+fitness

def add_nets_at_reproduction_file(new_nets):
    global nets
    nets=new_nets+nets

dead_agent_bucket_list=[]
dead_agent_genome_bucket_dict={}

def clear_dead_agent_bucket_list():
    global dead_agent_bucket_list
    dead_agent_bucket_list=[]